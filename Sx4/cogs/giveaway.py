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
from urllib.request import Request, urlopen
import json
import urllib
import re
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
    def __init__(self, bot):
        self.bot = bot
        self._giveaway_task = bot.loop.create_task(self.check_giveaway())

    def __unload(self):
        self._giveaway_task.cancel()

    @commands.group()
    async def giveaway(self, ctx):
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("giveaway").insert({"id": str(server.id), "giveaway#": 0, "giveaways": []}).run()

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
    async def delete(self, ctx, id: int):
        """delete a giveaway"""
        server = ctx.guild
        serverdata = r.table("giveaway").get(str(server.id))
        try:
            message = await self.bot.get_channel(int(serverdata["giveaways"].filter({"id": id})[0]["channel"].run())).get_message(int(serverdata["giveaways"].filter({"id": id})[0]["message"].run()))
        except:
            await ctx.send("Not a valid id :no_entry:")
            return
        try:
            await message.delete()
        except:
            pass
        serverdata.update({"giveaways": r.row["giveaways"].filter(lambda x: x["id"] != id)}).run()
        await ctx.send("That giveaway has been cancelled and deleted.")

    @giveaway.command()
    @checks.has_permissions("manage_roles")
    async def setup(self, ctx):
        """Setup a giveaway, minimum time 120 seconds"""
        giveaway = {}
        server = ctx.guild
        serverdata = r.table("giveaway").get(str(server.id))
        def checkchar(m):
            return m.channel == ctx.channel and m.author == ctx.author and len(m.content) <= 256
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and len(m.content) <= 2000
        def check_winner(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content.isdigit()
        def check_time(m):
            if m.content.lower() == "cancel" and m.channel == ctx.channel and m.author == ctx.author:
                return True
            if m.channel == ctx.channel and m.author == ctx.author and m.content.isdigit() and int(m.content) >= 120 and int(m.content) <= 31556926:
                return True
        def check_channel(m):
            if m.channel == ctx.channel and m.author == ctx.author:
                if m.content.lower() == "cancel":
                    return True
                if "<" in m.content.lower() and "#" in m.content.lower():
                    channel = m.content.replace("#", "").replace("<", "").replace(">", "")
                    channel = discord.utils.get(ctx.guild.text_channels, id=int(channel))
                else:
                    try:
                        channel = discord.utils.get(ctx.guild.text_channels, id=int(m.content.lower()))
                    except:
                        channel = discord.utils.get(ctx.guild.text_channels, name=m.content)
                if channel:
                    return True
        await ctx.send("What channel would you like me to start this giveaway? Type \"cancel\" at anytime to cancel the creation (Respond below)")
        try:
            channel = await self.bot.wait_for("message", check=check_channel, timeout=300)
            if channel.content.lower() == "cancel":
                await ctx.send("Cancelled")
                return
            if "<" in channel.content and "#" in channel.content:
                channel = channel.content.replace("#", "").replace("<", "").replace(">", "")
                channel = discord.utils.get(ctx.guild.text_channels, id=int(channel))
            else:
                try:
                    channel = discord.utils.get(ctx.guild.text_channels, id=int(channel.content.lower()))
                except:
                    channel = discord.utils.get(ctx.guild.text_channels, name=channel.content)
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
        except asyncio.TimeoutError:
            await ctx.send("Timed out :stopwatch:")
            return
        await ctx.send("How many winners would you like? (Respond below)")
        try:
            winners = await self.bot.wait_for("message", check=check_winner, timeout=300)
            if winners.content.lower() == "cancel":
                await ctx.send("Cancelled")
                return
        except asyncio.TimeoutError:
            await ctx.send("Timed out :stopwatch:")
            return
        await ctx.send("How long do you want your giveaway to last (in seconds, minimum seconds: 120)? (Respond below)")
        try:
            time2 = await self.bot.wait_for("message", check=check_time, timeout=300)
            if time2.content.lower() == "cancel":
                await ctx.send("Cancelled")
                return
        except asyncio.TimeoutError:
            await ctx.send("Timed out :stopwatch:")
            return
        await ctx.send("What are you giving away? (Respond below)")
        try:
            item = await self.bot.wait_for("message", check=check, timeout=300)
            if item.content.lower() == "cancel":
                await ctx.send("Cancelled")
                return
        except asyncio.TimeoutError:
            await ctx.send("Timed out :stopwatch:")
            return
        serverdata.update({"giveaway#": r.row["giveaway#"] + 1}).run()
        id = serverdata["giveaway#"].run()
        starttime = datetime.utcnow().timestamp()
        endtime = datetime.utcnow().timestamp() + int(time2.content)
        s=discord.Embed(title=title.content, description="Enter by reacting with :tada:\n\nThis giveaway is for **{}**\nDuration: **{}**\nWinners: **{}**".format(item.content, await self.giveaway_time(starttime, endtime), int(winners.content)), timestamp=datetime.fromtimestamp(datetime.utcnow().timestamp() + int(time2.content)))
        s.set_footer(text="Ends")
        message = await channel.send(embed=s)
        await message.add_reaction("🎉")
        giveaway["title"] = title.content
        giveaway["endtime"] = datetime.utcnow().timestamp() + int(time2.content)
        giveaway["length"] = int(time2.content)
        giveaway["item"] = item.content
        giveaway["channel"] = str(channel.id)
        giveaway["message"] = str(message.id)
        giveaway["winners"] = int(winners.content)
        giveaway["id"] = id
        serverdata.update({"giveaways": r.row["giveaways"].append(giveaway)}).run()
        await ctx.send("Your giveaway has been created :tada:\nGiveaway ID: `{}` (This can be used to delete giveaways)".format(id))
        
    async def check_giveaway(self):
        await self.bot.wait_until_ready()
        data = r.table("giveaway")
        while not self.bot.is_closed():
            for sdata in data.run():
                serverdata = data.get(sdata["id"])
                for x in sdata["giveaways"]:
                    if x["endtime"] <= datetime.utcnow().timestamp():
                        try:
                            message = await self.bot.get_channel(int(x["channel"])).get_message(int(x["message"]))
                            reaction = [x for x in message.reactions if x.emoji == "🎉"][0]
                            try:
                                winner = random.sample([x for x in await reaction.users().flatten() if x != self.bot.user], k=x["winners"])
                            except:
                                winner = random.sample([x for x in await reaction.users().flatten() if x != self.bot.user], k=len([x for x in await reaction.users().flatten() if x != self.bot.user]))
                            if winner == []:
                                await self.bot.get_channel(int(x["channel"])).send("No one entered the giveaway :no_entry:")
                                await message.delete()
                                serverdata.update({"giveaways": r.row["giveaways"].filter(lambda y: y["id"] != x["id"])}).run()
                                return
                            s=discord.Embed(title=x["title"], description="**{}** has won **{}**".format(", ".join([str(x) for x in winner]), x["item"]))
                            s.set_footer(text="Giveaway Ended")
                            await message.edit(embed=s)
                            await self.bot.get_channel(int(x["channel"])).send("{}, Congratulations you won the giveaway for **{}**".format(", ".join([x.mention for x in winner]), x["item"]))
                            serverdata.update({"giveaways": r.row["giveaways"].filter(lambda y: y["id"] != x["id"])}).run()
                        except:
                            pass
            await asyncio.sleep(120)


    async def giveaway_time(self, starttime, endtime):
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
        if d == 0 and h == 0:
            duration = "%d {} %d {}".format(minutes, seconds) % (m, s)
        elif d == 0 and h == 0 and m == 0:
            duration = "%d {}".format(seconds) % (s)
        elif d == 0:
            duration = "%d {} %d {} %d {}".format(hours, minutes, seconds) % (h, m, s)
        else:
            duration = "%d {} %d {} %d {} %d {}".format(days, hours, minutes, seconds) % (d, h, m, s)
        return duration

def setup(bot): 
    bot.add_cog(giveaway(bot))