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
import html
from urllib.request import Request, urlopen
import json
import urllib
from iso639 import languages
import re
import os
from random import choice
from threading import Timer
from utils import Token 
import requests
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
import rethinkdb as r
from enum import Enum
import asyncio
from difflib import get_close_matches

rps_settings = {"rps_wins": 0, "rps_draws": 0, "rps_losses": 0}

class fun:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["tran", "tr"])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def translate(self, ctx, language, *, text):
        """Translate one language to another"""
        if len(language) == 2:
            try:
                language = languages.get(part1=language).name
            except:
                pass
        elif len(language) == 3:
            try:
                language = languages.get(part3=language).name
            except:
                pass
        elif len(language) > 3:
            language = language
        request = requests.get("http://localhost:8080/translate/{}?{}".format(language, urllib.parse.urlencode({"q": text.lower()})))
        try:
            await ctx.send(request.json()["message"].replace("'", "`") + " :no_entry:")
        except:
            s=discord.Embed(colour=0x4285f4)
            s.set_author(name="Google Translate", icon_url="https://upload.wikimedia.org/wikipedia/commons/d/db/Google_Translate_Icon.png")
            s.add_field(name="Input Text ({})".format(languages.get(part1=request.json()["from"]["language"]["iso"]).name), value=html.unescape(request.json()["from"]["text"]["value"]) if request.json()["from"]["text"]["value"] else text, inline=False)
            s.add_field(name="Output Text ({})".format(language.title()), value=request.json()["text"])
            await ctx.send(embed=s)

    @commands.command(aliases=["vg"])
    @commands.cooldown(1, 6, commands.BucketType.default)
    async def vainglory(self, ctx, ign: str, region: str="na"):
        """Get stats of a player make sure to include their ign and region they play on"""
        regions = ["cn", "na", "eu", "sa", "ea", "sg"]
        if region not in regions:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Invalid region, valid regions are {} :no_entry:".format(", ".join(regions)))
        request = requests.get("https://api.dc01.gamelockerapp.com/shards/{}/players?{}".format(region, urllib.parse.urlencode({"filter[playerNames]": ign})), headers={"Authorization": Token.vainglory(), "Accept": "application/vnd.api+json"}).json()
        try:
            if request["errors"]:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send("I could not find that user :no_entry:")  
        except:
            pass
        userdata = request["data"][0]["attributes"]
        id = request["data"][0]["id"]
        s=discord.Embed(colour=ctx.author.colour)
        s.set_author(name=ign, icon_url=ctx.author.avatar_url)
        s.set_footer(text="ID: {} | Guild Tag: {}".format(id, userdata["stats"]["guildTag"] if  userdata["stats"]["guildTag"] else "None"))
        s.add_field(name="Games Played", value="{}\nWins: {:,}".format("\n".join(["{}: {:,}".format(x[0].replace("_", " ").title(), x[1]) for x in userdata["stats"]["gamesPlayed"].items()]), userdata["stats"]["wins"]))
        s.add_field(name="ELO Earned", value="\n".join(sorted(["{}: {:,}".format(x.split("_", 2)[2].replace("_", " ").title(), userdata["stats"][x]) for x in userdata["stats"] if "season" in x], key=lambda x: x.split(" ")[1])))
        s.add_field(name="Levels", value="Level {:,}\n{:,} XP\nKarma Level: {:,}".format(userdata["stats"]["level"], userdata["stats"]["xp"], userdata["stats"]["karmaLevel"]))
        s.add_field(name="Streaks", value="Win Streak: {:,}\nLoss Streak: {:,}".format(userdata["stats"]["winStreak"], userdata["stats"]["lossStreak"]))
        s.add_field(name="Ranked Points", value="{}".format("\n".join(["{}: {:,}".format(x[0].replace("_", " ").title(), round(x[1])) for x in userdata["stats"]["rankPoints"].items()])))
        s.add_field(name="Skill Tier", value="{:,}".format(userdata["stats"]["skillTier"]))
        await ctx.send(embed=s)

    @commands.command(aliases=["calc"])
    async def calculator(self, ctx, *, equation):
        """Calculate simple equations"""
        answer = os.popen('./calc {}'.format(equation.replace(" ", "").replace("(", "l").replace(")", "r"))).read()
        if answer == "":
            return await ctx.send("Invalid equation :no_entry:")
        await ctx.send(answer)

    @commands.command()
    async def quote(self, ctx):
        """Gives you a random quote"""
        request = requests.post("https://andruxnet-random-famous-quotes.p.mashape.com/", headers={"X-Mashape-Key": Token.mashape(),"Content-Type": "application/x-www-form-urlencoded","Accept": "application/json"}).json()[0]
        await ctx.send(embed=discord.Embed(description=request["quote"], title=request["author"], colour=ctx.author.colour))

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, search: str):
        """Search for a youtube video by query"""
        url = "https://www.googleapis.com/youtube/v3/search?key=" + Token.youtube() + "&part=snippet&safeSearch=none&{}".format(urllib.parse.urlencode({"q": search}))
        request = requests.get(url)
        try:
            await ctx.send("https://www.youtube.com/watch?v={}".format(request.json()["items"][0]["id"]["videoId"]))
        except:
            await ctx.send("No results :no_entry:")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def shorten(self, ctx, *, url):
        """Shorten a url"""
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
        """Gives you a random meme"""
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
        if ctx.channel.is_nsfw():
            url = "https://www.googleapis.com/customsearch/v1?key=" + Token.google() + "&cx=014023765838117903829:mm334tqd3kg&safe=off&{}".format(urllib.parse.urlencode({"q": search}))
        else:
            url = "https://www.googleapis.com/customsearch/v1?key=" + Token.google() + "&cx=014023765838117903829:mm334tqd3kg&safe=active&{}".format(urllib.parse.urlencode({"q": search}))
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
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
        if ctx.channel.is_nsfw():
            url = "https://www.googleapis.com/customsearch/v1?key=" + Token.google() + "&cx=014023765838117903829:klo2euskkae&safe=off&searchType=image&{}".format(urllib.parse.urlencode({"q": search}))
        else:
            url = "https://www.googleapis.com/customsearch/v1?key=" + Token.google() + "&cx=014023765838117903829:klo2euskkae&safe=active&searchType=image&{}".format(urllib.parse.urlencode({"q": search}))
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
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
        if not ctx.channel.is_nsfw():
            return await ctx.send("You can not use this command in non-nsfw channels :no_entry:")
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
        """Say something with the bot in a embed"""
        author = ctx.message.author
        s=discord.Embed(description=text[:2000], colour=author.colour)
        s.set_author(name=author.name, icon_url=author.avatar_url)
        await ctx.send(embed=s)

    @commands.command()
    async def clapify(self, ctx, *, text):
        """Claps your text"""
        if "@everyone" in text.lower():
            await ctx.send("@Everyone. Ha get pranked :middle_finger:")
            return
        if "@here" in text.lower():
            await ctx.send("@Here. Ha get pranked :middle_finger:")
            return
        await ctx.send(text.replace(" ", ":clap:")[:2000])

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
        authordata = r.table("rps").get(str(author.id))
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
            authordata.update({"rps_losses": r.row["rps_losses"] + 1}).run(durability="soft")
        if end == "Draw, let's go again!":
            authordata.update({"rps_draws": r.row["rps_draws"] + 1}).run(durability="soft")
        if end == "You win! :trophy:":
            authordata.update({"rps_wins": r.row["rps_wins"] + 1}).run(durability="soft")
         
    @commands.command(pass_context=True, aliases=["rpss"])
    async def rpsstats(self, ctx, *, user: discord.Member=None): 
        """Check your rps win/loss record"""    
        author = ctx.message.author
        if not user:
            user = author
        userdata = r.table("rps").get(str(user.id))
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s RPS Stats".format(user.name), icon_url=user.avatar_url)
        if not userdata:
            s.add_field(name="Wins", value="0")
            s.add_field(name="Draws", value="0")
            s.add_field(name="Losses", value="0")
        else:
            s.add_field(name="Wins", value=userdata["rps_wins"].run(durability="soft"))
            s.add_field(name="Draws", value=userdata["rps_draws"].run(durability="soft"))
            s.add_field(name="Losses", value=userdata["rps_losses"].run(durability="soft"))
        await ctx.send(embed=s)
        
def setup(bot):
    bot.add_cog(fun(bot))