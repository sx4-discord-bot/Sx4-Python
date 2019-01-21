import discord
import asyncio
from discord.ext import commands
import time
import random
import math
import psutil
import datetime
from datetime import datetime, timedelta
import urllib
from urllib.request import Request, urlopen
import json
import sys
import re
from . import owner as dev
import os
from utils import arg, Token, checks, arghelp, paged
from random import choice, randint
import requests
import rethinkdb as r


giveaway = {"users": None}

permsjson = {'change_nickname': 67108864, 'use_vad': 33554432, 'manage_channels': 16, 'manage_guild': 32, 'connect': 1048576, 'read_message_history': 65536, 'view_channel': 1024, 'move_members': 16777216, 'mention_everyone': 131072, 'manage_nicknames': 134217728, 'view_audit_log': 128, 'use_external_emojis': 262144, 'add_reactions': 64, 'manage_roles': 268435456, 'speak': 2097152, 'ban_members': 4, 'manage_webhooks': 536870912, 'send_messages': 2048, 'manage_messages': 8192, 'create_instant_invite': 1, 'embed_links': 16384, 'priority_speaker': 256, 'read_messages': 1024, 'manage_emojis': 1073741824, 'attach_files': 32768, 'mute_members': 4194304, 'administrator': 8, 'deafen_members': 8388608, 'send_tts_messages': 4096, 'kick_members': 2}

class general:
    def __init__(self, bot):
        self.bot = bot
        self._stats = []
        self._stats_task = bot.loop.create_task(self.checktime())
        self._database_check = bot.loop.create_task(self.update_database())

    def __unload(self):
        self._stats_task.cancel()
        self._database_check.cancel()

    @commands.command()
    async def suggest(self, ctx, *, suggestion: str):
        """Suggest a feature to the current server, if it's set up"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        if not data.run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        elif not data["channel"].run() or not data["toggle"].run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        channel = ctx.guild.get_channel(int(data["channel"].run()))
        s=discord.Embed(description=suggestion)
        s.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        s.set_footer(text="This suggestion is currently pending")
        message = await channel.send(embed=s)
        await message.add_reaction("✅")
        await message.add_reaction("❌") 
        await ctx.send("Your suggestion has been sent to {}".format(channel.mention))
        data.update({"suggestions": r.row["suggestions"].append({"id": str(message.id), "user": str(ctx.author.id), "accepted": None})}).run(durability="soft", noreply=True)

    @commands.group()
    async def suggestion(self, ctx):
        """Set up a suggestions system up in your server and monitor it"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("suggestions").insert({"id": str(ctx.guild.id), "suggestions": [], "toggle": False, "channel": None}).run(durability="soft")
        
    @suggestion.command(name="toggle")
    @checks.has_permissions("manage_messages")
    async def _toggle_(self, ctx):
        """Toggle suggestions on/off in the current server"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        if data["toggle"].run():
            await ctx.send("Suggestions are now disabled.")
            data.update({"toggle": False}).run(durability="soft", noreply=True)
        elif not data["toggle"].run():
            await ctx.send("Suggestions are now enabled providing you have set a suggestion channel with `{}suggestion channel`".format(ctx.prefix))
            data.update({"toggle": True}).run(durability="soft", noreply=True)

    @suggestion.command(name="channel")
    @checks.has_permissions("manage_messages")
    async def _channel(self, ctx, *, channel: str):
        """Set the suggestions channel in the current server"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        channel = arg.get_text_channel(ctx, channel)
        if not channel:
            return await ctx.send("I could not find that text channel :no_entry:")
        if data["channel"].run() == str(channel.id):
            return await ctx.send("The suggestions channel is already set to {}".format(channel.mention))
        await ctx.send("The suggestions channel has been set to {}".format(channel.mention))
        data.update({"channel": str(channel.id)}).run(durability="soft", noreply=True)

    @suggestion.command()
    @checks.has_permissions("manage_guild")
    async def accept(self, ctx, message_id, *, reason: str=None):
        """Accept a suggestion which has been sent to your servers suggestion channel"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        if not data.run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        elif not data["channel"].run() or not data["toggle"].run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        if str(message_id) in data["suggestions"].map(lambda x: x["id"]).run():
            message = await ctx.guild.get_channel(int(data["channel"].run())).get_message(message_id)
            embed = message.embeds[0]
            embed.colour = 0x5fe468
            embed.add_field(name="Moderator", value=ctx.author)
            embed.add_field(name="Reason", value=reason if reason else "No reason given")
            embed.set_footer(text="Suggestion Accepted")
            await message.edit(embed=embed)
            await ctx.send("That suggestion has been accepted <:done:403285928233402378>")
            suggestions = data["suggestions"].run()
            message_db = list(filter(lambda x: x["id"] == str(message_id), suggestions))[0]
            suggestions.remove(message_db)
            message_db["accepted"] = True
            suggestions.append(message_db)
            data.update({"suggestions": suggestions}).run(durability="soft", noreply=True)
        else:
            return await ctx.send("That message is not a suggestion message :no_entry:")

    @suggestion.command()
    @checks.has_permissions("manage_guild")
    async def deny(self, ctx, message_id: int, *, reason: str=None):
        """Deny a suggestion which has been sent to your servers suggestion channel"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        if not data.run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        elif not data["channel"].run() or not data["toggle"].run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        if str(message_id) in data["suggestions"].map(lambda x: x["id"]).run():
            message = await ctx.guild.get_channel(int(data["channel"].run())).get_message(message_id)
            embed = message.embeds[0]
            embed.colour = 0xf84b50
            embed.add_field(name="Moderator", value=ctx.author)
            embed.add_field(name="Reason", value=reason if reason else "No reason given")
            embed.set_footer(text="Suggestion Denied")
            await message.edit(embed=embed)
            await ctx.send("That suggestion has been denied <:done:403285928233402378>")
            suggestions = data["suggestions"].run()
            message_db = list(filter(lambda x: x["id"] == str(message_id), suggestions))[0]
            suggestions.remove(message_db)
            message_db["accepted"] = False
            suggestions.append(message_db)
            data.update({"suggestions": suggestions}).run(durability="soft", noreply=True)
        else:
            return await ctx.send("That message is not a suggestion message :no_entry:")

    @suggestion.command(name="delete", aliases=["wipe"])
    @checks.has_permissions("manage_guild")
    async def _delete(self, ctx):
        """Delete all suggestions which have been sent to your servers suggestion channel"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        if not data.run():
            return await ctx.send("You have no suggestions in your server :no_entry:")
        elif not data["suggestions"].run():
            return await ctx.send("You have no suggestions in your server :no_entry:")
        await ctx.send("Are you sure you want to wipe all data for suggestions in your server? (Respond below)")
        try:
            def check(m):
                return m.channel == ctx.channel and ctx.author == m.author
            response = await self.bot.wait_for("message", check=check, timeout=30)
            if response.content.lower() == "yes":
                await ctx.send("All suggestions have been deleted.")
                data.update({"suggestions": []}).run(durability="soft", noreply=True)
            else:
                await ctx.send("Cancelled.")
        except asyncio.TimeoutError:
            await ctx.send("Timed out :stopwatch:")        

    @suggestion.command(name="remove")
    @checks.has_permissions("manage_guild")
    async def _remove(self, ctx, message_id: int):
        """Removes a suggestion which has been sent to your servers suggestion channel"""
        data = r.table("suggestions").get(str(ctx.guild.id))
        if not data.run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        elif not data["channel"].run() or not data["toggle"].run():
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        if str(message_id) in data["suggestions"].map(lambda x: x["id"]).run():
            message = await ctx.guild.get_channel(int(data["channel"].run())).get_message(message_id)
            try:
                await message.delete()
            except:
                pass
            await ctx.send("That suggestion has been deleted <:done:403285928233402378>")
            data.update({"suggestions": r.row["suggestions"].filter(lambda x: x["id"] != str(message_id))}).run(durability="soft", noreply=True)
        else:
            return await ctx.send("That message is not a suggestion message :no_entry:")

    @suggestion.command(name="list")
    async def _list(self, ctx):
        """List all suggestions which have been sent to your servers suggestion channel"""
        data = r.table("suggestions").get(str(ctx.guild.id)).run()
        if not data:
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        elif not data["channel"] or not data["toggle"]:
            return await ctx.send("Suggestions are not set up in this server :no_entry:")
        elif not data["suggestions"]:
            return await ctx.send("No suggestions have been sent yet :no_entry:")
        url = "https://discordapp.com/channels/{}/{}/".format(ctx.guild.id, data["channel"])
        def function(x):
            if x["accepted"] == None:
                accepted = "Pending"
            elif x["accepted"] == True:
                accepted = "Accepted"
            else:
                accepted = "Denied"
            return "[{}'s Suggestion - {}]({})".format(self.bot.get_user(int(x["user"])).name if self.bot.get_user(int(x["user"])) else x["user"], accepted, url + x["id"])
        await paged.page(ctx, sorted(data["suggestions"], key=lambda x: int(x["id"])), indexed=False, function=function, per_page=20, author={"name": "Suggestions", "icon_url": ctx.guild.icon_url})

    @commands.group()
    async def imagemode(self, ctx):
        """Set image mode on in a channel it'll delete any messages which are not an image"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("imagemode").insert({"id": str(ctx.guild.id), "channels": []}).run(durability="soft")
            
    @imagemode.command(name="toggle")
    @checks.has_permissions("manage_messages")
    async def _toggle(self, ctx):
        """Type this is the channel you want to turn image mode on/off for"""
        data = r.table("imagemode").get(str(ctx.guild.id))
        if str(ctx.channel.id) in data["channels"].map(lambda x: x["id"]).run():
            data.update({"channels": r.row["channels"].filter(lambda x: x["id"] != str(ctx.channel.id))}).run(durability="soft")
            await ctx.send("Image mode is now disabled in this channel.")
        else:
            channel = {"id": str(ctx.channel.id), "slowmode": "0", "users": []}
            data.update({"channels": r.row["channels"].append(channel)}).run(durability="soft")
            await ctx.send("Image mode is now enabled in this channel.")

    @imagemode.command(name="slowmode")
    @checks.has_permissions("manage_messages")
    async def _slowmode(self, ctx, time_interval):
        """Set the slowmode on a channel with image mode on so people can only post images once every however long"""
        try:
            if time_interval.endswith("d"):
                time_interval = int(time_interval[:-1])*86400
            elif time_interval.endswith("h"):
                time_interval = int(time_interval[:-1])*3600
            elif time_interval.endswith("m"):
                time_interval = int(time_interval[:-1])*60
            elif time_interval.endswith("s"):
                time_interval = int(time_interval[:-1])
            elif time_interval.lower() in ["off", "none"]:
                time_interval = 0
            else:
                time_interval = int(time_interval)
        except:
            return await ctx.send("Invalid time interval :no_entry:")
        data = r.table("imagemode").get(str(ctx.guild.id))
        if str(ctx.channel.id) not in data["channels"].map(lambda x: x["id"]).run():
            await ctx.send("Turn image mode on for this channel using `{}imagemode toggle` before you set the slowmode.".format(ctx.prefix))
        else:
            data.update({"channels": r.row["channels"].map(lambda x: r.branch(x["id"] == str(ctx.channel.id), x.merge({"slowmode": str(time_interval)}), x))}).run(durability="soft")
            await ctx.send("Slowmode has been updated for image mode in this channel.")

    @imagemode.command(name="stats")
    async def __stats(self, ctx, channel: discord.TextChannel=None):
        data = r.table("imagemode").get(str(ctx.guild.id))
        if not channel:
            channel = ctx.channel
        if str(channel.id) not in data["channels"].map(lambda x: x["id"]).run():
            await ctx.send("Image mode is not enabled in this channel :no_entry:")
        else:
            s=discord.Embed()
            s.set_author(name="Image Mode Settings ({})".format(channel.name), icon_url=self.bot.user.avatar_url)
            s.add_field(name="Status", value="Enabled")
            s.add_field(name="Slowmode", value=data["channels"].filter(lambda x: x["id"] == str(channel.id))[0]["slowmode"].run() if data["channels"].filter(lambda x: x["id"] == str(channel.id))[0]["slowmode"].run() != 0 else "Disabled")
            await ctx.send(embed=s)

    @commands.command()
    async def invitegenerator(self, ctx, bot: str, *permissions):
        """Generates an invite for any specific bot with permissions of your choice"""
        bot = await arg.get_member(ctx, bot)
        if not bot:
            return await ctx.send("I could not find that bot :no_entry:")
        elif not bot.bot:
            return await ctx.send("`{}` is not a bot :no_entry:".format(bot))
        value = 0
        if permissions:
            for x in permissions:
                try:
                    value += permsjson[x]
                except: 
                    pass
        await ctx.send("https://discordapp.com/oauth2/authorize?client_id={}{}&scope=bot".format(bot.id, "" if not permissions or value == 0 else "&permissions=" + str(value)))

    @commands.command()
    async def usage(self, ctx, *, command: str):
        if " " in command:
            command = command.split(" ", 1)
            try:
                command = self.bot.all_commands[command[0]].all_commands[command[1]]
            except KeyError:
                return await ctx.send("Invalid command :no_entry:")
        else:
            try:
                command = self.bot.all_commands[command]
            except KeyError:
                return await ctx.send("Invalid command :no_entry:")
        try:
            data = r.table("botstats").get("stats")["commandcounter"].filter(lambda x: x["name"] == str(command))[0].run()
        except:
            return await ctx.send("This command has not been used yet :no_entry:")
        await ctx.send("`{}` has been used **{}** times since (14/10/18)".format(command, data["amount"]))
        

    @commands.command(aliases=["topcmds"])
    async def topcommands(self, ctx, page: int=None):
        """View the top commands used on the bot"""
        per_page = 20
        listcom = sorted(r.table("botstats").get("stats")["commandcounter"].run(durability="soft"), key=lambda x: x["amount"], reverse=True) 
        if not page:
            page = 1
        elif page < 1 or page > math.ceil(len(listcom)/per_page):
            return await ctx.send("Invalid Page :no_entry:")   
        msg = ""   
        i = page * per_page - per_page
        for command in listcom[page * per_page - per_page:page * per_page]:
            i += 1
        
            name = command["name"]
            used = command["amount"]
            
            msg += "{}. `{}` - {:,} {}\n".format(i, name, used, "use" if used == 1 else "uses")
        await ctx.send(embed=discord.Embed(description=msg).set_author(name="Top Commands", icon_url=self.bot.user.avatar_url).set_footer(text="Page {}/{}".format(page, math.ceil(len(listcom)/per_page))))


    @commands.command()
    async def decode(self, ctx):
        """Decode any text file (Supports languages and will use markdown)"""
        if ctx.message.attachments:
            try:
                contents = requests.get(ctx.message.attachments[0].url).content.decode()
            except:
                return await ctx.send("Failed to decode the file :no_entry:")
            amount = ctx.message.attachments[0].url.rfind(".")
            if len(contents) > 2000:
                return await ctx.send("This file contains more than 2000 characters :no_entry:")
            await ctx.send("```{}\n".format(ctx.message.attachments[0].url[amount+1:]) + contents  + "```")
        else:
            await ctx.send("You didn't attach a text file with the command :no_entry:")

    @commands.command(aliases=["cinfo"])
    async def channelinfo(self, ctx, *, channel_or_category: str=None):
        if not channel_or_category:
            channel = ctx.channel
        else:
            channel = arg.get_voice_channel(ctx, channel_or_category)
        if not channel:
            channel = arg.get_text_channel(ctx, channel_or_category)
        if not channel:
            channel = arg.get_category(ctx, channel_or_category)
        if not channel:
            return await ctx.send("Invalid channel/category :no_entry:")
        perms = "\n".join(list(map(lambda x: x[0].replace("_", " ").title(), filter(lambda x: x[1] == True, channel.permissions_for(ctx.author)))))
        if isinstance(channel, discord.TextChannel):
            s=discord.Embed(colour=ctx.author.colour, description=ctx.channel.topic)
            s.set_author(name=channel.name, icon_url=ctx.guild.icon_url)
            s.set_thumbnail(url=ctx.guild.icon_url)
            s.add_field(name="ID", value=channel.id)
            s.add_field(name="NSFW Channel", value="Yes" if channel.is_nsfw() else "No")
            s.add_field(name="Channel Position", value=channel.position + 1)
            s.add_field(name="Slowmode", value="{} {}".format(channel.slowmode_delay, "second" if channel.slowmode_delay == 1 else "seconds") if channel.slowmode_delay != 0 else "Disabled")
            s.add_field(name="Channel Category", value=channel.category.name if channel.category else "None")
            s.add_field(name="Members", value=len(channel.members))
            s.add_field(name="Author Permissions", value=perms if perms else "None", inline=False)
        elif isinstance(channel, discord.VoiceChannel):
            s=discord.Embed(colour=ctx.author.colour, description=ctx.channel.topic)
            s.set_author(name=channel.name, icon_url=ctx.guild.icon_url)
            s.set_thumbnail(url=ctx.guild.icon_url)
            s.add_field(name="ID", value=channel.id)
            s.add_field(name="Channel Position", value=channel.position + 1)
            s.add_field(name="Channel Category", value=channel.category.name if channel.category else "None")
            s.add_field(name="Members Inside", value=len(channel.members))
            s.add_field(name="User Limit", value="Unlimited" if channel.user_limit == 0 else channel.user_limit)
            s.add_field(name="Bitrate", value="{} kbps".format(round(channel.bitrate/1000)))
            s.add_field(name="Author Permissions", value=perms if perms else "None", inline=False)
        elif isinstance(channel, discord.CategoryChannel):
            channels = "\n".join(map(lambda x: x.mention if isinstance(x, discord.TextChannel) else x.name, channel.channels))
            s=discord.Embed(colour=ctx.author.colour, description=ctx.channel.topic)
            s.set_author(name=channel.name, icon_url=ctx.guild.icon_url)
            s.set_thumbnail(url=ctx.guild.icon_url)
            s.add_field(name="ID", value=channel.id)
            s.add_field(name="NSFW Category", value="Yes" if channel.is_nsfw() else "No")
            s.add_field(name="Category Position", value=channel.position + 1, inline=False)
            s.add_field(name="Author Permissions", value=perms if perms else "None", inline=True)
            s.add_field(name="Channels", value=channels if channels else "None", inline=True)
        await ctx.send(embed=s)



    @commands.command(aliases=["updates", "changelog"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def changes(self, ctx, date: str=None):
        """View changes which have recently happened on the bot or on a specific date"""
        message = None
        if not date:
            message = list(await self.bot.get_channel(455806567577681921).history(limit=1).flatten())[0]
        else:
            if "/" in date:
                year = int(datetime.now().strftime("%y"))
                try:
                    day = int(date.split("/")[0])
                    month = int(date.split("/")[1])
                except IndexError:
                    return await ctx.send("Invalid date format :no_entry:")
                try:
                    year = int(date.split("/")[2])
                except IndexError:
                    pass
                for x in await self.bot.get_channel(455806567577681921).history(limit=100).flatten():
                    date = x.content.split("\n\n")[7].split("(")[1][:-1]
                    day_message = int(date.split("/")[0])
                    month_message = int(date.split("/")[1])
                    year_message = int(date.split("/")[2])
                    if day == day_message and month_message == month and year == year_message:
                        message = x
                        break
            else:
                return await ctx.send("Invalid date format :no_entry:")
        if not message:
            return await ctx.send("I could not find changes from that date (Make sure the date is within 100 days within today and isn't in the future) :no_entry:")
        bugfixes = message.content.split("\n\n")[2]
        updates = message.content.split("\n\n")[4]
        announcements = message.content.split("\n\n")[6]
        date = message.content.split("\n\n")[7]
        s=discord.Embed(timestamp=message.edited_at if message.edited_at else message.created_at).set_author(name="Sx4 Change Log", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Bug Fixes", value=bugfixes, inline=False)
        s.add_field(name="Updates", value=updates, inline=False)
        s.add_field(name="Announcements", value=announcements, inline=False)
        s.set_footer(text=date + " | Last Updated")
        await ctx.send(embed=s)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reaction(self, ctx):
        """Test your reaction time"""
        interval1 = time.perf_counter()
        await ctx.channel.trigger_typing()
        interval2 = time.perf_counter()
        ping = interval2-interval1
        await ctx.send("In the next 2-10 seconds i'm going to send a message this is when you type whatever you want in the chat from there i will work out the time between me sending the message and you sending your message and that'll be your reaction time :stopwatch:")
        await asyncio.sleep(randint(2, 10))
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            message = await ctx.send("**GO!**")
            response = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Either you have a really poor reaction speed or you're afk (Timed out) :stopwatch:")
            return
        if response:
            responsetime = response.created_at.timestamp()
        await ctx.send("Your reaction speed was **{}ms** (Discord API ping and Message ping have been excluded)".format(round(((responsetime - message.created_at.timestamp()) - self.bot.latency - ping)*1000)))

    @commands.command()
    async def invites(self, ctx, *, user: str=None):
        """View how many invites you have or a user has"""
        if not user:
            user = ctx.author
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                return await ctx.send("I could not find that user :no_entry:")
        amount = 0
        total = 0
        entries = {}
        for x in await ctx.guild.invites():
            if user == x.inviter:
                amount += x.uses
            total += x.uses
        for x in await ctx.guild.invites():
            if x.uses > 0:
                if "user" not in entries:
                    entries["user"] = {}
                if str(x.inviter.id) not in entries["user"]:
                    entries["user"][str(x.inviter.id)] = {}
                if "uses" not in entries["user"][str(x.inviter.id)]:
                    entries["user"][str(x.inviter.id)]["uses"] = 0
                entries["user"][str(x.inviter.id)]["uses"] += x.uses
        try: 
            entries["user"]
        except:
            return await ctx.send("No-one has made an invite in this server :no_entry:")
        if str(user.id) not in entries["user"]:
            await ctx.send("{} has no invites :no_entry:".format(user))
            return
        sorted_invites = sorted(entries["user"].items(), key=lambda x: x[1]["uses"], reverse=True)
        place = 0
        percent = (amount/total)*100
        if percent < 1:
            percent = "<1"
        else:
            percent = round(percent)
        for x in sorted_invites:
            place += 1
            if x[0] == str(user.id):
                break 
        await ctx.send("{} has **{}** invites which means they have the **{}** most invites. They have invited **{}%** of all users.".format(user, amount, self.prefixfy(place), percent))
        del entries

    @commands.command(aliases=["ilb", "inviteslb"])
    async def invitesleaderboard(self, ctx, page: int=None):
        """View a leaderboard sorted by the users with the most invites"""
        if not page:
            page = 1
        entries, total = {}, 0
        for x in await ctx.guild.invites():
            if x.uses > 0:
                if "user" not in entries:
                    entries["user"] = {}
                if str(x.inviter.id) not in entries["user"]:
                    entries["user"][str(x.inviter.id)] = {}
                if "uses" not in entries["user"][str(x.inviter.id)]:
                    entries["user"][str(x.inviter.id)]["uses"] = 0
                entries["user"][str(x.inviter.id)]["uses"] += x.uses
                total += x.uses
        try: 
            entries["user"]
        except:
            return await ctx.send("No-one has made an invite in this server :no_entry:")
        if page < 1 or page > math.ceil(len(entries["user"])/10):
            return await ctx.send("Invalid Page :no_entry:")
        sorted_invites = sorted(entries["user"].items(), key=lambda x: x[1]["uses"], reverse=True)
        msg, i = "", page*10-10
        try:
            place = list(map(lambda x: x[0], sorted_invites)).index(str(ctx.author.id))
        except:
            place = None
        for x in sorted_invites[page*10-10:page*10]:
            i += 1
            percent = (x[1]["uses"]/total)*100
            if percent < 1:
                percent = "<1"
            else:
                percent = round(percent)
            user = ctx.guild.get_member(int(x[0]))
            if not user:
                user = x[0]
            msg += "{}. `{}` - {:,} {} ({}%)\n".format(i, user, x[1]["uses"], "invite" if x[1]["uses"] == 1 else "invites", percent)
        s=discord.Embed(title="Invites Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(place) if place else "Unranked", page, math.ceil(len(entries["user"])/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)

    @commands.command(name="await")
    async def _await(self, ctx, *users: discord.Member):
        """The bot will notify you when a certain user or users come online"""
        author = ctx.author
        r.table("await").insert({"id": str(author.id), "users": []}).run(durability="soft")
        authordata = r.table("await").get(str(author.id))
        if not users:
            await ctx.send("At least one user is required as an argument :no_entry:")
            return
        userlist = [x for x in users if x.status == discord.Status.offline and x != author]
        if userlist == [] and len(users) > 1:
            await ctx.send("All those users are already online :no_entry:")
            return
        if userlist == [] and len(users) == 1:
            await ctx.send("That user is already online :no_entry:")
            return
        for x in userlist:
            authordata.update({"users": r.row["users"].append(str(x.id))}).run(durability="soft")
        await ctx.send("You will be notified when {} comes online.".format(", ".join(["`" + str(x) + "`" for x in userlist])))


    @commands.command()
    async def joinposition(self, ctx, user_or_number=None):
        """See what you or a users join position is or what user joined at a specific join position"""
        author = ctx.author
        if not user_or_number:
            user = author
        elif "<" in user_or_number and "@" in user_or_number:
            user_or_number = user_or_number.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            user = discord.utils.get(ctx.guild.members, id=int(user_or_number))
        elif "#" in user_or_number:
            number = len([x for x in user_or_number if "#" not in x])
            usernum = number - 4
            user = discord.utils.get(ctx.guild.members, name=user_or_number[:usernum], discriminator=user_or_number[usernum + 1:len(user_or_number)])
        else:
            try:
                user = discord.utils.get(ctx.guild.members, id=int(user_or_number))
            except:
                user = discord.utils.get(ctx.guild.members, name=user_or_number)
        if not user:
            try:
                number = int(user_or_number)
                user = "".join([str(x) for x in sorted([x for x in ctx.guild.members if x.joined_at], key=lambda x: x.joined_at)[number-1:number]])
                if user == "":
                    await ctx.send("Invalid join position :no_entry:")
                    return
                input = number
                await ctx.send("**{}** was the {} user to join {}".format(user, self.prefixfy(input), ctx.guild.name))
            except:
                await ctx.send("You have not given a valid number or user :no_entry:")
                return
        else:
            input = sorted([x for x in ctx.guild.members if x.joined_at], key=lambda x: x.joined_at).index(user) + 1
            await ctx.send("{} was the **{}** user to join {}".format(user, self.prefixfy(input), ctx.guild.name))            

    @commands.command()
    @checks.has_permissions("manage_emojis")
    async def createemote(self, ctx, emote: str=None):
        if not emote:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
                split1 = url.split("/")
                split2 = split1[6].split(".")
                emotename = split2[0].replace("-", "_")
            else:
                await ctx.send("An image, url or emote is a required argument :no_entry:")
                return
        elif "https://" in emote or "http://" in emote:
            url = emote
            if "https://cdn.discordapp.com/attachments/" in url:
                split1 = url.split("/")
                split2 = split1[6].split(".")
                emotename = split2[0].replace("-", "_")
            else:
                await ctx.send("Because you're uploading an image and i'm not able to grab the name, the emote needs a name respond with one below. (Respond Below)")
                try:
                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel
                    response = await self.bot.wait_for("message", check=check, timeout=30)
                    emotename = response.content.replace(" ", "_").replace("-", "_")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out :stopwatch:")
                    return
        else:
            try:
                emote1 = self.bot.get_emoji(int(emote))
                if not emote1:
                    request = requests.get("https://cdn.discordapp.com/emojis/" + emote + ".gif")
                    if request.text == "":
                        url = "https://cdn.discordapp.com/emojis/" + emote + ".png"
                    else:
                        url = "https://cdn.discordapp.com/emojis/" + emote + ".gif"
                    await ctx.send("I was unable to find this emote in any servers i am in so please provide a name for it below. (Respond Below)")
                    try:
                        def check(m):
                            return m.author == ctx.author and m.channel == ctx.channel
                        response = await self.bot.wait_for("message", check=check, timeout=30)
                        emotename = response.content.replace(" ", "_").replace("-", "_")
                    except asyncio.TimeoutError:
                        await ctx.send("Timed out :stopwatch:")
                        return
                else:
                    emotename = emote1.name
                    url = emote1.url
            except:
                try:
                    if emote.startswith("<a:"):
                        splitemote = emote.split(":")
                        emotename = splitemote[1]
                        emoteid = str(splitemote[2])[:-1]
                        extend = ".gif"
                    else:
                        splitemote = emote.split(":")
                        emotename = splitemote[1]
                        emoteid = str(splitemote[2])[:-1]
                        extend = ".png"
                except:
                    await ctx.send("Invalid emoji :no_entry:")
                    return
                url = "https://cdn.discordapp.com/emojis/" + emoteid + extend
        image = requests.get(url).content
        try:
            emoji = await ctx.guild.create_custom_emoji(name=emotename, image=image)
        except discord.errors.Forbidden:
            await ctx.send("I do not have the manage emojis permission :no_entry:")
            return
        except discord.errors.HTTPException:
            await ctx.send("I was unable to make the emote this may be because you've hit the emote cap :no_entry:")
            return
        except:
            await ctx.send("Invalid emoji/url (Check if it's been deleted or you've made a typo) :no_entry:")
            return
        await ctx.send("{} has been copied and created".format(emoji))
		
    @commands.command(pass_context=True, aliases=["emote"])
    async def emoji(self, ctx, emote: discord.Emoji):
        """Find a random emoji the bot can find"""
        s=discord.Embed(colour=ctx.message.author.colour) 
        s.set_author(name=emote.name, url=emote.url)		
        s.set_image(url=emote.url)
        s.set_footer(text="ID: " + str(emote.id))
        await ctx.send(embed=s)

    @commands.command(aliases=["emotes", "emojis", "semotes", "semojis", "serveremojis"])
    async def serveremotes(self, ctx):
        """View all the emotes in a server"""
        msg = ""
        for x in ctx.guild.emojis:
            if x.animated:
                msg += "<a:{}:{}> ".format(x.name, x.id)
            else:
                msg += "<:{}:{}> ".format(x.name, x.id)
        if msg == "":
            await ctx.send("There are no emojis in this server :no_entry:")
            return
        else:
            i = 0 
            n = 2000
            for x in range(math.ceil(len(msg)/2000)):
                while msg[n-1:n] != " ":
                    n -= 1
                s=discord.Embed(description=msg[i:n])
                i += n
                n += n
                if i <= 2000:
                    s.set_author(name="{} Emojis".format(ctx.guild.name), icon_url=ctx.guild.icon_url)
                await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dblowners(self, ctx, *, user: str=None):
        """Look up the developers of a bot on discord bot list"""
        if not user:
            user = str(self.bot.user.id)
        if "<" in user and "@" in user:
            userid = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            url = "https://discordbots.org/api/bots?search=id:{}&fields=owners,username&limit=1&sort=points".format(userid)
        elif "#" in user: 
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            url = "https://discordbots.org/api/bots?search=username:{}&discriminator:{}&fields=owners,username&limit=1&sort=points".format(user[:usernum], user[usernum + 1:len(user)])
        else:
            try:
                int(user)
                url = "https://discordbots.org/api/bots?search=id:{}&fields=owners,username&limit=1&sort=points".format(user)
            except:
                user = urllib.parse.quote(user)
                url = "https://discordbots.org/api/bots?search=username:{}&fields=owners,username&limit=1&sort=points".format(user)
        request = Request(url, headers={"Authorization": Token.dbl()})
        data = json.loads(urlopen(request).read().decode())["results"]
        if len(data) == 0:
            await ctx.send("I could not find that bot :no_entry:")
            return
        data = data[0]
        msg = ""
        for x in data["owners"]:
            user = await self.bot.get_user_info(x)
            msg += str(user) + ", "
        await ctx.send("{}'s Owners: {}".format(data["username"], msg[:-2]))
        
    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dbltag(self, ctx, *, dbl_tag):
        """Shows the top 10 bots (sorted by monthly upvotes) in the tag form there you can select and view 1"""
        url = "https://discordbots.org/api/bots?search=tag:{}&limit=10&sort=monthlyPoints&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot,tags".format(urllib.parse.urlencode({"": dbl_tag}).replace("=", ""))
        try:
            request = requests.get(url, headers={"Authorization": Token.dbl()}, timeout=2)
        except:
            return await ctx.send("That tag could not be found :no_entry:")
        data = request.json()
        n = 0
        msg = ""
        tag = None
        for x in data["results"]:
            msg += "{}. **{}#{}**\n".format(n+1, x["username"], x["discriminator"])
            n = n + 1
            for y in x["tags"]:         
                if dbl_tag.lower() in y.lower():
                    tag = y 
        if not tag:
            return await ctx.send("That tag could not be found :no_entry:")
        s=discord.Embed(title="Bots in the tag {}".format(tag), description=msg)
        s.set_footer(text="Choose a number | cancel")
        message = await ctx.send(embed=s)
        def dbltag(m):
            if m.content.isdigit() or m.content.lower() == "cancel":
                if m.author == ctx.author:
                    return True
        try:
            response = await self.bot.wait_for("message", timeout=60, check=dbltag) 
        except asyncio.TimeoutError:
            try:
                await message.delete()
                await response.delete()
            except:
                pass
            return
        if response.content == "cancel":
            try:
                await message.delete()
                await response.delete()
            except:
                pass
            return
        else:
            try:
                await message.delete()
                await response.delete()
            except:
                pass
            response = int(response.content) - 1
            if data["results"][response]["certifiedBot"] == True:
                s=discord.Embed(description="<:dblCertified:392249976639455232> | " + data["results"][response]["shortdesc"])
            else:
                s=discord.Embed(description=data["results"][response]["shortdesc"])
            s.set_author(name=data["results"][response]["username"] + "#" + data["results"][response]["discriminator"], icon_url="https://cdn.discordapp.com/avatars/{}/{}".format(data["results"][response]["id"], data["results"][response]["avatar"]), url="https://discordbots.org/bot/{}".format(data["results"][response]["id"]))
            s.set_thumbnail(url="https://cdn.discordapp.com/avatars/{}/{}".format(data["results"][response]["id"], data["results"][response]["avatar"]))
            try:
                s.add_field(name="Guilds", value="{:,}".format(data["results"][response]["server_count"]))
            except:
                s.add_field(name="Guilds", value="N/A")
            s.add_field(name="Prefix", value=data["results"][response]["prefix"])
            s.add_field(name="Library", value=data["results"][response]["lib"])
            s.add_field(name="Approval Date", value=datetime.strptime(data["results"][response]["date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y"))
            s.add_field(name="Monthly votes", value="{:,}".format(data["results"][response]["monthlyPoints"]) + " :thumbsup:")
            s.add_field(name="Total votes", value="{:,}".format(data["results"][response]["points"]) + " :thumbsup:")
            if "https://" not in data["results"][response]["invite"]:
                s.add_field(name="Invite", value="**[Invite {} to your server](https://discordapp.com/oauth2/authorize?client_id={}&scope=bot)**".format(data["results"][response]["username"], data["results"][response]["id"]))
            else:
                s.add_field(name="Invite", value="**[Invite {} to your server]({})**".format(data["results"][response]["username"], data["results"][response]["invite"]))

            await ctx.send(embed=s)
         
    @commands.command(pass_context=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def dbl(self, ctx, user: str=None):
        """Look up any bot on discord bot list and get statistics from it"""
        request2 = requests.get("https://discordbots.org/api/bots?sort=server_count&limit=500&fields=id,username", headers={"Authorization": Token.dbl()}).json()["results"]
        request3 = requests.get("https://discordbots.org/api/bots?sort=points&limit=500&fields=username,id", headers={"Authorization": Token.dbl()}).json()["results"]
        if not user:
            user = self.bot.user
            url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,owners,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(user.id)
        elif "<" in user and "@" in user:
            userid = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,owners,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(userid)
            user = discord.utils.get(self.bot.get_all_members(), id=int(userid))
        elif "#" in user: 
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            url = "https://discordbots.org/api/bots?search=username:{}&discriminator:{}&fields=shortdesc,username,owners,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(user[:usernum], user[usernum + 1:len(user)])
            user = discord.utils.get(self.bot.get_all_members, name=user[:usernum], discriminator=user[usernum + 1:len(user)])
        else:
            try:
                int(user)
                url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,owners,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(user)
                user = discord.utils.get(self.bot.get_all_members(), id=int(user))
            except:
                username = user
                user = urllib.parse.quote(user)
                url = "https://discordbots.org/api/bots?search=username:{}&fields=shortdesc,username,owners,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&limit=1&sort=points".format(user)
                try:
                    user = [x for x in list(set(self.bot.get_all_members())) if x.bot and str(x.id) == [x["id"] for x in request3 if username.lower() in x["username"].lower()][0]][0]
                except:
                    try:
                        user = [x for x in list(set(self.bot.get_all_members())) if x.bot and username in x.name][0]
                    except:
                        user = None
        request = Request(url, headers={"Authorization": Token.dbl()})
        data = json.loads(urlopen(request).read().decode())["results"]
        if len(data) == 0:
            await ctx.send("I could not find that bot :no_entry:")
            return
        try:
            number = [x["id"] for x in request2].index(str(user.id)) + 1
        except:
            number = None
        data = data[0]
        if data["certifiedBot"] == True:
            s=discord.Embed(description="<:dblCertified:392249976639455232> | " + data["shortdesc"])
        else:
            s=discord.Embed(description=data["shortdesc"])
        s.set_author(name=data["username"] + "#" + data["discriminator"], icon_url="https://cdn.discordapp.com/avatars/{}/{}".format(data["id"], data["avatar"]), url="https://discordbots.org/bot/{}".format(data["id"]))
        s.set_thumbnail(url="https://cdn.discordapp.com/avatars/{}/{}".format(data["id"], data["avatar"]))
        try:
            if not number:
                s.add_field(name="Guilds", value="{:,}".format(data["server_count"]))
            else:
                s.add_field(name="Guilds", value="{:,}".format(data["server_count"]) + " ({})".format(self.prefixfy(number)))
        except:
            s.add_field(name="Guilds", value="N/A")
        s.add_field(name="Prefix", value=data["prefix"])
        s.add_field(name="Library", value=data["lib"])
        s.add_field(name="Approval Date", value=datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y"))
        s.add_field(name="Monthly votes", value="{:,}".format(data["monthlyPoints"]) + " :thumbsup:")
        s.add_field(name="Total votes", value="{:,}".format(data["points"]) + " :thumbsup:")
        if "https://" not in data["invite"]:
            s.add_field(name="Invite", value="**[Invite {} to your server](https://discordapp.com/oauth2/authorize?client_id={}&scope=bot)**".format(data["username"], data["id"]))
        else:
            s.add_field(name="Invite", value="**[Invite {} to your server]({})**".format(data["username"], data["invite"]))
        owner = discord.utils.get(self.bot.get_all_members(), id=data["owners"][0])
        if not owner:
            owner = await self.bot.get_user_info(data["owners"][0])
        s.set_footer(text="Primary Owner: {}".format(owner), icon_url=owner.avatar_url)

        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botlist(self, ctx, page: int=None):
        """A list of the bots with the most servers on discord bot list"""
        if not page:
            page = 0
        else: 
            page = page - 1
        if page < 0 or page > 49:
            await ctx.send("Invalid page :no_entry:")
            return
        url="https://discordbots.org/api/bots?sort=server_count&limit=10&offset={}&fields=username,server_count,id".format((page + 1)*10-10)
        request = Request(url, headers={"Authorization": Token.dbl()})
        data = json.loads(urlopen(request).read().decode())
        n = page*10
        l = 0
        msg = ""
        for x in data["results"]:
            n = n + 1
            l = l + 1
            msg += "{}. [{}]({}) - **{:,}** servers\n".format(n, data["results"][l-1]["username"], "https://discordbots.org/bot/{}".format(data["results"][l-1]["id"]), data["results"][l-1]["server_count"])
        s=discord.Embed(description=msg)
        s.set_author(name="Bot List")
        s.set_footer(text="Page {}/50".format(page+1))
        await ctx.send(embed=s)
        
    @commands.command()
    async def ping(self, ctx):
        """Am i alive? (Well if you're reading this, yes)"""
        current = ctx.message.edited_at.timestamp() if ctx.message.edited_at else ctx.message.created_at.timestamp()
        await ctx.send('Pong! :ping_pong:\n\n:stopwatch: **{}ms**\n:heartbeat: **{}ms** (Shard {})'.format(round((datetime.utcnow().timestamp() - current)*1000), round(self.bot.latencies[ctx.guild.shard_id][1]*1000), ctx.guild.shard_id + 1))
        
    @commands.command()
    async def bots(self, ctx): 
        """Look at all my bot friends in the server"""
        server = ctx.guild
        page = 1
        bots = sorted([str(x) for x in ctx.guild.members if x.bot], key=lambda x: x.lower())[page*20-20:page*20]
        botnum = len(list(map(lambda m: m.name, filter(lambda m: m.bot, server.members))))
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        s.add_field(name="Bot List ({})".format(botnum), value="\n".join(bots))
        s.set_footer(text="Page {}/{}".format(page, math.ceil(botnum / 20)))
        message = await ctx.send(embed=s)
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user == ctx.author:
                if reaction.message.id == message.id:
                    if reaction.emoji == "▶" or reaction.emoji == "◀":
                        return True
        page2 = True
        while page2:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=reactioncheck)
                if reaction.emoji == "▶":
                    if page != math.ceil(botnum / 20):
                        page += 1
                        bots = sorted([str(x) for x in ctx.guild.members if x.bot], key=lambda x: x.lower())[page*20-20:page*20]
                        s=discord.Embed(colour=0xfff90d)
                        s.set_author(name=server.name, icon_url=server.icon_url)
                        s.add_field(name="Bot List ({})".format(botnum), value="\n".join(bots))
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(botnum / 20)))
                        await message.edit(embed=s)
                    else:
                        page = 1
                        bots = sorted([str(x) for x in ctx.guild.members if x.bot], key=lambda x: x.lower())[page*20-20:page*20]
                        s=discord.Embed(colour=0xfff90d)
                        s.set_author(name=server.name, icon_url=server.icon_url)
                        s.add_field(name="Bot List ({})".format(botnum), value="\n".join(bots))
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(botnum / 20)))
                        await message.edit(embed=s)
                if reaction.emoji == "◀":
                    if page != 1:
                        page -= 1
                        bots = sorted([str(x) for x in ctx.guild.members if x.bot], key=lambda x: x.lower())[page*20-20:page*20]
                        s=discord.Embed(colour=0xfff90d)
                        s.set_author(name=server.name, icon_url=server.icon_url)
                        s.add_field(name="Bot List ({})".format(botnum), value="\n".join(bots))
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(botnum / 20)))
                        await message.edit(embed=s)
                    else:
                        page = math.ceil(botnum / 20)
                        bots = sorted([str(x) for x in ctx.guild.members if x.bot], key=lambda x: x.lower())[page*20-20:page*20]
                        s=discord.Embed(colour=0xfff90d)
                        s.set_author(name=server.name, icon_url=server.icon_url)
                        s.add_field(name="Bot List ({})".format(botnum), value="\n".join(bots))
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(botnum / 20)))
                        await message.edit(embed=s)
            except asyncio.TimeoutError:
                await message.remove_reaction("◀", ctx.me)
                await message.remove_reaction("▶", ctx.me)
                page2 = False
        
    @commands.command()
    async def donate(self, ctx):
        """Get my donation link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&redirect_uri=https%3A%2F%2Fvjserver.ddns.net%2Fthanksx4.html&scope=bot)\n[Support Server](https://discord.gg/PqJNcfB)\n[PayPal](https://www.paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/Sx4)", colour=0xfff90d)
        s.set_author(name="Donate!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command()
    async def invite(self, ctx):
        """Get my invite link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&redirect_uri=https%3A%2F%2Fvjserver.ddns.net%2Fthanksx4.html&scope=bot)\n[Support Server](https://discord.gg/PqJNcfB)\n[PayPal](https://www.paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/Sx4)", colour=0xfff90d)
        s.set_author(name="Invite!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)

    @commands.command()
    async def support(self, ctx):
        """Get my support server link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&redirect_uri=https%3A%2F%2Fvjserver.ddns.net%2Fthanksx4.html&scope=bot)\n[Support Server](https://discord.gg/PqJNcfB)\n[PayPal](https://www.paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/Sx4)", colour=0xfff90d)
        s.set_author(name="Support!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def info(self, ctx): 
        """Info about me"""
        ping = round(self.bot.latency*1000)
        users = str(len(set(self.bot.get_all_members())))
        servers = len(self.bot.guilds)
        channel = ctx.message.channel
        shea = discord.utils.get(self.bot.get_all_members(), id=402557516728369153)
        joakim = discord.utils.get(self.bot.get_all_members(), id=190551803669118976)
        description = ("Sx4 is a bot which intends to make your discord experience easier yet fun, it has multiple different purposes"
        ", which includes Moderation, utility and economy. Sx4 began as a red bot to help teach it's owner more about coding, it has now evolved in to"
        " a self coded bot with the help of some bot developers and intends to go further.")
        s=discord.Embed(description=description, colour=0xfff90d)
        s.set_author(name="Info!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Stats", value="Ping: {}ms\nServers: {}\nUsers: {}".format(ping, servers, users))
        s.add_field(name="Credits", value="[Victor#6359 (Host)](https://vjserver.ddns.net/discordbots.html)\n[ETLegacy](https://discord.gg/MqQsmF7)\n[Nexus](https://discord.gg/MqQsmF7)\n[RethinkDB](https://www.rethinkdb.com/api/python/)\n[Lavalink (Music)](https://github.com/Devoxin/Lavalink.py/)\n[Python](https://www.python.org/downloads/release/python-352/)\n[discord.py](https://pypi.python.org/pypi/discord.py/)")
        s.add_field(name="Sx4", value="Developers: {}, {}\nInvite: [Click Here](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&redirect_uri=https%3A%2F%2Fvjserver.ddns.net%2Fthanksx4.html&scope=bot)\nSupport: [Click Here](https://discord.gg/PqJNcfB)\nDonate: [PayPal](https://paypal.me/SheaCartwright), [Patreon](https://www.patreon.com/Sx4)".format(shea, joakim))
        await ctx.send(embed=s)

    @commands.command(aliases=["shards"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def shardinfo(self, ctx):
        "Look at Sx4s' shards"
        s=discord.Embed(colour=0xffff00)
        s.set_author(name="Shard Info!", icon_url=self.bot.user.avatar_url)
        s.set_footer(text="> indicates what shard your server is in | Users are not unique", icon_url=ctx.author.avatar_url)
        servers = self.bot.guilds
        for x in range(self.bot.shard_count):
            if x == ctx.guild.shard_id:
                guildshard = ">"
            else:
                guildshard = ""
            s.add_field(name="{} Shard {}".format(guildshard, x + 1), value="{:,} servers\n{:,} users\n{}ms".format(len([guild for guild in servers if guild.shard_id == x]), sum([guild.member_count for guild in servers if guild.shard_id == x]), round(self.bot.latencies[x][1]*1000)))
        await ctx.send(embed=s)
        
    @commands.command(aliases=["shared"])
    async def sharedservers(self, ctx, user=None, page: int=None):
        """Find out what mutual servers i'm in with another user or yourself"""
        if not page:
            page = 1
        if not user:
            user = ctx.message.author
        else:
            user = await arg.get_member(ctx, user)
            if user == self.bot.user:
                return await ctx.send("You can check `s?servers` for that :no_entry:")
            if not user:
                return await ctx.send("Invalid user :no_entry:")
        shared = ["{}. `{}`".format(i, x.name) for i, x in enumerate(filter(lambda x: user in x.members, self.bot.guilds), start=1)]
        if page < 1 or page > math.ceil(len(shared)/20):
            return await ctx.send("Invalid page :no_entry:")
        s=discord.Embed(description="\n".join(shared[page*20-20:page*20]) if shared else "None", colour=user.colour)
        s.set_author(name="Shared servers with {}".format(user), icon_url=user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(shared)/20)))
        await ctx.send(embed=s)
    
    @commands.command(pass_context=True)
    async def servers(self, ctx):
        """View all the servers i'm in"""
        page = 1
        msg = "\n".join(["`{}` - {} members".format(x.name, x.member_count) for x in sorted(sorted(self.bot.guilds, key=lambda x: x.name.lower()), key=lambda x: x.member_count, reverse=True)][0:20])
        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
        message = await ctx.send(embed=s)
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user == ctx.author:
                if reaction.message.id == message.id:
                    if reaction.emoji == "▶" or reaction.emoji == "◀":
                        return True
        page2 = True
        while page2:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=reactioncheck)
                if reaction.emoji == "▶":
                    if page != math.ceil(len(list(set(self.bot.guilds))) / 20):
                        page += 1
                        msg = "\n".join(["`{}` - {} members".format(x.name, x.member_count) for x in sorted(sorted(self.bot.guilds, key=lambda x: x.name.lower()), key=lambda x: x.member_count, reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
                    else:
                        page = 1
                        msg = "\n".join(["`{}` - {} members".format(x.name, x.member_count) for x in sorted(sorted(self.bot.guilds, key=lambda x: x.name.lower()), key=lambda x: x.member_count, reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
                if reaction.emoji == "◀":
                    if page != 1:
                        page -= 1
                        msg = "\n".join(["`{}` - {} members".format(x.name, x.member_count) for x in sorted(sorted(self.bot.guilds, key=lambda x: x.name.lower()), key=lambda x: x.member_count, reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
                    else:
                        page = math.ceil(len(list(set(self.bot.guilds)))/ 20)
                        msg = "\n".join(["`{}` - {} members".format(x.name, x.member_count) for x in sorted(sorted(self.bot.guilds, key=lambda x: x.name.lower()), key=lambda x: x.member_count, reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
            except asyncio.TimeoutError:
                try:
                    await message.remove_reaction("◀", ctx.me)
                    await message.remove_reaction("▶", ctx.me)
                except:
                    pass
                page2 = False
        

    @commands.command(aliases=["sc", "scount"])
    async def servercount(self, ctx):
        """My current server and user count"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        name = self.bot.user.name
        avatar = self.bot.user.avatar_url if self.bot.user.avatar else self.bot.user.default_avatar_url
        users = len(set(self.bot.get_all_members()))
        servers = (len(self.bot.guilds))
        s=discord.Embed(title="", colour=discord.Colour(value=colour))
        s.add_field(name="Servers", value="{}".format(servers))
        s.add_field(name="Users", value="{}".format(users))
        s.add_field(name="Shards", value="{}/{}".format(ctx.guild.shard_id + 1, self.bot.shard_count))
        s.set_author(name="{}'s servercount!".format(name), icon_url=avatar)
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True, aliases=["perms"])
    async def permissions(self, ctx, *, user: discord.Member=None):
        """Check the permissions a user has"""
        author = ctx.message.author
        if not user:
            user = author
        x = "\n".join([x[0].replace("_", " ").title() for x in filter(lambda p: p[1] == True, user.guild_permissions)])
        s=discord.Embed(description=x, colour=user.colour)
        s.set_author(name="{}'s permissions".format(user.name), icon_url=user.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def inrole(self, ctx, *, role: str):
        """Check who's in a specific role"""
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("Invalid role :no_entry:")
        server = ctx.guild
        page = 1
        number = len(role.members)
        if number < 1:
            return await ctx.send("There is no one in this role :no_entry:")
        users = "\n".join([str(x) for x in sorted(role.members, key=lambda x: x.name.lower())][page*20-20:page*20])
        s=discord.Embed(description=users, colour=0xfff90d)
        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
        message = await ctx.send(embed=s)
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user == ctx.author:
                if reaction.message.id == message.id:
                    if reaction.emoji == "▶" or reaction.emoji == "◀":
                        return True
        page2 = True
        while page2:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=reactioncheck)
                if reaction.emoji == "▶":
                    if page != math.ceil(number / 20):
                        page += 1
                        users = "\n".join([str(x) for x in sorted(role.members, key=lambda x: x.name.lower())][page*20-20:page*20])
                        s=discord.Embed(description=users, colour=0xfff90d)
                        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
                        await message.edit(embed=s)
                    else:
                        page = 1
                        users = "\n".join([str(x) for x in sorted(role.members, key=lambda x: x.name.lower())][page*20-20:page*20])
                        s=discord.Embed(description=users, colour=0xfff90d)
                        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
                        await message.edit(embed=s)
                if reaction.emoji == "◀":
                    if page != 1:
                        page -= 1
                        users = "\n".join([str(x) for x in sorted(role.members, key=lambda x: x.name.lower())][page*20-20:page*20])
                        s=discord.Embed(description=users, colour=0xfff90d)
                        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
                        await message.edit(embed=s)
                    else:
                        page = math.ceil(number / 20)
                        users = "\n".join([str(x) for x in sorted(role.members, key=lambda x: x.name.lower())][page*20-20:page*20])
                        s=discord.Embed(description=users, colour=0xfff90d)
                        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
                        await message.edit(embed=s)
            except asyncio.TimeoutError:
                try:
                    await message.remove_reaction("◀", ctx.me)
                    await message.remove_reaction("▶", ctx.me)
                except:
                    pass
                page2 = False

    @commands.command(pass_context=True, aliases=["mc", "mcount"])
    async def membercount(self, ctx):
        """Get all the numbers about a server"""
        server = ctx.guild
        members = set(server.members)
        bots = set(filter(lambda m: m.bot, members))
        online = set(filter(lambda m: m.status is discord.Status.online, members))
        idle = set(filter(lambda m: m.status is discord.Status.idle, members))
        dnd = set(filter(lambda m: m.status is discord.Status.do_not_disturb, members))
        offline = set(filter(lambda m: m.status is discord.Status.offline, members))
        sn = server.name
        users = members - bots
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        s=discord.Embed(title=":busts_in_silhouette: **{}'s** Membercount :busts_in_silhouette:".format(sn), colour=discord.Colour(value=colour), timestamp=__import__('datetime').datetime.utcnow())
        if len(users) == 1:
            s.add_field(name="Total users :busts_in_silhouette:", value="{} user".format(len(users)))
        else:
            s.add_field(name="Total users :busts_in_silhouette:", value="{} users".format(len(users)))
        if len(users - offline) == 1:
            s.add_field(name="Total users online :busts_in_silhouette:", value="{} user".format(len(users - offline)))
        else:
            s.add_field(name="Total users online :busts_in_silhouette:", value="{} users".format(len(users - offline)))
        if len(online - bots) == 1:
            s.add_field(name="Online users<:online:361440486998671381>", value="{} user".format(len(online - bots)))
        else:
            s.add_field(name="Online users<:online:361440486998671381>", value="{} users".format(len(online - bots)))
        if len(idle - bots) == 1:
            s.add_field(name="Idle users<:idle:361440487233814528>", value="{} user".format(len(idle - bots)))
        else:
            s.add_field(name="Idle users<:idle:361440487233814528>", value="{} users".format(len(idle - bots)))
        if len(dnd - bots) == 1:
            s.add_field(name="DND users<:dnd:361440487179157505>", value="{} user".format(len(dnd - bots)))
        else:
            s.add_field(name="DND users<:dnd:361440487179157505>", value="{} users".format(len(dnd - bots)))
        if len(offline - bots) == 1:
            s.add_field(name="Offline users<:offline:361445086275567626>", value="{} user".format(len(offline - bots)))
        else:
            s.add_field(name="Offline users<:offline:361445086275567626>", value="{} users".format(len(offline - bots)))
        if len(bots) == 1:
            s.add_field(name="Total bots :robot:", value="{} bot".format(len(bots)))
        else:
            s.add_field(name="Total bots :robot:", value="{} bots".format(len(bots)))
        if len(bots - offline) == 1:
            s.add_field(name="Total bots online :robot:", value="{} bot".format(len(bots - offline)))
        else:
            s.add_field(name="Total bots online :robot:", value="{} bots".format(len(bots - offline)))
        if len(members) == 1:
            s.add_field(name="Total users and bots :busts_in_silhouette::robot:", value="{} users/bots".format(len(members)), inline=False)
        else:
            s.add_field(name="Total users and bots :busts_in_silhouette::robot:", value="{} users/bots".format(len(members)), inline=False)
        s.set_thumbnail(url=server.icon_url)
        await ctx.send(embed=s)
    
    @commands.command(pass_context=True, aliases=["ri", "rinfo"]) 
    async def roleinfo(self, ctx, *, role: str):
        """Find out stuff about a role"""
        server = ctx.guild
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        perms = role.permissions
        members = len([x for x in server.members if role in x.roles])
        if perms.value == 0: 
            msg = "No Permissions"
        else:
            msg = "\n".join([x[0].replace("_", " ").title() for x in filter(lambda p: p[1] == True, perms)])
        if role.hoist:
            hoist = "Yes"
        else:
            hoist = "No"
        if role.mentionable:
            mention = "Yes"
        else:
            mention = "No"
        btt = self.prefixfy(ctx.guild.roles.index(role) + 1)
        ttb = self.prefixfy(ctx.guild.roles[::-1].index(role) + 1)
        s=discord.Embed(colour=role.colour)
        s.set_author(name="{} Role Info".format(role.name), icon_url=ctx.guild.icon_url)
        s.add_field(name="Role ID", value=role.id)
        s.add_field(name="Role Colour", value=role.colour)
        s.add_field(name="Role Position", value="{} (Bottom to Top)\n{} (Top to Bottom)".format(btt, ttb))
        s.add_field(name="Users in Role", value=members)
        s.add_field(name="Hoisted", value=hoist)
        s.add_field(name="Mentionable", value=mention)
        s.add_field(name="Role Permissions", value=msg, inline=False)
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def discrim(self, ctx, discriminator: str, page: int=None):
        """Check how many users have the discriminator 0001 seeing as though that's all people care about"""
        if not page:
            page = 1
        number = len([x for x in list(set(self.bot.get_all_members())) if x.discriminator == discriminator])
        if page - 1 > number / 20:
            await ctx.send("Invalid Page :no_entry:")
            return
        if page < 1:
            await ctx.send("Invalid Page :no_entry:")
            return
        msg = "\n".join(["{}#{}".format(x.name, x.discriminator) for x in sorted(list(set(self.bot.get_all_members())), key=lambda x: x.name.lower()) if x.discriminator == discriminator][page*20-20:page*20])
        if number == 0: 
            await ctx.send("There's no one with that discriminator or it's not a valid discriminator :no_entry:")
            return
        s=discord.Embed(title="{} users in the Discriminator #{}".format(number, discriminator), description=msg, colour=0xfff90d)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
        await ctx.send(embed=s)
            
    @commands.command(pass_context=True, aliases=["av"])
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Look at your own or someone elses avatar"""
        author = ctx.message.author
        if not user:
            user = author
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s Avatar".format(user.name), icon_url=user.avatar_url, url=user.avatar_url)
        s.set_image(url=user.avatar_url_as(size=1024))
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True, no_pm=True, aliases=["savatar"])
    async def serveravatar(self, ctx):
        """Look at the current server avatar"""
        server = ctx.guild
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        s=discord.Embed(colour=discord.Colour(value=colour))
        s.set_author(name="{}'s Icon".format(server.name), icon_url=server.icon_url, url=server.icon_url_as(format="png", size=1024))
        s.set_image(url=server.icon_url_as(format="png", size=1024))
        await ctx.send(embed=s)
        
    @commands.group(pass_context=True)
    async def trigger(self, ctx): 
        """Make the bot say something after a certain word is said"""
        server = ctx.guild 
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("triggers").insert({"id": str(server.id), "case": True, "toggle": True, "triggers": []}).run(durability="soft")
        
        
    @trigger.command(pass_context=True)
    @checks.has_permissions("manage_guild")
    async def toggle(self, ctx):
        """Toggle triggers on or off"""
        server = ctx.guild 
        serverdata = r.table("triggers").get(str(server.id))
        if serverdata["toggle"].run(durability="soft") == True:
            serverdata.update({"toggle": False}).run(durability="soft")
            await ctx.send("Triggers are now disabled on this server.")
            return
        if serverdata["toggle"].run(durability="soft") == False:
            serverdata.update({"toggle": True}).run(durability="soft")
            await ctx.send("Triggers are now enabled on this server.")
            return
            
    @trigger.command(pass_context=True)
    async def case(self, ctx):
        """Toggles your triggers between case sensitive and not"""
        server = ctx.guild 
        serverdata = r.table("triggers").get(str(server.id))
        if serverdata["case"].run(durability="soft") == True:
            serverdata.update({"case": False}).run(durability="soft")
            await ctx.send("Triggers are no longer case sensitive.")
            return
        if serverdata["case"].run(durability="soft") == False:
            serverdata.update({"case": True}).run(durability="soft")
            await ctx.send("Triggers are now case sensitive.")
            return
            
    @trigger.command(pass_context=True)
    async def list(self, ctx, page: int=None): 
        """List all your triggers"""
        msg = ""
        server = ctx.guild
        serverdata = r.table("triggers").get(str(server.id))
        if serverdata["triggers"].run(durability="soft") == []:
            return await ctx.send("This server has no triggers :no_entry:")
        if not page: 
            page = 1
        if page < 1:
            await ctx.send("Invalid Page :no_entry:")
            return
        if page - 1 > len(serverdata["triggers"].run(durability="soft")) / 5:
            await ctx.send("Invalid Page :no_entry:")
            return
        data = serverdata["triggers"].run(durability="soft")[page*5-5:page*5]
        datasize = len("".join([str(x["trigger"]) + x["response"].decode() if type(x["response"]) == r.ast.RqlBinary else x["response"] for x in data]))
        for x in data:
            if datasize >= 6000:
                msg += "Trigger: {}\n\n".format(x["trigger"])
            else:
                msg += "Trigger: {}\nResponse: {}\n\n".format(x["trigger"], x["response"].decode() if type(x["response"]) == r.ast.RqlBinary else x["response"])
        s=discord.Embed(description=msg, colour=0xfff90d)
        s.set_author(name="Server Triggers", icon_url=server.icon_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(serverdata["triggers"].run(durability="soft")) / 5)))
        await ctx.send(embed=s)
    

    @trigger.command(pass_context=True)
    @checks.has_permissions("manage_messages")
    async def add(self, ctx, trigger, *, response):
        """Add a trigger to the server"""
        server = ctx.guild
        serverdata = r.table("triggers").get(str(server.id))
        if trigger == response:
            await ctx.send("You can't have a trigger and a response with the same content :no_entry:")
            return
        if trigger in serverdata["triggers"].map(lambda x: x["trigger"]).run(durability="soft"):
            return await ctx.send("There is already a trigger with that name :no_entry:")
        serverdata.update({"triggers": r.row["triggers"].append({"trigger": trigger, "response": response})}).run(durability="soft")
        await ctx.send("The trigger **{}** has been created <:done:403285928233402378>".format(trigger))
        
    @trigger.command(pass_context=True)  
    @checks.has_permissions("manage_messages")
    async def remove(self, ctx, *, trigger):
        """Remove a trigger to the server"""
        server = ctx.guild
        serverdata = r.table("triggers").get(str(server.id))
        if trigger in serverdata["triggers"].map(lambda x: x["trigger"]).run(durability="soft"):
            serverdata.update({"triggers": r.row["triggers"].difference(serverdata["triggers"].filter(lambda x: x["trigger"] == trigger).run(durability="soft"))}).run(durability="soft")
        else:
            await ctx.send("Invalid trigger name :no_entry:")
            return
        await ctx.send("The trigger **{}** has been removed <:done:403285928233402378>".format(trigger))
        
    async def on_message(self, message):
        server = message.guild
        statsdata = r.table("botstats").get("stats")
        r.table("stats").insert({"id": str(server.id), "messages": 0, "members": 0}).run(durability="soft", noreply=True)
        triggerdata = r.table("triggers").get(str(server.id))
        imagemodedata = r.table("imagemode").get(str(server.id))
        if message.author == self.bot.user:
            statsdata.update({"messages": r.row["messages"] + 1}).run(durability="soft", noreply=True)
        if not message.author.bot:
            if server.id not in map(lambda x: x["id"], self._stats):
                self._stats.append({"id": server.id, "messages": 1, "members": 0})
            else:
                list(filter(lambda x: x["id"] == server.id, self._stats))[0]["messages"] += 1
        if message.author == self.bot.user:
            return
        if triggerdata.run():
            if triggerdata["toggle"].run() == False:
                pass
            else:
                if triggerdata["case"].run() == True:
                    for x in triggerdata["triggers"].run():
                        if message.content == x["trigger"]:
                            await message.channel.send(x["response"].decode() if type(x["response"]) == r.ast.RqlBinary else x["response"])
                else:
                    for x in triggerdata["triggers"].run():
                        if message.content.lower() == x["trigger"].lower():
                            await message.channel.send(x["response"].decode() if type(x["response"]) == r.ast.RqlBinary else x["response"])
        if imagemodedata.run():
            if str(message.channel.id) in imagemodedata["channels"].map(lambda x: x["id"]).run():
                channel = imagemodedata["channels"].filter(lambda x: x["id"] == str(message.channel.id))[0]
                users = channel["users"]
                usersran = channel["users"].run()
                supported = ["png", "jpg", "jpeg", "gif", "webp", "mp4", "gifv", "mov"]
                if not message.attachments:
                    embeds = message.embeds
                    if embeds:
                        image_type = embeds[0].type
                    else:
                        await message.delete()
                        return await message.channel.send("{}, You can only send images in this channel :no_entry:".format(message.author.mention), delete_after=10)
                else:
                    attach = message.attachments[0].url
                    index = attach.rfind(".") + 1
                    image_type = attach[index:]
                if image_type not in supported:
                    await message.delete()
                    return await message.channel.send("{}, You can only send images in this channel :no_entry:".format(message.author.mention), delete_after=10)
                else:
                    if int(channel["slowmode"].run()) != 0:
                        if str(message.author.id) not in users.map(lambda x: x["id"]).run():
                            usersran.append({"id": str(message.author.id), "timestamp": message.created_at.timestamp()})
                            imagemodedata.update({"channels": r.row["channels"].map(lambda x: r.branch(x["id"] == str(message.channel.id), x.merge({"users": usersran}), x))}).run(durability="soft", noreply=True)
                        else:
                            if message.created_at.timestamp() - users.filter(lambda x: x["id"] == str(message.author.id))[0]["timestamp"].run() < int(channel["slowmode"].run()):
                                time = users.filter(lambda x: x["id"] == str(message.author.id))[0]["timestamp"].run() - message.created_at.timestamp() + int(channel["slowmode"].run())
                                await message.delete()
                                await message.channel.send("{}, You can send another image in {}".format(message.author.mention, self.format_time_activity(time)), delete_after=10)
                            else:
                                user = users.filter(lambda x: x["id"] == str(message.author.id))[0].run()
                                usersran.remove(user)
                                user["timestamp"] = message.created_at.timestamp()
                                usersran.append(user)
                                imagemodedata.update({"channels": r.row["channels"].map(lambda x: r.branch(x["id"] == str(message.channel.id), x.merge({"users": usersran}), x))}).run(durability="soft", noreply=True)
            
    @commands.command(pass_context=True, aliases=["uid"])
    async def userid(self, ctx, *, user: discord.Member=None):
        """Get someone userid"""
        author = ctx.message.author
        if not user:
            user = author
        await ctx.send("{}'s ID: `{}`".format(user, user.id))
        
    @commands.command(pass_context=True, aliases=["rid"])
    async def roleid(self, ctx, *, role: discord.Role):
        """Get a roles id"""
        await ctx.send("{}'s ID: `{}`".format(role.name, role.id))
    
    @commands.command(pass_context=True, aliases=["sid"])
    async def serverid(self, ctx):
        """Get the servers id"""
        server = ctx.guild
        await ctx.send("{}'s ID: `{}`".format(server.name, server.id))
        
    @commands.command(pass_context=True, aliases=["cid"])
    async def channelid(self, ctx, *, channel: str=None):
        """Get a channels id"""
        if not channel:
            channel = ctx.message.channel
        else:
            channel = arg.get_text_channel(ctx, channel)
            if not channel:
                return await ctx.send("I could not find that channel :no_entry:")
        await ctx.send("<#{}> ID: `{}`".format(channel.id, channel.id))
        
    @commands.command(pass_context=True, aliases=["uinfo", "user"])
    async def userinfo(self, ctx, *, user: str=None):
        """Get some info on a user in the server"""
        author = ctx.message.author
        server = ctx.guild
        if not user:
            user = author
        else:
            user = await arg.get_member_info(ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
        if user not in ctx.guild.members:
            description = ""
            status = None
            if not isinstance(user, discord.User):
                if user.status == discord.Status.online:
                    status="Online<:online:361440486998671381>"
                if user.status == discord.Status.idle:
                    status="Idle<:idle:361440487233814528>"
                if user.status == discord.Status.do_not_disturb:
                    status="DND<:dnd:361440487179157505>"
                if user.status == discord.Status.offline:
                    status="Offline<:offline:361445086275567626>"
                if not user.activity:
                    pass
                elif isinstance(user.activity, discord.Spotify):
                    m, s = divmod(user.activity.duration.total_seconds(), 60)
                    duration = "%d:%02d" % (m, s)
                    description = "Listening to {} by {} `[{}]`".format(user.activity.title, user.activity.artists[0], duration)
                elif user.activity:
                    description="{} {}{}".format(user.activity.type.name.title(), user.activity.name, (" for " + self.format_time_activity(datetime.now().timestamp() - (user.activity.timestamps["start"]/1000)) if hasattr(user.activity, "timestamps") and "start" in user.activity.timestamps else ""))
                elif user.activity.url:
                    description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
                author_name = str(user) + (" 📱" if user.is_on_mobile() else "")
            else:
                author_name = str(user)
            if user.bot:
                bot = "Yes"
            else:
                bot = "No"
            joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
            s=discord.Embed(description=description, timestamp=datetime.utcnow())
            s.set_author(name=author_name, icon_url=user.avatar_url)
            s.set_thumbnail(url=user.avatar_url)
            s.add_field(name="User ID", value=user.id)
            s.add_field(name="Joined Discord", value=joined_discord)
            if status:
                s.add_field(name="Status", value=status)
            s.add_field(name="Bot", value=bot)
            await ctx.send(embed=s)
            return
        joined_server = user.joined_at.strftime("%d %b %Y %H:%M")
        joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
        if user.status == discord.Status.online:
            status="Online<:online:361440486998671381>"
        if user.status == discord.Status.idle:
            status="Idle<:idle:361440487233814528>"
        if user.status == discord.Status.do_not_disturb:
            status="DND<:dnd:361440487179157505>"
        if user.status == discord.Status.offline:
            status="Offline<:offline:361445086275567626>"
        description=""
        input = sorted([x for x in ctx.guild.members if x.joined_at], key=lambda x: x.joined_at).index(user) + 1
        if not user.activity:
            pass
        elif isinstance(user.activity, discord.Spotify):
            m, s = divmod(user.activity.duration.total_seconds(), 60)
            duration = "%d:%02d" % (m, s)
            description = "Listening to {} by {} `[{}]`".format(user.activity.title, user.activity.artists[0], duration)
        elif user.activity:
            description="{} {}{}".format(user.activity.type.name.title(), user.activity.name, (" for " + self.format_time_activity(datetime.now().timestamp() - (user.activity.timestamps["start"]/1000)) if hasattr(user.activity, "timestamps") and "start" in user.activity.timestamps and "start" in user.activity.timestamps else ""))
        elif user.activity.url:
            description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
        roles=[x.mention for x in user.roles if x.name != "@everyone"][::-1][:20]
        s=discord.Embed(description=description, colour=user.colour, timestamp=datetime.utcnow())
        s.set_author(name=user.name + (" 📱" if user.is_on_mobile() else ""), icon_url=user.avatar_url)
        s.set_thumbnail(url=user.avatar_url)
        s.add_field(name="Joined Discord", value=joined_discord)
        s.add_field(name="Joined {}".format(server.name), value=joined_server)
        s.add_field(name="Name", value="{}".format(user.name))
        s.add_field(name="Nickname", value="{}".format(user.nick))
        s.add_field(name="Discriminator", value=user.discriminator)
        s.add_field(name="Status", value="{}".format(status))
        s.add_field(name="User's Colour", value="{}".format(user.colour))
        s.add_field(name="User's ID", value="{}".format(user.id))
        s.set_footer(text="Join Position: {} | Requested by {}".format(self.prefixfy(input), author))
        s.add_field(name="Highest Role", value=user.top_role)
        s.add_field(name="Number of Roles", value=len(user.roles) - 1) 
        if not roles:
            s.add_field(name="Roles", value="None", inline=False) 
        else:
            if len(user.roles) - 1 > 20:
                s.add_field(name="Roles", value="{}... and {} more roles".format(", ".join(roles), (len(user.roles) - 21)), inline=False) 
            else:
                s.add_field(name="Roles", value=", ".join(roles), inline=False) 
        await ctx.send(embed=s)

    @commands.command(pass_context=True, no_pm=True, aliases=["sinfo"])
    async def serverinfo(self, ctx, *, server=None):
        """Get some info on the current server"""
        if not server:
            server = ctx.guild
        else:
            try:
                server = self.bot.get_guild(int(server))
            except:
                server = discord.utils.get(self.bot.guilds, name=server)
            if not server:
                return await ctx.send("I could not find that guild :no_entry:")
        author = ctx.message.author
        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        m, s = divmod(server.afk_timeout, 60)
        user = author
        verificationlevel = server.verification_level
        if verificationlevel == server.verification_level.none:
            verificationlevel = "Unrestricted"
        if verificationlevel == server.verification_level.low:
            verificationlevel = "Low"
        if verificationlevel == server.verification_level.medium:
            verificationlevel = "Medium"
        if verificationlevel == server.verification_level.high:
            verificationlevel = "High"
        if verificationlevel is 4:
            verificationlevel = "Very High"
        members = set(server.members)
        server_created = server.created_at.strftime("%d %b %Y %H:%M")
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        online = filter(lambda m: m.status is discord.Status.online, members)
        online = set(online)
        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)
        users = members - bots             
        total_users = len(server.members)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categorys = len(ctx.guild.categories)
        s=discord.Embed(description="{} was created on {}".format(server.name, server_created), colour=discord.Colour(value=colour), timestamp=datetime.utcnow())
        s.set_author(name=server.name, icon_url=server.icon_url)
        s.set_thumbnail(url=server.icon_url)
        s.add_field(name="Region", value=str(server.region))
        s.add_field(name="Total users/bots", value="{} users/bots".format(len(server.members)))
        if len(users) == 1:
            s.add_field(name="Users", value="{} user ({} Online)".format(len(users), (len(users - offline))))
        else:
            s.add_field(name="Users", value="{} users ({} Online)".format(len(users), (len(users - offline))))
        if len(bots) == 1:
            s.add_field(name="Bots", value="{} bot ({} Online)".format(len(bots), (len(bots - offline))))
        else:
            s.add_field(name="Bots", value="{} bots ({} Online)".format(len(bots), (len(bots - offline))))
        s.add_field(name="Text Channels", value=text_channels)
        s.add_field(name="Voice Channels", value=voice_channels)
        s.add_field(name="Categories", value=categorys)        
        s.add_field(name="Verification level", value=verificationlevel)
        s.add_field(name="AFK Timeout", value="{} minutes".format(m, s))
        s.add_field(name="AFK Channel",value=str(server.afk_channel))
        s.add_field(name="Explicit Content Filter", value=str(ctx.guild.explicit_content_filter).title().replace("_", " "))
        s.add_field(name="Roles", value=len(server.roles))
        s.add_field(name="Owner", value="{}".format(server.owner))
        s.add_field(name="Server ID", value=server.id)
        s.set_footer(text="Requested by {}".format(author))
        await ctx.send(embed=s)
        
    @commands.command()
    async def serverstats(self, ctx):
        server = ctx.guild
        serverdata = r.table("stats").get(str(server.id)).run(durability="soft")
        s=discord.Embed()
        s.set_author(name=server.name + " Stats", icon_url=server.icon_url)
        s.add_field(name="Users Joined Today", value=serverdata["members"] if serverdata else "0")
        s.add_field(name="Messages Sent Today", value=serverdata["messages"] if serverdata else "0")
        await ctx.send(embed=s)
        
    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def stats(self, ctx):
        """View the bots live stats"""
        server = ctx.guild
        r.table("botstats").insert({"id": "stats", "messages": 0, "commands": 0, "servers": 0, "users": [], "commandcounter": []}).run(durability="soft")
        botdata = r.table("botstats").get("stats").run(durability="soft")
        uptime = self.format_time_stats(ctx.message.created_at.timestamp() - self.bot.uptime)
        members = list(set(self.bot.get_all_members()))
        online = len(set(filter(lambda m: not m.status == discord.Status.offline, members)))
        offline = len(set(filter(lambda m: m.status == discord.Status.offline, members)))
        process = psutil.Process(os.getpid())
        s=discord.Embed(description="Bot ID: {}".format(self.bot.user.id))
        s.set_author(name=self.bot.user.name + " Stats", icon_url=self.bot.user.avatar_url)
        s.set_thumbnail(url=self.bot.user.avatar_url)
        s.set_footer(text="Uptime: {} | Python {}.{}.{}".format(uptime, sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        s.add_field(name="Developer", value=str(discord.utils.get(self.bot.get_all_members(), id=402557516728369153)))
        s.add_field(name="Library", value="Discord.py {}".format(discord.__version__))
        s.add_field(name="Memory Usage", value="{:,}".format(round(process.memory_info().rss/1000000)) + " MB")
        s.add_field(name="CPU Usage", value=str(psutil.cpu_percent()) + "%")
        s.add_field(name="Text Channels", value="{:,}".format(len([x for x in self.bot.get_all_channels() if isinstance(x, discord.TextChannel)])))
        s.add_field(name="Voice Channels", value="{:,}".format(len([x for x in self.bot.get_all_channels() if isinstance(x, discord.VoiceChannel)])))
        s.add_field(name="Servers Joined Today", value="{:,}".format(len(self.bot.guilds) - botdata["servercountbefore"]))
        s.add_field(name="Commands Used Today", value="{:,}".format(botdata["commands"]))
        s.add_field(name="Messages Sent Today", value="{:,}".format(botdata["messages"]))
        s.add_field(name="Connected Channels", value=len(set(filter(lambda x: x[1].connected_channel, self.bot.lavalink.players))))
        s.add_field(name="Servers", value="{:,}".format(len(self.bot.guilds)))
        s.add_field(name="Users ({:,} total)".format(len(members)), value="{:,} Online\n{:,} Offline\n{:,} use the bot".format(online, offline, len(botdata["users"])))
        await ctx.send(embed=s)

    def format_time_stats(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 1:
            days = "day"
        else: 
            days = "days"
        if h == 1:
            hours = "hour"
        else: 
            hours = "hours"
        if m == 1:
            minutes = "minute"
        else: 
            minutes = "minutes"
        if s == 1:
            seconds = "second"
        else: 
            seconds = "seconds"
        if d == 0 and h == 0:
            time = "%d {} %d {}".format(minutes, seconds) % (m, s)
        elif d == 0 and h == 0 and m == 0:
            time = "%d {}".format(seconds) % (s)
        elif d == 0:
            time = "%d {} %d {} %d {}".format(hours, minutes, seconds) % (h, m, s)
        else:
            time = "%d {} %d {} %d {} %d {}".format(days, hours, minutes, seconds) % (d, h, m, s)
        return time
        
    def prefixfy(self, input):
        number = str(input)
        num = len(number) - 2
        num2 = len(number) - 1
        if int(number[num:]) < 11 or int(number[num:]) > 13:
            if int(number[num2:]) == 1:
                prefix = "st"
            elif int(number[num2:]) == 2:
                prefix = "nd"
            elif int(number[num2:]) == 3:
                prefix = "rd"
            else:
                prefix = "th"
        else:
            prefix = "th"
        return number + prefix

    def format_time_activity(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d != 0:
            return "{} {}".format(round(d), "day" if round(d) == 1 else "days")
        elif h != 0:
            return "{} {}".format(round(h), "hour" if round(h) == 1 else "hours")
        elif m != 0:
            return "{} {}".format(round(m), "minute" if round(m) == 1 else "minutes")
        else:
            return "{} {}".format(round(s), "second" if round(s) == 1 else "seconds")

    async def on_member_join(self, member):
        server = member.guild
        r.table("stats").insert({"id": str(server.id), "messages": 0, "members": 0}).run(durability="soft", noreply=True)
        if server.id not in map(lambda x: x["id"], self._stats):
            self._stats.append({"id": server.id, "messages": 0, "members": 1})
        else:
            list(filter(lambda x: x["id"] == server.id, self._stats))[0]["members"] += 1
 
    async def on_member_remove(self, member):
        server = member.guild
        r.table("stats").insert({"id": str(server.id), "messages": 0, "members": 0}).run(durability="soft", noreply=True)
        if server.id not in map(lambda x: x["id"], self._stats):
            self._stats.append({"id": server.id, "messages": 0, "members": -1})
        else:
            list(filter(lambda x: x["id"] == server.id, self._stats))[0]["members"] -= 1
   
    async def on_command(self, ctx):
        botdata = r.table("botstats").get("stats")
        if str(ctx.author.id) not in botdata["users"].run(durability="soft"):
            botdata.update({"users": r.row["users"].append(str(ctx.author.id)), "commands": r.row["commands"] + 1}).run(durability="soft", noreply=True)
        else:
            botdata.update({"commands": r.row["commands"] + 1}).run(durability="soft", noreply=True)
        if str(ctx.command) not in botdata["commandcounter"].map(lambda x: x["name"]).run(durability="soft"):
            counter = {}
            counter["name"] = str(ctx.command)
            counter["amount"] = 1
            botdata.update({"commandcounter": r.row["commandcounter"].append(counter)}).run(durability="soft", noreply=True)
        else:
            r.table("botstats").get("stats").update({"commandcounter": r.row["commandcounter"].map(lambda x: r.branch(x["name"] == str(ctx.command), x.merge({"amount": x["amount"] + 1}), x))}).run(durability="soft", noreply=True)

    async def checktime(self):
        while not self.bot.is_closed():
            if datetime.utcnow().hour == 23:
                botdata = r.table("botstats").get("stats")
                servers = len(self.bot.guilds) - botdata["servercountbefore"].run()
                s=discord.Embed(colour=0xffff00, timestamp=datetime.utcnow())
                s.set_author(name="Bot Logs", icon_url=self.bot.user.avatar_url)
                if 86400/botdata["commands"].run(durability="soft") >= 1:
                   s.add_field(name="Average Command Usage", value="1 every {}s ({})".format(round(86400/botdata["commands"].run(durability="soft")), botdata["commands"].run()))
                else:
                    s.add_field(name="Average Command Usage", value="{} every second ({})".format(round(botdata["commands"].run(durability="soft")/86400), botdata["commands"].run()))
                s.add_field(name="Servers", value="{} ({})".format(len(self.bot.guilds), "+" + str(servers) if servers >= 0 else servers), inline=False)
                s.add_field(name="Users (No Bots)", value=len(set(filter(lambda m: not m.bot, list(set(self.bot.get_all_members()))))))
                await self.bot.get_channel(445982429522690051).send(embed=s)
                botdata.update({"commands": 0, "messages": 0, "servercountbefore": len(self.bot.guilds)}).run(durability="soft", noreply=True)
                r.table("stats").delete().run(durability="soft", noreply=True)
            await asyncio.sleep(3580)

    async def update_database(self):
        while not self.bot.is_closed():
            try:
                for x in self._stats:
                    data = r.table("stats").get(str(x["id"]))
                    if data.run():
                        data.update({"messages": r.row["messages"] + x["messages"], "members": r.row["members"] + x["members"]}).run(durability="soft", noreply=True)
                self._stats = []
            except Exception as e:
                await self.bot.get_channel(344091594972069888).send(e)
            await asyncio.sleep(300)

    async def on_member_update(self, before, after):
        if after.status != discord.Status.offline and before.status == discord.Status.offline:
            data = r.table("await")
            for x in data.run():
                if str(after.id) in x["users"]:
                    try:
                        author = self.bot.get_user(int(x["id"]))
                    except:
                        continue
                    data.update({"users": r.row["users"].difference([str(after.id)])}).run(durability="soft", noreply=True)
                    await author.send("**{}** is now online<:online:361440486998671381>".format(after))
        
def setup(bot):
    bot.add_cog(general(bot))