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

rps_settings = {"rps_wins": 0, "rps_draws": 0, "rps_losses": 0}
giveaway = {"users": None}

class general:
    def __init__(self, bot):
        self.bot = bot
        self._stats_task = bot.loop.create_task(self.checktime())
        self.JSON = 'data/general/rps.json'
        self.settings = dataIO.load_json(self.JSON)
        self.settings = defaultdict(lambda: rps_settings, self.settings)
        self.file = "data/general/triggers.json"
        self.d = dataIO.load_json(self.file)
        self._shop_file = 'data/economy/shop.json'
        self._shop = dataIO.load_json(self._shop_file)
        self._stats_file = 'data/general/stats.json'
        self._stats = dataIO.load_json(self._stats_file)

    def __unload(self):
        self._stats_task.cancel()

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def shorten(self, ctx, *, url):
        url1 = "https://api.rebrandly.com/v1/links"
        request = requests.post(url1, data=json.dumps({"destination": url}), headers={"Content-Type": "application/json", "apikey": ""})
        try:
            request.json()["message"]
            await ctx.send("Invalid Url :no_entry:")
        except:
            await ctx.send("https://" + request.json()["shortUrl"])

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.default)
    async def meme(self, ctx):
        number = randint(0, 100)
        url = "https://www.reddit.com/r/meme.json?sort=new&limit=100"
        url2 = "https://www.reddit.com/r/memeeconomy.json?sort=new&limit=100"
        url = random.choice([url, url2])
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())["data"]["children"][number]["data"]
        s=discord.Embed()
        s.set_author(name=data["title"], url="https://www.reddit.com" + data["permalink"])
        s.set_image(url=data["url"])
        await ctx.send(embed=s)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def copyemote(self, ctx, emote: discord.PartialEmoji):
        with open("image.png", "wb") as f:
            f.write(requests.get(emote.url).content)
        with open("image.png", "rb") as f:
            image = f.read()
            image = bytearray(image)
        try:
            emoji = await ctx.guild.create_custom_emoji(name=emote.name, image=image)
        except discord.errors.Forbidden:
            await ctx.send("I do not have the manage emojis permission :no_entry:")
            return
        except discord.errors.HTTPException:
            await ctx.send("I was unable to make the emote this may be because you've hit the emote cap :no_entry:")
            return
        await ctx.send("{} has been copied and created".format(emoji))
        os.remove("image.png")
		
    @commands.command(pass_context=True, aliases=["emote"])
    async def emoji(self, ctx, emote: discord.PartialEmoji):
        """Find a random emoji the bot can find"""
        s=discord.Embed(colour=ctx.message.author.colour) 
        s.set_author(name=emote.name, url=emote.url)		
        s.set_image(url=emote.url)
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
    async def discordmeme(self, ctx):
        """Have a discord meme"""
        url = "https://api.weeb.sh/images/random?type=discord_memes"
        request = Request(url)
        request.add_header("Authorization",  "")
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(); s.set_image(url=data["url"]); s.set_footer(text="Powered by weeb.sh"); await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def google(self, ctx, *, search): 
        """returns the top 5 results from google of your search query"""
        url = "https://www.googleapis.com/customsearch/v1?key=&cx=&{}".format(urllib.parse.urlencode({"q": search}))
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        try:
            results = "\n\n".join(["**[{}]({})**\n{}".format(x["title"], x["link"], x["snippet"]) for x in data["items"]][:5])
        except:
            await ctx.send("No Results :no_entry:")
            return
        s=discord.Embed(description=results)
        s.set_author(name="Google", icon_url="https://images-ext-1.discordapp.net/external/UsMM0mPPHEKn6WMst8WWG9qMCX_A14JL6Izzr47ucOk/http/i.imgur.com/G46fm8J.png", url="https://www.google.co.uk/search?{}".format(urllib.parse.urlencode({"q": search})))
        await ctx.send(embed=s)
		
    @commands.command(pass_context=True)
    async def googleimage(self, ctx, *, search): 
        """returns an image based on your search from google"""
        url = "https://www.googleapis.com/customsearch/v1?key=&cx=&searchType=image&{}".format(urllib.parse.urlencode({"q": search}))
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed()
        s.set_author(name="Google", icon_url="https://images-ext-1.discordapp.net/external/UsMM0mPPHEKn6WMst8WWG9qMCX_A14JL6Izzr47ucOk/http/i.imgur.com/G46fm8J.png", url="https://www.google.co.uk/search?{}".format(urllib.parse.urlencode({"q": search})))
        try:
            s.set_image(url=data["items"][0]["image"]["thumbnailLink"])
        except:
            await ctx.send("No results :no_entry:")
            return
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def dictionary(self, ctx, *, word): 
        """Look up the definition of any word using an actual dictionary"""
        url = "https://od-api.oxforddictionaries.com:443/api/v1/entries/en/{}".format(word)
        request = Request(url)
        request.add_header("Accept", "application/json")
        request.add_header("app_id", "")
        request.add_header("app_key", "")
        try:
            data = json.loads(urlopen(request).read().decode())
        except:
            await ctx.send("No results :no_entry:")
            return
        definition = data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
        pronounce = data["results"][0]["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
        s=discord.Embed(colour=ctx.message.author.colour)
        s.set_author(name=data["results"][0]["id"], url="https://en.oxforddictionaries.com/definition/{}".format(data["results"][0]["id"]))
        s.add_field(name="Definition", value=definition)
        s.add_field(name="Pronunciation", value=pronounce, inline=False)
        await ctx.send(embed=s)

    @commands.command(pass_context=True)
    async def steam(self, ctx, *, profile_url: str):
        """To get a steam profile you need to click on the users profile and get the vanityurl which is the name after /id/{} <--- The name should be there""" 
        idurl = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=&{}".format(urllib.parse.urlencode({"vanityurl": profile_url.replace("https://steamcommunity.com/id/", "")}))
        idrequest = Request(idurl)
        try:
            id = json.loads(urlopen(idrequest).read().decode())["response"]["steamid"]
        except:
            id = profile_url.replace("https://steamcommunity.com/id/", "")
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=&steamids={}".format(id)
        request = Request(url)
        try:
            data = json.loads(urlopen(request).read().decode())["response"]["players"][0]
        except:
            await ctx.send("No results :no_entry:")
            return
        m, s = divmod(ctx.message.created_at.timestamp() - data["lastlogoff"], 60)
        h , m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 0 and h == 0:
            time = "%dm %ds ago" % (m, s)
        elif d == 0 and h == 0 and m == 0:
            time = "%ds ago" % (s)
        elif d == 0:
            time = "%dh %dm %ds ago" % (h, m, s)
        else:
            time = "%dd %dh %dm %ds ago" % (d, h, m, s)
        if data["personastate"] == 0:
            if data["communityvisibilitystate"] == 1:
                state = "Private Account"
            else:
                state = "Offline"
        if data["personastate"] == 1:
            state = "Online"
        if data["personastate"] == 2:
            state = "Busy"
        if data["personastate"] == 3:
            state = "Away"
        if data["personastate"] == 4:
            state = "Snooze"
        if data["personastate"] == 5 or data["personastate"] == 6:
            state = "Online"
        s=discord.Embed(description="Steam Profile <:steam:392219187184926732>")
        s.set_author(name=data["personaname"], icon_url=data["avatarfull"], url=data["profileurl"])
        s.set_thumbnail(url=data["avatarfull"])
        s.add_field(name="Status", value=state)
        if state != "Offline":
            s.add_field(name="Last time logged in", value="Online now")
        else:
            s.add_field(name="Last time logged in", value=time)
        if data["communityvisibilitystate"] == 1:
            await ctx.send(embed=s)
            return
        try:
            s.add_field(name="Real name", value=data["realname"])
        except:
            pass
        try:
            s.add_field(name="Currently Playing", value=data["gameextrainfo"])
        except:
            s.add_field(name="Currently Playing", value="Nothing")
        await ctx.send(embed=s)         
        
    @commands.command(pass_context=True)
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
        request = Request(url)
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
    async def dbltag(self, ctx, *, dbl_tag):
        """Shows the top 10 bots (sorted by monthly upvotes) in the tag form there you can select and view 1"""
        url = "https://discordbots.org/api/bots?search=tags:{}&limit=10&sort=monthlyPoints&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot,tags".format(urllib.parse.urlencode({"": dbl_tag}).replace("=", ""))
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        if len(data["results"]) == 0:
            await ctx.send("That is not a valid tag :no_entry:")
            return
        n = 0
        msg = ""
        for x in data["results"]:
            msg += "{}. **{}#{}**\n".format(n+1, x["username"], x["discriminator"])
            n = n + 1
            for y in x["tags"]:         
                if dbl_tag.lower() in y.lower():
                    tag = y 
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
                s.add_field(name="Guilds", value=data["results"][response]["server_count"])
            except:
                s.add_field(name="Guilds", value="N/A")
            s.add_field(name="Prefix", value=data["results"][response]["prefix"])
            s.add_field(name="Library", value=data["results"][response]["lib"])
            s.add_field(name="Approval Date", value=datetime.strptime(data["results"][response]["date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y"))
            s.add_field(name="Monthly votes", value=str(data["results"][response]["monthlyPoints"]) + " :thumbsup:")
            s.add_field(name="Total votes", value=str(data["results"][response]["points"]) + " :thumbsup:")
            if "https://" not in data["results"][response]["invite"]:
                s.add_field(name="Invite", value="**[Invite {} to your server](https://discordapp.com/oauth2/authorize?client_id={}&scope=bot)**".format(data["results"][response]["username"], data["results"][response]["id"]))
            else:
                s.add_field(name="Invite", value="**[Invite {} to your server]({})**".format(data["results"][response]["username"], data["results"][response]["invite"]))

            await ctx.send(embed=s)
         
    @commands.command(pass_context=True)
    async def dbl(self, ctx, user: str=None):
        """Look up any bot on discord bot list and get statistics from it"""
        if not user:
            user = str(self.bot.user.id)
        if "<" in user and "@" in user:
            userid = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(userid)
        elif "#" in user: 
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            url = "https://discordbots.org/api/bots?search=username:{}&discriminator:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(user[:usernum], user[usernum + 1:len(user)])
        else:
            try:
                int(user)
                url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&sort=points".format(user)
            except:
                user = urllib.parse.quote(user)
                url = "https://discordbots.org/api/bots?search=username:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&limit=1&sort=points".format(user)
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())["results"]
        if len(data) == 0:
            await ctx.send("I could not find that bot :no_entry:")
            return
        data = data[0]
        if data["certifiedBot"] == True:
            s=discord.Embed(description="<:dblCertified:392249976639455232> | " + data["shortdesc"])
        else:
            s=discord.Embed(description=data["shortdesc"])
        s.set_author(name=data["username"] + "#" + data["discriminator"], icon_url="https://cdn.discordapp.com/avatars/{}/{}".format(data["id"], data["avatar"]), url="https://discordbots.org/bot/{}".format(data["id"]))
        s.set_thumbnail(url="https://cdn.discordapp.com/avatars/{}/{}".format(data["id"], data["avatar"]))
        try:
            s.add_field(name="Guilds", value=data["server_count"])
        except:
            s.add_field(name="Guilds", value="N/A")
        s.add_field(name="Prefix", value=data["prefix"])
        s.add_field(name="Library", value=data["lib"])
        s.add_field(name="Approval Date", value=datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y"))
        s.add_field(name="Monthly votes", value=str(data["monthlyPoints"]) + " :thumbsup:")
        s.add_field(name="Total votes", value=str(data["points"]) + " :thumbsup:")
        if "https://" not in data["invite"]:
            s.add_field(name="Invite", value="**[Invite {} to your server](https://discordapp.com/oauth2/authorize?client_id={}&scope=bot)**".format(data["username"], data["id"]))
        else:
            s.add_field(name="Invite", value="**[Invite {} to your server]({})**".format(data["username"], data["invite"]))

        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def botlist(self, ctx, page: int=None):
        """A list of the bots with the most servers on discord bot list"""
        if not page:
            page = 0
        else: 
            page = page - 1
        if page < 0 or page > 49:
            await ctx.send("Invalid page :no_entry:")
            return
        url="https://discordbots.org/api/bots?sort=server_count&limit=10&offset={}&fields=username,server_count".format((page + 1)*10-10)
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        n = page*10
        l = 0
        msg = ""
        for x in data["results"]:
            n = n + 1
            l = l + 1
            msg += "{}. {} - **{}** servers\n".format(n, data["results"][l-1]["username"], data["results"][l-1]["server_count"])
        s=discord.Embed(description=msg)
        s.set_author(name="Bot List")
        s.set_footer(text="Page {}/50".format(page+1))
        await ctx.send(embed=s)

    @commands.command(pass_context=True, aliases=["ud"])
    async def urbandictionary(self, ctx, search_term, page: int=None):
        """Look up the definition of a word on the urbandictionary"""
        if not page:
            page = 0
        else:
            page = page - 1
        url = "http://api.urbandictionary.com/v0/define?" + urllib.parse.urlencode({"term": search_term})
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        if data["result_type"] == "no_results":
            await ctx.send("No results :no_entry:")
            return
        if len(data["list"]) < page + 1:
            await ctx.send("That is not a valid page :no_entry:")
            return
        if len([x for x in str(data["list"][page]["definition"])]) > 900:
            definition = str(data["list"][page]["definition"])[:900] + '... [Read more]({})'.format(data["list"][page]["permalink"])
        else:
            definition = str(data["list"][page]["definition"])
        if len([x for x in str(data["list"][page]["example"])]) > 900:
            example = str(data["list"][page]["example"])[:900] + '... [Read more]({})'.format(data["list"][page]["permalink"])
        else:
            example = str(data["list"][page]["example"])
        s=discord.Embed(colour=ctx.message.author.colour)
        s.set_author(name=data["list"][page]["word"], url=data["list"][page]["permalink"])
        s.add_field(name="Definition", value=definition, inline=False)
        if example != "":
            s.add_field(name="Example", value=example)
        s.set_footer(text="{} 👍 | {} 👎 | Page {}/{}".format(data["list"][page]["thumbs_up"], data["list"][page]["thumbs_down"], page + 1, len(data["list"])))
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Am i alive? (Well if you're reading this, yes)"""
        if ctx.message.edited_at:
            await ctx.send('Pong! :ping_pong:\n\n:stopwatch: **{}ms**\n:heartbeat: **{}ms**'.format(round((datetime.utcnow().timestamp() - ctx.message.edited_at.timestamp())*1000), round(self.bot.latency*1000)))
        else:
            await ctx.send('Pong! :ping_pong:\n\n:stopwatch: **{}ms**\n:heartbeat: **{}ms**'.format(round((datetime.utcnow().timestamp() - ctx.message.created_at.timestamp())*1000), round(self.bot.latency*1000)))
        
    @commands.command(pass_context=True)
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
            if user != self.bot.user:
                if user == ctx.author:
                    if reaction.message.channel == ctx.channel:
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
        
    @commands.command(pass_context=True)
    async def ascend(self, ctx, *, text):
        """Make text look cool"""
        if "@everyone" in text.lower():
            await ctx.send("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await ctx.send("@Here. Ha get pranked :middle_finger:")
            return
        await ctx.send(text.replace("", " ")[:2000])
         
    @commands.command(pass_context=True)
    async def backwards(self, ctx, *, text: str):
        """Make text go backwards"""
        text = text[::-1]
        if "@everyone" in text.lower():
            await ctx.send("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await ctx.send("@Here. Ha get pranked :middle_finger:")
            return
        await ctx.send(text[:2000])
        
    @commands.command()
    async def randcaps(self, ctx, *, text: str):
        """Make your text look angry"""
        if "@everyone" in text.lower():
            await ctx.send("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await ctx.send("@Here. Ha get pranked :middle_finger:")
            return
        msg = ""
        for letter in text:
            number = randint(0, 1)
            if number == 0:
                letter = letter.upper()
            else:
                letter = letter.lower()
            msg += letter
        await ctx.send(msg[:2000])
            
    @commands.command(aliases=["altcaps"])
    async def alternatecaps(self, ctx, *, text):
        """Make your text look neatly angry"""
        if "@everyone" in text.lower():
            await ctx.send("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await ctx.send("@Here. Ha get pranked :middle_finger:")
            return
        number = 0
        msg = ""
        for letter in text:
            if number == 0:
                letter = letter.upper()
                number = 1
            else:
                letter = letter.lower()
                number = 0
            msg += letter
        await ctx.send(msg[:2000])
        
    @commands.command()
    async def donate(self, ctx):
        """Get my donation link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&scope=bot)\n[Support Server](https://discord.gg/f2K7FxX)\n[PayPal](https://paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/SheaBots)", colour=0xfff90d)
        s.set_author(name="Donate!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command()
    async def invite(self, ctx):
        """Get my invite link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&scope=bot)\n[Support Server](https://discord.gg/f2K7FxX)\n[PayPal](https://paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/SheaBots)", colour=0xfff90d)
        s.set_author(name="Invite!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def info(self, ctx): 
        """Info about me"""
        ping = round(self.bot.latency*1000)
        users = str(len(set(self.bot.get_all_members())))
        servers = len(self.bot.guilds)
        channel = ctx.message.channel
        shea = discord.utils.get(self.bot.get_all_members(), id=402557516728369153)
        legacy = discord.utils.get(self.bot.get_all_members(), id=153286414212005888)
        joakim = discord.utils.get(self.bot.get_all_members(), id=190551803669118976)
        description = ("Sx4 is a bot which intends to make your discord experience easier yet fun, it has multiple different purposes"
        ", which includes Moderation, utility and economy. Sx4 began as a red bot to help teach it's owner more about coding, it has now evolved in to"
        " a self coded bot with the help of some bot developers and intends to go further.")
        s=discord.Embed(description=description, colour=0xfff90d)
        s.set_author(name="Info!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Stats", value="Ping: {}ms\nServers: {}\nUsers: {}".format(ping, servers, users))
        s.add_field(name="Credits", value="[Nexus](https://discord.gg/t2umQq3)\n[Python](https://www.python.org/downloads/release/python-352/)\n[discord.py](https://pypi.python.org/pypi/discord.py/)")
        s.add_field(name="Sx4", value="Developers: {}, {}, {}\nInvite: [Click Here](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&scope=bot)\nSupport: [Click Here](https://discord.gg/p5cWHjS)\nDonate: [PayPal](https://paypal.me/SheaCartwright), [Patreon](https://www.patreon.com/SheaBots)".format(shea, legacy, joakim))
        await ctx.send(embed=s)

    @commands.command(aliases=["shards"])
    async def shardinfo(self, ctx):
        "Look at Sx4s' shards"
        i = 0
        s=discord.Embed(colour=0xffff00)
        s.set_author(name="Shard Info!", icon_url=self.bot.user.avatar_url)
        s.set_footer(text="> indicates what shard your server is in", icon_url=ctx.author.avatar_url)
        for x in range(self.bot.shard_count):
            if i == ctx.guild.shard_id:
                guildshard = ">"
            else:
                guildshard = None
            s.add_field(name="{} Shard {}".format(guildshard, i + 1), value="{} servers\n{} users\n{}ms".format(len([x for x in self.bot.guilds if x.shard_id == i]), len([x for x in list(set(self.bot.get_all_members())) if x.guild.shard_id == i]), round(self.bot.latencies[i][1]*1000)))
            i += 1
        await ctx.send(embed=s)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def dm(self, ctx, user_id, *, text):
        """Dm a user using me"""
        author = ctx.message.author 
        server = ctx.guild
        channel = ctx.message.channel
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await ctx.send("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await ctx.send("The ID specified does not exist :no_entry:")
            return
        s=discord.Embed(title="You received a Message :mailbox_with_mail:", colour=0xfff90d)
        s.add_field(name="Message", value=text, inline=False)
        s.add_field(name="Author", value=author)
        s.set_thumbnail(url=author.avatar_url)
        try:
            await user.send(embed=s)
        except:
            await ctx.send("I am unable to send a message to that user :no_entry:")
            return
        await ctx.send("I have sent a message to **{}** <:done:403285928233402378>".format(user))
        
        
    @commands.command(pass_context=True, aliases=["shared"])
    async def sharedservers(self, ctx, *, user: discord.Member=None):
        """Find out what mutual servers i'm in with another user or yourself"""
        if not user:
            user = ctx.message.author
        shared = "\n".join([x.name for x in self.bot.guilds if user in x.members])
        s=discord.Embed(description=shared, colour=user.colour)
        s.set_author(name="Shared servers with {}".format(user), icon_url=user.avatar_url)
        await ctx.send(embed=s)
    
    @commands.command(pass_context=True)
    async def servers(self, ctx):
        """View all the servers i'm in"""
        page = 1
        msg = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True)][0:20])
        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
        message = await ctx.send(embed=s)
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user != self.bot.user:
                if user == ctx.author:
                    if reaction.message.channel == ctx.channel:
                        if reaction.emoji == "▶" or reaction.emoji == "◀":
                            return True
        page2 = True
        while page2:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=reactioncheck)
                if reaction.emoji == "▶":
                    if page != math.ceil(len(list(set(self.bot.guilds))) / 20):
                        page += 1
                        msg = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
                    else:
                        page = 1
                        msg = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
                if reaction.emoji == "◀":
                    if page != 1:
                        page -= 1
                        msg = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
                    else:
                        page = math.ceil(len(list(set(self.bot.guilds)))/ 20)
                        msg = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.guilds, key=lambda x: len(x.members), reverse=True)][page*20-20:page*20])
                        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                        s.set_author(name="Servers ({})".format(len(self.bot.guilds)), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.guilds))) / 20)))
                        await message.edit(embed=s)
            except asyncio.TimeoutError:
                await message.remove_reaction("◀", ctx.me)
                await message.remove_reaction("▶", ctx.me)
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
        
    @commands.command(pass_context=True)
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
    async def inrole(self, ctx, role: discord.Role, page: int=None):
        """Check who's in a specific role"""
        server = ctx.guild
        if not page:
            page = 1
        number = len([x for x in server.members if role in x.roles])
        if page - 1 > number / 20:
            await ctx.send("Invalid Page :no_entry:")
            return
        if page < 1:
            await ctx.send("Invalid Page :no_entry:")
            return
        users = "\n".join([str(x) for x in role.members])
        s=discord.Embed(description=users, colour=0xfff90d)
        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True, aliases=["mc", "mcount"])
    async def membercount(self, ctx):
        """Get all the numbers about a server"""
        server = ctx.guild
        members = set(server.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        online = filter(lambda m: m.status is discord.Status.online, members)
        online = set(online)
        idle = filter(lambda m: m.status is discord.Status.idle, members)
        idle = set(idle)
        dnd = filter(lambda m: m.status is discord.Status.do_not_disturb, members)
        dnd = set(dnd)
        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)
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
    async def roleinfo(self, ctx, *, role: discord.Role):
        """Find out stuff about a role"""
        server = ctx.guild
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
        s=discord.Embed(colour=role.colour)
        s.set_author(name="{} Role Info".format(role.name), icon_url=ctx.guild.icon_url)
        s.add_field(name="Role ID", value=role.id)
        s.add_field(name="Role Colour", value=role.colour)
        s.add_field(name="Role Position", value="{} (Bottom to Top)\n{} (Top to Bottom)".format(role.position, (len(server.roles) - (role.position)) + 1))
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
            await ctx.send("There's no one with the discriminator of **{}** or it's not a valid discriminator :no_entry:".format(discriminator))
            return
        s=discord.Embed(title="{} users in the Discriminator #{}".format(number, discriminator), description=msg, colour=0xfff90d)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
        await ctx.send(embed=s)
            
    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Look at your own or someone elses avatar"""
        author = ctx.message.author
        if not user:
            user = author
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s Avatar".format(user.name), icon_url=user.avatar_url, url=user.avatar_url.replace("webp", "png"))
        s.set_image(url=user.avatar_url.replace("webp", "png"))
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True, no_pm=True, aliases=["savatar"])
    async def serveravatar(self, ctx):
        """Look at the current server avatar"""
        server = ctx.guild
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        s=discord.Embed(colour=discord.Colour(value=colour))
        s.set_author(name="{}'s Icon".format(server.name), icon_url=server.icon_url, url=server.icon_url.replace("webp", "png"))
        s.set_image(url=server.icon_url.replace("webp", "png"))
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def say(self, ctx, *, text):
        """Say something with the bot"""
        if "@everyone" in text.lower():
            await ctx.send("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await ctx.send("@Here. Ha get pranked :middle_finger:")
            return
        await ctx.send(text[:2000])
        
    @commands.command(pass_context=True, aliases=["embed"])
    async def esay(self, ctx, *, text):
        """Say something with the bot in a embed 0w0"""
        author = ctx.message.author
        s=discord.Embed(description=text[:2000], colour=author.colour)
        s.set_author(name=author.name, icon_url=author.avatar_url)
        await ctx.send(embed=s)
        
    @commands.group(pass_context=True)
    async def trigger(self, ctx): 
        """Make the bot say something after a certain word is said"""
        server = ctx.guild 
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "case" not in self.d[str(server.id)]:
            self.d[str(server.id)]["case"] = True
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[str(server.id)]:
            self.d[str(server.id)]["toggle"] = True
            dataIO.save_json(self.file, self.d)
        
        
    @trigger.command(pass_context=True)
    @checks.admin_or_permissions(manage_guild=True)
    async def toggle(self, ctx):
        """Toggle triggers on or off"""
        server = ctx.guild 
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[str(server.id)]:
            self.d[str(server.id)]["toggle"] = True
            dataIO.save_json(self.file, self.d)
        if self.d[str(server.id)]["toggle"] == True:
            self.d[str(server.id)]["toggle"] = False
            dataIO.save_json(self.file, self.d)
            await ctx.send("Triggers are now disabled on this server.")
            return
        if self.d[str(server.id)]["toggle"] == False:
            self.d[str(server.id)]["toggle"] = True
            dataIO.save_json(self.file, self.d)
            await ctx.send("Triggers are now enabled on this server.")
            return
            
    @trigger.command(pass_context=True)
    async def case(self, ctx):
        """Toggles your triggers between case sensitive and not"""
        server = ctx.guild 
        if "case" not in self.d[str(server.id)]:
            self.d[str(server.id)]["case"] = True
            dataIO.save_json(self.file, self.d)
        if self.d[str(server.id)]["case"] == True:
            self.d[str(server.id)]["case"] = False
            dataIO.save_json(self.file, self.d)
            await ctx.send("Triggers are no longer case sensitive.")
            return
        if self.d[str(server.id)]["case"] == False:
            self.d[str(server.id)]["case"] = True
            dataIO.save_json(self.file, self.d)
            await ctx.send("Triggers are now case sensitive.")
            return
            
    @trigger.command(pass_context=True)
    async def list(self, ctx, page: int=None): 
        """List all your triggers"""
        msg = ""
        server = ctx.guild
        if not page: 
            page = 1
        if page < 1:
            await ctx.send("Invalid Page :no_entry:")
            return
        if page - 1 > len(self.d[str(server.id)]["trigger"]) / 5:
            await ctx.send("Invalid Page :no_entry:")
            return
        data = list(self.d[str(server.id)]["trigger"])[(page * 5) - 5:page * 5]
        for trigger in data:
            msg += "Trigger: {}\nResponse: {}\n\n".format(trigger, self.d[str(server.id)]["trigger"][trigger]["response"])
        s=discord.Embed(description=msg, colour=0xfff90d)
        s.set_author(name="Server Triggers", icon_url=server.icon_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(self.d[str(server.id)]["trigger"]) / 5)))
        await ctx.send(embed=s)
    

    @trigger.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def add(self, ctx, trigger, *, response):
        """Add a trigger to the server"""
        server = ctx.guild
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "trigger" not in self.d[str(server.id)]:
            self.d[str(server.id)]["trigger"] = {}
            dataIO.save_json(self.file, self.d)
        if trigger == response:
            await ctx.send("You can't have a trigger and a response with the same content :no_entry:")
            return
        for trigger2 in self.d[str(server.id)]["trigger"]:
            if trigger2.lower() == trigger.lower():
                await ctx.send("There is already a trigger with that name :no_entry:")
                return
        if trigger not in self.d[str(server.id)]["trigger"]:
            self.d[str(server.id)]["trigger"][trigger] = {}
            dataIO.save_json(self.file, self.d)
        if "response" not in self.d[str(server.id)]["trigger"][trigger]:
            self.d[str(server.id)]["trigger"][trigger]["response"] = {}
            dataIO.save_json(self.file, self.d)
        self.d[str(server.id)]["trigger"][trigger]["response"] = response
        dataIO.save_json(self.file, self.d)
        await ctx.send("The trigger **{}** has been created <:done:403285928233402378>".format(trigger))
        
    @trigger.command(pass_context=True)  
    @checks.admin_or_permissions(manage_messages=True)
    async def remove(self, ctx, *, trigger):
        """Remove a trigger to the server"""
        server = ctx.guild
        try:
            del self.d[str(server.id)]["trigger"][trigger]
            dataIO.save_json(self.file, self.d)
        except:
            await ctx.send("Invalid trigger name :no_entry:")
            return
        await ctx.send("The trigger **{}** has been removed <:done:403285928233402378>".format(trigger))
        
    async def on_message(self, message):
        server = message.guild
        if str(server.id) not in self._stats:
            self._stats[str(server.id)] = {}
        if "messages" not in self._stats[str(server.id)]:
            self._stats[str(server.id)]["messages"] = 0
        self._stats[str(server.id)]["messages"] += 1
        dataIO.save_json(self._stats_file, self._stats)
        if message.author.id == self.bot.user.id:
            return
        if self.d[str(server.id)]["toggle"] == False:
            return 
        if self.d[str(server.id)]["case"] == True:
            if message.content in self.d[str(server.id)]["trigger"]:
                await message.channel.send(self.d[str(server.id)]["trigger"][message.content]["response"])
        else:
            for trigger in self.d[str(server.id)]["trigger"]:
                if message.content.lower() == trigger.lower():
                    await message.channel.send(self.d[str(server.id)]["trigger"][trigger]["response"])
        
    @commands.command(pass_context=True)
    async def rps(self, ctx, your_choice):
        """Play rock paper scissors with the bot"""
        author = ctx.message.author
        if your_choice == "rock" or your_choice == "scissors" or your_choice == "paper" or your_choice == "r" or your_choice == "s" or your_choice == "p":
            if your_choice == "rock" or your_choice == "r":
                your_choice = 1
            if your_choice == "paper" or your_choice == "p":
                your_choice = 2
            if your_choice == "scissors" or your_choice == "s":
                your_choice = 3            
        else:
            await ctx.send("You have to choose rock, paper or scissors :no_entry:")
            return
        bot_choice = randint(1, 3)
        if bot_choice == your_choice:
            end = "Draw, let's go again!"
        if bot_choice == 1 and your_choice == 2:
            end = "You win! :trophy:"
        if bot_choice == 1 and your_choice == 3:
            end = "You lose, better luck next time."
        if bot_choice == 2 and your_choice == 1:
            end = "You lose, better luck next time."
        if bot_choice == 2 and your_choice == 3:
            end = "You win! :trophy:"
        if bot_choice == 3 and your_choice == 1:
            end = "You win! :trophy:"
        if bot_choice == 3 and your_choice == 2:
            end = "You lose, better luck next time."
        if bot_choice == 1:
            bot_choice = "**Rock :moyai:**"
        if bot_choice == 2:
            bot_choice = "**Paper :page_facing_up:**"
        if bot_choice == 3:
            bot_choice = "**Scissors :scissors:**"
        if your_choice == 1:
            your_choice = "**Rock :moyai:**"
        if your_choice == 2:
            your_choice = "**Paper :page_facing_up:**"
        if your_choice == 3:
            your_choice = "**Scissors :scissors:**"
        await ctx.send("{}: {}\nSx4: {}\n\n{}".format(author.name, your_choice, bot_choice, end))
        if end == "You lose, better luck next time.":
            self.settings[str(author.id)]["rps_losses"] = self.settings[str(author.id)]["rps_losses"] + 1
        if end == "Draw, let's go again!":
            self.settings[str(author.id)]["rps_draws"] = self.settings[str(author.id)]["rps_draws"] + 1
        if end == "You win! :trophy:":
            self.settings[str(author.id)]["rps_wins"] = self.settings[str(author.id)]["rps_wins"] + 1
        dataIO.save_json(self.JSON, self.settings)
         
    @commands.command(pass_context=True, aliases=["rpss"])
    async def rpsstats(self, ctx, *, user: discord.Member=None): 
        """Check your rps win/loss record"""    
        author = ctx.message.author
        if not user:
            user = author
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s RPS Stats".format(user.name), icon_url=user.avatar_url)
        s.add_field(name="Wins", value=self.settings[str(author.id)]["rps_wins"])
        s.add_field(name="Draws", value=self.settings[str(author.id)]["rps_draws"])
        s.add_field(name="Losses", value=self.settings[str(author.id)]["rps_losses"])
        await ctx.send(embed=s)
            
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
    async def channelid(self, ctx):
        """Get a channels id"""
        channel = ctx.message.channel
        await ctx.send("<#{}> ID: `{}`".format(channel.id, channel.id))
    
        
    @commands.command(pass_context=True, aliases=["uinfo"])
    async def userinfo(self, ctx, *, user_arg: str=None):
        """Get some info on a user in the server"""
        author = ctx.message.author
        server = ctx.guild
        if not user_arg:
            user = author
        else:
            if "<" in user_arg and "@" in user_arg:
                user = user_arg.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
                user = discord.utils.get(ctx.guild.members, id=int(user))
            elif "#" in user_arg:
                number = len([x for x in user_arg if "#" not in x])
                usernum = number - 4
                user = discord.utils.get(ctx.guild.members, name=user_arg[:usernum], discriminator=user_arg[usernum + 1:len(user_arg)])
                if not user:
                    description = ""
                    status = None
                    user = discord.utils.get(self.bot.get_all_members(), name=user_arg[:usernum], discriminator=user_arg[usernum + 1:len(user_arg)])
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
                        description="{} {}".format(user.activity.type.name.title(), user.activity.name)
                    elif user.activity.url:
                        description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
                    if not user:
                        user = await self.bot.get_user_info(int(user_arg))
                    if user.bot:
                        bot = "Yes"
                    else:
                        bot = "No"
                    joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
                    s=discord.Embed(description=description, timestamp=datetime.utcnow())
                    s.set_author(name=user, icon_url=user.avatar_url)
                    s.set_thumbnail(url=user.avatar_url)
                    s.add_field(name="User ID", value=user.id)
                    s.add_field(name="Joined Discord", value=joined_discord)
                    if status:
                        s.add_field(name="Status", value=status)
                    s.add_field(name="Bot", value=bot)
                    await ctx.send(embed=s)
                    return
            else:
                try:
                    user = discord.utils.get(ctx.guild.members, id=int(user_arg))
                    if not user:
                        user = discord.utils.get(self.bot.get_all_members(), id=int(user_arg))
                        description = ""
                        status = None
                        if user:
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
                                description="{} {}".format(user.activity.type.name.title(), user.activity.name)
                            elif user.activity.url:
                                description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
                        if not user:
                            user = await self.bot.get_user_info(int(user_arg))
                        if user.bot:
                            bot = "Yes"
                        else:
                            bot = "No"
                        joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
                        s=discord.Embed(description=description, timestamp=datetime.utcnow())
                        s.set_author(name=user, icon_url=user.avatar_url)
                        s.set_thumbnail(url=user.avatar_url)
                        s.add_field(name="User ID", value=user.id)
                        s.add_field(name="Joined Discord", value=joined_discord)
                        if status:
                            s.add_field(name="Status", value=status)
                        s.add_field(name="Bot", value=bot)
                        await ctx.send(embed=s)
                        return
                except:
                    user = discord.utils.get(ctx.guild.members, name=user_arg)
                    if not user:
                        try:
                            description = ""
                            status = None
                            user = discord.utils.get(self.bot.get_all_members(), name=user_arg)
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
                                description="{} {}".format(user.activity.type.name.title(), user.activity.name)
                            elif user.activity.url:
                                description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
                            if user.bot:
                                bot = "Yes"
                            else:
                                bot = "No"
                            joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
                            s=discord.Embed(description=description, timestamp=datetime.utcnow())
                            s.set_author(name=user, icon_url=user.avatar_url)
                            s.set_thumbnail(url=user.avatar_url)
                            s.add_field(name="User ID", value=user.id)
                            s.add_field(name="Joined Discord", value=joined_discord)
                            if status:
                                s.add_field(name="Status", value=status)
                            s.add_field(name="Bot", value=bot)
                            await ctx.send(embed=s)
                            return
                        except: 
                            pass
            if not user:
                await ctx.send("I could not find that user :no_entry:")
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
        input = sorted(ctx.guild.members, key=lambda x: x.joined_at).index(user) + 1
        if not user.activity:
            pass
        elif isinstance(user.activity, discord.Spotify):
            m, s = divmod(user.activity.duration.total_seconds(), 60)
            duration = "%d:%02d" % (m, s)
            description = "Listening to {} by {} `[{}]`".format(user.activity.title, user.activity.artists[0], duration)
        elif user.activity:
            description="{} {}".format(user.activity.type.name.title(), user.activity.name)
        elif user.activity.url:
            description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
        roles=[x.mention for x in user.roles if x.name != "@everyone"][:20]
        roles = sorted(roles, key=[x.mention for x in server.role_hierarchy if x.name != "@everyone"].index)
        s=discord.Embed(description=description, colour=user.colour, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=user.name, icon_url=user.avatar_url)
        s.set_thumbnail(url=user.avatar_url)
        s.add_field(name="Joined Discord", value=joined_discord)
        s.add_field(name="Joined {}".format(server.name), value=joined_server)
        s.add_field(name="Name", value="{}".format(user.name))
        s.add_field(name="Nickname", value="{}".format(user.nick))
        s.add_field(name="Discriminator", value="#{}".format(user.discriminator))
        s.add_field(name="Status", value="{}".format(status))
        s.add_field(name="User's Colour", value="{}".format(user.colour))
        s.add_field(name="User's ID", value="{}".format(user.id))
        s.set_footer(text="Join Position: {} | Requested by {}".format(await self.prefixfy(input), author))
        s.add_field(name="Highest Role", value=user.top_role)
        s.add_field(name="Number of Roles", value=len(user.roles)) 
        if not roles:
            s.add_field(name="Roles", value="None", inline=False) 
        else:
            if len(user.roles) - 1 > 20:
                s.add_field(name="Roles", value="{}... and {} more roles".format(", ".join(roles), (len(user.roles) - 21)), inline=False) 
            else:
                s.add_field(name="Roles", value=", ".join(roles), inline=False) 
        await ctx.send(embed=s)

    @commands.command(pass_context=True, no_pm=True, aliases=["sinfo"])
    async def serverinfo(self, ctx):
        """Get some info on the current server"""
        server = ctx.guild
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
        s=discord.Embed(description="{} was created on {}".format(server.name, server_created), colour=discord.Colour(value=colour), timestamp=__import__('datetime').datetime.utcnow())
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
        s.add_field(name="Roles", value=len(server.roles))
        s.add_field(name="Owner", value="{}".format(server.owner))
        s.add_field(name="Server ID", value=server.id)
        s.set_footer(text="Requested by {}".format(author))
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def serverstats(self, ctx):
        server = ctx.guild
        if str(server.id) not in self._stats:
            self._stats[str(server.id)] = {}
            dataIO.save_json(self._stats_file, self._stats)
        if "messages" not in self._stats[str(server.id)]:
            self._stats[str(server.id)]["messages"] = 0
            dataIO.save_json(self._stats_file, self._stats)
        if "members" not in self._stats[str(server.id)]:
            self._stats[str(server.id)]["members"] = 0
            dataIO.save_json(self._stats_file, self._stats)
        s=discord.Embed()
        s.set_author(name=server.name + " Stats", icon_url=server.icon_url)
        s.add_field(name="Users Joined Today", value=self._stats[str(server.id)]["members"])
        s.add_field(name="Messages Sent Today", value=self._stats[str(server.id)]["messages"])
        await ctx.send(embed=s)
        
    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """View the bots live stats"""
        if "servers" not in self._stats:
            self._stats["servers"] = 0
            dataIO.save_json(self._stats_file, self._stats)
        if "commands" not in self._stats:
            self._stats["commands"] = 0
            dataIO.save_json(self._stats_file, self._stats)
        m, s = divmod(ctx.message.created_at.timestamp() - self.bot.uptime, 60)
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
            uptime = "%d {} %d {}".format(minutes, seconds) % (m, s)
        elif d == 0 and h == 0 and m == 0:
            uptime = "%d {}".format(seconds) % (s)
        elif d == 0:
            uptime = "%d {} %d {} %d {}".format(hours, minutes, seconds) % (h, m, s)
        else:
            uptime = "%d {} %d {} %d {} %d {}".format(days, hours, minutes, seconds) % (d, h, m, s)
        members = list(set(self.bot.get_all_members()))
        online = len(set(filter(lambda m: not m.status == discord.Status.offline, members)))
        offline = len(set(filter(lambda m: m.status == discord.Status.offline, members)))
        process = psutil.Process(os.getpid())
        s=discord.Embed(description="Bot ID: {}".format(self.bot.user.id))
        s.set_author(name=self.bot.user.name + " Stats", icon_url=self.bot.user.avatar_url)
        s.set_thumbnail(url=self.bot.user.avatar_url)
        s.set_footer(text="Uptime: {} | Python 3.5.3".format(uptime))
        s.add_field(name="Developer", value=str(discord.utils.get(self.bot.get_all_members(), id=402557516728369153)))
        s.add_field(name="Library", value="Discord.py {}".format(discord.__version__))
        s.add_field(name="Memory Usage", value=str(round(process.memory_info().rss/1000000)) + " MB")
        s.add_field(name="CPU Usage", value=str(psutil.cpu_percent()) + "%")
        s.add_field(name="Text Channels", value=len([x for x in self.bot.get_all_channels() if isinstance(x, discord.TextChannel)]))
        s.add_field(name="Voice Channels", value=len([x for x in self.bot.get_all_channels() if isinstance(x, discord.VoiceChannel)]))
        s.add_field(name="Servers Joined Today", value=self._stats["servers"])
        s.add_field(name="Commands Used Today", value=self._stats["commands"])
        s.add_field(name="Servers", value=len(self.bot.guilds))
        s.add_field(name="Users ({} total)".format(len(members)), value="{} Online\n{} Offline".format(online, offline))
        await ctx.send(embed=s)
        
    async def prefixfy(self, input):
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
        
    async def on_guild_join(self, guild):
        self._stats["servers"] += 1
        dataIO.save_json(self._stats_file, self._stats) 
        
    async def on_guild_remove(self, guild):
        self._stats["servers"] -= 1
        dataIO.save_json(self._stats_file, self._stats) 
        
    async def on_member_join(self, member):
        server = member.guild
        if str(server.id) not in self._stats:
            self._stats[str(server.id)] = {}
        if "members" not in self._stats[str(server.id)]:
            self._stats[str(server.id)]["members"] = 0
        self._stats[str(server.id)]["members"] += 1
        dataIO.save_json(self._stats_file, self._stats) 
        
    async def on_member_remove(self, member):
        server = member.guild
        if str(server.id) not in self._stats:
            self._stats[str(server.id)] = {}
        if "members" not in self._stats[str(server.id)]:
            self._stats[str(server.id)]["members"] = 0
        self._stats[str(server.id)]["members"] -= 1
        dataIO.save_json(self._stats_file, self._stats) 
        
    async def on_command(self, ctx):
        self._stats["commands"] += 1
        dataIO.save_json(self._stats_file, self._stats) 

    async def checktime(self):
        while not self.bot.is_closed():
            if datetime.utcnow().strftime("%H") == "23":
                s=discord.Embed(colour=0xffff00, timestamp=datetime.now())
                s.set_author(name="Bot Logs", icon_url=self.bot.user.avatar_url)
                if 86400/self._stats["commands"] >= 1:
                    s.add_field(name="Average Command Usage", value="1 every {}s".format(round(86400/self._stats["commands"])))
                else:
                    s.add_field(name="Average Command Usage", value="{} every second".format(round(self._stats["commands"]/86400)))
                s.add_field(name="Servers", value=len(self.bot.guilds), inline=False)
                s.add_field(name="Users (No Bots)", value=len(set(filter(lambda m: not m.bot, list(set(self.bot.get_all_members()))))))
                await self.bot.get_channel(445982429522690051).send(embed=s)
                self._stats["servers"] = 0
                self._stats["commands"] = 0
                for serverid in [x for x in self._stats if x != "commands" and x != "servers"]:
                    self._stats[serverid]["members"] = 0
                    self._stats[serverid]["messages"] = 0
                dataIO.save_json(self._stats_file, self._stats) 
            await asyncio.sleep(3540)
        
def check_folders():
    if not os.path.exists("data/general"):
        print("Creating data/general folder...")
        os.makedirs("data/general")


def check_files():
    f = 'data/general/rps.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default rps.json...')
    f = 'data/general/triggers.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default triggers.json...')
    f = 'data/general/stats.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default stats.json...')
        
def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(general(bot))