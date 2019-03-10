import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import html
import aiohttp
import random
import math
from utils import arghelp
import functools
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
import traceback
import re
import os
from random import choice
from utils import arg, data
from threading import Timer
from utils import Token 
import requests
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
import rethinkdb as r
from enum import Enum
from utils import paged
import asyncio
from difflib import get_close_matches

rps_settings = {"rps_wins": 0, "rps_draws": 0, "rps_losses": 0}

class fun:
    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
        self.steam_cache = bot.loop.create_task(self.update_games())

    def __unload(self):
        self.steam_cache.cancel()

    @commands.command()
    async def tts(self, ctx, *, text: str):
        """Returns an mp3 file using text to speech of text of your choice"""
        if len(text) > 200:
            return await ctx.send("Text to speech can be no longer than 200 characters :no_entry:")
        await ctx.send(file=discord.File(requests.get("https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&{}".format(urllib.parse.urlencode({"q": text}))).content, "{}.mp3".format(text)))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, country_code: str, *, city: str):
        """Shows weather info on a city"""
        data = requests.get("https://api.openweathermap.org/data/2.5/weather?{},{}&APPID=af50a6ae4e6abac046b1a95af816669b&units=metric".format(urllib.parse.urlencode({"q": city.lower()}), country_code.lower())).json()
        if "message" in data:
            return await ctx.send(data["message"].capitalize() + " :no_entry:")
        direction = min({360: "North", 0: "North", 45: "North East", 90: "East", 135: "South East", 180: "South", 225: "South West", 270: "West", 315:  "North West"}.items(), key=lambda x: abs(x[0]-data["wind"]["deg"]))[1]
        s=discord.Embed()
        s.set_author(name=data["name"] + " (" + data["sys"]["country"] + ")")
        s.add_field(name="Temperature", value="Minimum: {}°C\nCurrent: {}°C\nMaximum: {}°C".format(round(data["main"]["temp_min"]), round(data["main"]["temp"]), round(data["main"]["temp_max"])))
        s.add_field(name="Humidity", value="{}%".format(data["main"]["humidity"]))
        s.add_field(name="Wind", value="Speed: {}m/s\nDirection: {}° ({})".format(data["wind"]["speed"], data["wind"]["deg"], direction))
        s.set_thumbnail(url="http://openweathermap.org/img/w/{}.png".format(data["weather"][0]["icon"]))
        await ctx.send(embed=s)

    @commands.command(aliases=["randomgame"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def randomsteamgame(self, ctx):
        """Fetches a random steam game and shows you info about it"""
        games = data.read_json("data/fun/steamgames.json")["applist"]["apps"]
        game_id = random.choice(games)["appid"]
        game = requests.get("https://store.steampowered.com/api/appdetails?appids=" + str(game_id)).json()[str(game_id)]
        if not game["success"]:
            return await ctx.send("Something went wrong on steams end, but there is no data for the random game that was selected :no_entry:")
        else:
            game = game["data"]
        s=discord.Embed(description=game["short_description"])
        s.set_image(url=game["header_image"])
        s.set_author(name=game["name"], icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/2000px-Steam_icon_logo.svg.png", url="https://store.steampowered.com/app/" + str(game_id))
        s.add_field(name="Price", value=game["price_overview"]["final_formatted"] if "price_overview" in game else ("Free" if game["is_free"] else "Unknown"))
        s.add_field(name="Release Date", value=game["release_date"]["date"] + (" (Coming Soon)" if game["release_date"]["coming_soon"] else ""))
        s.add_field(name="Required Age", value=game["required_age"] if game["required_age"] != 0 else "No Age Restriction")
        s.add_field(name="Recommendations", value="{:,}".format(game["recommendations"]["total"]) if "recommendations" in game else "Unknown/None")
        s.add_field(name="Supported Languages", value=game["supported_languages"].replace("<br>", "\n").replace("</br>", "\n").replace("<strong>", "").replace("</strong>", "").replace("*", "\*"))
        s.add_field(name="Genres", value="\n".join(map(lambda x: x["description"], game["genres"])) if "genres" in game else "None")
        s.set_footer(text="Developed by " + (", ".join(game["developers"]) if "developers" in game else "Unknown"))
        await ctx.send(embed=s)

    @commands.command()
    async def minesweeper(self, ctx, bomb_amount: int=10, grid: str="10x10"):
        """Play minesweeper with discords spoiler feature 10 bombs in a 10x10 grid"""
        bombs = []
        if not re.match("[0-9]+x[0-9]+", grid):
            return await ctx.send("Invalid grid format make sure to format it like so <x axis>x<y axis> so like 10x10 :no_entry:")
        grid_x = int(grid.split("x")[0])
        grid_y = int(grid.split("x")[1])
        if grid_x < 2 or grid_y < 2:
            return await ctx.send("The grid has to be at least 2x2 in size :no_entry:")
        if bomb_amount > grid_x * grid_y - 1:
            return await ctx.send("**{}** is the max amount of bombs you can have :no_entry:".format(grid_x * grid_y - 1))
        elif bomb_amount < 1:
            return await ctx.send("**1** is the minimum amount of bombs you can have :no_entry:")
        for x in range(bomb_amount):
            tuple = (random.choice(range(grid_x)), random.choice(range(grid_y)), "x")
            while tuple in bombs:
                tuple = (random.choice(range(grid_x)), random.choice(range(grid_y)), "x")
            bombs.append(tuple)
        number = 0
        numbers = []
        for x in range(grid_x):
            for y in range(grid_y):
                if (x, y, "x") in bombs:
                    pass
                else:
                    for xar in range(3):
                        for yar in range(3):
                            if (x + (xar - 1), y + (yar - 1), "x") in bombs:
                                number += 1
                    numbers.append((x, y, number))
                    number = 0
        all = bombs + numbers
        all = sorted(sorted(all, key=lambda x: x[1]), key=lambda x: x[0])
        i = 0
        num = {"0": ":zero:", "1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:", "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:", "9": ":nine:", "x": ":bomb:"}
        msg = ""
        for x in all:
            if i == grid_x:
                msg += "\n"
                i = 0
            msg += "||{}||".format(num[str(x[2])])
            i += 1
        if len(msg) > 2000:
            return await ctx.send("The grid size is too big :no_entry:")
        await ctx.send(msg)

    @commands.command(aliases=["gamesearch"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def steamsearch(self, ctx, *, game_name: str=None):
        """Looks up a game on steam and returns info on it aswell as the link to the game page"""
        games = data.read_json("data/fun/steamgames.json")["applist"]["apps"]
        if not game_name:
            game = sorted(games, key=lambda x: x["name"])
        else:
            game = sorted(list(filter(lambda x: x["name"].lower() == game_name.lower() or game_name.lower() in x["name"].lower(), games)), key=lambda x: x["name"])
        if not game:
            return await ctx.send("No games matched your query (Make sure the game is on Steam) :no_entry:")
        else:
            event = await paged.page(ctx, game, selectable=True, function=lambda x: x["name"], auto_select=True)
            if event:
                game_id = event["object"]["appid"]
            else:
                return
        game = requests.get("https://store.steampowered.com/api/appdetails?appids=" + str(game_id)).json()[str(game_id)]
        if not game["success"]:
            return await ctx.send("Something went wrong on steams end, but there is no data for that game :no_entry:")
        else:
            game = game["data"]
        s=discord.Embed(description=game["short_description"])
        s.set_image(url=game["header_image"])
        s.set_author(name=game["name"], icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/2000px-Steam_icon_logo.svg.png", url="https://store.steampowered.com/app/" + str(game_id))
        s.add_field(name="Price", value=game["price_overview"]["final_formatted"] if "price_overview" in game else ("Free" if game["is_free"] else "Unknown"))
        s.add_field(name="Release Date", value=game["release_date"]["date"] + (" (Coming Soon)" if game["release_date"]["coming_soon"] else ""))
        s.add_field(name="Required Age", value=game["required_age"] if game["required_age"] != 0 else "No Age Restriction")
        s.add_field(name="Recommendations", value="{:,}".format(game["recommendations"]["total"]) if "recommendations" in game else "Unknown/None")
        s.add_field(name="Supported Languages", value=game["supported_languages"].replace("<br>", "\n").replace("</br>", "\n").replace("<strong>", "").replace("</strong>", "").replace("*", "\*"))
        s.add_field(name="Genres", value="\n".join(map(lambda x: x["description"], game["genres"])) if "genres" in game else "None")
        s.set_footer(text="Developed by " + (", ".join(game["developers"]) if "developers" in game else "Unknown"))
        await ctx.send(embed=s)

    @commands.command(aliases=["perksearch", "searchperk"])
    async def dbdperksearch(self, ctx, *, perk: str=None):
        """Look up a perk on dead by daylight"""
        killerperks = data.read_json("dbd_data/KillerPerks.json")
        survivorperks = data.read_json("dbd_data/SurvivorPerks.json")
        array = killerperks + survivorperks 
        if perk:
            additional = None
            if perk.startswith("--"):
                additional = perk[2:]
                perk = None
                event = None
            elif " --" in perk:
                additional = perk.split(" --")[1]
                perk = perk.split(" --")[0]
            if additional:
                if additional.lower() == "killer":
                    array = killerperks
                elif additional.lower() == "survivor":
                    array = survivorperks
            if perk:
                event = list(filter(lambda x: perk.lower() == x["name"].lower(), array))
        else:
            event = None
        if not event:
            if perk:
                array = list(filter(lambda x: perk.lower() in x["name"].lower(), array))
            if not array:
                return await ctx.send("I could not find that perk :no_entry:")
            event = await paged.page(ctx, array, selectable=True, per_page=15, function=lambda x: x["name"], auto_select=True)
            if event:
                event = event["object"]
            else:
                return
            event2 = await paged.page(ctx, event["rarity"], function=lambda x: x.title().replace("_", " "), selectable=True)
            if event2:
                image = "dbd_perks/iconPerks_" + event["image"] + ".png"
                description = event["description"].replace("%b", "**").replace("%/b", "**").replace("%i", "*").replace("%/i", "*") % tuple(event["tiers"][event2["index"]])
                s=discord.Embed(description=description, title=event["name"])
                s.add_field(name="Rarity", value=event["rarity"][event2["index"]].title().replace("_", " "))
                s.add_field(name="Teachable", value="Yes ({})".format(event["owner"].title().replace("_", " ")) if event["owner"] != "ALL" else "No")
                s.set_thumbnail(url="attachment://image.png")
                await ctx.send(file=discord.File(image, "image.png"), embed=s)
        else:
            event = event[0]
            event2 = await paged.page(ctx, event["rarity"], function=lambda x: x.title().replace("_", " "), selectable=True)
            if event2:
                image = "dbd_perks/iconPerks_" + event["image"] + ".png"
                description = event["description"].replace("%b", "**").replace("%/b", "**").replace("%i", "*").replace("%/i", "*") % tuple(event["tiers"][event2["index"]])
                s=discord.Embed(description=description, title=event["name"])
                s.add_field(name="Rarity", value=event["rarity"][event2["index"]].title().replace("_", " "))
                s.add_field(name="Teachable", value="Yes ({})".format(event["owner"].title().replace("_", " ")) if event["owner"] != "ALL" else "No")
                s.set_thumbnail(url="attachment://image.png")
                await ctx.send(file=discord.File(image, "image.png"), embed=s)

    @commands.command(aliases=["survivorset"])
    async def dbdsurvivorset(self, ctx, survivor: str=None):
        """Generates a random survivor set on dead by daylight"""
        def get_survivor(survivor: str):
            try:
                survivor = list(filter(lambda x: survivor == x["index"].lower(), data.read_json("dbd_data/Survivors.json")))[0]
            except IndexError:
                try:
                   survivor = list(filter(lambda x: survivor in x["index"].lower(), data.read_json("dbd_data/Survivors.json")))[0] 
                except IndexError:
                   return None
            return survivor
        if survivor:
            survivor = get_survivor(survivor)
            if not survivor:
                return await ctx.send("I could not find that survivor :no_entry:")
        else:
            survivor = random.choice(data.read_json("dbd_data/Survivors.json"))
        perks = data.read_json("dbd_data/SurvivorPerks.json")
        items = data.read_json("dbd_data/Items.json")
        addons = data.read_json("dbd_data/SurvivorAddons.json") 
        offerings = data.read_json("dbd_data/SurvivorOfferings.json") + data.read_json("dbd_data/SharedOfferings.json")
        perks = random.sample(perks, 4)
        item = random.choice(items)
        addons = random.sample(list(filter(lambda x: x["type"] == item["type"], addons)), 2)
        offering = random.choice(offerings)
        s=discord.Embed(title=survivor["name"])
        s.add_field(name="Perks", value="\n".join(map(lambda x: "{} - {} perk on the {} page".format(x["name"], self.suffix(self.index_dbd(x["name"])[1]), self.suffix(self.index_dbd(x["name"])[0])), perks)))
        s.add_field(name="Item", value=item["name"])
        s.add_field(name="Addons", value="\n".join(map(lambda x: x["name"], addons)))
        s.add_field(name="Offering", value=offering["name"])
        await ctx.send(embed=s)

    @commands.command(aliases=["killerset"])
    async def dbdkillerset(self, ctx, *, killer: str=None):
        """Generates a random killer set on dead by daylight"""
        def get_killer(killer: str):
            try:
                killer = list(filter(lambda x: killer == x["index"].lower(), data.read_json("dbd_data/Killers.json")))[0]
            except IndexError:
                try:
                   killer = list(filter(lambda x: killer in x["index"].lower(), data.read_json("dbd_data/Killers.json")))[0] 
                except IndexError:
                   return None
            return killer
        if killer:
            killer = get_killer(killer)
            if not killer:
                return await ctx.send("I could not find that killer :no_entry:")
        else:
            killer = random.choice(data.read_json("dbd_data/Killers.json"))
        perks = data.read_json("dbd_data/KillerPerks.json")
        addons = data.read_json("dbd_data/KillerAddons.json")
        offerings = data.read_json("dbd_data/KillerOfferings.json") + data.read_json("dbd_data/SharedOfferings.json")
        perks = random.sample(perks, 4)
        addons = random.sample(list(filter(lambda x: x["owner"] == killer["index"], addons)), 2)
        offering = random.choice(offerings)
        s=discord.Embed(title=killer["name"])
        s.add_field(name="Perks", value="\n".join(map(lambda x: "{} - {} perk on the {} page".format(x["name"], self.suffix(self.index_dbd(x["name"], "killer")[1]), self.suffix(self.index_dbd(x["name"], "killer")[0])), perks)))
        s.add_field(name="Addons", value="\n".join(map(lambda x: x["name"], addons)))
        s.add_field(name="Offering", value=offering["name"])
        await ctx.send(embed=s)

    @commands.command()
    async def teams(self, ctx, amount_of_teams: int, *players):
        """Randomizes a specified amount of teams for you"""
        players = list(players)
        if amount_of_teams <= 0:
            return await ctx.send("Amount of teams has to be more than 0 :no_entry:")
        for player in players:
            user = arg.get_server_member(ctx, player)
            role = arg.get_role(ctx, player)
            if user:
                players.remove(player)
                players.append(user.name)
            elif role:
                players.remove(player)
                for mems in map(lambda x: x.name, role.members):
                    players.append(mems)
        players = list(set(players))
        if len(players) < amount_of_teams:
            return await ctx.send("You gave more teams than players :no_entry:")
        teams = []
        for i in range(amount_of_teams):
            teams.append([])
        i = 0
        while len(players) > 0:
            player = random.choice(players)
            players.remove(player)
            teams[i].append(player)
            if i == amount_of_teams - 1:
                i = 0
            else:
                i += 1
        await ctx.send("\n".join(["**Team {}**\n\n{}\n".format(i, ", ".join(x)) for i, x in enumerate(teams, start=1)]))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def convert(self, ctx, amount: float, currency_from: str, currency_to: str):
        request = requests.get("https://free.currencyconverterapi.com/api/v6/convert?q={}_{}&apiKey=4a355639d6e2e3ab32c6".format(currency_from.upper(), currency_to.upper())).json()
        if request["query"]["count"] == 0:
            return await ctx.send("Invalid currency :no_entry:")
        else:
            result = request["results"]["{}_{}".format(currency_from.upper(), currency_to.upper())]
            currency = format(result["val"] * amount, ".2f")
            amount = format(amount, ".2f")
            await ctx.send("**{}** {} \➡ **{}** {}".format(amount, currency_from.upper(), currency, currency_to.upper()))

    @commands.command(aliases=["gtn"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def guessthenumber(self, ctx, user: str, bet: int=None):
        """Who ever gets closest to the number gets the others money if you bet money"""
        user = arg.get_server_member(ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        if user == ctx.author:
            return await ctx.send("You can't play this game by yourself :no_entry:")
        if bet:
            if bet > 0:
                authordata = r.table("bank").get(str(ctx.author.id))
                userdata = r.table("bank").get(str(user.id))
                if not authordata.run(self.db):
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("**{}** doesn't have enough money :no_entry:".format(ctx.author))
                if not userdata.run(self.db):
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("**{}** doesn't have enough money :no_entry:".format(user))
                if userdata["balance"].run(self.db) < bet:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("**{}** doesn't have enough money :no_entry:".format(user))
                if authordata["balance"].run(self.db) < bet:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("**{}** doesn't have enough money :no_entry:".format(ctx.author))
            else: 
                ctx.command.reset_cooldown(ctx)
                return await ctx.send("The bet must be more than $0 :no_entry:")
        await ctx.send("{}, type `accept` if you would like to play guess the number{}".format(user.mention, " for **${:,}**".format(bet) if bet else "."))
        def user_confirmation_check(m):
            return m.channel == ctx.channel and m.author == user
        def author_check(m):
            if m.author == ctx.author and isinstance(m.channel, discord.DMChannel) and m.content.isdigit():
                if int(m.content) > 0 and int(m.content) < 51:
                    return True
            return False
        def user_check(m):
            if m.author == user and isinstance(m.channel, discord.DMChannel) and m.content.isdigit():
                if int(m.content) > 0 and int(m.content) < 51:
                    return True
            return False
        try:
            user_confirmation = await self.bot.wait_for("message", check=user_confirmation_check, timeout=60)
            if user_confirmation.content.lower() == "accept":
                await ctx.send("I will send a message to **{}** first, once they've responded I will send a message to **{}**".format(user.name, ctx.author.name))
                try:
                    await user.send("I'm thinking of a number between 1-50, try and guess the number the person who gets the closest out of you and your opponent will get the others money. (Respond below)")
                except:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("{}, Make sure i am able to message you :no_entry:".format(user.mention))
                try:
                    user_answer = await self.bot.wait_for("message", check=user_check, timeout=20)
                except asyncio.TimeoutError:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("{}'s response timed out :stopwatch:".format(user.name))
                if user_answer:
                    await user.send("Your answer has been locked in, waiting for an answer from {}. Answers will be sent in {}".format(ctx.author, ctx.channel.mention))
                try:
                    await ctx.author.send("I'm thinking of a number between 1-50, try and guess the number the person who gets the closest out of you and your opponent will get the others money. (Respond below)")
                except:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("{}, Make sure i am able to message you :no_entry:".format(ctx.author.mention))
                try:
                    author_answer = await self.bot.wait_for("message", check=author_check, timeout=20)
                except asyncio.TimeoutError:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("{}'s response timed out :stopwatch:".format(ctx.author.name))
                if author_answer:
                    await ctx.author.send("Your answer has been locked in, answers have been sent in {}".format(ctx.channel.mention))
                if author_answer and user_answer:
                    number = randint(1, 50)
                    user_number = int(user_answer.content)
                    author_number = int(author_answer.content)
                    user_difference = abs(number - user_number)
                    author_difference = abs(number - author_number)
                    msg = "My number was **{}**\n{}'s number was **{}**\n{}'s number was **{}**\n\n".format(number, user.name, user_number, ctx.author.name, author_number)
                    if user_difference == author_difference:
                        msg += "You both guessed the same number, It was a draw!"
                        winner = None
                    elif user_difference < author_difference:
                        msg += "{} won! They were the closest to {}".format(user.name, number)
                        winner = user
                    else:
                        msg += "{} won! They were the closest to {}".format(ctx.author.name, number)
                        winner = ctx.author
                    if bet and winner:
                        if winner == ctx.author:
                            if userdata["balance"].run(self.db) < bet:
                                msg += "\nBet was cancelled due to **{}** not having enough money.".format(user.name)
                            else:
                                msg += "\nThey have been rewarded **${:,}**".format(bet*2)
                                authordata.update({"balance": r.row["balance"] + bet}).run(self.db, durability="soft")
                                userdata.update({"balance": r.row["balance"] - bet}).run(self.db, durability="soft")
                        elif winner == user:
                            if authordata["balance"].run(self.db) < bet:
                                msg += "\nBet was cancelled due to **{}** not having enough money.".format(ctx.author.name)
                            else:
                                msg += "\nThey have been rewarded **${:,}**".format(bet*2)
                                userdata.update({"balance": r.row["balance"] + bet}).run(self.db, durability="soft")
                                authordata.update({"balance": r.row["balance"] - bet}).run(self.db, durability="soft")
                    await ctx.send(msg)
            else:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send("User declined :no_entry:")
        except asyncio.TimeoutError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Response timed out :stopwatch:")


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
        request = requests.get("http://localhost:8080/translate/{}?{}".format(language, urllib.parse.urlencode({"q": text.lower()})), timeout=3)
        try:
            await ctx.send(request.json()["message"].replace("'", "`") + " :no_entry:")
        except:
            input_text = request.json()["from"]["language"]["iso"]
            if "-" in input_text:
                input_text = input_text.split("-")[0]
            if input_text == "iw":
                input_text = "Hebrew"
            elif len(input_text) == 2:
                input_text = languages.get(part1=input_text).name
            elif len(input_text) == 3:
                input_text = languages.get(part3=input_text).name
            s=discord.Embed(colour=0x4285f4)
            s.set_author(name="Google Translate", icon_url="https://upload.wikimedia.org/wikipedia/commons/d/db/Google_Translate_Icon.png")
            s.add_field(name="Input Text ({})".format(input_text), value=html.unescape(request.json()["from"]["text"]["value"]) if request.json()["from"]["text"]["value"] else text, inline=False)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quote(self, ctx):
        """Gives you a random quote"""
        request = requests.post("https://andruxnet-random-famous-quotes.p.mashape.com/", headers={"X-Mashape-Key": Token.mashape(),"Content-Type": "application/x-www-form-urlencoded","Accept": "application/json"}).json()[0]
        await ctx.send(embed=discord.Embed(description=request["quote"], title=request["author"], colour=ctx.author.colour))

    @commands.command(aliases=["yt"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def youtube(self, ctx, *, search: str):
        """Search for a youtube video by query"""
        url = "https://www.googleapis.com/youtube/v3/search?key=" + Token.youtube() + "&part=snippet&safeSearch=none&{}".format(urllib.parse.urlencode({"q": search}))
        request = requests.get(url).json()
        if not request["items"]:
            return await ctx.send("No results :no_entry:")
        youtube_id = request["items"][0]["id"]
        if youtube_id["kind"] == "youtube#channel":
            await ctx.send("https://www.youtube.com/channel/{}".format(youtube_id["channelId"]))
        elif youtube_id["kind"] == "youtube#video":
            await ctx.send("https://www.youtube.com/watch?v={}".format(youtube_id["videoId"]))
        elif youtube_id["kind"] == "youtube#playlist":
            await ctx.send("https://www.youtube.com/playlist?list={}".format(youtube_id["playlistId"]))

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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as f:
                if f.status == 200:
                    data = (await f.json())["data"]["children"][number]["data"]
                    s=discord.Embed()
                    s.set_author(name=data["title"], url="https://www.reddit.com" + data["permalink"])
                    s.set_image(url=data["url"])
                    s.set_footer(text="Score: " + str(data["score"]))
                    await ctx.send(embed=s)
                else:
                    await ctx.send(await f.text())

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def discordmeme(self, ctx):
        """Have a discord meme"""
        url = "https://api.weeb.sh/images/random?type=discord_memes"
        request = Request(url)
        request.add_header("Authorization",  "Wolke " + Token.wolke())
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(); s.set_image(url=data["url"]); s.set_footer(text="Powered by weeb.sh"); await ctx.send(embed=s)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
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
    @commands.cooldown(1, 3, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        s=discord.Embed(description="Steam Profile <:steam:530830699821793281>")
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
    @commands.cooldown(1, 3, commands.BucketType.user)
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
    async def say(self, ctx, *, text: commands.clean_content):
        """Say something with the bot"""
        await ctx.send(text[:2000])

    @commands.command()
    async def spoilerfy(self, ctx, *, text: commands.clean_content):
        """Make any text annoying to unvail"""
        await ctx.send("".join(["||" + x + "||" if x != " " else x for x in text])[:2000])
        
    @commands.command(name="embed", aliases=["esay"])
    async def _embed(self, ctx, *, text):
        """Say something with the bot in a embed"""
        author = ctx.message.author
        s=discord.Embed(description=text[:2000], colour=author.colour)
        s.set_author(name=author.name, icon_url=author.avatar_url)
        await ctx.send(embed=s)

    @commands.command()
    async def devembed(self, ctx, *, embed_json):
        """An advanced way to create an embed with full customizability as long as you know how to use json\nExample format: {'title': 'text here', 'description': 'text here', 'colour': 'hex code here', 
        'author': {'name': 'text here', 'icon_url': 'image url here', 'url': 'url here'}, 'footer': {'text': 'text here', 'icon_url': 'image url here'}, fields: [{'name': 'title here', 'value': 'description here', 'inline': true},
        {'name': 'title here', 'value': 'description here', 'inline': false}], 'image': 'image url here', 'thumbnail': 'url here'}"""
        hex_re = re.compile("(?:#|)((?:[a-fA-F]|[0-9]){6})")
        try:
            embed_json = json.loads(embed_json)
        except:
            return await ctx.send("The argument does not follow JSON format make sure all keys are in quotations and you are not missing any syntax :no_entry:")
        s=discord.Embed()
        if "title" in embed_json:
            if len(embed_json["title"]) > 256:
                return await ctx.send("Embed titles cannot be longer than 256 characters :no_entry:")
            s.title = embed_json["title"]
        if "description" in embed_json:
            if len(embed_json["description"]) > 2048:
                return await ctx.send("Embed descriptions cannot be longer than 256 characters :no_entry:")
            s.description = embed_json["description"]
        if "colour" in embed_json:
            match = hex_re.match(embed_json["colour"])
            if not match:
                return await ctx.send("Invalid hex for embed colour :no_entry:")
            s.colour = discord.Colour(int(match.group(1), 16))
        if "fields" in embed_json:
            if len(embed_json["fields"]) > 25:
                return await ctx.send("You are only able to have a maximum of 25 field objects in an embed :no_entry:")
            for i, x in enumerate(embed_json["fields"]):
                if "name" not in x or "value" not in x:
                    return await ctx.send("Name and Value are required parameters for fields in an embed (Field at index {}) :no_entry:".format(i))
                if len(x["name"]) > 256:
                    return await ctx.send("Field names in embeds can't be more than 256 characters (Field at index {}) :no_entry:".format(i))
                if len(x["value"]) > 1024:
                    return await ctx.send("Field values in embeds can't be more than 1024 characters (Field at index {}) :no_entry:".format(i))
                s.add_field(name=x["name"], value=x["value"], inline=x["inline"] if "inline" in x else True)
        if "image" in embed_json:
            s.set_image(url=embed_json["image"])
        if "thumbnail" in embed_json:
            s.set_thumbnail(url=embed_json["thumbnail"])
        if "footer" in embed_json:
            if "text" not in embed_json["footer"]:
                return await ctx.send("Text is required in an embed footer :no_entry:")
            if len(embed_json["footer"]["text"]) > 2048:
                return await ctx.send("The text in the footer cannot be longer than 2048 characters :no_entry:")
            s.set_footer(text=embed_json["footer"]["text"], icon_url=embed_json["footer"]["icon_url"] if "icon_url" in embed_json["footer"] else discord.Embed.Empty)
        if "author" in embed_json:
            if "name" not in embed_json["author"]:
                return await ctx.send("Name is required in an embed author :no_entry:")
            if len(embed_json["author"]["name"]) > 256:
                return await ctx.send("Author names cannot be longer than 256 characters :no_entry:")
            s.set_author(name=embed_json["author"]["name"], icon_url=embed_json["author"]["icon_url"] if "icon_url" in embed_json["author"] else discord.Embed.Empty, url=embed_json["author"]["url"] if "url" in embed_json["author"] else "")
        await ctx.send(embed=s)

    @commands.command()
    async def clapify(self, ctx, *, text: commands.clean_content):
        """Claps your text"""
        await ctx.send(text.replace(" ", ":clap:")[:2000])

    @commands.command(pass_context=True)
    async def ascend(self, ctx, *, text: commands.clean_content):
        """Make text look cool"""
        await ctx.send(text.replace("", " ")[:2000])
         
    @commands.command(pass_context=True)
    async def backwards(self, ctx, *, text: commands.clean_content):
        """Make text go backwards"""
        text = text[::-1]
        await ctx.send(text[:2000])
        
    @commands.command()
    async def randcaps(self, ctx, *, text: commands.clean_content):
        """Make your text look angry"""
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
    async def alternatecaps(self, ctx, *, text: commands.clean_content):
        """Make your text look neatly angry"""
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
            authordata.update({"rps_losses": r.row["rps_losses"] + 1}).run(self.db, durability="soft")
        if end == "Draw, let's go again!":
            authordata.update({"rps_draws": r.row["rps_draws"] + 1}).run(self.db, durability="soft")
        if end == "You win! :trophy:":
            authordata.update({"rps_wins": r.row["rps_wins"] + 1}).run(self.db, durability="soft")
         
    @commands.command(pass_context=True, aliases=["rpss"])
    async def rpsstats(self, ctx, *, user: discord.Member=None): 
        """Check your rps win/loss record"""    
        author = ctx.message.author
        if not user:
            user = author
        userdata = r.table("rps").get(str(user.id)).run(self.db)
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s RPS Stats".format(user.name), icon_url=user.avatar_url)
        if not userdata:
            s.add_field(name="Wins", value="0")
            s.add_field(name="Draws", value="0")
            s.add_field(name="Losses", value="0")
        else:
            s.add_field(name="Wins", value=userdata["rps_wins"])
            s.add_field(name="Draws", value=userdata["rps_draws"])
            s.add_field(name="Losses", value=userdata["rps_losses"])
        await ctx.send(embed=s)

    async def _set_bank(self, author):
        if author.bot:
            return
        r.table("bank").insert({"id": str(author.id), "rep": 0, "balance": 0, "streak": 0, "streaktime": None,
        "reptime": None, "items": [], "pickdur": None, "roddur": None, "minertime": None, "winnings": 0,
        "fishtime": None, "factorytime": None, "picktime": None}).run(self.db, durability="soft")

    def index_dbd(self, perk: str, type: str="survivor"):
        index = {"UNCOMMON": 1, "RARE": 2, "VERY_RARE": 3, "ULTRA_RARE": 3}

        per_row = 5
        per_page = per_row * 3
        
        if type == "survivor":
            perks = data.read_json("dbd_data/SurvivorPerks.json")
        elif type == "killer":
            perks = data.read_json("dbd_data/KillerPerks.json")
        def compare(perk, perk2):
            perk_index = index[perk["rarity"][-1]]
            perk2_index = index[perk2["rarity"][-1]]

            if perk_index > perk2_index:
                return -1
            elif perk_index < perk2_index:
                return 1
            else:
                sorted = [perk, perk2]
                sorted.sort(key=lambda perk: perk["name"].lower().replace('"', ''))

                if sorted.index(perk) == 0:
                    return -1
                else:
                    return 1

        perks.sort(key=functools.cmp_to_key(compare))
        perks_by_name = dict((e["name"], i) for i, e in enumerate(perks))

        index_of_perk = perks_by_name[perk]

        page = int(index_of_perk/per_page)
        row = index_of_perk % per_page

        return page + 1, row + 1

    def suffix(self, number: int):
        num = number % 100
        if num >= 11 and num <= 13:
            suffix = "th"
        else:
            num = number % 10
            if num == 1:
                suffix = "st"
            elif num == 2:
                suffix = "nd"
            elif num == 3:
                suffix = "rd"
            else:
                suffix = "th"
        return "{:,}{}".format(number, suffix)

    async def update_games(self):
        while not self.bot.is_closed():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=" + Token.steam() + "&format=json", timeout=7) as f:
                        if f.status == 200:
                            data.write_json("data/fun/steamgames.json", await f.json())
                        else:
                            print("Steam applist api returned a {}, trying again in 60 minutes".format(f.status))
                        await asyncio.sleep(3600)
            except:
                return print("Failed updating steam games file, trying again in 60 minutes")
                await asyncio.sleep(3600)
        
def setup(bot, connection):
    bot.add_cog(fun(bot, connection))