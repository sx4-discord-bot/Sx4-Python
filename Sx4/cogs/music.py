import re
import discord
import logging
import math
import datetime
import urllib
import asyncio
from urllib.request import Request, urlopen
from utils import checks, paged
import lavalink
import random
import requests
from utils import arghelp
from utils import Token
from discord.ext import commands

url_re = re.compile('https?:\/\/(?:www\.)?.+')

class music:

    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
        self.votes = []
        self.timeout = bot.loop.create_task(self.check_timeout())
        if not hasattr(bot, 'lavalink'):
            lavalink.Client(ws_port=2086, rest_port=2333, bot=bot, password='youshallnotpass', shard_count=self.bot.shard_count, loop=self.bot.loop, log_level=logging.DEBUG)
            self.bot.lavalink.register_hook(self._events)

    async def _events(self, event):
        if isinstance(event, lavalink.Events.TrackStartEvent):
            if event.player.guild_id not in map(lambda x: x["id"], self.votes):
                self.votes.append({"id": event.player.guild_id, "votes": []})
            else:
                list(filter(lambda x: x["id"] == event.player.guild_id, self.votes))[0]["votes"] = []
            channel = event.player.fetch('channel')
            author = self.bot.get_user(event.track.requester)
            guild = self.bot.get_guild(int(event.player.guild_id))
            if channel:
                channel = guild.get_channel(channel)
                if channel:
                    s=discord.Embed()
                    s.set_author(name="Now Playing", url=event.track.uri)
                    s.add_field(name="Song", value="[{}]({})".format(event.track.title, event.track.uri), inline=False)
                    s.add_field(name="Duration", value=self.format_time(event.track.duration) if not event.track.stream else "Stream (Unknown)")
                    if author:
                        s.set_footer(text="Requested by {}".format(author), icon_url=author.avatar_url)
                    s.set_thumbnail(url=event.track.thumbnail)
                    await channel.send(embed=s)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            channel = event.player.fetch('channel')
            guild = self.bot.get_guild(int(event.player.guild_id))
            if channel:
                channel = guild.get_channel(channel)
                if channel:
                    await channel.send(embed=discord.Embed(title="Queue Ended", description="If you enjoyed it would be greatly appreciated if you upvoted the bot, you can do so here: **https://discordbots.org/bot/440996323156819968/vote**\n\nIf you enjoy using Sx4 and want to go that extra mile and help Sx4 run you can donate here: **https://www.patreon.com/Sx4**"))
        
    def __unload(self):
        self.timeout.cancel()

    @commands.command()
    async def seek(self, ctx, position: str):
        """Skip forwards or backwards in a song or set the exact time with the format hh:mm:ss"""
        position_re = re.compile("(?:([0-9]+):|)([0-9]+):([0-9]+)")
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not in a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if not player.current.can_seek:
            return await ctx.send("You cannot seek in this song, this may be because it's a stream :no_entry:")
        if player.fetch('sessionowner') == ctx.author.id or player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            match = position_re.match(position)
            if match:
                hours = int(match.group(1)) if match.group(1) else 0
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                time = ((hours * 3600) + (minutes * 60) + seconds) * 1000
            elif position.isdigit():
                time = player.position + int(position) * 1000
            elif position.startswith("-"):
                time = player.position + -(int(position[1:]) * 1000)
            else:
                return await ctx.send("Invalid time format :no_entry:")
            await player.seek(time)
            await ctx.send("Player time is now at **{}**".format(self.format_time(time)))
        else:
            return await ctx.send("You are not the session owner :no_entry:")
                
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
    async def play(self, ctx, *, query=None):
        """Play something by query or link"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if ctx.message.attachments and not query:
            query = ctx.message.attachments[0].url
        elif not ctx.message.attachments and not query:
            return await arghelp.send(self.bot, ctx)
        else:
            query = query.strip('<>').replace("music.", "")
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
            await ctx.send(embed=s)
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
            s.add_field(name="Duration", value=self.format_time(track["info"]["length"]) if not track["info"]["isStream"] else "Stream (Unknown)", inline=True)
            s.add_field(name="Position in Queue", value=index)
            if timetill != 0:
                s.add_field(name="Estimated time till playing", value=self.format_time(timetill-track["info"]["length"]))
            else:
                s.add_field(name="Estimated time till playing", value="Next")
            await ctx.send(embed=s)
        if not player.is_playing:
            await player.play()

    @commands.command()
    async def playnow(self, ctx, *, query=None):
        """Play something by query or link"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if ctx.message.attachments and not query:
            query = ctx.message.attachments[0].url
        elif not ctx.message.attachments and not query:
            return await arghelp.send(self.bot, ctx)
        else:
            query = query.strip('<>').replace("music.", "")
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
        if player.fetch("sessionowner") in map(lambda c: c.id, player.connected_channel.members) and player.fetch("sessionowner") != ctx.author.id:
            return await ctx.send("You have to be the session owner to use this command :no_entry:")
        if not url_re.match(query):
            query = "ytsearch:{}".format(query)
        results = await self.bot.lavalink.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send("I could not find any songs matching that query :no_entry:")
        s=discord.Embed()
        if results["loadType"] == "PLAYLIST_LOADED":
            queue_length = len(player.queue)
            tracks = results["tracks"]
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            if queue_length != 0:
                player.queue[:queue_length], player.queue[queue_length:] = player.queue[queue_length:], player.queue[:queue_length]
            s.description = "Enqueued {} with **{}** tracks <:done:403285928233402378>".format(results['playlistInfo']['name'], len(tracks))
            await ctx.send(embed=s)
        else:
            queue_length = len(player.queue)
            track = results["tracks"][0]
            player.add(requester=ctx.author.id, track=track)
            if queue_length != 0:
                player.queue[:queue_length], player.queue[queue_length+1:] = player.queue[queue_length+1:], player.queue[:queue_length]
            s.set_author(name="Added to Queue", icon_url=ctx.author.avatar_url)
            s.set_thumbnail(url="https://img.youtube.com/vi/{}/default.jpg".format(track["info"]["identifier"]))
            s.add_field(name="Song", value="[{}]({})".format(track["info"]["title"], track["info"]["uri"]), inline=False)
            s.add_field(name="Duration", value=self.format_time(track["info"]["length"]) if not track["info"]["isStream"] else "Stream (Unknown)", inline=True)
            s.add_field(name="Position in Queue", value="Next")
            s.add_field(name="Estimated time till playing", value="Next")
            await ctx.send(embed=s)
        if not player.is_playing:
            await player.play()
        await player.skip()

    @commands.command()
    async def movesong(self, ctx, track_index: int, new_index: int):
        """Moves a song index to another index in the queue"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.fetch("sessionowner") in map(lambda c: c.id, player.connected_channel.members) and player.fetch("sessionowner") != ctx.author.id:
            return await ctx.send("You have to be the session owner to use this command :no_entry:")
        if (new_index < 1 or new_index > len(player.queue)) or (track_index < 1 or track_index > len(player.queue)):
            return await ctx.send("Invalid Index :no_entry:")
        new_index -= 1
        track_index -= 1
        track = player.queue[track_index:track_index + 1][0]
        player.queue.pop(track_index)
        player.queue.insert(new_index, track)
        await ctx.send("Moved **{}** to index {} <:done:403285928233402378>".format(track.title, new_index + 1))

    @commands.command()
    async def playlist(self, ctx, *, query):
        """Search for an play a playlist from youtube"""
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
        if not request["items"]:
            return await ctx.send("No results :no_entry:")
        event = await paged.page(ctx, request["items"], selectable=True, function=lambda x: "**[{}]({})**".format(x["snippet"]["title"], "https://www.youtube.com/playlist?list=" + x["id"]["playlistId"]))
        if event:
            results = await self.bot.lavalink.get_tracks("https://www.youtube.com/playlist?list=" + event["object"]["id"]["playlistId"])
            tracks = results["tracks"]
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            s=discord.Embed()
            s.description = "Enqueued {} with **{}** tracks <:done:403285928233402378>".format(results['playlistInfo']['name'], len(tracks))
            await ctx.send(embed=s)
            if not player.is_playing:
                await player.play()

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
        event = await paged.page(ctx, results["tracks"], selectable=True, function=lambda x: "**[{}]({})**".format(x["info"]["title"], x["info"]["uri"]))
        if event:
            track = event["object"]
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
            s.add_field(name="Duration", value=self.format_time(track["info"]["length"]) if not track["info"]["isStream"] else "Stream (Unknown)", inline=True)
            s.add_field(name="Position in Queue", value=index)
            if timetill != 0:
                s.add_field(name="Estimated time till playing", value=self.format_time(timetill-track["info"]["length"]))
            else:
                s.add_field(name="Estimated time till playing", value="Next")
            await ctx.send(embed=s)
            if not player.is_playing:
                await player.play()

    @commands.command(aliases=["leave", "dc", "stop"])
    async def disconnect(self, ctx):
        """Make the bot end the queue and leave"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not currently connected to a voice channel :no_entry:")
        if not ctx.author.voice or (player.is_connected and player.connected_channel.id != ctx.author.voice.channel.id):
            return await ctx.send("You have to be in my voice channel to disconnect :no_entry:")
        if player.fetch("sessionowner") == ctx.author.id or player.fetch("sessionowner") not in map(lambda x: x.id, player.connected_channel.members):
            player.queue.clear()
            await player.disconnect()
            player.cleanup()
            await ctx.send("Disconnected <:done:403285928233402378>")
        else:
            await ctx.send("Only the session owner can disconnect the bot :no_entry:")

    @commands.command(aliases=["np", "now"])
    async def nowplaying(self, ctx):
        """Check what is currently playing"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.current:
            requester = self.bot.get_user(player.current.requester)
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
        if ctx.author not in player.connected_channel.members:
            return await ctx.send("You are not in the same voice channel as the bot :no_entry:")
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
        """Rewind the current track to the start again"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if not player.is_playing:
            return await ctx.send("Nothing is currently playing :no_entry:")
        if ctx.author not in player.connected_channel.members:
            return await ctx.send("You are not in the same voice channel as the bot :no_entry:")
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
        if ctx.author not in player.connected_channel.members:
            return await ctx.send("You are not in the same voice channel as the bot :no_entry:")
        try:
            guild_data = list(filter(lambda x: x["id"] == str(ctx.guild.id), self.votes))[0]
        except IndexError:
            guild_data = None
        if player.current.requester not in map(lambda c: c.id, player.connected_channel.members) and player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            await ctx.send("Skipped.")
            await player.skip()
        else:
            if player.current.requester == ctx.author.id:
                await ctx.send("Skipped.")
                await player.skip()
            else:
                if not guild_data:
                    return await ctx.send("Only the session owner can skip songs :no_entry:")
                if ctx.author.id in guild_data["votes"]:
                    return await ctx.send("You have already voted to skip :no_entry:")
                guild_data["votes"].append(ctx.author.id)
                if len(guild_data["votes"]) >= math.ceil(len(list(filter(lambda x: not x.bot, player.connected_channel.members)))*0.51):
                    await ctx.send("Skipped.")
                    await player.skip() 
                else:
                    await ctx.send("Skip? ({}/{} votes)".format(len(guild_data["votes"]), math.ceil(len(list(filter(lambda x: not x.bot, player.connected_channel.members)))*0.51)))

    @commands.command()
    async def volume(self, ctx, volume: int=None):
        """Set the volume of the bot"""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not volume:
            return await ctx.send("Volume is currently set to **{}%**".format(player.volume))
        if not player.is_connected:
            return await ctx.send("I'm not connected to a voice channel :no_entry:")
        if player.fetch("sessionowner") not in map(lambda c: c.id, player.connected_channel.members):
            await player.set_volume(volume)
            await ctx.send("Set the volume to **{}%**".format(player.volume))
        elif player.fetch("sessionowner") == ctx.author.id:
            await player.set_volume(volume)
            await ctx.send("Set the volume to **{}%**".format(player.volume))
        else:
            return await ctx.send("Only the session owner can change the volume :no_entry:")

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

    @commands.command(aliases=["loop"])
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

    @join.after_invoke
    @play.after_invoke
    @playlist.after_invoke
    @playnow.after_invoke
    @search.after_invoke
    async def deafen(self, ctx):
        if ctx.me.voice:
            if not ctx.me.voice.deaf:
                await ctx.me.edit(deafen=True)

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
                                if channel:
                                    await channel.send("No one has been in the voice channel for 2 minutes :wave:")
                                player.queue.clear()
                                await player.disconnect()
                                player.cleanup()
                    else:
                        player.delete("nousers")
            await asyncio.sleep(45)

def setup(bot, connection):
    bot.add_cog(music(bot, connection))
