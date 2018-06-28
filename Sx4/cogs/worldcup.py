import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import html
import random
import math
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
from utils.dataIO import dataIO
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
from enum import Enum
import asyncio
from difflib import get_close_matches

class worldcup:
    def __init__(self, bot):
        self.bot = bot

    
    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def worldcup(self, ctx):
        pass

    @worldcup.command()
    async def today(self, ctx):
        url = "http://worldcup.sfg.io/matches/today"
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(title="World Cup Fixtures Today")
        for x in data:
            if x["status"] == "future":
                s.add_field(name="{} vs {}".format(x["home_team"]["country"], x["away_team"]["country"]), value="Kick off: {}".format((datetime.strptime(x["datetime"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=1)).strftime("%H:%M BST")))
            else:
                s.add_field(name="{} vs {}".format(x["home_team"]["country"], x["away_team"]["country"]), value="{} - {}\nTime: {}".format(x["home_team"]["goals"], x["away_team"]["goals"], x["time"]))
        await ctx.send(embed=s)

    @worldcup.command()
    async def table(self, ctx):
        url = "http://worldcup.sfg.io/teams/results"
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        group_id = 1
        reactionstatus = True
        group = [x for x in data if x["group_id"] == group_id]
        table = "\n".join(["{} - {} points".format(x["country"], x["points"]) for x in sorted([x for x in group], key=lambda m: m["points"], reverse=True)])
        s=discord.Embed(title="Group {}".format([x["group_letter"] for x in group][0]), description=table)
        message = await ctx.send(embed=s)
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user != self.bot.user:
                if user == ctx.author:
                    if reaction.message.channel == ctx.channel:
                        if reaction.emoji == "▶" or reaction.emoji == "◀":
                            return True
        while reactionstatus:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=reactioncheck, timeout=30)
            except asyncio.TimeoutError:
                await message.remove_reaction("◀", ctx.me)
                await message.remove_reaction("▶", ctx.me)
                reactionstatus = False
                return
            if reaction.emoji == "▶":
                if group_id == 8:
                    group_id = 1
                else:
                    group_id += 1
                group = [x for x in data if x["group_id"] == group_id]
                table = "\n".join(["{} - {} points".format(x["country"], x["points"]) for x in sorted([x for x in group], key=lambda m: m["points"], reverse=True)])
                s=discord.Embed(title="Group {}".format([x["group_letter"] for x in group][0]), description=table)
                await message.edit(embed=s)
            if reaction.emoji == "◀":
                if group_id == 1:
                    group_id = 8
                else:
                    group_id -= 1
                group = [x for x in data if x["group_id"] == group_id]
                table = "\n".join(["{} - {} points".format(x["country"], x["points"]) for x in sorted([x for x in group], key=lambda m: m["points"], reverse=True)])
                s=discord.Embed(title="Group {}".format([x["group_letter"] for x in group][0]), description=table)
                await message.edit(embed=s)

    @worldcup.command()
    async def team(self, ctx, *, team: str):
        url = "http://worldcup.sfg.io/teams/results"
        url1 = "http://worldcup.sfg.io/matches"
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        request1 = Request(url1)
        data1 = json.loads(urlopen(request1).read().decode())
        group = [x for x in data if x["country"].lower() == team.lower()]
        matches = [x for x in data1 if x["home_team"]["country"].lower() == team.lower() or x["away_team"]["country"].lower() == team.lower()]
        if group == []:
            await ctx.send("That team isn't in the world cup :no_entry:")
            return
        s=discord.Embed(title="{} World Cup Statistics".format([x["country"] for x in group][0]))
        for x in group:
            s.add_field(name="Games Played", value=x["games_played"], inline=False)
            s.add_field(name="Wins", value=x["wins"], inline=True)
            s.add_field(name="Draws", value=x["draws"])
            s.add_field(name="Losses", value=x["losses"])
            s.add_field(name="Goals Scored", value=x["goals_for"])
            s.add_field(name="Goal Conceded", value=x["goals_against"])
            s.add_field(name="Goal Difference", value=x["goal_differential"])
        upcoming = "\n".join(["{} vs {}".format(x["home_team"]["country"], x["away_team"]["country"]) for x in matches if x["status"] == "future"])
        finished = "\n".join(["{} vs {} ({} - {})".format(x["home_team"]["country"], x["away_team"]["country"], x["home_team"]["goals"], x["away_team"]["goals"]) for x in matches if x["status"] == "completed"])
        current = "\n".join(["{} vs {} ({} - {})\nTime: {}".format(x["home_team"]["country"], x["away_team"]["country"], x["home_team"]["goals"], x["away_team"]["goals"], x["time"]) for x in matches if x["status"] == "in progress"])
        if upcoming != "":
            s.add_field(name="Upcoming Matches", value=upcoming)
        if finished != "":
            s.add_field(name="Matches Played", value=finished)
        if current != "":
            s.add_field(name="Currently Playing", value=current)
        await ctx.send(embed=s)



            

def setup(bot):
    bot.add_cog(worldcup(bot))

