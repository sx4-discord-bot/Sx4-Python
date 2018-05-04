import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import random
import math
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
from datetime import datetime
import asyncio
from difflib import get_close_matches

rps_settings = {"rps_wins": 0, "rps_draws": 0, "rps_losses": 0}
giveaway = {"users": None}

class General:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = 'data/general/rps.json'
        self.settings = dataIO.load_json(self.JSON)
        self.settings = defaultdict(lambda: rps_settings, self.settings)
        self.file = "data/general/triggers.json"
        self.d = dataIO.load_json(self.file)
        self._shop_file = 'data/economy/shop.json'
        self._shop = dataIO.load_json(self._shop_file)
        
    @commands.command(pass_context=True)
    async def google(self, ctx, *, search): 
        """returns the top 3 results from google of your search query"""
        url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyAelnun4v79DNvzvQalyPMsPY5XuaMTlIQ&{}&cx=014023765838117903829:mm334tqd3kg".format(urllib.parse.urlencode({"q": search}))
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        try:
            results = "\n\n".join(["**[{}]({})**\n{}".format(x["title"], x["link"], x["snippet"]) for x in data["items"]][:3])
        except:
            await self.bot.say("No Results :no_entry:")
            return
        s=discord.Embed(description=results)
        s.set_author(name="Google", icon_url="https://images-ext-1.discordapp.net/external/UsMM0mPPHEKn6WMst8WWG9qMCX_A14JL6Izzr47ucOk/http/i.imgur.com/G46fm8J.png", url="https://www.google.co.uk/search?{}".format(urllib.parse.urlencode({"q": search})))
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def dictionary(self, ctx, *, word): 
        """Look up the definition of any word using an actual dictionary"""
        url = "https://od-api.oxforddictionaries.com:443/api/v1/entries/en/{}".format(word)
        request = Request(url)
        request.add_header("Accept", "application/json")
        request.add_header("app_id", "e01b354a")
        request.add_header("app_key", "16589a290cbf2462ff51a4ff984ccf8f")
        try:
            data = json.loads(urlopen(request).read().decode())
        except:
            await self.bot.say("No results :no_entry:")
            return
        definition = data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"][0]
        pronounce = data["results"][0]["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
        s=discord.Embed(colour=ctx.message.author.colour)
        s.set_author(name=data["results"][0]["id"], url="https://en.oxforddictionaries.com/definition/{}".format(data["results"][0]["id"]))
        s.add_field(name="Definition", value=definition)
        s.add_field(name="Pronunciation", value=pronounce, inline=False)
        await self.bot.say(embed=s)

    @commands.command(pass_context=True)
    async def steam(self, ctx, *, profile_url: str=None):
        """To get a steam profile you need to click on the users profile and get the vanityurl which is the name after /id/{} <--- The name should be there""" 
        idurl = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=148756A557AACB36BF328E8534043BC1&{}".format(urllib.parse.urlencode({"vanityurl": profile_url.replace("https://steamcommunity.com/id/", "")}))
        idrequest = Request(idurl)
        try:
            id = json.loads(urlopen(idrequest).read().decode())["response"]["steamid"]
        except:
            await self.bot.say("No results :no_entry:")
            return
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=148756A557AACB36BF328E8534043BC1&steamids={}".format(id)
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())["response"]["players"][0]
        m, s = divmod(ctx.message.timestamp.timestamp() - data["lastlogoff"], 60)
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
            await self.bot.say(embed=s)
            return
        s.add_field(name="Real name", value=data["realname"])
        try:
            s.add_field(name="Currently Playing", value=data["gameextrainfo"])
        except:
            s.add_field(name="Currently Playing", value="Nothing")
        await self.bot.say(embed=s)
        
        
            
        
    @commands.command(pass_context=True)
    async def dblowners(self, ctx, *, user: str=None):
        """Look up the developers of a bot on discord bot list"""
        if not user:
            user = self.bot.user.id
        if "<" in user and "@" in user:
            userid = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            url = "https://discordbots.org/api/bots?search=id:{}&fields=owners,username".format(userid)
        elif "#" in user: 
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            url = "https://discordbots.org/api/bots?search=username:{}&discriminator:{}&fields=owners,username".format(user[:usernum], user[usernum + 1:len(user)])
        else:
            try:
                int(user)
                url = "https://discordbots.org/api/bots?search=id:{}&fields=owners,username".format(user)
            except:
                url = "https://discordbots.org/api/bots?search=username:{}&fields=owners,username&limit=1".format(user)
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())["results"]
        if len(data) == 0:
            await self.bot.say("I could not find that bot :no_entry:")
            return
        data = data[0]
        msg = ""
        for x in data["owners"]:
            user = await self.bot.get_user_info(x)
            msg += str(user) + ", "
        await self.bot.say("{}'s Owners: {}".format(data["username"], msg[:-2]))
        
    @commands.command(pass_context=True)
    async def dbltag(self, ctx, *, dbl_tag):
        """Shows the top 10 bots (sorted by monthly upvotes) in the tag form there you can select and view 1"""
        url = "https://discordbots.org/api/bots?search=tags:{}&limit=10&sort=monthlyPoints&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot,tags".format(urllib.parse.urlencode({"": dbl_tag}).replace("=", ""))
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        if len(data["results"]) == 0:
            await self.bot.say("That is not a valid tag :no_entry:")
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
        message = await self.bot.say(embed=s)
        response = await self.bot.wait_for_message(author=ctx.message.author, timeout=60, check=lambda m: m.content.isdigit() or m.content.lower() == "cancel" or m.content is None) 
        if response.content is None:
            try:
                await self.bot.delete_message(message)
                await self.bot.delete_message(response)
            except:
                pass
            return
        elif response.content == "cancel":
            try:
                await self.bot.delete_message(message)
                await self.bot.delete_message(response)
            except:
                pass
            return
        else:
            try:
                await self.bot.delete_message(message)
                await self.bot.delete_message(response)
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

            await self.bot.say(embed=s)
            
        
        
         
    @commands.command(pass_context=True)
    async def dbl(self, ctx, user: str=None):
        """Look up any bot on discord bot list and get statistics from it"""
        if not user:
            user = self.bot.user.id
        if "<" in user and "@" in user:
            userid = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot".format(userid)
        elif "#" in user: 
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            url = "https://discordbots.org/api/bots?search=username:{}&discriminator:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot".format(user[:usernum], user[usernum + 1:len(user)])
        else:
            try:
                int(user)
                url = "https://discordbots.org/api/bots?search=id:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot".format(user)
            except:
                url = "https://discordbots.org/api/bots?search=username:{}&fields=shortdesc,username,discriminator,server_count,points,avatar,prefix,lib,date,monthlyPoints,invite,id,certifiedBot&limit=1".format(user)
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())["results"]
        if len(data) == 0:
            await self.bot.say("I could not find that bot :no_entry:")
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

        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def botlist(self, ctx, page: int=None):
        """A list of the bots with the most servers on discord bot list"""
        if not page:
            page = 0
        else: 
            page = page - 1
        if page < 0 or page > 49:
            await self.bot.say("Invalid page :no_entry:")
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
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def catfact(self, ctx):
        """Learn cat stuff"""
        url = "https://catfact.ninja/fact"
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=data["fact"], colour=ctx.message.author.colour)
        s.set_author(name="Did you know?")
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/134/cat-face_1f431.png")
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def dogfact(self, ctx):
        """Learn dog stuff"""
        url = "https://fact.birb.pw/api/v1/dog"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=data["string"], colour=ctx.message.author.colour)
        s.set_author(name="Did you know?")
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/134/dog-face_1f436.png")
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True, aliases=["bird"])
    async def birb(self, ctx):
        """Look at a birb"""
        url = "http://random.birb.pw/tweet.json/"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=":bird:", colour=ctx.message.author.colour)
        s.set_image(url="http://random.birb.pw/img/" + data["file"])
        try:
            await self.bot.say(embed=s)
        except:
            await self.bot.say("The birb didn't make it, sorry :no_entry:")
        
    @commands.command(pass_context=True)
    async def dog(self, ctx):
        """Look at a dog"""
        url = "https://dog.ceo/api/breeds/image/random"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=":dog:", colour=ctx.message.author.colour)
        s.set_image(url=data["message"])
        try:
            await self.bot.say(embed=s)
        except:
            await self.bot.say("The dog didn't make it, sorry :no_entry:")
        
    @commands.command(pass_context=True)
    async def cat(self, ctx):
        """Look at a cat"""
        response = requests.get("http://thecatapi.com/api/images/get?format=src")
        image = response.url
        s=discord.Embed(description=":cat:", colour=ctx.message.author.colour)
        s.set_image(url=image)
        try:
            await self.bot.say(embed=s)
        except:
            await self.bot.say("The cat didn't make it, sorry :no_entry:")
        
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
            await self.bot.say("No results :no_entry:")
            return
        if len(data["list"]) < page + 1:
            await self.bot.say("That is not a valid page :no_entry:")
            return
        if len([x for x in str(data["list"][page]["definition"])]) > 976:
            definition = str(data["list"][page]["definition"])[:976] + '... [Read more]({})'.format(data["list"][page]["permalink"])
        else:
            definition = str(data["list"][page]["definition"])
        if len([x for x in str(data["list"][page]["example"])]) > 976:
            example = str(data["list"][page]["example"])[:976] + '... [Read more]({})'.format(data["list"][page]["permalink"])
        else:
            example = str(data["list"][page]["example"])
        s=discord.Embed(colour=ctx.message.author.colour)
        s.set_author(name=data["list"][page]["word"], url=data["list"][page]["permalink"])
        s.add_field(name="Definition", value=definition, inline=False)
        if example != "":
            s.add_field(name="Example", value=example)
        s.set_footer(text="{} 👍 | {} 👎 | Page {}/{}".format(data["list"][page]["thumbs_up"], data["list"][page]["thumbs_down"], page + 1, len(data["list"])))
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Am i alive? (Well if you're reading this, yes)"""
        channel = ctx.message.channel
        author = ctx.message.author
        t1 = time.perf_counter()
        msg = await self.bot.say("Pong! :ping_pong:")
        t2 = time.perf_counter()
        await self.bot.edit_message(msg, "Pong! :ping_pong: **{}ms**".format(round((t2-t1)*1000)))
        
    @commands.command(pass_context=True)
    async def report(self, ctx, *, bug_description):
        """Report a bug to my developer"""
        channel = ctx.message.channel
        author = ctx.message.author
        s=discord.Embed(description=bug_description, colour=author.colour)
        s.set_author(name=author.name, icon_url=author.avatar_url)
        s.set_thumbnail(url=author.avatar_url)
        s.set_footer(text="Report by {} ({})".format(author, author.id))
        await self.bot.send_message(self.bot.get_channel("375040822518743040"), embed=s)
        await self.bot.say("I have successfully reported your problem <:done:403285928233402378>")
        
    @commands.command(pass_context=True)
    async def bots(self, ctx): 
        """Look at all my bot friends in the server"""
        server = ctx.message.server
        bots = list(map(lambda m: m.name, filter(lambda m: m.bot, server.members)))
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        s.add_field(name="Bot List ({})".format(len(bots)), value=", ".join(bots))
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def ascend(self, ctx, *, text):
        """Make text look cool"""
        if "@everyone" in text.lower():
            await self.bot.say("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await self.bot.say("@Here. Ha get pranked :middle_finger:")
            return
        await self.bot.say(text.replace("", " "))
         
    @commands.command(pass_context=True)
    async def backwards(self, ctx, *, text: str):
        """Make text go backwards"""
        if "@everyone" in text.lower():
            await self.bot.say("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await self.bot.say("@Here. Ha get pranked :middle_finger:")
            return
        text = text[::-1]
        await self.bot.say(text)
        
    @commands.command()
    async def randcaps(self, *, text: str):
        """Make your text look angry"""
        if "@everyone" in text.lower():
            await self.bot.say("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await self.bot.say("@Here. Ha get pranked :middle_finger:")
            return
        msg = ""
        for letter in text:
            number = randint(0, 1)
            if number == 0:
                letter = letter.upper()
            else:
                letter = letter.lower()
            msg += letter
        await self.bot.say(msg)
            
    @commands.command(aliases=["altcaps"])
    async def alternatecaps(self, *, text):
        """Make your text look neatly angry"""
        if "@everyone" in text.lower():
            await self.bot.say("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await self.bot.say("@Here. Ha get pranked :middle_finger:")
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
        await self.bot.say(msg)
        
    @commands.command(pass_context=True)
    async def contact(self, ctx, *, question):
        """Contact my developer"""
        channel = ctx.message.channel
        author = ctx.message.author
        s=discord.Embed(description=question, colour=author.colour)
        s.set_author(name=author.name, icon_url=author.avatar_url)
        s.set_thumbnail(url=author.avatar_url)
        s.set_footer(text="Question by {} ({})".format(author, author.id))
        await self.bot.send_message(self.bot.get_channel("386688962326167558"), embed=s)
        await self.bot.say("I have successfully contacted my owner <:done:403285928233402378>")
        
    @commands.command(pass_context=True)
    async def topservers(self, ctx):
        """View the top servers i am in (sorted by members)"""
        servers = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.servers, key=lambda x: len(x.members), reverse=True)][:10])
        s=discord.Embed(description=servers, colour=0xfff90d)
        s.set_author(name="Top 10 Servers", icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True) 
    @checks.is_owner()
    async def answer(self, ctx, user_id: int, *, answer):
        channel = ctx.message.channel
        author = ctx.message.author
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await self.bot.say("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await self.bot.say("The ID specified does not exist :no_entry:")
            return
        message = "Answer: {}\n\nAnswered by {}".format(answer, author)
        await self.bot.send_message(self.bot.get_channel("386688962326167558"), message)
        await self.bot.send_message(user, message)
        
    @commands.command()
    async def donate(self):
        """Get my donation link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&scope=bot)\n[Support Server](https://discord.gg/f2K7FxX)\n[PayPal](https://paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/SheaBots)", colour=0xfff90d)
        s.set_author(name="Donate!", icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command()
    async def invite(self):
        """Get my invite link"""
        s=discord.Embed(description="[Invite](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&scope=bot)\n[Support Server](https://discord.gg/f2K7FxX)\n[PayPal](https://paypal.me/SheaCartwright)\n[Patreon](https://www.patreon.com/SheaBots)", colour=0xfff90d)
        s.set_author(name="Invite!", icon_url=self.bot.user.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def info(self, ctx): 
        """Info about me"""
        t1 = time.perf_counter()
        msg = await self.bot.say("Pinging...")
        t2 = time.perf_counter()
        ping = round((t2-t1)*1000)
        await self.bot.delete_message(msg)
        users = str(len(set(self.bot.get_all_members())))
        servers = len(self.bot.servers)
        channel = ctx.message.channel
        shea = discord.utils.get(self.bot.get_all_members(), id="151766611097944064")
        legacy = discord.utils.get(self.bot.get_all_members(), id="153286414212005888")
        joakim = discord.utils.get(self.bot.get_all_members(), id="190551803669118976")
        description = ("Sx4 is a bot which intends to make your discord experience easier yet fun, it has multiple different purposes"
        ", which includes Moderation, utility and music. Sx4 began as a red bot to help teach it's owner more about coding, it has now evolved in to"
        " a self coded bot with the help of some bot developers and intends to go further.")
        await self.bot.send_typing(channel)
        s=discord.Embed(description=description, colour=0xfff90d)
        s.set_author(name="Info!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Stats", value="Ping: {}ms\nServers: {}\nUsers: {}".format(ping, servers, users))
        s.add_field(name="Credits", value="[Nexus](https://discord.gg/u7J3c6C)\n[Python](https://www.python.org/downloads/release/python-352/)\n[discord.py](https://pypi.python.org/pypi/discord.py/)")
        s.add_field(name="Sx4", value="Developers: {}, {}, {}\nInvite: [Click Here](https://discordapp.com/oauth2/authorize?client_id=440996323156819968&permissions=8&scope=bot)\nSupport: [Click Here](https://discord.gg/p5cWHjS)\nDonate: [PayPal](https://paypal.me/SheaCartwright), [Patreon](https://www.patreon.com/SheaBots)".format(shea, legacy, joakim))
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def dm(self, ctx, user_id, *, text):
        """Dm a user using me"""
        author = ctx.message.author 
        server = ctx.message.server
        channel = ctx.message.channel
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await self.bot.say("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await self.bot.say("The ID specified does not exist :no_entry:")
            return
        s=discord.Embed(title="You received a Message :mailbox_with_mail:", colour=0xfff90d)
        s.add_field(name="Message", value=text, inline=False)
        s.add_field(name="Author", value=author)
        s.set_thumbnail(url=author.avatar_url)
        try:
            await self.bot.send_message(user, embed=s)
        except:
            await self.bot.say("I am unable to send a message to that user :no_entry:")
            return
        await self.bot.say("I have sent a message to **{}** <:done:403285928233402378>".format(user))
    
    @commands.command(pass_context=True)
    async def servers(self, ctx, page: int=None):
        """View all the servers i'm in"""
        if not page:
            page = 1
        if page < 1:
            await self.bot.say("Invalid Page :no_entry:")
            return
        if page - 1 > len(set(self.bot.servers)) / 20:
            await self.bot.say("Invalid Page :no_entry:")
            return
        msg = "\n".join(["`{}` - {} members".format(x.name, len(x.members)) for x in sorted(self.bot.servers, key=lambda x: len(x.members), reverse=True)][page*20-20:page*20])
        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Servers ({})".format(len(self.bot.servers)), icon_url=self.bot.user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(set(self.bot.servers))) / 20)))
        await self.bot.say(embed=s)

    @commands.command(aliases=["sc", "scount"])
    async def servercount(self):
        """My current server and user count"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        name = self.bot.user.name
        avatar = self.bot.user.avatar_url if self.bot.user.avatar else self.bot.user.default_avatar_url
        users = len(set(self.bot.get_all_members()))
        servers = (len(self.bot.servers))
        s=discord.Embed(title="", colour=discord.Colour(value=colour))
        s.add_field(name="Servers", value="{}".format(servers))
        s.add_field(name="Users", value="{}".format(users))
        s.set_author(name="{}'s servercount!".format(name), icon_url=avatar)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def permissions(self, ctx, user: discord.Member=None):
        """Check the permissions a user has"""
        author = ctx.message.author
        if not user:
            user = author
        x = "\n".join([x[0].replace("_", " ").title() for x in filter(lambda p: p[1] == True, user.server_permissions)])
        s=discord.Embed(description=x, colour=user.colour)
        s.set_author(name="{}'s permissions".format(user.name), icon_url=user.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def inrole(self, ctx, role: discord.Role, page: int=None):
        """Check who's in a specific role"""
        server = ctx.message.server
        if not page:
            page = 1
        number = len([x for x in server.members if role in x.roles])
        if page - 1 > number / 20:
            await self.bot.say("Invalid Page :no_entry:")
            return
        if page < 1:
            await self.bot.say("Invalid Page :no_entry:")
            return
        users = "\n".join([x.name + "#" + x.discriminator for x in server.members if role in x.roles][page*20-20:page*20])
        s=discord.Embed(description=users, colour=0xfff90d)
        s.set_author(name="Users in " + role.name + " ({})".format(number), icon_url=server.icon_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True, aliases=["mc", "mcount"])
    async def membercount(self, ctx):
        """Get all the numbers about a server"""
        server = ctx.message.server
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
        await self.bot.say(embed=s)
    
    @commands.command(pass_context=True, aliases=["ri", "rinfo"]) 
    async def roleinfo(self, ctx, *, role: discord.Role):
        """Find out stuff about a role"""
        server = ctx.message.server
        perms = role.permissions
        members = len([x for x in server.members if role in x.roles])
        msg = "\n".join([x[0].replace("_", " ").title() for x in filter(lambda p: p[1] == True, perms)])
        s=discord.Embed(colour=role.colour)
        s.set_author(name="{} Role Info".format(role.name), icon_url=ctx.message.server.icon_url)
        s.add_field(name="Role ID", value=role.id)
        s.add_field(name="Role Colour", value=role.colour)
        s.add_field(name="Role Position", value="{} (Bottom to Top)\n{} (Top to Bottom)".format(role.position, len(server.roles) - (role.position) + 2))
        s.add_field(name="Users in Role", value=members)
        s.add_field(name="Role Permissions", value=msg, inline=False)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def discrim(self, ctx, discriminator: str, page: int=None):
        """Check how many users have the discriminator 0001 seeing as though that's all people care about"""
        if not page:
            page = 1
        number = len([x for x in list(set(self.bot.get_all_members())) if x.discriminator == discriminator])
        if page - 1 > number / 20:
            await self.bot.say("Invalid Page :no_entry:")
            return
        if page < 1:
            await self.bot.say("Invalid Page :no_entry:")
            return
        msg = "\n".join(["{}#{}".format(x.name, x.discriminator) for x in list(set(self.bot.get_all_members())) if x.discriminator == discriminator][page*20-20:page*20])
        if number == 0: 
            await self.bot.say("There's no one with the discriminator of **{}** or it's not a valid discriminator :no_entry:".format(discriminator))
            return
        s=discord.Embed(title="{} users in the Discriminator #{}".format(number, discriminator), description=msg, colour=0xfff90d)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(number / 20)))
        await self.bot.say(embed=s)
            
    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Look at your own or someone elses avatar"""
        author = ctx.message.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if not user:
            user = author
        s=discord.Embed(description="[{}'s avatar :camera_with_flash:]({})".format(user.name, user.avatar_url), colour=user.colour)
        s.set_image(url=user.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True, no_pm=True, aliases=["savatar"])
    async def serveravatar(self, ctx):
        """Look at the current server avatar"""
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        s=discord.Embed(description="[{}]({})".format(server.name, server.icon_url), colour=discord.Colour(value=colour))
        s.set_image(url=server.icon_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def say(self, ctx, *, text):
        """Say something with the bot"""
        if "@everyone" in text.lower():
            await self.bot.say("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await self.bot.say("@Here. Ha get pranked :middle_finger:")
            return
        await self.bot.say(text)
        
    @commands.command(pass_context=True, aliases=["embed"])
    async def esay(self, ctx, *, text):
        """Say something with the bot in a embed 0w0"""
        author = ctx.message.author
        s=discord.Embed(description=text, colour=author.colour)
        s.set_author(name=author.name, icon_url=author.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.group(pass_context=True)
    async def trigger(self, ctx): 
        """Make the bot say something after a certain word is said"""
        server = ctx.message.server 
        if server.id not in self.d:
            self.d[server.id] = {}
            dataIO.save_json(self.file, self.d)
        if "case" not in self.d[server.id]:
            self.d[server.id]["case"] = True
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[server.id]:
            self.d[server.id]["toggle"] = True
            dataIO.save_json(self.file, self.d)
        
        
    @trigger.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def toggle(self, ctx):
        """Toggle triggers on or off"""
        server = ctx.message.server 
        if server.id not in self.d:
            self.d[server.id] = {}
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[server.id]:
            self.d[server.id]["toggle"] = True
            dataIO.save_json(self.file, self.d)
        if self.d[server.id]["toggle"] == True:
            self.d[server.id]["toggle"] = False
            dataIO.save_json(self.file, self.d)
            await self.bot.say("Triggers are now disabled on this server.")
            return
        if self.d[server.id]["toggle"] == False:
            self.d[server.id]["toggle"] = True
            dataIO.save_json(self.file, self.d)
            await self.bot.say("Triggers are now enabled on this server.")
            return
            
    @trigger.command(pass_context=True)
    async def case(self, ctx):
        """Toggles your triggers between case sensitive and not"""
        server = ctx.message.server 
        if "case" not in self.d[server.id]:
            self.d[server.id]["case"] = True
            dataIO.save_json(self.file, self.d)
        if self.d[server.id]["case"] == True:
            self.d[server.id]["case"] = False
            dataIO.save_json(self.file, self.d)
            await self.bot.say("Triggers are no longer case sensitive.")
            return
        if self.d[server.id]["case"] == False:
            self.d[server.id]["case"] = True
            dataIO.save_json(self.file, self.d)
            await self.bot.say("Triggers are now case sensitive.")
            return
            
    @trigger.command(pass_context=True)
    async def list(self, ctx, page: int=None): 
        """List all your triggers"""
        msg = ""
        server = ctx.message.server
        if not page: 
            page = 1
        if page < 1:
            await self.bot.say("Invalid Page :no_entry:")
            return
        if page - 1 > len(self.d[server.id]["trigger"]) / 5:
            await self.bot.say("Invalid Page :no_entry:")
            return
        data = list(self.d[server.id]["trigger"])[(page * 5) - 5:page * 5]
        for trigger in data:
            msg += "Trigger: {}\nResponse: {}\n\n".format(trigger, self.d[server.id]["trigger"][trigger]["response"])
        s=discord.Embed(description=msg, colour=0xfff90d)
        s.set_author(name="Server Triggers", icon_url=server.icon_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(self.d[server.id]["trigger"]) / 5)))
        await self.bot.say(embed=s)
    

    @trigger.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def add(self, ctx, trigger, *, response):
        """Add a trigger to the server"""
        server = ctx.message.server
        if server.id not in self.d:
            self.d[server.id] = {}
            dataIO.save_json(self.file, self.d)
        if "trigger" not in self.d[server.id]:
            self.d[server.id]["trigger"] = {}
            dataIO.save_json(self.file, self.d)
        if trigger == response:
            await self.bot.say("You can't have a trigger and a response with the same content :no_entry:")
            return
        for trigger2 in self.d[server.id]["trigger"]:
            if trigger2.lower() == trigger.lower():
                await self.bot.say("There is already a trigger with that name :no_entry:")
                return
        if trigger not in self.d[server.id]["trigger"]:
            self.d[server.id]["trigger"][trigger] = {}
            dataIO.save_json(self.file, self.d)
        if "response" not in self.d[server.id]["trigger"][trigger]:
            self.d[server.id]["trigger"][trigger]["response"] = {}
            dataIO.save_json(self.file, self.d)
        self.d[server.id]["trigger"][trigger]["response"] = response
        dataIO.save_json(self.file, self.d)
        await self.bot.say("The trigger **{}** has been created <:done:403285928233402378>".format(trigger))
        
    @trigger.command(pass_context=True)  
    @checks.admin_or_permissions(manage_messages=True)
    async def remove(self, ctx, *, trigger):
        """Remove a trigger to the server"""
        server = ctx.message.server
        try:
            del self.d[server.id]["trigger"][trigger]
            dataIO.save_json(self.file, self.d)
        except:
            await self.bot.say("Invalid trigger name :no_entry:")
            return
        await self.bot.say("The trigger **{}** has been removed <:done:403285928233402378>".format(trigger))
        
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        server = message.server
        if self.d[server.id]["toggle"] == False:
            return 
        if self.d[server.id]["case"] == True:
            if message.content in self.d[server.id]["trigger"]:
                await self.bot.send_message(message.channel, self.d[server.id]["trigger"][message.content]["response"])
        else:
            for trigger in self.d[server.id]["trigger"]:
                if message.content.lower() == trigger.lower():
                    await self.bot.send_message(message.channel, self.d[server.id]["trigger"][trigger]["response"])
        
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
            await self.bot.say("You have to choose rock, paper or scissors :no_entry:")
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
        await self.bot.say("{}: {}\nSx4: {}\n\n{}".format(author.name, your_choice, bot_choice, end))
        if end == "You lose, better luck next time.":
            self.settings[author.id]["rps_losses"] = self.settings[author.id]["rps_losses"] + 1
        if end == "Draw, let's go again!":
            self.settings[author.id]["rps_draws"] = self.settings[author.id]["rps_draws"] + 1
        if end == "You win! :trophy:":
            self.settings[author.id]["rps_wins"] = self.settings[author.id]["rps_wins"] + 1
        dataIO.save_json(self.JSON, self.settings)
         
    @commands.command(pass_context=True, aliases=["rpss"])
    async def rpsstats(self, ctx, user: discord.Member=None): 
        """Check your rps win/loss record"""	
        author = ctx.message.author
        if not user:
            user = author
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s RPS Stats".format(user.name), icon_url=user.avatar_url)
        s.add_field(name="Wins", value=self.settings[user.id]["rps_wins"])
        s.add_field(name="Draws", value=self.settings[user.id]["rps_draws"])
        s.add_field(name="Losses", value=self.settings[user.id]["rps_losses"])
        await self.bot.say(embed=s)
            
    @commands.command(pass_context=True, aliases=["uid"])
    async def userid(self, ctx, user: discord.Member=None):
        """Get someone userid"""
        author = ctx.message.author
        if not user:
            user = author
        await self.bot.say("{}'s ID: `{}`".format(user, user.id))
        
    @commands.command(pass_context=True, aliases=["rid"])
    async def roleid(self, ctx, *, role: discord.Role):
        """Get a roles id"""
        await self.bot.say("{}'s ID: `{}`".format(role.name, role.id))
    
    @commands.command(pass_context=True, aliases=["sid"])
    async def serverid(self, ctx):
        """Get the servers id"""
        server = ctx.message.server
        await self.bot.say("{}'s ID: `{}`".format(server.name, server.id))
        
    @commands.command(pass_context=True, aliases=["cid"])
    async def channelid(self, ctx):
        """Get a channels id"""
        channel = ctx.message.channel
        await self.bot.say("<#{}> ID: `{}`".format(channel.id, channel.id))
        
    @commands.command(pass_context=True, aliases=["guinfo"])
    async def globaluserinfo(self, ctx, user_id: int=None):  
        """Get some info about a user even if they're not in the server"""	
        try:
            author = ctx.message.author
            if user_id is None:
                user_id = author.id
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await self.bot.say("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await self.bot.say("The ID specified does not exist :no_entry:")
            return
        if (".gif" in user.avatar_url.lower()):
            nitro = "Yes"
        else:
            nitro = "No"
        joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=user, icon_url=user.avatar_url)
        s.set_thumbnail(url=user.avatar_url)
        s.add_field(name="User ID", value=user.id, inline=False)
        s.add_field(name="Joined Discord", value=joined_discord, inline=True)
        s.add_field(name="Nitro Account", value=nitro) 
        await self.bot.say(embed=s)
    
        
    @commands.command(pass_context=True, aliases=["uinfo"])
    async def userinfo(self, ctx, user: discord.Member=None):
        """Get some info on a user in the server"""
        author = ctx.message.author
        server = ctx.message.server
        if not user:
            user = author
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
        if user.game:
            description="Playing {}".format(user.game)
            if user.game.url:
                description="Streaming [{}]({})".format(user.game, user.game.url)
        roles=[x.name for x in user.roles if x.name != "@everyone"][:20]
        roles = sorted(roles, key=[x.name for x in server.role_hierarchy if x.name != "@everyone"].index)
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
        s.set_footer(text="Requested by {}".format(author))
        s.add_field(name="Highest Role", value=user.top_role)
        s.add_field(name="Number of Roles", value=len(user.roles)) 
        if not roles:
            s.add_field(name="Roles", value="None", inline=False) 
        else:
            s.add_field(name="Roles", value=", ".join(roles), inline=False) 
        await self.bot.say(embed=s)

    @commands.command(pass_context=True, no_pm=True, aliases=["sinfo"])
    async def serverinfo(self, ctx):
        """Get some info on the current server"""
        server = ctx.message.server
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
        text_channels = len([x for x in server.channels if x.type == discord.ChannelType.text])
        voice_channels = len([x for x in server.channels if x.type == discord.ChannelType.voice])
        categorys = (len(server.channels) - voice_channels - text_channels)
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
        if server.default_channel:
            s.add_field(name="Default Channel", value="<#{}>".format(server.default_channel.id))
        else:
            s.add_field(name="Default Channel", value="No Default Channel")
        s.add_field(name="Roles", value=len(server.roles))
        s.add_field(name="Owner", value="{}".format(server.owner))
        s.add_field(name="Server ID", value=server.id)
        s.set_footer(text="Requested by {}".format(author))
        await self.bot.say(embed=s)
        
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
        
def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(General(bot))