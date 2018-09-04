import re
import discord
import logging
import math
import datetime
import urllib
import asyncio
from urllib.request import Request, urlopen
from utils import checks
import lavalink
import random
import requests
from utils import arghelp
from utils import Token
from discord.ext import commands

url_re = re.compile('https?:\/\/(?:www\.)?.+')

class music:

    def __init__(self, bot):
        self.bot = bot
        self.timeout = bot.loop.create_task(self.check_timeout())
        if not hasattr(bot, 'lavalink'):
            lavalink.Client(ws_port=2086, rest_port=2333, bot=bot, password='youshallnotpass', shard_count=self.bot.shard_count, loop=self.bot.loop, log_level=logging.DEBUG)
            self.bot.lavalink.register_hook(self._events)

    async def _events(self, event):
        if isinstance(event, lavalink.Events.TrackStartEvent):
            channel = event.player.fetch('channel')
            author = discord.utils.get(self.bot.get_all_members(), id=event.track.requester)
            if channel:
                channel = self.bot.get_channel(channel)
                if channel:
                    s=discord.Embed()
                    s.set_author(name="Now Playing", url=event.track.uri)
                    s.add_field(name="Song", value="[{}]({})".format(event.track.title, event.track.uri), inline=False)
                    s.add_field(name="Duration", value=self.format_time(event.track.duration))
                    if author:
                        s.set_footer(text="Requested by {}".format(author), icon_url=author.avatar_url)
                    s.set_thumbnail(url=event.track.thumbnail)
                    await channel.send(embed=s)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            channel = event.player.fetch('channel')
            if channel:
                channel = self.bot.get_channel(channel)
                if channel:
                    await channel.send("There are no more songs left in the queue.")
        elif isinstance(event, lavalink.Events.TrackEndEvent):
            try:
                event.player.delete("votes")
            except:
                pass
        
    def __unload(self):
        self.timeout.cancel()
                
    @commands.command(aliases=["summon"])
    async def join(self, ctx):
        """Make the bot join your current voice channel"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.is_connected:
            if len(set(filter(lambda m: not m.bot, player.connected_channel.members))) == 0 or ctx.author.id == player.fetch("sessionowner"):
                if not ctx.author.voice or not ctx.author.voice.channel:
                    return await ctx.send("You are not in a voice channel :no_entry:")
                player.store('sessionowner', ctx.author.id)
                player.store('channel', ctx.channel.id)
                await player.connect(ctx.author.voice.channel.id)
                await ctx.send("Summoned to `{}` <:done:403285928233402378>".format(ctx.author.voice.channel.name))
            else:
                return await ctx.send("I'm already in a voice channel :no_entry:")
        else:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in a voice channel :no_entry:")
            player.store('sessionowner', ctx.author.id)
            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
            await ctx.send("Summoned to `{}` <:done:403285928233402378>".format(ctx.author.voice.channel.name))

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, query):
        """Play something by query or link"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        query = query.strip('<>')
        if player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("I'm already in a voice channel :no_entry:")
        else:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in a voice channel :no_entry:")
            else:
                player.store('sessionowner', ctx.author.id)
                player.store('channel', ctx.channel.id)
                await player.connect(ctx.author.voice.channel.id)
        if not url_re.match(query):
            query = "ytsearch:{}".format(query)
        results = await self.bot.lavalink.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send("I could not find any songs matching that query :no_entry:")
        s=discord.Embed()
        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            s.description = "Enqueued {} with **{}** tracks <:done:403285928233402378>".format(results['playlistInfo']['name'], len(tracks))
            await self.bot.get_channel(player.fetch('channel')).send(embed=s)
        else:
            track = results["tracks"][0]
            player.add(requester=ctx.author.id, track=track)
            timetill = 0
            for x in player.queue:
                timetill += x.duration
            if player.current:
                timetill += player.current.duration - player.position
            else:
                timetill = 0 
            index = [x.track for x in player.queue].index(track["track"]) + 1
            s.set_author(name="Added to Queue", icon_url=ctx.author.avatar_url)
            s.set_thumbnail(url="https://img.youtube.com/vi/{}/default.jpg".format(track["info"]["identifier"]))
            s.add_field(name="Song", value="[{}]({})".format(track["info"]["title"], track["info"]["uri"]), inline=False)
            s.add_field(name="Duration", value=self.format_time(track["info"]["length"]), inline=True)
            s.add_field(name="Position in Queue", value=index)
            if timetill != 0:
                s.add_field(name="Estimated time till playing", value=self.format_time(timetill-track["info"]["length"]))
            else:
                s.add_field(name="Estimated time till playing", value="Next")
            await self.bot.get_channel(player.fetch('channel')).send(embed=s)
        if not player.is_playing:
            await player.play()

    @commands.command()
    async def playlist(self, ctx, *, query):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("I'm already in a voice channel :no_entry:")
        else:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in a voice channel :no_entry:")
            else:
                player.store('sessionowner', ctx.author.id)
                player.store('channel', ctx.channel.id)
                await player.connect(ctx.author.voice.channel.id)
        url = "https://www.googleapis.com/youtube/v3/search?key=" + Token.youtube() + "&part=snippet&safeSearch=none&maxResults=10&type=playlist&{}".format(urllib.parse.urlencode({"q": query}))
        request = requests.get(url).json()
        try:
            request["items"][0]
        except:
            return await ctx.send("No results :no_entry:")
        msg = ""
        for i, x in enumerate(request["items"], start=1):
            msg += "{}. [{}]({})\n".format(i, x["snippet"]["title"], "https://www.youtube.com/playlist?list=" + x["id"]["playlistId"])
        message = await ctx.send(embed=discord.Embed(description=msg).set_footer(text="Choose a number to queue the playlist | cancel"))
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and (m.content.isdigit() or m.content.lower() == "cancel")
        try:
            response = await self.bot.wait_for("message", check=check, timeout=60)
            if response.content.lower() == "cancel":
                try:
                    await response.delete()
                    await message.delete()
                    return
                except:
                    pass
            elif int(response.content) > i or int(response.content) < 1:
                await response.delete()
                await message.delete()
                return await ctx.send("Invalid index :no_entry:")
            else:
                results = await self.bot.lavalink.get_tracks("https://www.youtube.com/playlist?list=" + request["items"][int(response.content) - 1]["id"]["playlistId"])
                tracks = results["tracks"]
                for track in tracks:
                    player.add(requester=ctx.author.id, track=track)
                s=discord.Embed()
                s.description = "Enqueued {} with **{}** tracks <:done:403285928233402378>".format(results['playlistInfo']['name'], len(tracks))
                await message.delete()
                await response.delete()
                await self.bot.get_channel(player.fetch('channel')).send(embed=s)
                if not player.is_playing:
                    await player.play()
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")

    @commands.command()
    async def search(self, ctx, *, query):
        """Search for a song on youtube and play it"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        query = "ytsearch:{}".format(query)
        if player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel or player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("I'm already in a voice channel :no_entry:")
        else:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in a voice channel :no_entry:")
            else:
                player.store('sessionowner', ctx.author.id)
                player.store('channel', ctx.channel.id)
                await player.connect(ctx.author.voice.channel.id)
        results = await self.bot.lavalink.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send("I could not find any songs matching that query :no_entry:")
        msg = ""
        for i, x in enumerate(results["tracks"][:10], start=1):
            msg += "{}. **[{}]({})**\n".format(i, x["info"]["title"], x["info"]["uri"])
        message = await ctx.send(embed=discord.Embed(description=msg).set_footer(text="Choose a number to queue the song | cancel"))
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and (m.content.isdigit() or m.content.lower() == "cancel")
        try:
            response = await self.bot.wait_for("message", check=check, timeout=60)
            if response.content.lower() == "cancel":
                try:
                    await response.delete()
                    return await message.delete()
                except:
                    pass
            elif int(response.content) > i or int(response.content) < 1:
                await response.delete()
                await message.delete()
                return await ctx.send("Invalid index :no_entry:")
            else:
                track = results["tracks"][int(response.content) - 1]
                player.add(requester=ctx.author.id, track=track)
                timetill = 0
                for x in player.queue:
                    timetill += x.duration
                if player.current:
                    timetill += player.current.duration - player.position
                else:
                    timetill = 0 
                index = [x.track for x in player.queue].index(track["track"]) + 1
                s=discord.Embed()
                s.set_author(name="Added to Queue", icon_url=ctx.author.avatar_url)
                s.set_thumbnail(url="https://img.youtube.com/vi/{}/default.jpg".format(track["info"]["identifier"]))
                s.add_field(name="Song", value="[{}]({})".format(track["info"]["title"], track["info"]["uri"]), inline=False)
                s.add_field(name="Duration", value=self.format_time(track["info"]["length"]), inline=True)
                s.add_field(name="Position in Queue", value=index)
                if timetill != 0:
                    s.add_field(name="Estimated time till playing", value=self.format_time(timetill-track["info"]["length"]))
                else:
                    s.add_field(name="Estimated time till playing", value="Next")
                await response.delete()
                await message.delete()
                await self.bot.get_channel(player.fetch('channel')).send(embed=s)
                if not player.is_playing:
                    await player.play()
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")

    @commands.command(aliases=["leave", "dc", "stop"])
    async def disconnect(self, ctx):
        """Make the bot end the queue and leave"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not currently connected to a voice channel :no_entry:")
        if not ctx.author.voice or (player.is_connected and player.connected_channel.id != ctx.author.voice.channel.id):
            return await ctx.send("You have to be in my voice channel to disconnect :no_entry:")
        if player.fetch("sessionowner") == ctx.author.id:
            player.queue.clear()
            await player.disconnect()
            player.delete("votes")
            await ctx.send("Disconnected <:done:403285928233402378>")
        else:
            await ctx.send("Only the session owner can disconnect the bot :no_entry:")

    @commands.command(aliases=["np", "now"])
    async def nowplaying(self, ctx):
        """Check what is currently playing"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.current:
            requester = discord.utils.get(self.bot.get_all_members(), id=player.current.requester)
            s=discord.Embed()
            s.set_author(name="Now Playing", icon_url=ctx.author.avatar_url)
            s.set_footer(text="Requested by {}".format(requester), icon_url=requester.avatar_url)
            s.set_thumbnail(url=player.current.thumbnail)
            s.add_field(name="Song", value="[{}]({})".format(player.current.title, player.current.uri), inline=False)
            s.add_field(name="Duration", value="{}/{}".format(self.format_time(player.position), self.format_time(player.current.duration)))
            await ctx.send(embed=s)
        else:
            return await ctx.send("Nothing is currently playing :no_entry:")

    @commands.command()
    async def rebind(self, ctx, channel: discord.TextChannel=None):
        """Rebind the text channel all the music notifications are being sent to"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not channel:
            channel = ctx.channel
        if player.fetch('sessionowner') == ctx.author.id or player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            player.store('channel', channel.id)
            await ctx.send("Messages will now be sent in {} <:done:403285928233402378>".format(channel.mention))
        else:
            return await ctx.send("You are not the session owner :no_entry:")

    @commands.command(aliases=["resume", "unpause"])
    async def pause(self, ctx):
        """Pause the music that is currently playing"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members): 
            if player.paused:
                await player.set_pause(False)
                await ctx.send("Resumed.")
            else:
                await player.set_pause(True)
                await ctx.send("Paused.")
        elif player.fetch("sessionowner") == ctx.author.id:
            if player.paused:
                await player.set_pause(False)
                await ctx.send("Resumed.")
            else:
                await player.set_pause(True)
                await ctx.send("Paused.")
        else:
            return await ctx.send("You are not the session owner :no_entry:")

    @commands.command()
    async def rewind(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if player.current.requester not in map(lambda c: c.id, player.connected_channel.members) and player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members): 
            await ctx.send("Rewound ⏪")
            await player.seek(0)
        elif player.current.requester == ctx.author.id or player.fetch("sessionowner") == ctx.author.id:
            await ctx.send("Rewound ⏪")
            await player.seek(0)
        else:
            return await ctx.send("You are not the session owner or the user who requested this song :no_entry:")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if player.current.requester not in map(lambda c: c.id, player.connected_channel.members) and player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            await ctx.send("Skipped.")
            await player.skip()
        else:
            if player.current.requester == ctx.author.id:
                await ctx.send("Skipped.")
                await player.skip()
            else:
                minpeople = math.ceil(len(set(filter(lambda x: not x.bot, player.connected_channel.members)))/2)
                votes = player.fetch("votes") if player.fetch("votes") else 0
                player.store("votes", votes + 1)
                if votes + 1 >= minpeople:
                    await ctx.send("Skipped.")
                    await player.skip()
                else:
                    await ctx.send("Skip? {}/{}".format(votes + 1, minpeople))


    @commands.command()
    async def remove(self, ctx, index: int):
        """Remove a song from the queue"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if not player.queue:
            return await ctx.send('Nothing is queued :no_entry:')
        if index > len(player.queue) or index < 1:
            return await ctx.send("Invalid song index :no_entry:")
        if player.queue[index-1].requester not in map(lambda c: c.id, player.connected_channel.members) and player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            index -= 1
            removed = player.queue.pop(index)
            await ctx.send("Removed **" + removed.title + "** from the queue <:done:403285928233402378>")
        elif player.queue[index-1].requester == ctx.author.id or player.fetch("sessionowner") == ctx.author.id:
            index -= 1
            removed = player.queue.pop(index)
            await ctx.send("Removed **" + removed.title + "** from the queue <:done:403285928233402378>")
        else:
            return await ctx.send("You are not the session owner or the user who requested this song :no_entry:")

    @commands.command()
    async def repeat(self, ctx):
        """Repeat the queue"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        player.repeat = not player.repeat
        if player.fetch('sessionowner') == ctx.author.id or player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            await ctx.send("Repeat turned **{}**".format("On" if player.repeat else "Off"))
        else:
            await ctx.send("You are not the session owner :no_entry:")

    @commands.command()
    async def shuffle(self, ctx):
        """Shuffle the queue"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if player.fetch('sessionowner') == ctx.author.id or player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            random.shuffle(player.queue)
            await ctx.send("The queue has been shuffled <:done:403285928233402378>")
        else:
            await ctx.send("You are not the session owner :no_entry:")

    @commands.command()
    async def queue(self, ctx, page=None):
        """View the queue for the current server"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send("There is nothing queued at the moment :no_entry:")
        if not page:
            page = 1
        try:
            page = int(page)
        except:
            if page == "clear":
                player.queue.clear()
                return await ctx.send("The queue has been cleared <:done:403285928233402378>")
            else:
                return await ctx.send("Inalid Page :no_entry:")
        if page < 1:
            return await ctx.send("Invalid Page :no_entry:")
        if page - 1 > math.ceil(len(player.queue)/10):
            return await ctx.send("Invalid Page :no_entry:")
        msg = ""
        for i, x in enumerate(player.queue[page*10-10:page*10], start=page*10-9):
            msg += "{}. [{}]({})\n".format(i, x.title, x.uri)
        await ctx.send(embed=discord.Embed(title="Queue for {}".format(ctx.guild.name), description=msg).set_footer(text="Page {}/{}".format(page, math.ceil(len(player.queue)/10))))

    @commands.command(hidden=True)
    async def connected(self, ctx):
        players = self.bot.lavalink.players
        msg = ""
        totallis, totalcon = 0, 0
        for x in players:
            player = x[1]
            if player.is_connected:
                listeners = len(set(filter(lambda x: not x.bot, player.connected_channel.members)))
                totallis += listeners
                totalcon += 1
                msg += "{} connected with {} {}\n".format(player.connected_channel.guild, listeners, "listener" if listeners == 1 else "listeners")
        if msg:
            await ctx.send(embed=discord.Embed(description=msg).set_footer(text="Total Connections: {} | Total Listeners: {}".format(totalcon, totallis)))
        else:
            await ctx.send("No connections :no_entry:")

    @commands.command(hidden=True)
    @checks.is_owner()
    async def forcedisconnect(self, ctx, *, server):
        server = discord.utils.get(self.bot.guilds, name=server)
        player = self.bot.lavalink.players.get(server.id)
        await player.connect([x.id for x in server.voice_channels][0])
        await player.disconnect()
        await ctx.send("Disconnected.")

    def format_time(self, time):
        h, r = divmod(time / 1000, 3600)
        m, s = divmod(r, 60)
        if h == 0:
            return '%02d:%02d' % (m, s)
        else:
            return '%02d:%02d:%02d' % (h, m, s)       

    async def check_timeout(self):
        while not self.bot.is_closed():
            for x in self.bot.lavalink.players:
                player = x[1]
                channel = self.bot.get_channel(player.fetch("channel"))
                if player.is_connected:
                    if len(set(filter(lambda x: not x.bot, player.connected_channel.members))) == 0:
                        if not player.fetch("nousers"):
                            player.store("nousers", datetime.datetime.utcnow().timestamp())
                        else:
                            if datetime.datetime.utcnow().timestamp() - player.fetch("nousers") >= 100:
                                player.queue.clear()
                                await player.disconnect()
                                player.delete("votes")
                                player.delete("nousers")
                                if channel:
                                    await channel.send("No one has been in the voice channel for 2 minutes :wave:")
                    else:
                        player.delete("nousers")
            await asyncio.sleep(45)

def setup(bot):
    bot.add_cog(music(bot))
