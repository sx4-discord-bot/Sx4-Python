import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import html
import random
import math
from utils import arghelp
from PIL import Image, ImageFilter, ImageEnhance
import psutil
from datetime import datetime, timedelta
from utils import checks
import psutil
from urllib.request import Request, urlopen
import json
import urllib
import re
import traceback
from utils import ctime, arg
import os
from random import choice
from threading import Timer
import requests
import rethinkdb as r
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
from enum import Enum
import asyncio
from difflib import get_close_matches

class giveaway:
    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
        self._giveaway_task = bot.loop.create_task(self.check_giveaway())

    def __unload(self):
        self._giveaway_task.cancel()

    @commands.group(usage="<sub command>")
    async def giveaway(self, ctx):
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("giveaway").insert({"id": str(server.id), "giveaway#": 0, "giveaways": []}).run(self.db, durability="soft")

    @giveaway.command()
    async def end(self, ctx, giveaway_id: int):
        serverdata = r.table("giveaway").get(str(ctx.guild.id))
        try:
            await self.determine_giveaway(serverdata, giveaway_id)
        except Exception as e:
            await ctx.send(e.args[0])

    @giveaway.command()
    async def reroll(self, ctx, message_id: int, winners: int=None):
        users = []
        if not winners:
            winners = 1
        try:
            message = await ctx.channel.get_message(message_id)
        except:
            return await ctx.send("Make sure you are re-rolling in the same channel as the giveaway message and that the ID is correct :no_entry:")
        if message.author != self.bot.user:
            return await ctx.send("Make sure the message id is a giveaway message :no_entry:")
        try:
            if message.embeds[0].footer.text == "Giveaway Ended":
                try:
                    regex = re.match("\*\*(.*)\*\* has won \*\*(.*)\*\*", message.embeds[0].description).group(1)
                    if regex:
                        for x in regex.split(", "):
                            user = discord.utils.get(ctx.guild.members, name=x.split("#")[0], discriminator=x.split("#")[1])
                            if user:
                                users.append(user)
                    else:
                        return await ctx.send("That's not a giveaway message :no_entry:")
                except:
                    return await ctx.send("That's not a giveaway message :no_entry:")
            else:
                return await ctx.send("The giveaway has not finished yet :no_entry:")
        except:
            return await ctx.send("That's not a giveaway message :no_entry:")
        try:
            reaction = list(filter(lambda x: x.emoji == "🎉", message.reactions))[0]
        except:
            return await ctx.send("This message has no :tada: reactions :no_entry:")
        try:
            winner = random.sample([x for x in await reaction.users().flatten() if x != self.bot.user and x not in users], k=winners)
        except:
            try:
                winner = random.sample([x for x in await reaction.users().flatten() if x != self.bot.user and x not in users], k=len([x for x in await reaction.users().flatten() if x != self.bot.user]))
            except:
                return await ctx.send("Not enough people reacted on the message to get a new winner :no_entry:")
        await ctx.send("The new {} {}, Congratulations :tada:".format("winner is" if len(winner) == 1 else "winners are", ", ".join([x.mention for x in winner])))

    @giveaway.command()
    @checks.has_permissions("manage_roles")
    async def delete(self, ctx, giveaway_id: int):
        """delete a giveaway"""
        server = ctx.guild
        serverdata = r.table("giveaway").get(str(server.id))
        giveaway = serverdata["giveaways"].filter(lambda x: x["id"] == giveaway_id).run(self.db)
        if not giveaway:
            return await ctx.send("That giveaway ID does not exist :no_entry:")
        else:
            giveaway = giveaway[0]
        channel = ctx.guild.get_channel(int(giveaway["channel"]))
        if channel:
            try:
                message = await channel.get_message(int(giveaway["message"]))
                try:
                    await message.delete()
                except:
                    pass
            except discord.errors.NotFound:
                pass
        serverdata.update({"giveaways": r.row["giveaways"].filter(lambda x: x["id"] != giveaway_id)}).run(self.db, durability="soft")
        await ctx.send("That giveaway has been cancelled and deleted.")

    @giveaway.command()
    @checks.has_permissions("manage_roles")
    async def setup(self, ctx, channel: str=None, winners: int=None, duration: str=None, *, giveaway_item: str=None):
        """Setup a giveaway, minimum time 120 seconds"""
        giveaway = {}
        server = ctx.guild
        serverdata = r.table("giveaway").get(str(server.id))
        if channel and duration and giveaway_item and winners:
            title = "Giveaway"
        else:
            def checkchar(m):
                return m.channel == ctx.channel and m.author == ctx.author and len(m.content) <= 256
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author and len(m.content) <= 2000
            def check_winner(m):
                return m.channel == ctx.channel and m.author == ctx.author and m.content.isdigit()
            def check_time(m):
                if m.channel == ctx.channel and m.author == ctx.author:
                    if m.content.lower() == "cancel":
                        return True
                    else:
                        try:
                            seconds = ctime.convert(m.content.lower())
                        except ValueError:
                            return False
                        if seconds >= 120 and seconds <= 31556926:
                            return True
            def check_channel(m):
                if m.channel == ctx.channel and m.author == ctx.author:
                    if m.content.lower() == "cancel":
                        return True
                    channel = arg.get_text_channel(ctx, m.content)
                    if channel:
                        return True
            if not channel:
                await ctx.send("What channel would you like me to start this giveaway? Type \"cancel\" at anytime to cancel the creation (Respond below)")
                try:
                    channel = await self.bot.wait_for("message", check=check_channel, timeout=300)
                    if channel.content.lower() == "cancel":
                        await ctx.send("Cancelled")
                        return
                    channel = channel.content
                except asyncio.TimeoutError:
                    await ctx.send("Timed out :stopwatch:")
                    return
                except asyncio.TimeoutError:
                    await ctx.send("Timed out :stopwatch:")
                    return
            await ctx.send("What do you want to name your giveaway? (Respond below)")
            try:
                title = await self.bot.wait_for("message", check=checkchar, timeout=300)
                if title.content.lower() == "cancel":
                    await ctx.send("Cancelled")
                    return
                title = title.content
            except asyncio.TimeoutError:
                await ctx.send("Timed out :stopwatch:")
                return
            if not winners:
                await ctx.send("How many winners would you like? (Respond below)")
                try:
                    winners = await self.bot.wait_for("message", check=check_winner, timeout=300)
                    if winners.content.lower() == "cancel":
                        await ctx.send("Cancelled")
                        return
                    winners = int(winners.content)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out :stopwatch:")
                    return
            if not duration:
                await ctx.send("How long do you want your giveaway to last? (After the numerical value add 'd' for days, 'h' for hours, 'm' for minutes, 's' for seconds) Minimum time: 2 minutes. (Respond below)")
                try:
                    time2 = await self.bot.wait_for("message", check=check_time, timeout=300)
                    if time2.content.lower() == "cancel":
                        await ctx.send("Cancelled")
                        return
                    duration = time2.content
                except asyncio.TimeoutError:
                    await ctx.send("Timed out :stopwatch:")
                    return
            if not giveaway_item:
                await ctx.send("What are you giving away? (Respond below)")
                try:
                    item = await self.bot.wait_for("message", check=check, timeout=300)
                    if item.content.lower() == "cancel":
                        await ctx.send("Cancelled")
                        return
                    giveaway_item = item.content
                except asyncio.TimeoutError:
                    await ctx.send("Timed out :stopwatch:")
                    return
            
        serverdata.update({"giveaway#": r.row["giveaway#"] + 1}).run(self.db, durability="soft")
        id = serverdata["giveaway#"].run(self.db, durability="soft")
        channel = arg.get_text_channel(ctx, channel)
        if not channel:
            return await ctx.send("I could not find that channel :no_entry:")
        try:
            giveaway_seconds = ctime.convert(duration)
        except ValueError:
            return await ctx.send("Invalid duration format :no_entry:")
        if giveaway_seconds < 120:
            return await ctx.send("Giveaways have to be at least 2 minutes long :no_entry:")
        starttime = datetime.utcnow().timestamp()
        endtime = datetime.utcnow().timestamp() + giveaway_seconds
        s=discord.Embed(title=title, description="Enter by reacting with :tada:\n\nThis giveaway is for **{}**\nDuration: **{}**\nWinners: **{}**".format(giveaway_item, self.giveaway_time(starttime, endtime), winners), timestamp=datetime.fromtimestamp(datetime.utcnow().timestamp() + giveaway_seconds))
        s.set_footer(text="Ends")
        message = await channel.send(embed=s)
        await message.add_reaction("🎉")
        giveaway["title"] = title
        giveaway["endtime"] = datetime.utcnow().timestamp() + giveaway_seconds
        giveaway["length"] = giveaway_seconds
        giveaway["item"] = giveaway_item
        giveaway["channel"] = str(channel.id)
        giveaway["message"] = str(message.id)
        giveaway["winners"] = winners
        giveaway["id"] = id
        serverdata.update({"giveaways": r.row["giveaways"].append(giveaway)}).run(self.db, durability="soft")
        await ctx.send("Your giveaway has been created :tada:\nGiveaway ID: `{}` (This can be used to delete and end giveaways)".format(id))
        
    async def check_giveaway(self):
        while not self.bot.is_closed():
            try:
                data = r.table("giveaway")
                for sdata in data.run(self.db, durability="soft"):
                    serverdata = data.get(sdata["id"])
                    for x in sdata["giveaways"]:
                        if x["endtime"] <= datetime.utcnow().timestamp():
                            try:
                                await self.determine_giveaway(serverdata, x["id"])
                            except:
                                serverdata.update({"giveaways": r.row["giveaways"].filter(lambda y: y["id"] != x["id"])}).run(self.db, durability="soft", noreply=True)
            except Exception as e:
                await self.bot.get_channel(344091594972069888).send(e)
            await asyncio.sleep(60)

    async def determine_giveaway(self, guild_data, giveaway_id):
        guild = self.bot.get_guild(int(guild_data["id"].run(self.db)))
        message_data = guild_data["giveaways"].filter(lambda x: x["id"] == giveaway_id).run(self.db)
        if not message_data:
            raise ValueError("Invalid giveaway ID :no_entry:")
        message_data = message_data[0]
        channel = guild.get_channel(int(message_data["channel"]))
        if channel is None:
            raise ValueError("The channel in which that giveaway was hosted has been deleted :no_entry:")
        try:
            message = await channel.get_message(int(message_data["message"]))
        except discord.errors.NotFound as e:
            raise discord.errors.NotFound(e.response, "The message in the giveaway no longer exists :no_entry:")
        try:
            reaction = [x for x in message.reactions if x.emoji == "🎉"][0]
        except IndexError:
            raise IndexError("There are not any :tada: reactions on that message :no_entry:")
        winner = random.sample([x for x in await reaction.users().flatten() if x != self.bot.user], k=min(len([x for x in await reaction.users().flatten() if x != self.bot.user]), message_data["winners"]))
        if winner == []:
            await channel.send("No one entered the giveaway :no_entry:")
            await message.delete()
            guild_data.update({"giveaways": r.row["giveaways"].filter(lambda y: y["id"] != message_data["id"])}).run(self.db, durability="soft", noreply=True)
            return
        s=discord.Embed(title=message_data["title"], description="**{}** has won **{}**".format(", ".join([str(x) for x in winner]), message_data["item"]))
        s.set_footer(text="Giveaway Ended")
        await message.edit(embed=s)
        await channel.send("{}, Congratulations you won the giveaway for **{}**".format(", ".join([x.mention for x in winner]), message_data["item"]))
        guild_data.update({"giveaways": r.row["giveaways"].filter(lambda y: y["id"] != message_data["id"])}).run(self.db, durability="soft", noreply=True)


    def giveaway_time(self, starttime, endtime):
        m, s = divmod(endtime - starttime, 60)
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
            seconds = "seconds"
        else: 
            seconds = "seconds"
        duration = ("%d %s " % (d, days) if d != 0 else "") + ("%d %s " % (h, hours) if h != 0 else "") + ("%d %s " % (m, minutes) if m != 0 else "") + ("%d %s " % (s, seconds) if s >= 1 else "")
        return duration

def setup(bot, connection): 
    bot.add_cog(giveaway(bot, connection))