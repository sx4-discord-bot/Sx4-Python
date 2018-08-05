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
from utils import Token
from utils import checks
from urllib.request import Request, urlopen
import json
import urllib
import re
import os
from random import choice
from threading import Timer
from utils import Token 
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

class fun:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = 'data/general/rps.json'
        self.settings = dataIO.load_json(self.JSON)
        self.settings = defaultdict(lambda: rps_settings, self.settings)

    @commands.command()
    async def quote(self, ctx):
        """Gives you a random quote"""
        request = requests.post("https://andruxnet-random-famous-quotes.p.mashape.com/", headers={"X-Mashape-Key": Token.mashape(),"Content-Type": "application/x-www-form-urlencoded","Accept": "application/json"}).json()[0]
        await ctx.send(embed=discord.Embed(description=request["quote"], title=request["author"], colour=ctx.author.colour))

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, search: str):
        url = "https://www.googleapis.com/youtube/v3/search?key=" + Token.youtube() + "&part=snippet&safeSearch=none&{}".format(urllib.parse.urlencode({"q": search}))
        request = requests.get(url)
        try:
            await ctx.send("https://www.youtube.com/watch?v={}".format(request.json()["items"][0]["id"]["videoId"]))
        except:
            await ctx.send("No results :no_entry:")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def shorten(self, ctx, *, url):
        url1 = "https://api.rebrandly.com/v1/links"
        request = requests.post(url1, data=json.dumps({"destination": url}), headers={"Content-Type": "application/json", "apikey": Token.rebrandly()})
        try:
            request.json()["message"]
            await ctx.send("Invalid Url :no_entry:")
        except:
            await ctx.send("<https://" + request.json()["shortUrl"] + ">")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.default)
    async def meme(self, ctx):
        number = randint(0, 100)
        url = "https://www.reddit.com/r/dankmemes.json?sort=new&limit=100"
        url2 = "https://www.reddit.com/r/memeeconomy.json?sort=new&limit=100"
        url = random.choice([url, url2])
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())["data"]["children"][number]["data"]
        s=discord.Embed()
        s.set_author(name=data["title"], url="https://www.reddit.com" + data["permalink"])
        s.set_image(url=data["url"])
        s.set_footer(text="Score: " + str(data["score"]))
        await ctx.send(embed=s)

    @commands.command(pass_context=True)
    async def discordmeme(self, ctx):
        """Have a discord meme"""
        url = "https://api.weeb.sh/images/random?type=discord_memes"
        request = Request(url)
        request.add_header("Authorization",  "Wolke " + Token.wolke())
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(); s.set_image(url=data["url"]); s.set_footer(text="Powered by weeb.sh"); await ctx.send(embed=s)

    @commands.command(pass_context=True)
    async def google(self, ctx, *, search): 
        """returns the top 5 results from google of your search query"""
        url = "https://www.googleapis.com/customsearch/v1?key=" + Token.google() + "&cx=014023765838117903829:mm334tqd3kg&{}".format(urllib.parse.urlencode({"q": search}))
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
        url = "https://www.googleapis.com/customsearch/v1?key=" + Token.google() + "&cx=014023765838117903829:klo2euskkae&searchType=image&{}".format(urllib.parse.urlencode({"q": search}))
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
        request.add_header("app_id", "e01b354a")
        request.add_header("app_key", Token.dictionary())
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
        idurl = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + Token.steam() + "&{}".format(urllib.parse.urlencode({"vanityurl": profile_url.replace("https://steamcommunity.com/id/", "")}))
        idrequest = Request(idurl)
        try:
            id = json.loads(urlopen(idrequest).read().decode())["response"]["steamid"]
        except:
            id = profile_url.replace("https://steamcommunity.com/id/", "")
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + Token.steam() + "&steamids={}".format(id)
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
        if len(data["list"]) == 0:
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

def check_folders():
    if not os.path.exists("data/general"):
        print("Creating data/general folder...")
        os.makedirs("data/general")


def check_files():
    f = 'data/general/rps.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default rps.json...')
        
def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(fun(bot))