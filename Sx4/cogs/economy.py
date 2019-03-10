import discord
from discord.ext import commands
import os
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import choice as randchoice
from random import randint
from utils import arghelp
from copy import deepcopy
from utils import checks, dateify
from calendar import monthrange
from enum import Enum
from collections import Counter
from utils import arg, dateify
import time
import logging
import rethinkdb as r
from pathlib import Path
from . import owner as dev
import cogs.image as img
from utils import paged
import re
import aiohttp
from calendar import monthrange
import datetime
import math
from cogs import general
import traceback
import typing
from PIL import Image, ImageDraw, ImageFont, ImageOps
from urllib.request import Request, urlopen
import json
from utils import data
import urllib.request
from utils.PagedResult import PagedResult
from utils.PagedResult import PagedResultData
import random
from utils import Token
from random import choice
import asyncio
from difflib import get_close_matches
import requests

token = Token.dbl()

shop = data.read_json("data/economy/shop.json")
mine = {x[0]: list(filter(lambda x: not x["hidden"], x[1])) for x in data.read_json("data/economy/materials.json").items()}
mine_all = data.read_json("data/economy/materials.json")
factories = {x[0]: list(filter(lambda x: not x["hidden"], x[1])) for x in data.read_json("data/economy/factory.json").items()}
factories_all = data.read_json("data/economy/factory.json")
wood = data.read_json("data/economy/wood.json")

class economy:
    """Make money"""

    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection

    @commands.group(usage="<sub command>")
    async def crate(self, ctx):
        """Test your luck and open crates to see what you'll get"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @crate.command(name="shop")
    async def ___shop(self, ctx):
        """The crate shop, buy crates and test your luck"""
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Crate shop use your currency in Sx4 to buy crates", colour=0xfff90d)
        s.set_author(name="Crate Shop", icon_url=self.bot.user.avatar_url)
        for item in filter(lambda x: not x["hidden"], shop["crates"]):
            s.add_field(name=item["name"], value="Price: ${:,}".format(item["price"]))
        try:    
            s.set_footer(text="Use s?crate buy <crate> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run(self.db)))
        except:
            s.set_footer(text="Use s?crate buy <crate> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @crate.command(name="buy")
    async def ___buy(self, ctx, *, crate: str):
        """Spend your money on crates here"""
        crate, amount = self.convert(crate)
        crates = list(filter(lambda x: not x["hidden"], shop["crates"]))
        crate = self.get_item(crates, crate)
        if not crate:
            return await ctx.send("That's not a valid crate :no_entry:")
        authordata = r.table("bank").get(str(ctx.author.id))
        if authordata["balance"].run(self.db) < crate["price"] * amount:
            return await ctx.send("You do not have enough money to buy this crate :no_entry:")
        else:
            await ctx.send("You just bought `{} {}` for **${:,}** :ok_hand:".format(amount, crate["name"], crate["price"] * amount))
            items = self.add_mats(authordata["items"].run(self.db), [(crate["name"], amount)])
            authordata.update({"items": items, "balance": r.row["balance"] - (crate["price"] * amount)}).run(self.db, durability="soft", noreply=True)

    @crate.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def open(self, ctx, *, crate: str):
        """Open a crate you own which is in your items"""
        authordata = r.table("bank").get(str(ctx.author.id))
        crate, amount = self.convert(crate)
        crate = self.get_item(shop["crates"], crate)
        if not crate:
            return await ctx.send("That's not a valid crate :no_entry:")
        user_crate = self.get_user_item(authordata["items"].run(self.db), crate["name"])
        if crate["name"] == "Present Crate" and datetime.datetime.utcnow().strftime("%d/%m") != "25/12":
            return await ctx.send("It's not christmas yet, {} till you can open your present :no_entry:".format(dateify.get((datetime.datetime(datetime.datetime.utcnow().year + (1 if datetime.datetime.utcnow().day >= 25 and datetime.datetime.utcnow().month == 12 else 0), 12, 25, 00, 00) - datetime.datetime.utcnow()).total_seconds())))
        if amount > user_crate["amount"]:
            return await ctx.send("You do not own that many `{}` :no_entry:".format(crate["name"]))
        items = shop["miners"] + mine["items"] + list(filter(lambda x: not x["hidden"], shop["crates"])) + wood["wood"]
        items.remove(crate)
        factories2 = factories["factory"]
        for x in factories2:
            items.append({"name": x["name"], "price": x["price"]*(list(filter(lambda y: y["name"] == x["item"], mine["items"]))[0]["price"])})
        items = [{item[0]: item[1] for item in x.items() if item[0] == "name" or item[0] == "price"} for x in items]
        total_items, wins = [], []
        for x in range(amount):
            for x in items:
                eq = round((1/((1/x["price"]) * crate["price"]))*20)
                number = randint(1, 2 if eq <= 1 else eq)
                if number == 1:
                    total_items.append(x)
            final_item = sorted(total_items, key=lambda x: x["price"], reverse=True)
            if final_item:
                wins.append(final_item[0])
            total_items = []
        if wins:
            tuples = Counter(map(lambda x: x["name"], wins)).most_common()
            counter = ", ".join([x[0] + " x{}".format(x[1]) for x in tuples])
            s=discord.Embed(description="You opened `{} {}` and won **{}** :tada:".format(amount, crate["name"], counter), colour=ctx.author.colour)
        else:
            s=discord.Embed(description="You opened `{} {}` and got scammed, there was nothing in the crate.".format(amount, crate["name"]), colour=ctx.author.colour)
        s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        items = authordata["items"].run(self.db)
        items = self.remove_mats(items, [(crate["name"], amount)])
        if wins:
            items = self.add_mats(items, tuples)
        authordata.update({"items": items}).run(self.db, durability="soft", noreply=True)

    @commands.command()
    async def tax(self, ctx):
        """Shows you how much tax there is currently (reset every week)"""
        s=discord.Embed(description="Their Balance: **${:,}**".format(r.table("tax").get("tax")["tax"].run(self.db, durability="soft")), colour=0xffff00)
        s.set_author(name="Sx4 the tax bot", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def transfertax(self, ctx, user: str):
        user = await arg.get_member(ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        self._set_bank(user)
        tax = r.table("tax").get("tax")
        r.table("bank").get(str(user.id)).update({"balance": r.row["balance"] + tax["tax"].run(self.db)}).run(self.db, durability="soft")
        tax.update({"tax": 0}).run(self.db, durability="soft")
        await ctx.send("Done")
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def parse(self, ctx, *, code: str=None):
        if not code:
            code = requests.get(ctx.message.attachments[0].url).content.decode()
        code = "    " + code.replace("\n", "\n    ")
        code = "async def __eval_function__():\n" + code
        additional = {}
        additional["self"] = self
        additional["ctx"] = ctx
        additional["channel"] = ctx.channel
        additional["author"] = ctx.author
        additional["guild"] = ctx.guild

        try:
            exec(code, {**globals(), **additional}, locals())

            t1 = time.perf_counter()
            await locals()["__eval_function__"]()
            t2 = time.perf_counter()
            await ctx.send(":stopwatch: **{}ms**".format(round((t2-t1)*1000, 2)))
        except:
            await ctx.send("```py\n" + traceback.format_exc() + "```")
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code):
        author = ctx.author
        server = ctx.guild
        channel = ctx.channel
        try:
            t1 = time.perf_counter()
            return_code = str(await eval(code))
            t2 = time.perf_counter()
            executed = round((t2-t1)*1000, 2)
        except:
            try:
                t1 = time.perf_counter()
                return_code = str(eval(code))
                t2 = time.perf_counter()
                executed = round((t2-t1)*1000, 2)
            except Exception as e:
                return await ctx.send(str(e))
        await ctx.send(":stopwatch: **{}ms**```py\n{}```".format(executed, return_code))

    @commands.command()
    async def trade(self, ctx, *, user: discord.Member):
        """Trade items and money with another user"""
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))
        userdata = r.table("bank").get(str(user.id))
        if author == user:
            return await ctx.send("You can't trade with yourself :no_entry:")
        if user in filter(lambda x: x.bot, self.bot.get_all_members()):
            return await ctx.send("You can't trade with a bot :no_entry:")
        self._set_bank(author)
        self._set_bank(user)
        await ctx.send("What are you offering to the user? Make sure you put a space between every thing you want to offer, for example: `2 gold 200 5 titanium 1 coal factory` would offer $200, 5 Titanium, 2 Gold and 1 Coal Factory (Respond Below)")
        tradeable = shop["miners"] + mine_all["items"] + shop["crates"] + shop["boosters"] + wood["wood"]
        factories2 = factories_all["factory"]
        for x in factories2:
            tradeable.append({"name": x["name"], "price": x["price"]*(list(filter(lambda y: y["name"] == x["item"], mine_all["items"]))[0]["price"])})
        tradeable = [{item[0]: item[1] for item in x.items() if item[0] == "name" or item[0] == "price"} for x in tradeable]
        def trade(content: str):
            split = content.split(" ")
            money, i, items = 0, -1, []
            lastthing = None
            for num, x in enumerate(split, start=1):
                if lastthing:
                    if lastthing.isdigit() and x.isdigit():
                        if int(lastthing) <= 0:
                            return "You can't give no or minus money :no_entry:"
                        money += int(lastthing)
                    elif lastthing.isdigit() and not x.isdigit():
                        if int(lastthing) <= 0:
                            return "You can't give zero or minus of an item :no_entry:"
                        items.append([int(lastthing), x.title()])
                        i += 1
                    elif not lastthing.isdigit() and x.isdigit():
                        if num == len(split):
                            if int(x) <= 0:
                                return "You can't give zero or minus of money :no_entry:"
                            money += int(x)
                    else:
                        items[i][1] += " " + x.title()
                    lastthing = x
                else:
                    if x.isdigit():
                        if num == len(split):
                            if int(x) <= 0:
                                return "You can't give zero or minus of money :no_entry:"
                            money += int(x)
                        else:
                            lastthing = x
                    else:
                        return "Invalid Format :no_entry:"
            new = []
            for x, y in items:
                if y in map(lambda x: x[1], new):
                    list(filter(lambda item: item[1] == y, new))[0][0] += x
                else:
                    new.append([x, y])
            for item in new:
                try:
                    price = list(filter(lambda x: x["name"] == item[1], tradeable))[0]["price"]
                except:
                    return "There was an invalid/non-tradeable item so the trade has been cancelled, Pickaxes and Rods are untradeable :no_entry:"
                price = price * item[0]
                item.append(price)
            return money, new
        def user_check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            response = await self.bot.wait_for("message", check=user_check, timeout=300)
            if response.content.lower() == "cancel":
                return await ctx.send("Cancelled.")
            else:
                tradeuser = trade(response.content)
                if type(tradeuser) == str:
                    return await ctx.send(tradeuser)
                else:
                    money = tradeuser[0]
                    materials2 = tradeuser[1]
                    usergetsmoney = money if money else None
                    usergetsmaterials = materials2
                    await ctx.send(content="What would you like from the user? Make sure you put a space between every thing you want to offer, for example: `2 gold 200 5 titanium 1 coal factory` would offer $200, 5 Titanium, 2 Gold and 1 Coal Factory (Respond Below)",
                    embed=discord.Embed(title="What you're offering", description="{}\n{}".format("${:,}".format(money) if money else "", "\n".join(["{}x {}".format(x[0], x[1]) for x in usergetsmaterials]))))
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")
        try:
            response = await self.bot.wait_for("message", check=user_check, timeout=300)
            if response.content.lower() == "cancel":
                return await ctx.send("Cancelled.")
            else:
                tradeauthor = trade(response.content)
                if type(tradeauthor) == str:
                    return await ctx.send(tradeauthor)
                else:
                    money = tradeauthor[0]
                    materials2 = tradeauthor[1]
                    authorgetsmoney = money if money else None
                    authorgetsmaterials = materials2
                    await ctx.send(embed=discord.Embed(title="The Final Trade").add_field(name="{} Gets".format(user), value="{}\n{}".format("${:,}".format(usergetsmoney) if usergetsmoney else "", "\n".join(["{}x {}".format(x[0], x[1]) for x in usergetsmaterials])),
                    inline=False).add_field(name="{} Gets".format(author), value="{}\n{}".format("${:,}".format(authorgetsmoney) if authorgetsmoney else "", "\n".join(["{}x {}".format(x[0], x[1]) for x in authorgetsmaterials]))).set_footer(
                    text="{} needs to type yes to accept the trade or it will be declined".format(user)))
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")
        try:
            def check(m):
                return m.author == user and m.channel == ctx.channel
            userresponse = await self.bot.wait_for("message", check=check, timeout=60)
            if userresponse.content.lower() in ["yes", "y"]:
                usertotal = 0
                authortotal = 0
                if authorgetsmoney:
                    if userdata["balance"].run(self.db, durability="soft") < authorgetsmoney:
                        return await ctx.send("The user no longer has enough money to give like shown in the deal :no_entry:")
                    else:
                        authortotal += authorgetsmoney
                if usergetsmoney:
                    if authordata["balance"].run(self.db, durability="soft") < usergetsmoney:
                        return await ctx.send("You no longer have enough money to give like shown in the deal :no_entry:")
                    else:
                        usertotal += usergetsmoney
                if usergetsmaterials:
                    for x in usergetsmaterials:
                        usertotal += x[2]
                if authorgetsmaterials:
                    for x in authorgetsmaterials:
                        authortotal += x[2]
                if usertotal / authortotal > 20 or authortotal / usertotal > 20:
                    return await ctx.send("You have to trade at least 5% worth of the other persons trade :no_entry:")
                user_items = userdata["items"].run(self.db)
                author_items = authordata["items"].run(self.db)
                if usergetsmaterials:
                    for x in usergetsmaterials:
                        amount = x[0]
                        item = x[1]
                        author_item = self.get_user_item(author_items, item)
                        if author_item["amount"] < amount:
                            return await ctx.send("**{}** does not have `{:,} {}` :no_entry:".format(ctx.author, amount, item))
                        author_items = self.remove_mats(author_items, [(item, amount)])
                        user_items = self.add_mats(user_items, [(item, amount)])
                if authorgetsmaterials:
                    for x in authorgetsmaterials:
                        amount = x[0]
                        item = x[1]
                        user_item = self.get_user_item(user_items, item)
                        if user_item["amount"] < amount:
                            return await ctx.send("**{}** does not have `{:,} {}` :no_entry:".format(user, amount, item))
                        user_items = self.remove_mats(user_items, [(item, amount)])
                        author_items = self.add_mats(author_items, [(item, amount)])
                if authorgetsmaterials or usergetsmaterials:
                    authordata.update({"items": author_items}).run(self.db, durability="soft")
                    userdata.update({"items": user_items}).run(self.db, durability="soft")
                if authorgetsmoney:
                    authordata.update({"balance": r.row["balance"] + authorgetsmoney}).run(self.db, durability="soft")
                    userdata.update({"balance": r.row["balance"] - authorgetsmoney}).run(self.db, durability="soft")
                if usergetsmoney:
                    authordata.update({"balance": r.row["balance"] - usergetsmoney}).run(self.db, durability="soft")
                    userdata.update({"balance": r.row["balance"] + usergetsmoney}).run(self.db, durability="soft")
                await ctx.send("All items and money have been transferred <:done:403285928233402378>")
            else:
                await ctx.send("Trade Declined.")
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")

    @commands.group(usage="<sub command>")
    async def booster(self, ctx):
        """Buy and activate boosters here"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @booster.command(name="shop")
    async def _shop_(self, ctx):
        """Check what boosters you can buy"""
        
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="You can buy boosters to avoid annoying things like cooldowns on commands", colour=0xfff90d)
        s.set_author(name="Booster Shop", icon_url=self.bot.user.avatar_url)
        for item in shop["boosters"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDescription: {}".format(item["price"], item["description"]))
        try:    
            s.set_footer(text="Use s?booster buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run(self.db, durability="soft")))
        except:
            s.set_footer(text="Use s?booster buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @booster.command(name="buy")
    async def _buy_(self, ctx, *, booster):
        """Buy booster here"""
        booster, amount = self.convert(booster)
        booster = self.get_item(shop["boosters"], booster)
        if not booster:
            return await ctx.send("That booster does not exist :no_entry:")
        if booster["name"] == "Miner Repair":
            return await ctx.send("Miner repairs are disabled as they need to be rebalanced :no_entry:")
        authordata = r.table("bank").get(str(ctx.author.id))
        if booster["price"] * amount <= authordata["balance"].run(self.db, durability="soft"):
            items = self.add_mats(authordata["items"].run(self.db), [(booster["name"], amount)])
            authordata.update({"balance": r.row["balance"] - (booster["price"] * amount), "items": items}).run(self.db, durability="soft")
            return await ctx.send("You just bought the booster `{} {}` for **${:,}** :ok_hand:".format(amount, booster["name"], booster["price"] * amount))
        else:
            return await ctx.send("You don't have enough money to buy that booster :no_entry:")
        

    @booster.command()
    async def activate(self, ctx, *, booster):
        """Activate booster which say they needed to be activated here"""
        authordata = r.table("bank").get(str(ctx.author.id))
        booster = self.get_item(shop["boosters"], booster)
        if not booster:
            return await ctx.send("Invalid booster :no_entry:")
        user_booster = self.get_user_item(authordata["items"].run(self.db), booster["name"])
        if user_booster["amount"] <= 0:
            return await ctx.send("You do not own a `{}` :no_entry:".format(booster["name"]))
        if booster["name"] == "Lended Pickaxe":
            has_pick = False
            for item in authordata["items"].run(self.db, durability="soft"):
                for pick in shop["picitems"]:
                    if pick["name"] == item["name"]:
                        has_pick = True
                        break
            if has_pick:
                list = authordata["items"].run(self.db, durability="soft")
                items = self.remove_mats(list, [(booster["name"], 1)])
                authordata.update({"items": items, "picktime": None}).run(self.db, durability="soft")
                await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster["name"]))
            else:
                await ctx.send("You do not own a pickaxe you should probably own one to use this booster :no_entry:")
        elif booster["name"] == "Miner Repair":
            return await ctx.send("Miner repairs are disabled as they need to be rebalanced :no_entry:")
            has_miner = False
            for item in authordata["items"].run(self.db, durability="soft"):
                for miner in shop["miners"]:
                    if miner["name"] == item["name"]:
                        has_miner = True
                        break
            if has_miner:
                if "minerrepairtime" not in authordata.run(self.db):
                    list = authordata["items"].run(self.db, durability="soft")
                    items = self.remove_mats(list, [(booster["name"], 1)])
                    authordata.update({"items": items, "minertime": None, "minerrepairtime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft")
                    await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster["name"]))
                else:
                    m, s = divmod(authordata["minerrepairtime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 3600, 60)
                    h, m = divmod(m, 60)
                    if h == 0:
                        time = "%d minutes %d seconds" % (m, s)
                    elif h == 0 and m == 0:
                        time = "%d seconds" % (s)
                    else:
                        time = "%d hours %d minutes %d seconds" % (h, m, s)
                    if ctx.message.created_at.timestamp() - authordata["minerrepairtime"].run(self.db, durability="soft") <= 3600:
                        await ctx.send("You are too early, you can activate this booster again in {}".format(time))
                        return
                    else:
                        list = authordata["items"].run(self.db, durability="soft")
                        items = self.remove_mats(list, [(booster["name"], 1)])
                        authordata.update({"items": items, "minertime": None, "minerrepairtime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft")
                        await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster["name"]))
            else:
                await ctx.send("You do not own a miner you should probably own one to use this booster :no_entry:")
        else:
            await ctx.send("That booster doesn't exist or isn't activatable :no_entry:")

    @commands.command(aliases=["referralurl"])
    async def referral(self, ctx, user: discord.Member=None):
        """Get given your referral urls for votes"""
        if not user:
            user = ctx.author
        await ctx.send("__**{}'s** referral urls__\n<https://discordbots.org/bot/440996323156819968/vote?referral={}> (Sx4)\n<https://discordbots.org/bot/411916947773587456/vote?referral={}> (Jockie Music)".format(user, user.id, user.id))
 
    @commands.command(aliases=["vote", "upvote"])
    async def votebonus(self, ctx):
        """Get some extra credits by simply upvoting the bot on dbl"""
        author = ctx.author
        self._set_bank(author)
        authordata = r.table("bank").get(str(ctx.author.id))
        try:
            request = requests.get("http://localhost:8080/440996323156819968/votes/user/{}/unused/use".format(author.id), headers={"Authorization": Token.jockie()}, timeout=3).json()
            requestjockie = requests.get("http://localhost:8080/411916947773587456/votes/user/{}/unused/use".format(author.id), headers={"Authorization": Token.jockie_music()}, timeout=3).json()
            weekend = requests.get("http://discordbots.org/api/weekend").json()["is_weekend"]
        except:
            return await ctx.send("Vote Bonus is currently disabled as the webhook/discord bot list api the bot uses is currently down so it just returns errors, sorry for the inconvenience :no_entry:")
        if request["success"] or requestjockie["success"]:
            amount, votes, votes2 = 0, None, None
            try:
                votes = request["votes"]
                amount += len(votes)
            except:
                pass
            try:
                votes2 = requestjockie["votes"]
                amount += len(votes2)
            except: 
                pass
            try:
                money, referred = 0, []
                if votes:
                    for vote in votes:
                        money += 1000 if vote["weekend"] else 500
                        if "referral" in vote["query"]:
                            if type(vote["query"]["referral"]) == str:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"]))
                            elif type(vote["query"]["referral"]) == list:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"][0]))
                            else:
                                return await ctx.send("No clue what you've done there to cause this, report this to the Sx4 Support Server or add Joakim#9814 and spam his dms telling him you found this. Thank you!")
                            if user and user != author and not user.bot:
                                if r.table("bank").get(str(user.id)).run(self.db, durability="soft"):
                                    r.table("bank").get(str(user.id)).update({"balance": r.row["balance"] + (500 if vote["weekend"] else 250)}).run(self.db, durability="soft")
                                    referred.append(user)
                if votes2:
                    for vote in votes2:
                        money += 600 if vote["weekend"] else 300
                        if "referral" in vote["query"]:
                            if type(vote["query"]["referral"]) == str:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"]))
                            elif type(vote["query"]["referral"]) == list:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"][0]))
                            else:
                                return await ctx.send("No clue what you've done there to cause this, report this to the Sx4 Support Server or add Joakim#9814 and spam his dms telling him you found this. Thank you!")
                            if user and user != author and not user.bot:
                                if r.table("bank").get(str(user.id)).run(self.db, durability="soft"):
                                    r.table("bank").get(str(user.id)).update({"balance": r.row["balance"] + (300 if vote["weekend"] else 150)}).run(self.db, durability="soft")
                                    referred.append(user)
                    
                await ctx.send("You have voted for the bots **{}** {} since you last used the command gathering you a total of **${:,}**, Vote for the bots again in 12 hours for more money. Referred users: {}".format(
                amount, "time" if amount == 1 else "times", money, ", ".join(map(lambda x: str(x) + " x" + str(referred.count(x)), list(set(referred)))) if referred != [] else "None"))
                self._set_bank(author)
                authordata.update({"balance": r.row["balance"] + money}).run(self.db, durability="soft")
            except Exception as e:
                await ctx.send(e)
                for vote in votes: 
                    try:
                        requests.get("http://localhost:8080/440996323156819968/votes/vote/{}/unuse".format(vote["id"]), headers={"Authorization": Token.jockie()}).json()
                    except: # This is unlikely to happen but just in case
                        pass
                for vote in votes2:
                    try:
                        requests.get("http://localhost:8080/411916947773587456/votes/vote/{}/unuse".format(vote["id"]), headers={"Authorization": Token.jockie_music()}).json()
                    except:
                        pass
                
                await ctx.send("Ops, something unexpected happened")
                
        else:
            if request["error"] == "This user has no unused votes":
                latest = requests.get("http://localhost:8080/440996323156819968/votes/user/{}/latest".format(ctx.author.id), headers={"Authorization": Token.jockie()}).json()
                latestjockie = requests.get("http://localhost:8080/411916947773587456/votes/user/{}/latest".format(ctx.author.id), headers={"Authorization": Token.jockie_music()}).json()
                if latest["success"] == False:
                    timesx4 = None
                else:
                    timesx4 = latest["vote"]["time"]
                if latestjockie["success"] == False:
                    timejockie = None
                else:
                    timejockie = latestjockie["vote"]["time"]
                if timesx4:
                    timesx4 = self._vote_time(timesx4)
                if timejockie:
                    timejockie = self._vote_time(timejockie)
                s=discord.Embed()
                s.set_author(name="Vote Bonus", icon_url=self.bot.user.avatar_url)
                s.add_field(name="Sx4", value="**[You have voted recently you can vote for the bot again in {}](https://discordbots.org/bot/440996323156819968/vote)**".format(timesx4)
                if timesx4 else "**[You can vote for Sx4 for an extra ${}](https://discordbots.org/bot/440996323156819968/vote)**".format(1000 if weekend else 500), inline=False)
                s.add_field(name="Jockie Music", value="**[You have voted recently you can vote for the bot again in {}](https://discordbots.org/bot/411916947773587456/vote)**".format(timejockie)
                if timejockie else "**[You can vote for Jockie Music for an extra ${}](https://discordbots.org/bot/411916947773587456/vote)**".format(600 if weekend else 300), inline=False)
                await ctx.send(embed=s)
            else:
                await ctx.send("Ops, something unexpected happened")

    @commands.command()
    async def badges(self, ctx):
        """A list of badges and what you can do to get them"""
        s=discord.Embed(title="Badges", description=("<:server_owner:441255213450526730> - Be an owner of a server in which Sx4 is in\n"
        "<:developer:441255213068845056> - Be a developer of Sx4\n<:helper:441255213131628554> - You have at some point contributed to the bot\n"
        "<:donator:441255213224034325> - Donate to Sx4 either through PayPal or Patreon\n<:profile_editor:441255213207126016> - Edit your profile"
		"\n<:married:441255213106593803> - Be married to someone on the bot\n<:playing:441255213513572358> - Have a playing status\n<:streaming:441255213106724865> - Have a streaming status"
        "\n<:insx4server:472895584856965132> - Be in the Sx4 Support Server"))
        await ctx.send(embed=s)
 
    @commands.command(no_pm=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, *, user: discord.Member=None):
        """Lists aspects about you on discord with Sx4. Defaults to author."""
        author = ctx.author
        server = ctx.guild
        if not user:
            user = author
        if user.bot:
            await ctx.send("Bots don't have profiles :no_entry:")
            return
        r.table("userprofile").insert({"id": str(user.id), "birthday": None, "description": None, "height": None, "colour": None}).run(self.db, durability="soft")
        r.table("marriage").insert({"id": str(user.id), "marriedto": []}).run(self.db, durability="soft")
        self._set_bank(user)
        userdata = r.table("bank").get(str(user.id)).run(self.db)
        usermarriage = r.table("marriage").get(str(user.id)).run(self.db)
        userprofile = r.table("userprofile").get(str(user.id)).run(self.db)

        background_path = "file://" + str(Path("profile-images/{}.png".format(user.id)).absolute())
        
        married_users = []
        for married_user_id in usermarriage["marriedto"]:
            married_user = self.bot.get_user(int(married_user_id))
            if married_user:
                married_users.append(str(married_user))

        if userprofile["colour"]:
            colour = userprofile["colour"]
        else:
            colour = "#ffffff"
        if not userprofile["birthday"]:
            birthday = "Not set"
        else:
            birthday = userprofile["birthday"]
        if not userprofile["description"]:
            description = "Not set"
        else:
            description = userprofile["description"]
        if not userprofile["height"]:
            height = "Not set"
        else:
            height = userprofile["height"]
        badges = []
        support_server = self.bot.get_guild(330399610273136641)
        member = support_server.get_member(user.id)
        if member:
            if support_server.get_role(330400064541425664) in member.roles:
                badges.append("developer.png")
            if support_server.get_role(355083059336314881) in member.roles:
                badges.append("donator.png")

        for guild in self.bot.guilds:
            if user == guild.owner:
                badges.append("server_owner.png")
                break

        if user.id in [153286414212005888, 285451236952768512, 388424304678666240, 250815960250974209, 223424602150273024]:
            badges.append("helper.png")

        if userprofile["birthday"] or userprofile["description"] or userprofile["height"]:
            badges.append("profile_editor.png")

        if user in support_server.members:
            badges.append("sx4-circle.png")

        if usermarriage["marriedto"]:
            badges.append("married.png")

        if not user.activity:
            pass
        elif user.activity:
            badges.append("playing.png") 
        elif user.activity.url:
            badges.append("streaming.png") 

        balance = "{:,}".format(userdata["balance"])
        reputation = userdata["rep"]
        data = {"user_name": str(user), "background_path": background_path, "colour": colour, "balance": balance, "reputation": reputation, "description": description, "birthday": birthday,
        "height": height, "badges": badges, "married_users": married_users, "user_avatar_url": user.avatar_url_as(format="png")}
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8443/api/profile", json=data, headers={"Content-Type": "application/json"}) as f:
                    if f.status == 200:
                        await ctx.send(file=discord.File(f.content, "profile.png"))
                    elif f.status == 400:
                        return await ctx.send(await f.text())
                    else:
                        return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
        
    @commands.command(aliases=["pd", "payday"])
    async def daily(self, ctx):
        """Collect your daily money"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        authordata = r.table("bank").get(str(author.id))
        self._set_bank(author)
        if not authordata["streaktime"].run(self.db, durability="soft"):
            authordata.update({"streaktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + 100, "streak": 0}).run(self.db, durability="soft")
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        if ctx.message.created_at.timestamp() - authordata["streaktime"].run(self.db, durability="soft") <= 86400:
            time = dateify.get(authordata["streaktime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 86400)
            await ctx.send("You are too early, come collect your money again in {}".format(time))
            return
        elif ctx.message.created_at.timestamp() - authordata["streaktime"].run(self.db, durability="soft") <= 172800:
            crate = []
            for x in filter(lambda x: not x["hidden"], shop["crates"]):
                eq = round(x["chance"]/(authordata["streak"].run(self.db, durability="soft") + 1)*4)
                number = randint(1, 2 if eq <= 1 else eq)
                if number == 1:
                    crate.append(x)
            if authordata["streak"].run(self.db, durability="soft") + 1 == 1:
                money = 120
            elif authordata["streak"].run(self.db, durability="soft") + 1 == 2:
                money = 145
            elif authordata["streak"].run(self.db, durability="soft") + 1 == 3:
                money = 170
            elif authordata["streak"].run(self.db, durability="soft") + 1 == 4:
                money = 200
            elif authordata["streak"].run(self.db, durability="soft") + 1 >= 5:
                money = 250
            else:
                money = 100
            authordata.update({"streaktime": ctx.message.created_at.timestamp(), "streak": r.row["streak"] + 1, "balance": r.row["balance"] + money}).run(self.db, durability="soft")
            if money != 100:
                try:
                    crate = sorted(crate, key=lambda x: x["price"], reverse=True)[0]
                    cratemsg = "You also received a `{}` (**${:,}**), it has been added to your items.".format(crate["name"], crate["price"])
                    items = self.add_mats(authordata["items"].run(self.db), [(crate["name"], 1)])
                    authordata.update({"items": items}).run(self.db, durability="soft", noreply=True)
                except:
                    crate = None
                s=discord.Embed(description="You have collected your daily money! (**+${}**)\nYou had a bonus of ${} for having a {} day streak.\n\n{}".format(money, (money-100), authordata["streak"].run(self.db, durability="soft"), cratemsg if crate else ""), colour=colour)
            else:
                s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        else: 
            authordata.update({"streaktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + 100, "streak": 0}).run(self.db, durability="soft")
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
    @commands.command()
    async def rep(self, ctx, user: discord.Member):
        """Give reputation to another user"""
        server = ctx.guild
        author = ctx.author
        if user.bot:
            await ctx.send("No bots :angry:")
            return
        if (datetime.datetime.utcnow() - ctx.author.created_at).days <= 30:
            return await ctx.send("Your account was made too recently to be repping people :no_entry:")
        if user == author:
            await ctx.send("You can not give reputation to yourself :no_entry:")
            return
        self._set_bank(author)
        self._set_bank(user)
        userdata = r.table("bank").get(str(user.id))
        authordata = r.table("bank").get(str(author.id))
        if not authordata["reptime"].run(self.db, durability="soft"):
            authordata.update({"reptime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft")
            userdata.update({"rep": r.row["rep"] + 1}).run(self.db, durability="soft")
            await ctx.send("**+1**, {} has gained reputation".format(user.name))
            return
        m, s = divmod(authordata["reptime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - authordata["reptime"].run(self.db, durability="soft") <= 86400:
            await ctx.send("You are too early, give out your reputation in {}".format(time))
            return
        else:
            authordata.update({"reptime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft")
            userdata.update({"rep": r.row["rep"] + 1}).run(self.db, durability="soft")
            await ctx.send("**+1**, {} has gained reputation".format(user.name))
            return
            
    @commands.command(aliases=["bal"])
    async def balance(self, ctx, *, user=None):
        """Check how much money you have"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if not user or await arg.get_member(ctx, user) == ctx.author:
            user = ctx.author
            if user.bot:
                return await ctx.send("Bots can't make money :no_entry:")
            self._set_bank(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Your balance: **${:,}**".format(userdata["balance"].run(self.db, durability="soft") if userdata["balance"].run(self.db, durability="soft") else 0), colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
            if user.bot:
                return await ctx.send("Bots can't make money :no_entry:")
            self._set_bank(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Their balance: **${:,}**".format(userdata["balance"].run(self.db, durability="soft") if userdata["balance"].run(self.db, durability="soft") else 0), colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(name="winnings")
    async def _winnings(self, ctx, user=None):
        """Check your all time winnings"""
        if not user or await arg.get_member(ctx, user) == ctx.author:
            user = ctx.author
            if user.bot:
                return await ctx.send("Bots can't gamble :no_entry:")
            self._set_bank(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Your winnings: **${:,}**".format(userdata["winnings"].run(self.db, durability="soft") if userdata["winnings"].run(self.db, durability="soft") else 0), colour=user.colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
            if user.bot:
                return await ctx.send("Bots can't gamble :no_entry:")
            self._set_bank(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Their winnings: **${:,}**".format(userdata["winnings"].run(self.db, durability="soft") if userdata["winnings"].run(self.db, durability="soft") else 0), colour=user.colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(name="networth")
    async def _networth(self, ctx, *, user=None):
        """Check your networth"""
        check = False
        if not user:
            user = ctx.author
            check = True
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        userdata = r.table("bank").get(str(user.id)).run(self.db, durability="soft")
        all_items = shop["picitems"] + shop["items"] + mine["items"] + shop["roditems"] + shop["miners"] + shop["boosters"] + shop["crates"] + wood["wood"]
        if userdata:
            user_data = userdata
            worth = 0
            items = [item for item in all_items if item["name"] in map(lambda x: x["name"], user_data["items"])]
            for item in items:
                user_item = self.get_user_item(user_data["items"], item["name"])
                if "price" in user_item:
                    if self.get_exact_item(shop["picitems"], user_item["name"]):
                        worth += (user_item["price"]/user_item["durability"])*user_data["pickdur"]
                    elif self.get_exact_item(shop["roditems"], user_item["name"]):
                        worth += (user_item["price"]/user_item["durability"])*user_data["roddur"]
                    elif self.get_exact_item(shop["axes"], user_item["name"]):
                        worth += (user_item["price"]/user_item["durability"])*user_data["axedur"]
                    else:
                        worth += user_item["price"] * user_item["amount"]
                else:
                    if self.get_exact_item(shop["picitems"], user_item["name"]):
                        worth += (item["price"]/item["durability"])*user_data["pickdur"]
                    elif self.get_exact_item(shop["roditems"], user_item["name"]):
                        worth += (item["price"]/item["durability"])*user_data["roddur"]
                    elif self.get_exact_item(shop["axes"], user_item["name"]):
                        worth += (item["price"]/item["durability"])*user_data["axedur"]
                    else:
                        worth += item["price"] * user_item["amount"] 
            for item2 in [item for item in factories["factory"] if item["name"] in map(lambda x: x["name"], user_data["items"])]:
                user_factory = self.get_user_item(user_data["items"], item2["name"])
                for item3 in mine["items"]:
                    if item3["name"] == item2["item"]:
                        worth += (item2["price"]*item3["price"]) * user_factory["amount"]
            worth += user_data["balance"]
            worth = round(worth)
        if check is True or user == ctx.author:
            self._set_bank(user)
            try:
                s=discord.Embed(description="Your networth: **${:,}**".format(worth), colour=colour)
            except:
                s=discord.Embed(description="Your networth: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            self._set_bank(user)
            try:
                s=discord.Embed(description="Their networth: **${:,}**".format(worth), colour=colour)
            except:
                s=discord.Embed(description="Their networth: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
            
    @commands.command(aliases=["don", "allin", "dn"])
    @commands.cooldown(1, 40, commands.BucketType.user) 
    async def doubleornothing(self, ctx):
        """You double your money or lose it all it's that simple"""
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))
        if not authordata.run(self.db):
            await ctx.send("You don't have enough money to do double or nothing :no_entry:")
            ctx.command.reset_cooldown(ctx)
            return
        if authordata["balance"].run(self.db, durability="soft") <= 0:
            await ctx.send("You don't have enough money to do double or nothing :no_entry:")
            ctx.command.reset_cooldown(ctx)
            return
        msg = await ctx.send("This will bet **${:,}**, are you sure you want to bet this?\nYes or No".format(authordata["balance"].run(self.db, durability="soft")))
        try:
            def don(m):
                return m.author == ctx.author
            response = await self.bot.wait_for("message", check=don, timeout=30)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("The bet has been canceled.")
            ctx.command.reset_cooldown(ctx)
            return
        if "yes" == response.content.lower():
            await msg.delete()
        else:
            await msg.delete()
            await ctx.send("The bet has been canceled.")
            ctx.command.reset_cooldown(ctx)
            return
        number = randint(0, 1)
        message = await ctx.send("You just put **${:,}** on the line and...".format(authordata["balance"].run(self.db, durability="soft")))
        await asyncio.sleep(2)
        if number == 0:
            await message.edit(content="You lost it all! **-${:,}**".format(authordata["balance"].run(self.db, durability="soft")))
            authordata.update({"winnings": r.row["winnings"] - r.row["balance"], "balance": 0}).run(self.db, durability="soft")
        if number == 1:
            await message.edit(content="You double your money! **+${:,}**".format(authordata["balance"].run(self.db, durability="soft")))
            authordata.update({"winnings": r.row["winnings"] + r.row["balance"], "balance": r.row["balance"] * 2}).run(self.db, durability="soft")
        ctx.command.reset_cooldown(ctx)

    @commands.group(usage="<sub command>")
    async def miner(self, ctx):
        """Buys miners and get materials every 2 hours"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @miner.command(name="shop")
    async def __shop(self, ctx):
        """View the miner shop"""
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Buy miners for an easier way to gather materials", colour=0xfff90d)
        s.set_author(name="Miners", icon_url=self.bot.user.avatar_url)
        for item in shop["miners"]:
            s.add_field(name=item["name"], value="Price: ${:,}".format(item["price"]))
        try:    
            s.set_footer(text="Use s?miner buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run(self.db, durability="soft")))
        except:
            s.set_footer(text="Use s?miner buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @miner.command(name="buy")
    async def _buy(self, ctx, *, miner: str):
        """Buy a miner"""
        miner, amount = self.convert(miner)
        miner = self.get_item(shop["miners"], miner)
        if not miner:
            return await ctx.send("That's not a valid miner :no_entry:")
        authordata = r.table("bank").get(str(ctx.author.id))
        if authordata["balance"].run(self.db, durability="soft") >= miner["price"] * amount:
            items = self.add_mats(authordata["items"].run(self.db), [(miner["name"], amount)])
            authordata.update({"items": items, "balance": r.row["balance"] - (miner["price"] * amount)}).run(self.db, durability="soft")
            await ctx.send("You just bought `{} {}` for **${:,}** :ok_hand:".format(amount, miner["name"].title(), miner["price"] * amount)) 
            return
        else:
            return await ctx.send("You do not have enough money to buy this miner :no_entry:")

    @miner.command(name="collect")
    async def _collect(self, ctx):
        """Collect money from your miners"""
        i = 0
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))
        for miner in shop["miners"]:
            for item in authordata["items"].run(self.db, durability="soft"):
                if item["name"] == miner["name"]:
                    i += 1
        if i == 0:
            return await ctx.send("You do not own any miners :no_entry:")
        if not authordata["minertime"].run(self.db, durability="soft"):
            counter = Counter()
            for miner in shop["miners"]:
                for item in authordata["items"].run(self.db, durability="soft"):
                    if item["name"] == miner["name"]:
                        for x in range(item["amount"]):
                            for x in range(miner["max_mats"]):
                                for mat in mine["items"]:
                                    if round(mat["rand_max"] * miner["multiplier"]) <= 0:
                                        number = 1
                                    else:
                                        number = round(mat["rand_max"] * miner["multiplier"])
                                    if randint(0, number) == 0:
                                        counter[mat["name"]] += 1

            msg = ""
            if len(counter) > 0:
                emote = {x["name"]: x["emote"] for x in mine["items"]}
                tuples = counter.most_common()
                for entry in tuples:
                    msg += ", " + entry[0] + " x" + str(entry[1]) + emote[entry[0]]
                msg = msg[2:]
            else:
                msg = "Absolutely nothing"

            s=discord.Embed(colour=ctx.author.colour, description="You used your miners and gathered these materials: {}".format(msg)) 
            s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(embed=s)
            if len(counter) > 0:
                items = self.add_mats(authordata["items"].run(self.db), tuples)  
                authordata.update({"items": items, "minertime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft", noreply=True)
            else:
                authordata.update({"minertime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft", noreply=True)
        else:
            time = dateify.get(authordata["minertime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 7200)
            if ctx.message.created_at.timestamp() - authordata["minertime"].run(self.db, durability="soft") <= 7200:
                await ctx.send("You are too early, come back to your miner in {}".format(time))
                return
            else:
                counter = Counter()
                for miner in shop["miners"]:
                    for item in authordata["items"].run(self.db, durability="soft"):
                        if item["name"] == miner["name"]:
                            for x in range(item["amount"]):
                                for x in range(miner["max_mats"]):
                                    for mat in mine["items"]:
                                        if round(mat["rand_max"] * miner["multiplier"]) <= 0:
                                            number = 1
                                        else:
                                            number = round(mat["rand_max"] * miner["multiplier"])
                                        if randint(0, number) == 0:
                                            counter[mat["name"]] += 1

                msg = ""
                if len(counter) > 0:
                    emote = {x["name"]: x["emote"] for x in mine["items"]}
                    tuples = counter.most_common()
                    for entry in tuples:
                        msg += ", " + entry[0] + " x" + str(entry[1]) + emote[entry[0]]
                    msg = msg[2:]
                else:
                    msg = "Absolutely nothing"

                s=discord.Embed(colour=ctx.author.colour, description="You used your miners and gathered these materials: {}".format(msg)) 
                s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

                await ctx.send(embed=s)
                if len(counter) > 0:
                    items = self.add_mats(authordata["items"].run(self.db), tuples)
                    authordata.update({"items": items, "minertime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft", noreply=True)
                else:
                    authordata.update({"minertime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft", noreply=True)

    @commands.group(name="pickaxe", aliases=["pick"])
    async def _pickaxe_(self, ctx):
        """Some commands where you can buy and view pickaxes"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @_pickaxe_.command(name="buy")
    async def buy____(self, ctx, *, item: str):
        """Buy a pickaxe from the pickaxe shop"""
        pickaxe = self.get_item(shop["picitems"], item)
        if not pickaxe:
            return await ctx.send("I could not find that pickaxe :no_entry:")
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))   
        if pickaxe["price"]:
            if self.has_pickaxe(author):
                return await ctx.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                    
            author_data = authordata.run(self.db, durability="soft")
                    
            if author_data["balance"] >= pickaxe["price"]:
                items = self.add_mats(author_data["items"], [(pickaxe["name"], 1)], {"upgrades": 0, "multiplier": pickaxe["multiplier"], "rand_min": pickaxe["rand_min"], "rand_max": pickaxe["rand_max"], "durability": pickaxe["durability"], "price": pickaxe["price"]})
                authordata.update({"balance": r.row["balance"] - pickaxe["price"], "items": items, "pickdur": pickaxe["durability"]}).run(self.db, durability="soft")
                            
                return await ctx.send("You just bought a {} for **${:,}** :ok_hand:".format(pickaxe["name"], pickaxe["price"]))
            else:
                return await ctx.send("You don't have enough money to buy that item :no_entry:")
        else:
            return await ctx.send("This pickaxe is not buyable :no_entry:")
    
    @_pickaxe_.command(name="shop")
    async def shop____(self, ctx):
        """View all the available pickaxes"""
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Sx4 shop use your currency in Sx4 to buy pickaxes", colour=0xfff90d)
        s.set_author(name="Shop", icon_url=self.bot.user.avatar_url)
        for item in shop["picitems"]:
            s.add_field(name=item["name"], value="Price: {}\nCraft: {}\nDurability: {}".format("${:,}".format(item["price"]) if item["price"] else "Not Buyable", "\n".join(["{} {}".format(x[1], x[0]) for x in item["craft"]]) if item["craft"] else "Not Craftable", item["durability"]))
        try:    
            s.set_footer(text="Use s?pickaxe buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run(self.db, durability="soft")))
        except:
            s.set_footer(text="Use s?pickaxe buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @_pickaxe_.command(name="info")
    async def __info(self, ctx, *, user: str=None):
        """Displays your or another users pickaxe if you have one"""
        if not user:
            user = ctx.author 
        else:
            user = arg.get_server_member(ctx, user)
            if not user:
                return await ctx.send("I could not find that user :no_entry:")
        
        userdata = r.table("bank").get(str(user.id))
        if userdata.run(self.db):
            if self.has_pickaxe(user):
                item = self.get_user_pickaxe(user)
                if "upgrades" not in item:
                    pick = self.get_exact_item(shop["picitems"], item["name"])
                    item.update({"upgrades": 0, "rand_min": pick["rand_min"], "rand_max": pick["rand_max"], "durability": pick["durability"], "multiplier": pick["multiplier"], "price": pick["price"]})
                s=discord.Embed(colour=user.colour)
                s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                s.add_field(name="Durability", value="{}/{}".format(userdata["pickdur"].run(self.db, durability="soft"), item["durability"]), inline=False)
                s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * userdata["pickdur"].run(self.db, durability="soft"))), inline=False)
                s.add_field(name="Original Price", value= "$" + str(item["price"]), inline=False)
                s.add_field(name="Upgrades", value=item["upgrades"], inline=False)
                s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/131/pick_26cf.png")
                await ctx.send(embed=s)
            else:
                await ctx.send("That user does not have a pickaxe :no_entry:")
        else:
            await ctx.send("That user does not have a pickaxe :no_entry:")      
        
    @commands.group(usage="<sub command>")
    async def repair(self, ctx):
        """Repair your pickaxe/rod/axe with resources"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @repair.command(name="pickaxe", aliases=["pick"])
    async def __pickaxe(self, ctx, durability: int=None):
        """Repair your pickaxe with materials you currently have"""
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))   
        def repair(m):
            return m.author == ctx.author and m.channel == ctx.channel
        item = self.get_user_pickaxe(author)
        if not item:
            return await ctx.send("You do not own a pickaxe :no_entry:")
        if "upgrades" not in item:
            pick = self.get_exact_item(shop["picitems"], item["name"])
            item.update({"upgrades": 0, "rand_min": pick["rand_min"], "rand_max": pick["rand_max"], "durability": pick["durability"], "multiplier": pick["multiplier"], "price": pick["price"]})
        if not durability: 
            if authordata["pickdur"].run(self.db, durability="soft") >= item["durability"]:
                await ctx.send("You already have full durability on your pickaxe :no_entry:")
                return
            material = item["name"][:-8]
            for mat in mine["items"]:
                if material == mat["name"]:
                    calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * (item["durability"] - authordata["pickdur"].run(self.db, durability="soft")))
                    author_item = self.get_user_item(authordata["items"].run(self.db), material)
                    if calc > author_item["amount"]:
                        estimate = author_item["amount"]/((item["price"] / mat["price"]) / item["durability"])
                        await ctx.send("You do not have enough materials to fix this pickaxe, you would need `{} {}` to fix this pickaxe fully. You can approximatly fix this pickaxe by {} durability with your current materials :no_entry:".format(calc, material, math.floor(estimate)))
                    else:
                        msg = await ctx.send("It will cost you **{} {}** to fix your pickaxe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                        try:
                            response = await self.bot.wait_for("message", timeout=60, check=repair)
                        except asyncio.TimeoutError:
                            await msg.delete()
                            return
                        if response.content.lower() == "yes": 
                            await msg.delete()
                            user_items = authordata["items"].run(self.db, durability="soft")
                            if author_item["amount"] < calc:
                                estimate = author_item["amount"]/((item["price"] / mat["price"]) / item["durability"])
                                await ctx.send("You do not have enough materials to fix this pickaxe, you would need `{} {}` to fix this pickaxe fully. You can approximatly fix this pickaxe by {} durability with your current materials :no_entry:".format(calc, material, math.floor(estimate)))
                            user_items = self.remove_mats(user_items, [(material, calc)])
                            authordata.update({"items": user_items, "pickdur": item["durability"]}).run(self.db, durability="soft")
                            await ctx.send("You have repaired your pickaxe to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], item["durability"]))
                        else:
                            await msg.delete()
                    return
            await ctx.send("You cannot repair this pickaxe :no_entry:")
        else:
            if authordata["pickdur"].run(self.db, durability="soft") >= item["durability"]:
                await ctx.send("You already have full durability on your pickaxe :no_entry:")
                return
            material = item["name"][:-8]
            for mat in mine["items"]:
                if material == mat["name"]:
                    calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * durability)
                    author_item = self.get_user_item(authordata["items"].run(self.db), material)
                    if calc > author_item["amount"]:
                        await ctx.send("You do not have enough materials to fix this pickaxe, you need `{} {}` to get an extra {} durability :no_entry:".format(calc, material, durability))
                    else:
                        msg = await ctx.send("It will cost you **{} {}** to fix your pickaxe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                        try:
                            response = await self.bot.wait_for("message", timeout=60, check=repair)
                        except asyncio.TimeoutError:
                            await msg.delete()
                            return
                        if response.content.lower() == "yes": 
                            await msg.delete()
                            user_items = authordata["items"].run(self.db, durability="soft")
                            if author_item["amount"] < calc:
                                return await ctx.send("You do not have enough materials to fix this pickaxe :no_entry:")
                            user_items = self.remove_mats(user_items, [(material, calc)])
                            authordata.update({"items": user_items, "pickdur": r.row["pickdur"] + durability}).run(self.db, durability="soft")
                            await ctx.send("You have repaired your pickaxe. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], authordata["pickdur"].run(self.db, durability="soft")))
                        else:
                            await msg.delete()
                    return
            await ctx.send("You cannot repair this pickaxe :no_entry:")
        
    @repair.command(name="axe")
    async def _axe_(self, ctx, durability: int=None):
        """Repair your axe with materials you currently have"""
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))   
        def repair(m):
            return m.author == ctx.author and m.channel == ctx.channel
        item = self.get_user_axe(author)
        if not item:
            return await ctx.send("You do not own a axe :no_entry:")
        if "upgrades" not in item:
            axe = self.get_exact_item(shop["axes"], item["name"])
            item.update({"upgrades": 0, "durability": axe["durability"], "price": axe["price"]})
        if not durability: 
            if authordata["axedur"].run(self.db, durability="soft") >= item["durability"]:
                await ctx.send("You already have full durability on your axe :no_entry:")
                return
            material = item["name"][:-4]
            for mat in mine["items"]:
                if material == mat["name"]:
                    calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * (item["durability"] - authordata["axedur"].run(self.db, durability="soft")))
                    author_item = self.get_user_item(authordata["items"].run(self.db), material)
                    if calc > author_item["amount"]:
                        estimate = author_item["amount"]/((item["price"] / mat["price"]) / item["durability"])
                        await ctx.send("You do not have enough materials to fix this axe, you would need `{} {}` to fix this axe fully. You can approximatly fix this axe by {} durability with your current materials :no_entry:".format(calc, material, math.floor(estimate)))
                    else:
                        msg = await ctx.send("It will cost you **{} {}** to fix your axe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                        try:
                            response = await self.bot.wait_for("message", timeout=60, check=repair)
                        except asyncio.TimeoutError:
                            await msg.delete()
                            return
                        if response.content.lower() == "yes": 
                            await msg.delete()
                            user_items = authordata["items"].run(self.db, durability="soft")
                            if author_item["amount"] < calc:
                                estimate = author_item["amount"]/((item["price"] / mat["price"]) / item["durability"])
                                await ctx.send("You do not have enough materials to fix this axe, you would need `{} {}` to fix this axe fully. You can approximatly fix this axe by {} durability with your current materials :no_entry:".format(calc, material, math.floor(estimate)))
                            user_items = self.remove_mats(user_items, [(material, calc)])
                            authordata.update({"items": user_items, "axedur": item["durability"]}).run(self.db, durability="soft")
                            await ctx.send("You have repaired your axe to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], item["durability"]))
                        else:
                            await msg.delete()
                    return
            await ctx.send("You cannot repair this axe :no_entry:")
        else:
            if authordata["axedur"].run(self.db, durability="soft") >= item["durability"]:
                await ctx.send("You already have full durability on your axe :no_entry:")
                return
            material = item["name"][:-4]
            for mat in mine["items"]:
                if material == mat["name"]:
                    calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * durability)
                    author_item = self.get_user_item(authordata["items"].run(self.db), material)
                    if calc > author_item["amount"]:
                        await ctx.send("You do not have enough materials to fix this axe, you need `{} {}` to get an extra {} durability :no_entry:".format(calc, material, durability))
                    else:
                        msg = await ctx.send("It will cost you **{} {}** to fix your axe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                        try:
                            response = await self.bot.wait_for("message", timeout=60, check=repair)
                        except asyncio.TimeoutError:
                            await msg.delete()
                            return
                        if response.content.lower() == "yes": 
                            await msg.delete()
                            user_items = authordata["items"].run(self.db, durability="soft")
                            if author_item["amount"] < calc:
                                return await ctx.send("You do not have enough materials to fix this axe :no_entry:")
                            user_items = self.remove_mats(user_items, [(material, calc)])
                            authordata.update({"items": user_items, "axedur": r.row["axedur"] + durability}).run(self.db, durability="soft")
                            await ctx.send("You have repaired your axe. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], authordata["axedur"].run(self.db, durability="soft")))
                        else:
                            await msg.delete()
                    return
            await ctx.send("You cannot repair this axe :no_entry:")    

    @repair.command(name="fishingrod", aliases=["rod"])
    async def __fishingrod(self, ctx, durability: int=None):
        """Repair your rod with materials you currently have"""
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))   
        def repair(m):
            return m.author == ctx.author and m.channel == ctx.channel
        item = self.get_user_rod(author)
        if not item:
            return await ctx.send("You do not own a rod :no_entry:")
        if "upgrades" not in item:
            rod = self.get_exact_item(shop["roditems"], item["name"])
            item.update({"upgrades": 0, "rand_min": rod["rand_min"], "rand_max": rod["rand_max"], "durability": rod["durability"], "price": rod["price"]})
        if not durability: 
            if authordata["roddur"].run(self.db, durability="soft") >= item["durability"]:
                await ctx.send("You already have full durability on your rod :no_entry:")
                return
            material = item["name"][:-4]
            for mat in mine["items"]:
                if material == mat["name"]:
                    calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * (item["durability"] - authordata["roddur"].run(self.db, durability="soft")))
                    author_item = self.get_user_item(authordata["items"].run(self.db), material)
                    if calc > author_item["amount"]:
                        estimate = author_item["amount"]/((item["price"] / mat["price"]) / item["durability"])
                        await ctx.send("You do not have enough materials to fix this rod, you would need `{} {}` to fix this rod fully. You can approximatly fix this rod by {} durability with your current materials :no_entry:".format(calc, material, math.floor(estimate)))
                    else:
                        msg = await ctx.send("It will cost you **{} {}** to fix your rod in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                        try:
                            response = await self.bot.wait_for("message", timeout=60, check=repair)
                        except asyncio.TimeoutError:
                            await msg.delete()
                            return
                        if response.content.lower() == "yes": 
                            await msg.delete()
                            user_items = authordata["items"].run(self.db, durability="soft")
                            if author_item["amount"] < calc:
                                estimate = author_item["amount"]/((item["price"] / mat["price"]) / item["durability"])
                                await ctx.send("You do not have enough materials to fix this rod, you would need `{} {}` to fix this rod fully. You can approximatly fix this rod by {} durability with your current materials :no_entry:".format(calc, material, math.floor(estimate)))
                            user_items = self.remove_mats(user_items, [(material, calc)])
                            authordata.update({"items": user_items, "roddur": item["durability"]}).run(self.db, durability="soft")
                            await ctx.send("You have repaired your rod to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], item["durability"]))
                        else:
                            await msg.delete()
                    return
            await ctx.send("You cannot repair this rod :no_entry:")
        else:
            if authordata["roddur"].run(self.db, durability="soft") >= item["durability"]:
                await ctx.send("You already have full durability on your rod :no_entry:")
                return
            material = item["name"][:-4]
            for mat in mine["items"]:
                if material == mat["name"]:
                    calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * durability)
                    author_item = self.get_user_item(authordata["items"].run(self.db), material)
                    if calc > author_item["amount"]:
                        await ctx.send("You do not have enough materials to fix this rod, you need `{} {}` to get an extra {} durability :no_entry:".format(calc, material, durability))
                    else:
                        msg = await ctx.send("It will cost you **{} {}** to fix your rod in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                        try:
                            response = await self.bot.wait_for("message", timeout=60, check=repair)
                        except asyncio.TimeoutError:
                            await msg.delete()
                            return
                        if response.content.lower() == "yes": 
                            await msg.delete()
                            user_items = authordata["items"].run(self.db, durability="soft")
                            if author_item["amount"] < calc:
                                return await ctx.send("You do not have enough materials to fix this rod :no_entry:")
                            user_items = self.remove_mats(user_items, [(material, calc)])
                            authordata.update({"items": user_items, "roddur": r.row["roddur"] + durability}).run(self.db, durability="soft")
                            await ctx.send("You have repaired your rod. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], authordata["roddur"].run(self.db, durability="soft")))
                        else:
                            await msg.delete()
                    return
            await ctx.send("You cannot repair this rod :no_entry:")     
        
    @commands.command()
    async def give(self, ctx, user: discord.Member, amount):
        """Give someone some money"""
        author = ctx.author
        if user in filter(lambda m: m.bot and m != self.bot.user, self.bot.get_all_members()):
            await ctx.send("Bots can't make money :no_entry:")
            return
        self._set_bank(author)
        self._set_bank(user)
        authordata = r.table("bank").get(str(author.id))
        userdata = r.table("bank").get(str(user.id))
        taxdata = r.table("tax").get("tax")
        if user == author:
            await ctx.send("You can't give yourself money :no_entry:")
            return
        if amount.lower() == "all":
            amount = authordata["balance"].run(self.db, durability="soft")
        else:
            try:
                amount = int(amount)
            except:
                return await ctx.send("Invalid amount :no_entry:")
        if amount > authordata["balance"].run(self.db, durability="soft"):
            await ctx.send("You don't have that much money to give :no_entry:")
            return
        if amount < 1:
            await ctx.send("You can't give them less than a dollar, too mean :no_entry:")
            return
        fullamount = amount
        if self.bot.user != user:
            amount = fullamount if "Tax Avoider" in map(lambda x: x["name"], authordata["items"].run(self.db, durability="soft")) else round(amount * 0.95)
            tax = fullamount - amount
            userdata.update({"balance": r.row["balance"] + amount}).run(self.db, durability="soft")
        else:
            tax = fullamount
            amount = fullamount
        taxdata.update({"tax": r.row["tax"] + tax}).run(self.db, durability="soft")
        authordata.update({"balance": r.row["balance"] - fullamount}).run(self.db, durability="soft")
        if "Tax Avoider" in map(lambda x: x["name"], authordata["items"].run(self.db, durability="soft")):
            list = authordata["items"].run(self.db, durability="soft")
            list = self.remove_mats(list, [("Tax Avoider", 1)])
            authordata.update({"items": list}).run(self.db, durability="soft")
        s=discord.Embed(description="You have gifted **${:,}** to **{}**\n\n{}'s new balance: **${:,}**\n{}'s new balance: **${:,}**".format(amount, user.name, author.name, authordata["balance"].run(self.db, durability="soft"), user.name, userdata["balance"].run(self.db, durability="soft") if user != self.bot.user else taxdata["tax"].run(self.db, durability="soft")), colour=author.colour)
        s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://cdn0.iconfinder.com/data/icons/social-messaging-ui-color-shapes/128/money-circle-green-3-512.png")
        s.set_footer(text="{}".format("${:,} ({}%) tax was taken".format(tax, round((tax/fullamount)*100))))
        await ctx.send(embed=s)
		
    @commands.command(aliases=["givemats"])
    async def givematerials(self, ctx, user: discord.Member, amount: int, *, item: str):
        """Give materials to another user (you are taxed 5% of the worth of the materials you are giving)"""
        author = ctx.author
        if user.bot:
            await ctx.send("Bots can't get items :no_entry:")
            return
        self._set_bank(author)
        self._set_bank(user)    
        authordata = r.table("bank").get(str(author.id))
        userdata = r.table("bank").get(str(user.id))
        factories2 = factories_all["factory"]
        items = []
        for x in factories2:
            items.append({"name": x["name"], "price": x["price"]*(list(filter(lambda y: y["name"] == x["item"], mine_all["items"]))[0]["price"])})
        allowed_items = shop["miners"] + mine_all["items"] + shop["crates"] + items + shop["boosters"] + wood["wood"]
        actual_item = self.get_item(allowed_items, item)
        if not actual_item:
            return await ctx.send("That item is not transferrable/doesn't exist :no_entry:")
        author_item = self.get_user_item(authordata["items"].run(self.db), actual_item["name"])
        user_item = self.get_user_item(userdata["items"].run(self.db), actual_item["name"])
        price_item = amount * actual_item["price"]
        tax = round(price_item * 0.05)
        if user == author:
            return await ctx.send("You can't give yourself items :no_entry:")
        if author_item["amount"] >= amount:
            if tax > authordata["balance"].run(self.db):
                return await ctx.send("You cannot afford the tax when transferring these items, the tax would be **${:,}** :no_entry:".format(tax))
            usercount = user_item["amount"] + amount
            authorcount = author_item["amount"] - amount
            s=discord.Embed(description="You have gifted **{} {}** to **{}**\n\n{}'s new {} amount: **{} {}**\n{}'s new {} amount: **{} {}**".format(amount, actual_item["name"], user.name, author.name, actual_item["name"], authorcount, actual_item["name"], user.name, actual_item["name"], usercount, actual_item["name"]), colour=author.colour)
            s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://cdn0.iconfinder.com/data/icons/social-messaging-ui-color-shapes/128/money-circle-green-3-512.png")
            s.set_footer(text="Tax: ${:,} ({}%)".format(tax, round((tax/price_item)*100)))
            await ctx.send(embed=s)
            author_items = authordata["items"].run(self.db, durability="soft")
            user_items = userdata["items"].run(self.db, durability="soft")
            author_items = self.remove_mats(author_items, [(actual_item["name"], amount)])
            user_items = self.add_mats(user_items, [(actual_item["name"], amount)])
            authordata.update({"items": author_items, "balance": r.row["balance"] - tax}).run(self.db, durability="soft")
            userdata.update({"items": user_items}).run(self.db, durability="soft")
            r.table("tax").get("tax").update({"tax": r.row["tax"] + tax}).run(self.db, durability="soft")
        else:
            await ctx.send("You don't have enough `{}` to give :no_entry:".format(actual_item["name"]))
                

    @commands.command(aliases=["roulette", "rusr"])
    async def russianroulette(self, ctx, bullets: int, bet: int):
        """Risk your money with a revolver to your head with a certain amount of bullets in it, if you get shot you lose if not you win"""
        author = ctx.author
        server = ctx.guild
        self._set_bank(author)
        authordata = r.table("bank").get(str(author.id))
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if bet < 20:
            await ctx.send("This game requires $20 to play :no_entry:")
            return
        if authordata["balance"].run(self.db, durability="soft") < bet:
            await ctx.send("You don't have that amount to bet :no_entry:")
            return
        if bullets <= 0:
            await ctx.send("Invalid number of bullets :no_entry:")
            return
        if bullets >= 6:
            await ctx.send("Invalid number of bullets :no_entry:")
            return
        authordata.update({"balance": r.row["balance"] - bet, "winnings": r.row["winnings"] - bet}).run(self.db, durability="soft")
        rr = randint(1, 6)
        winnings = math.ceil((5.7 * bet)/(6 - bullets))
        if bullets >= rr:
            s=discord.Embed(description="You were shot :gun:\nYou lost your bet of **${:,}**".format(bet), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        else:
            authordata.update({"balance": r.row["balance"] + winnings, "winnings": r.row["winnings"] + winnings}).run(self.db, durability="soft")
            s=discord.Embed(description="You're lucky, you get to live another day.\nYou Won **${:,}**".format(winnings), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)

    @commands.group(usage="<sub command>")
    async def upgrade(self, ctx):
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @upgrade.command(name="shop")
    async def __shop___(self, ctx):
        """View the upgrades compatible with certain items and their prices"""
        authordata = r.table("bank").get(str(ctx.author.id)).run(self.db)
        if self.has_pickaxe(ctx.author):
            pick = self.get_user_pickaxe(ctx.author)
            pickaxe = self.get_exact_item(shop["picitems"], pick["name"])
            if "upgrades" not in pick:
                pick.update({"upgrades": 0, "rand_min": pickaxe["rand_min"], "rand_max": pickaxe["rand_max"], "durability": pickaxe["durability"], "multiplier": pickaxe["multiplier"], "price": pickaxe["price"]})
            pickprice = "${:,}".format(round((pickaxe["price"] * 0.025) + (pick["upgrades"] * (pickaxe["price"] * 0.015))))
        else:
            pickprice = "Unknown"
        if self.has_rod(ctx.author):
            rod = self.get_user_rod(ctx.author)
            rodd = self.get_exact_item(shop["roditems"], rod["name"])
            if "upgrades" not in rod:
                rod.update({"upgrades": 0, "rand_min": rodd["rand_min"], "rand_max": rodd["rand_max"], "durability": rodd["durability"], "price": rodd["price"]})
            rodprice = "${:,}".format(round((rodd["price"] * 0.025) + (rod["upgrades"] * (rodd["price"] * 0.015))))
        else:
            rodprice = "Unknown"
        if self.has_axe(ctx.author):
            axe = self.get_user_axe(ctx.author)
            axee = self.get_exact_item(shop["axes"], axe["name"])
            if "upgrades" not in axe:
                axe.update({"upgrades": 0, "max_mats": axee["max_mats"], "durability": axee["durability"], "multiplier": axee["multiplier"], "price": axee["price"]})
            axeprice = "${:,}".format(round((axee["price"] * 0.025) + (axe["upgrades"] * (axee["price"] * 0.015))))
        else:
            axeprice = "Unknown"
        s=discord.Embed(colour=0xffff00)
        s.set_author(name="Upgrades", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Pickaxe", value="__Multiplier__\nDescription: Multiplier upgrades increase your chance to get better materials per mine.\nPrice: {0}\n\n"
        "__Money__\nDescription: Money upgrades your minimum yield and maximum yield of money from your pickaxe by 1% the worth of the original minimum yield.\nPrice: {0}\n\n"
        "__Durability__\nDescription: Durability upgrades your max pickaxe durability by 2.\nPrice: {0}".format(pickprice))
        s.add_field(name="Rod", value="__Money__\nDescription: Money upgrades your minimum yield and maximum yield of money from your rod by 1% the worth of the original minimum yield.\nPrice: {0}\n\n"
        "__Durability__\nDescription: Durability upgrades your max rod durability by 2.\nPrice: {0}".format(rodprice))
        s.add_field(name="Axe", value="__Multiplier__\nDescription: Multiplier upgrades increase your chance to get better materials per chop.\nPrice: {0}\n\n"
        "__Durability__\nDescription: Durability upgrades your max axe durability by 2.\nPrice: {0}".format(axeprice))
        s.set_footer(text="Use s?upgrade <item_type> <upgrade> to upgrade your item")
        await ctx.send(embed=s)

    @upgrade.command(name="pickaxe", aliases=["pick"])
    async def _pickaxe(self, ctx, *, upgrade: str):
        """Upgrrade your pickaxe"""
        authordata = r.table("bank").get(str(ctx.author.id))
        user_pickaxe = self.get_user_pickaxe(ctx.author)
        items = authordata["items"].run(self.db)
        if not user_pickaxe or not authordata.run(self.db):
            return await ctx.send("You do not own a pickaxe you can upgrade :no_entry:")
        shop_pickaxe = self.get_exact_item(shop["picitems"], user_pickaxe["name"])
        price = round((shop_pickaxe["price"] * 0.025) + ((user_pickaxe["upgrades"] if "upgrades" in user_pickaxe else 0) * (shop_pickaxe["price"] * 0.015)))
        if authordata["balance"].run(self.db) < price:
            return await ctx.send("You cannot afford your pickaxes next upgrade you need ${:,} to be able to upgrade your pickaxe :no_entry:".format(price))
        if "upgrades" not in user_pickaxe:
            updated = {"upgrades": 0, "rand_min": shop_pickaxe["rand_min"], "rand_max": shop_pickaxe["rand_max"], "durability": shop_pickaxe["durability"], "multiplier": shop_pickaxe["multiplier"], "price": shop_pickaxe["price"]}
            items = self.update_item(items, user_pickaxe["name"], updated)
            user_rod.update(updated)
        if upgrade.lower() == "money":
            items = self.upgrade_item(items, user_pickaxe, {"rand_min": round(shop_pickaxe["rand_min"] * 0.02), "rand_max": round(shop_pickaxe["rand_min"] * 0.02), "upgrades": 1, "price": shop_pickaxe["price"] * 0.015})
        elif upgrade.lower() == "durability":
            items = self.upgrade_item(items, user_pickaxe, {"durability": 2, "upgrades": 1, "price": shop_pickaxe["price"] * 0.015})
            authordata.update({"pickdur": r.row["pickdur"] + 2}).run(self.db, durability="soft", noreply=True)
        elif upgrade.lower() == "multiplier":
            items = self.upgrade_item(items, user_pickaxe, {"multiplier": shop_pickaxe["multiplier"] * 0.01, "upgrades": 1, "price": shop_pickaxe["price"] * 0.015})
        else: 
            return await ctx.send("That is not a valid upgrade for your pickaxe :no_entry:")
        authordata.update({"items": items, "balance": r.row["balance"] - price}).run(self.db, durability="soft")
        await ctx.send("You just upgraded your {} for your `{}` for **${:,}** :ok_hand:".format(upgrade.title(), user_pickaxe["name"], price))

    @upgrade.command(name="fishingrod", aliases=["rod"])
    async def _fishingrod(self, ctx, *, upgrade: str):
        """Upgrade your fishing rod"""
        authordata = r.table("bank").get(str(ctx.author.id))
        user_rod = self.get_user_rod(ctx.author)
        if not user_rod or not authordata["items"].run(self.db):
            return await ctx.send("You do not have a rod :no_entry:")
        shop_rod = self.get_exact_item(shop["roditems"], user_rod["name"])
        items = authordata["items"].run(self.db)
        if not user_rod or not authordata.run(self.db):
            return await ctx.send("You do not own a rod you can upgrade :no_entry:")
        price = round((shop_rod["price"] * 0.025) + ((user_rod["upgrades"] if "upgrades" in user_rod else 0) * (shop_rod["price"] * 0.015)))
        if authordata["balance"].run(self.db) < price:
            return await ctx.send("You cannot afford your rods next upgrade you need ${:,} to be able to upgrade your rod :no_entry:".format(price))
        if "upgrades" not in user_rod:
            updated = {"upgrades": 0, "rand_min": round(shop_rod["rand_min"] * 0.02), "rand_max": round(shop_rod["rand_min"] * 0.02), "durability": shop_rod["durability"], "price": shop_rod["price"]}
            items = self.update_item(items, user_rod["name"], updated)
            user_rod.update(updated)
        if upgrade.lower() == "money":
            items = self.upgrade_item(items, user_rod, {"rand_min": round(shop_rod["rand_min"] * 0.02), "rand_max": round(shop_rod["rand_min"] * 0.02), "upgrades": 1, "price": shop_rod["price"] * 0.015})
        elif upgrade.lower() == "durability":
            items = self.upgrade_item(items, user_rod, {"durability": 2, "upgrades": 1, "price": shop_rod["price"] * 0.015})
            authordata.update({"roddur": r.row["roddur"] + 2}).run(self.db, durability="soft", noreply=True)
        else: 
            return await ctx.send("That is not a valid upgrade for your rod :no_entry:")
        authordata.update({"items": items, "balance": r.row["balance"] - price}).run(self.db, durability="soft")
        await ctx.send("You just upgraded your {} for your `{}` for **${:,}** :ok_hand:".format(upgrade.title(), user_rod["name"], price))

    @upgrade.command(name="axe")
    async def _axe(self, ctx, *, upgrade: str):
        """Upgrade your axe"""
        authordata = r.table("bank").get(str(ctx.author.id))
        user_axe = self.get_user_axe(ctx.author)
        items = authordata["items"].run(self.db)
        if not user_axe or not authordata.run(self.db):
            return await ctx.send("You do not own a axe you can upgrade :no_entry:")
        shop_axe = self.get_exact_item(shop["axes"], user_axe["name"])
        price = round((shop_axe["price"] * 0.025) + ((user_axe["upgrades"] if "upgrades" in user_axe else 0) * (shop_axe["price"] * 0.015)))
        if authordata["balance"].run(self.db) < price:
            return await ctx.send("You cannot afford your axes next upgrade you need ${:,} to be able to upgrade your axe :no_entry:".format(price))
        if "upgrades" not in user_axe:
            updated = {"upgrades": 0, "durability": shop_axe["durability"], "multiplier": shop_axe["multiplier"], "price": shop_axe["price"], "max_mats": shop_axe["max_mats"]}
            items = self.update_item(items, user_axe["name"], updated)
            user_axe.update(updated)
        if upgrade.lower() == "durability":
            items = self.upgrade_item(items, user_axe, {"durability": 2, "upgrades": 1, "price": shop_axe["price"] * 0.015})
            authordata.update({"axedur": r.row["axedur"] + 2}).run(self.db, durability="soft", noreply=True)
        elif upgrade.lower() == "multiplier":
            items = self.upgrade_item(items, user_axe, {"multiplier": shop_axe["multiplier"] * 0.01, "upgrades": 1, "price": shop_axe["price"] * 0.015})
        else: 
            return await ctx.send("That is not a valid upgrade for your axe :no_entry:")
        authordata.update({"items": items, "balance": r.row["balance"] - price}).run(self.db, durability="soft")
        await ctx.send("You just upgraded your {} for your `{}` for **${:,}** :ok_hand:".format(upgrade.title(), user_axe["name"], price))

    @commands.group(usage="<sub command>")
    async def factory(self, ctx):
        """Factorys you can buy with resources"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @factory.command(aliases=["buy"])
    async def purchase(self, ctx, *, factory_name):
        """Buy a factory with your resources gained by mining"""
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))
        if factory_name.lower() == "all":
            bought = []
            author_items = authordata["items"].run(self.db)
            for x in factories["factory"]:
                user_item = self.get_user_item(author_items, x["item"])
                buyable = math.floor(user_item["amount"]/x["price"])
                if buyable >= 1:
                    bought.append((x["name"], buyable))
                    author_items = self.remove_mats(author_items, [(x["item"], x["price"] * buyable)])
            if not bought:
                return await ctx.send("You are not able to buy any factories :no_entry:")
            else:
                await ctx.send("With all your materials you have bought:\n{}".format("\n".join(["`{} {}`".format(x[1], x[0]) for x in bought])))
                author_items = self.add_mats(author_items, bought)
                authordata.update({"items": author_items}).run(self.db, durability="soft")
        else:
            factory_name, amount = self.convert(factory_name)
            item = self.get_item(factories["factory"], factory_name)
            if not item:
                return await ctx.send("That is not a valid factory :no_entry:")
            for item2 in authordata["items"].run(self.db, durability="soft"):              
                if item["item"] == item2["name"]:
                    itemamount = item2["amount"]
                    if item["price"] * amount <= itemamount:
                        await ctx.send("You just bought `{} {}`".format(amount, item["name"]))
                        author_items = authordata["items"].run(self.db, durability="soft")
                        author_items = self.remove_mats(author_items, [(item2["name"], item["price"] * amount)])
                        author_items = self.add_mats(author_items, [(item["name"], amount)])
                        authordata.update({"items": author_items}).run(self.db, durability="soft")
                        return
                    else:
                        return await ctx.send("You don't have enough `{}` to buy this :no_entry:".format(item2["name"]))  

                        
    @factory.command(aliases=["shop"]) 
    async def market(self, ctx):
        """View factorys you can buy"""
        author = ctx.author
        s=discord.Embed(description="You can buy factories using materials you have gathered", colour=0xfff90d)
        s.set_author(name="Factories", icon_url=self.bot.user.avatar_url)
        authordata = r.table("bank").get(str(author.id))
        
        for item2 in mine["items"]:
            for item in factories["factory"]:
                sortedfactory = sorted(factories["factory"], key=lambda x: (x["price"] * item2["price"]), reverse=True)
        for x in sortedfactory:
            user_item = self.get_user_item(authordata["items"].run(self.db), x["item"])
            s.add_field(name=x["name"], value="Price: {}/{} {} ({})".format(user_item["amount"], str(x["price"]), x["item"], math.floor(user_item["amount"]/x["price"])))
             
        s.set_footer(text="Use s?factory purchase <factory> to buy a factory.")
        
        await ctx.send(embed=s)
        
    @factory.command()
    async def collect(self, ctx):
        """If you have a factory or mutliple use this to collect your money from them every 12 hours"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        
        authordata = r.table("bank").get(str(author.id))
        number = 0
        has_factory = False
        for item_ in authordata["items"].run(self.db, durability="soft"):
            for _item in factories_all["factory"]:
                if  _item["name"] == item_["name"]:
                    has_factory = True
                    break
        if not has_factory:
            await ctx.send("You do not own a factory :no_entry:")
            return
        if not authordata["factorytime"].run(self.db, durability="soft"):
            for item in authordata["items"].run(self.db, durability="soft"):
                for item2 in factories_all["factory"]:
                    if item2["name"] == item["name"]:
                        for x in range(item["amount"]):
                            number += randint(item2["rand_min"], item2["rand_max"])
            authordata.update({"factorytime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + number}).run(self.db, durability="soft", noreply=True)
            s=discord.Embed(description="Your factories made you **${:,}** today".format(number), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        if ctx.message.created_at.timestamp() - authordata["factorytime"].run(self.db, durability="soft") <= 43200:
            time = dateify.get(authordata["factorytime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 43200)
            await ctx.send("You are too early, come back to your factory in {}".format(time))
            return
        else:
            for item in authordata["items"].run(self.db, durability="soft"):
                for item2 in factories_all["factory"]:
                    if item2["name"] == item["name"]:
                        for x in range(item["amount"]):
                            number += randint(item2["rand_min"], item2["rand_max"])
            authordata.update({"factorytime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + number}).run(self.db, durability="soft", noreply=True)
            s=discord.Embed(description="Your factories made you **${:,}** today".format(number), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
    @commands.group(usage="<sub command>")
    async def auction(self, ctx):
        """The Sx4 Auction house"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            pass
        
    @auction.command()
    async def refund(self, ctx):
        """Refund an item you've put on the auction house"""
        author = ctx.author
        self._set_bank(author)
        auctiondata = r.table("auction")
        authordata = r.table("bank").get(str(author.id))
        filtered = auctiondata.filter({"ownerid": str(author.id)}).run(self.db, durability="soft")
        filtered = sorted(filtered, key=lambda x: x["price"])
        if not filtered:
            await ctx.send("You have no items for sale on the auction house :no_entry:")
            return
        server = ctx.guild
        channel = ctx.channel
        author = ctx.author
            
        event = await paged.page(ctx, filtered, selectable=True, per_page=5, function=lambda item: "\n**Name:** " + item["item"]["name"] + "\n**Price:** ${:,}".format(int(item["price"])) + "\n" + ("**Durability:** {}".format(item["durability"]) + ("/{}\n".format(item["item"]["durability"]) if "durability" in item["item"] else "\n") if "durability" in item else "") + ("**Upgrades:** {}\n".format(item["item"]["upgrades"]) if "upgrades" in item["item"] else "") + ("**Amount:** " + str(item["item"]["amount"]) + "\n"))
        if event:
            item = event["object"]["item"]
            if self.get_exact_item(shop["picitems"], item["name"]):
                if self.has_pickaxe(ctx.author):
                    return await ctx.send("You already have a pickaxe :no_entry:")
            elif self.get_exact_item(shop["roditems"], item["name"]):
                if self.has_rod(ctx.author):
                    return await ctx.send("You already have a rod :no_entry:")
            elif self.get_exact_item(shop["axes"], item["name"]):
                if self.has_axe(ctx.author):
                    return await ctx.send("You already have an axe :no_entry:")
            if event["object"] not in auctiondata.run(self.db, durability="soft"):
                await ctx.send("That item was recently bought :no_entry:")
                return
            auctiondata.get(event["object"]["id"]).delete().run(self.db, durability="soft")
                
            if self.get_exact_item(shop["picitems"], item["name"]):
                authordata.update({"pickdur": event["object"]["durability"]}).run(self.db, durability="soft")
            elif self.get_exact_item(shop["roditems"], item["name"]):
                authordata.update({"roddur": event["object"]["durability"]}).run(self.db, durability="soft")
            elif self.get_exact_item(shop["axes"], item["name"]):
                authordata.update({"axedur": event["object"]["durability"]}).run(self.db, durability="soft")
                
            items = self.add_mats(authordata["items"].run(self.db), [(item["name"], item["amount"])], {x[0]: x[1] for x in item.items() if x[0] != "amount" and x[0] != "name"})
            authordata.update({"items": items}).run(self.db, durability="soft")
                    
            await ctx.send("You just refunded `{} {}`.".format(item["amount"], item["name"]))
        
    @auction.command()
    async def sell(self, ctx, item: str, price: int, amount: int=None):
        """Sell items on the auction house"""
        author = ctx.author
        if not amount:
            amount = 1
        if amount <= 0:
            await ctx.send("You can't sell no items, we're not ebay :no_entry:")
            return
        if price < 0:
            await ctx.send("You can't sell something for less than $0 :no_entry:")
            return
        self._set_bank(author)
        auctiondata = r.table("auction")
        authordata = r.table("bank").get(str(author.id))
        item3 = authordata["items"].run(self.db, durability="soft")
        all_items = shop["items"] + mine_all["items"] + shop["miners"] + shop["boosters"] + wood["wood"] + shop["crates"]
        for x in factories_all["factory"]:
            all_items.append({"name": x["name"], "price": x["price"]*(list(filter(lambda y: y["name"] == x["item"], mine_all["items"]))[0]["price"])})
        if item.lower() in map(lambda x: x["name"].lower(), item3):
            author_items = authordata["items"].run(self.db)
            if self.get_exact_item(shop["picitems"], item):
                final_item = self.get_exact_item(shop["picitems"], item)
                durability = authordata["pickdur"].run(self.db, durability="soft")
            elif self.get_exact_item(shop["roditems"], item):
                final_item = self.get_exact_item(shop["roditems"], item)
                durability = authordata["roddur"].run(self.db, durability="soft")
            elif self.get_exact_item(shop["axes"], item):
                final_item = self.get_exact_item(shop["axes"], item)
                durability = authordata["axedur"].run(self.db, durability="soft")
            else:
                final_item = self.get_exact_item(all_items, item)
                durability = None
            user_item = self.get_user_item(author_items, final_item["name"]) 
            user_item.update({"amount": amount})
            if user_item["amount"] < amount:
                await ctx.send("You don't have that amount of `{}` to sell :no_entry:".format(user_item["name"]))
                return            
            if (final_item["price"] * amount) / price > 20:
                return await ctx.send("You have to sell this item for at least 5% it's worth (**${:,}**)".format(round((final_item["price"] * (amount if amount else 1))/20)))
            name = final_item["name"]
            ownerid = str(author.id)
            list2 = authordata["items"].run(self.db, durability="soft")
            list2 = self.remove_mats(list2, [(name, amount)])
            authordata.update({"items": list2}).run(self.db, durability="soft")
            auctiondata.insert({"ownerid": ownerid, "price": str(price), "item": user_item, "durability": durability}).run(self.db, durability="soft")
            await ctx.send("Your item has been put on the auction house <:done:403285928233402378>")
        else:
            await ctx.send("You don't own that item :no_entry:")
            
    @auction.command()
    async def buy(self, ctx, *, auction_item: str):
        """Buy items on the auction house"""
        author = ctx.author
        self._set_bank(author)
        auctiondata = r.table("auction")
        authordata = r.table("bank").get(str(author.id))
        
        i = 0
        if self.get_exact_item(shop["picitems"], auction_item):
            if self.has_pickaxe(ctx.author):
                return await ctx.send("You already have a pickaxe :no_entry:")
        elif self.get_exact_item(shop["roditems"], auction_item):
            if self.has_rod(ctx.author):
                return await ctx.send("You already have a rod :no_entry:")
        elif self.get_exact_item(shop["axes"], auction_item):
            if self.has_axe(ctx.author):
                return await ctx.send("You already have an axe :no_entry:")
        filtered = filter(lambda x: x["item"]["name"].lower() == auction_item.lower(), auctiondata.run(self.db, durability="soft")) 
        filtered = sorted(filtered, key=lambda x: int(x["price"])/x["item"]["amount"])
        if not filtered:
            await ctx.send("There is no `{}` on the auction house :no_entry:".format(auction_item.title()))
            return
        server = ctx.guild
        channel = ctx.channel
        author = ctx.author

        event = await paged.page(ctx, filtered, selectable=True, per_page=5, function=lambda item: "\n**Name:** " + item["item"]["name"] + "\n**Price:** ${:,}".format(int(item["price"])) + "\n" + ("**Durability:** {}".format(item["durability"]) + ("/{}\n".format(item["item"]["durability"]) if "durability" in item["item"] else "\n") if "durability" in item else "") + ("**Upgrades:** {}\n".format(item["item"]["upgrades"]) if "upgrades" in item["item"] else "") + "**Price Per Item:** ${}\n".format(format(int(item["price"])/item["item"]["amount"], ".2f")) + ("**Amount:** {:,}".format(item["item"]["amount"]) + "\n"))
        if event:
            item = event["object"]["item"]
            if event["object"] not in auctiondata.run(self.db, durability="soft"):
                await ctx.send("That item was recently bought :no_entry:")
                return
            owner = discord.utils.get(self.bot.get_all_members(), id=int(event["object"]["ownerid"]))
            if owner:
                if owner == author:
                    await ctx.send("You can't buy your own items :no_entry:")
                    return
            if int(event["object"]["price"]) > authordata["balance"].run(self.db, durability="soft"):
                await ctx.send("You don't have enough money for that item :no_entry:")
                return
            auctiondata.get(event["object"]["id"]).delete().run(self.db, durability="soft")
            
            authordata.update({"balance": r.row["balance"] - int(event["object"]["price"])}).run(self.db, durability="soft")
            if owner:
                if r.table("bank").get(str(owner.id)).run(self.db, durability="soft"):
                    r.table("bank").get(str(owner.id)).update({"balance": r.row["balance"] + int(event["object"]["price"])}).run(self.db, durability="soft")
                
            if self.get_exact_item(shop["picitems"], item["name"]):
                authordata.update({"pickdur": event["object"]["durability"]}).run(self.db, durability="soft")
            elif self.get_exact_item(shop["roditems"], item["name"]):
                authordata.update({"roddur": event["object"]["durability"]}).run(self.db, durability="soft")
            elif self.get_exact_item(shop["axes"], item["name"]):
                authordata.update({"axedur": event["object"]["durability"]}).run(self.db, durability="soft")
                
            items = self.add_mats(authordata["items"].run(self.db), [(item["name"], item["amount"])], {x[0]: x[1] for x in item.items() if x[0] != "amount" and x[0] != "name"})
            authordata.update({"items": items}).run(self.db, durability="soft")
            await ctx.send("You just bought `{} {}` for **${:,}** :tada:".format(item["amount"], item["name"], int(event["object"]["price"])))
            try:
                await owner.send("Your `{}` just got bought on the auction house, it was sold for **${:,}** :tada:".format(item["name"], int(event["object"]["price"])))
            except:
                pass

    @commands.group(aliases=["rod", "fishing_rod"])
    async def fishingrod(self, ctx):
        """Some commands where you can buy and view fishing rods"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @fishingrod.command(name="buy")
    async def ___buy_(self, ctx, item: str):
        """Buy a fishing rod from the fishing rod shop"""
        rod = self.get_item(shop["roditems"], item)
        author = ctx.author
        authordata = r.table("bank").get(str(author.id))
        if not rod:
            return await ctx.send("I could not find that fishing rod :no_entry:")
        if rod["price"]:
            if self.has_rod(author):
                return await ctx.send("You already own a fishing rod, sell your rod and try again :no_entry:")
                    
            author_data = authordata.run(self.db, durability="soft")
                
            if author_data["balance"] >= rod["price"]:
                items = self.add_mats(author_data["items"], [(rod["name"], 1)], {"upgrades": 0, "rand_min": rod["rand_min"], "rand_max": rod["rand_max"], "durability": rod["durability"], "price": rod["price"]})
                authordata.update({"balance": r.row["balance"] - rod["price"], "items": items, "roddur": rod["durability"]}).run(self.db, durability="soft")
                    
                return await ctx.send("You just bought a {} for **${:,}** :ok_hand:".format(rod["name"], rod["price"]))
            else:
                return await ctx.send("You don't have enough money to buy that item :no_entry:")
        else:
            return await ctx.send("This rod is not buyable :no_entry:")

    @fishingrod.command(name="shop")
    async def ____shop(self, ctx):
        """Check what fishing rods you can buy"""
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Sx4 shop use your currency in Sx4 to buy fishing rods", colour=0xfff90d)
        s.set_author(name="Shop", icon_url=self.bot.user.avatar_url)
        for item in shop["roditems"]:
            s.add_field(name=item["name"], value="Price: {}\nCraft: {}\nDurability: {}".format("${:,}".format(item["price"]) if item["price"] else "Not Buyable", "\n".join(["{} {}".format(x[1], x[0]) for x in item["craft"]]) if item["craft"] else "Not Craftable", item["durability"]))
        try:    
            s.set_footer(text="Use s?fishingrod buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run(self.db, durability="soft")))
        except:
            s.set_footer(text="Use s?fishingrod buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @fishingrod.command(name="info")
    async def _info(self, ctx, user: str=None):
        """View your or a users fishing rod"""
        if not user:
            user = ctx.author 
        else:
            user = arg.get_server_member(ctx, user)
            if not user:
                return await ctx.send("I could not find that user :no_entry:")
        
        userdata = r.table("bank").get(str(user.id))
        if not userdata.run(self.db):
            return await ctx.send("This user does not have a fishing rod :no_entry:")
        item = self.get_user_rod(user)
        if not item:
            return await ctx.send("That user does not have a fishing rod :no_entry:")
        if "upgrades" not in item:
            rod = self.get_exact_item(shop["roditems"], item["name"])
            item.update({"upgrades": 0, "rand_min": rod["rand_min"], "rand_max": rod["rand_max"], "durability": rod["durability"], "price": rod["price"]})
        s=discord.Embed(colour=user.colour)
        s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
        s.add_field(name="Durability", value="{}/{}".format(userdata["roddur"].run(self.db, durability="soft"), item["durability"]), inline=False)
        s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * userdata["roddur"].run(self.db, durability="soft"))), inline=False)
        s.add_field(name="Original Price", value= "$" + str(item["price"]), inline=False)
        s.add_field(name="Upgrades", value=item["upgrades"], inline=False)
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/147/fishing-pole-and-fish_1f3a3.png")
        await ctx.send(embed=s)
          
    @commands.command()
    async def fish(self, ctx):
        """Fish for some extra money"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        msg = ""
        self._set_bank(author)
        rod = self.get_user_rod(author)
        
        authordata = r.table("bank").get(str(author.id))
        items = authordata["items"].run(self.db)
        if not authordata["fishtime"].run(self.db, durability="soft"):
            if rod:
                try:
                    money = randint(rod["rand_min"], rod["rand_max"])
                except KeyError:
                    rod = self.get_item(shop["roditems"], rod["name"])
                    money = randint(rod["rand_min"], rod["rand_max"])
                authordata.update({"roddur": r.row["roddur"] - 1}).run(self.db, durability="soft")
                msg = "Your fishing rod broke in the process" if authordata["roddur"].run(self.db, durability="soft") <= 0 else ""
                if authordata["roddur"].run(self.db, durability="soft") <= 0:
                    items = self.remove_mats(items, [(rod["name"], 1)])
            else:
                money = randint(2, 15)
            authordata.update({"fishtime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + money, "items": items}).run(self.db, durability="soft", noreply=True)
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n{}".format(money, msg), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        elif ctx.message.created_at.timestamp() - authordata["fishtime"].run(self.db, durability="soft") <= 300:
            time = dateify.get(authordata["fishtime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 300)
            return await ctx.send("You are too early, come collect your money again in {}".format(time))
        else:
            if rod:
                try:
                    money = randint(rod["rand_min"], rod["rand_max"])
                except KeyError:
                    rod = self.get_item(shop["roditems"], rod["name"])
                    money = randint(rod["rand_min"], rod["rand_max"])
                authordata.update({"roddur": r.row["roddur"] - 1}).run(self.db, durability="soft")
                msg = "Your fishing rod broke in the process" if authordata["roddur"].run(self.db, durability="soft") <= 0 else ""
                if authordata["roddur"].run(self.db, durability="soft") <= 0:
                    items = self.remove_mats(items, [(rod["name"], 1)])
            else:
                money = randint(2, 15)
            authordata.update({"fishtime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + money, "items": items}).run(self.db, durability="soft", noreply=True)
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n{}".format(money, msg), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def slot(self, ctx, bet: int=None):
        """Bid your money into slots with a chance of winning big"""
        author = ctx.author
        if bet:
            self._set_bank(author)
            authordata = r.table("bank").get(str(author.id))
            if authordata["balance"].run(self.db, durability="soft") < bet:
                await ctx.send("You don't have that much to bet :no_entry:")
                return
            if bet <= 0:
                await ctx.send("At least bet a dollar :no_entry:")
                return
            authordata.update({"balance": r.row["balance"] - bet, "winnings": r.row["winnings"] - bet}).run(self.db, durability="soft")
        slots = [
                {"icon" : ":athletic_shoe:", "percentage" : 12.5, "number" : 1}, {"icon" : "<:coal:441006067523256350>", "percentage" : 3.7, "number" : 2}, {"icon" : "<:copper:441006065828757504>", "percentage" : 0.8, "number" : 3},
                {"icon" : "<:iron:441006065069326357>", "percentage" : 0.2, "number" : 4}, {"icon" : "<:aluminium:441006064545300491>", "percentage" : 0.08, "number" : 5}, {"icon" : "<:gold:441006068328300551>", "percentage" : 0.03, "number" : 6}, 
                {"icon" : "<:oil:441006064243179531>", "percentage" : 0.01, "number" : 7}, {"icon" : "<:titanium:441006065639751683>", "percentage" : 0.0012, "number" : 8}, {"icon" : "<:bitcoin:441006066273353750>", "percentage" : 0.00042, "number" : 9}, 
                {"icon" : "<:platinum:441006059008688139>", "percentage" : 0.0002, "number" : 10}, {"icon" : "<:diamond:441251890186158081>", "percentage" : 0.0001, "number" : 11}
                ]
        slot1 = None
        slot2 = None
        slot3 = None
        while True:
            slots[0]["chance"] = randint(0, 1)
            slots[1]["chance"] = randint(0, 2)
            slots[2]["chance"] = randint(0, 4)
            slots[3]["chance"] = randint(0, 7)
            slots[4]["chance"] = randint(0, 10)
            slots[5]["chance"] = randint(0, 15)
            slots[6]["chance"] = randint(0, 21)
            slots[7]["chance"] = randint(0, 43)
            slots[8]["chance"] = randint(0, 61)
            slots[9]["chance"] = randint(0, 83)
            slots[10]["chance"] = randint(0, 100)
            for slot in slots:
                if slot["chance"] == 1:
                    slot1 = slot["icon"]
                    number1 = slot["number"]
                    break
            else:
                continue
            break
        while True:
            slots[0]["chance"] = randint(0, 1)
            slots[1]["chance"] = randint(0, 2)
            slots[2]["chance"] = randint(0, 4)
            slots[3]["chance"] = randint(0, 7)
            slots[4]["chance"] = randint(0, 10)
            slots[5]["chance"] = randint(0, 15)
            slots[6]["chance"] = randint(0, 21)
            slots[7]["chance"] = randint(0, 43)
            slots[8]["chance"] = randint(0, 61)
            slots[9]["chance"] = randint(0, 83)
            slots[10]["chance"] = randint(0, 100)
            for slot in slots:
                if slot["chance"] == 1:
                    slot2 = slot["icon"]
                    number2 = slot["number"]
                    break
            else:
                continue
            break
        while True:
            slots[0]["chance"] = randint(0, 1)
            slots[1]["chance"] = randint(0, 2)
            slots[2]["chance"] = randint(0, 4)
            slots[3]["chance"] = randint(0, 7)
            slots[4]["chance"] = randint(0, 10)
            slots[5]["chance"] = randint(0, 15)
            slots[6]["chance"] = randint(0, 21)
            slots[7]["chance"] = randint(0, 43)
            slots[8]["chance"] = randint(0, 61)
            slots[9]["chance"] = randint(0, 83)
            slots[10]["chance"] = randint(0, 100)
            for slot in slots:
                if slot["chance"] == 1:
                    slot3 = slot["icon"]
                    number3 = slot["number"]
                    break
            else:
                continue
            break
        number1a = number1 - 1
        number2a = number2 - 1
        number3a = number3 - 1
        number1b = number1 + 1
        number2b = number2 + 1
        number3b = number3 + 1
        if number1a == 0:
            number1a = 11
        if number2a == 0:
            number2a = 11
        if number3a == 0:
            number3a = 11
        if number1b == 12:
            number1b = 1
        if number2b == 12:
            number2b = 1
        if number3b == 12:
            number3b = 1
        if slot1 == slot3 and slot2 == slot3:
            for slot in slots:
                if slot["icon"] == slot1:
                    if bet:
                        winnings = bet * round((100/slot["percentage"]) * 0.5)
                        msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou won **${:,}**!".format(winnings)
                        authordata.update({"balance": r.row["balance"] + winnings, "winnings": r.row["winnings"] + winnings}).run(self.db, durability="soft")
                    else:
                        msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou would have won **{:,}x** your bet!".format(round((100/slot["percentage"]) * 0.5))
        else:
            msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou {} won **nothing**!".format("would have" if not bet else "")
        s=discord.Embed(description=msg, colour=0xfff90d)
        s.set_author(name="🎰 Slot Machine 🎰")
        s.set_thumbnail(url="https://images.emojiterra.com/twitter/512px/1f3b0.png")
        s.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @auction.command(aliases=["house"])
    async def list(self, ctx, itemname=None, page: int=None):  
        """See what's in the auction house"""
        itemnamesearch = False
        if not page and not itemname:
            page = 1
        elif not page and itemname:
            try:
                page = int(itemname)
            except:
                itemnamesearch = True
                page = 1
        elif itemname and page:
            itemnamesearch = True
        auctiondata = r.table("auction")
        all_data = auctiondata.run(self.db, durability="soft")
        if itemnamesearch == True:
            type = sorted(filter(lambda x: x["item"]["name"].lower() == itemname.lower(), all_data), key=lambda x: int(x["price"])/x["item"]["amount"])
        else:
            type = sorted(all_data, key=lambda x: int(x["price"])/x["item"]["amount"])
        if page < 1 or page - 1 > len(type) / 5:
            await ctx.send("Invalid Page :no_entry:")
            return
        msg = ""
        for item in type[page*5-5:page*5]:
            if item["durability"]:
                msg += "**__{}__**\nPrice: ${:,}\nDurability: {}/{}\nAmount: {:,}\n{}Price Per Item: ${}\n\n".format(item["item"]["name"], int(item["price"]), item["durability"], item["item"]["durability"] if "durability" in item["item"] else self.get_exact_item(shop["picitems"] + shop["roditems"] + shop["axes"], item["item"]["name"])["durability"], item["item"]["amount"], "Upgrades: {:,}\n".format(item["item"]["upgrades"]) if "upgrades" in item["item"] else "", format(int(item["price"])/item["item"]["amount"], ".2f"))
            else:
                msg += "**__{}__**\nPrice: ${:,}\nAmount: {:,}\n{}Price Per Item: ${}\n\n".format(item["item"]["name"], int(item["price"]), item["item"]["amount"], "Upgrades: {:,}\n".format(item["item"]["upgrades"]) if "upgrades" in item["item"] else "", format(int(item["price"])/item["item"]["amount"], ".2f"))
        if not msg and itemnamesearch == True:
            await ctx.send("There are none of that item on the auction house :no_entry:")
            return
        if not msg and itemnamesearch == False:
            await ctx.send("There are no items for sale on the auction house :no_entry:")
            return
        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=datetime.datetime.utcnow())
        s.set_author(name="Auction House", icon_url=self.bot.user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(type)/5)))
        await ctx.send(embed=s) 

    @commands.command()
    async def craft(self, ctx, *, item: str):
        """Craft a pickaxe/axe/rod with the specified materials for the item"""
        pickaxe = self.get_item(shop["picitems"], item)
        rod = self.get_item(shop["roditems"], item)
        self._set_bank(ctx.author)
        authordata = r.table("bank").get(str(ctx.author.id))   
        if pickaxe:
            if pickaxe["craft"]:
                if self.has_pickaxe(ctx.author):
                    return await ctx.send("You already have a pickaxe :no_entry:")
                craft_items = [tuple(x) for x in pickaxe["craft"]]
                for x in craft_items:
                    user_item = self.get_user_item(authordata["items"].run(self.db), x[0])
                    if user_item["amount"] < x[1]:
                        return await ctx.send("You do not have enough `{}` to craft this pickaxe :no_entry:".format(x[0]))
                items = self.add_mats(authordata["items"].run(self.db), [(pickaxe["name"], 1)], {"upgrades": 0, "multiplier": pickaxe["multiplier"], "rand_min": pickaxe["rand_min"], "rand_max": pickaxe["rand_max"], "durability": pickaxe["durability"], "price": pickaxe["price"]})
                items = self.remove_mats(items, craft_items) 
                await ctx.send("You have crafted a {} with {} :ok_hand:".format(pickaxe["name"], ", ".join(["{} {}".format(x[1], x[0]) for x in craft_items])))
                authordata.update({"items": items, "pickdur": pickaxe["durability"]}).run(self.db, durability="soft")
            else:
                return await ctx.send("This pickaxe is not craftable :no_entry:")
        elif rod:
            if rod["craft"]:
                if self.has_rod(ctx.author):
                    return await ctx.send("You already have a rod :no_entry:")
                craft_items = [tuple(x) for x in rod["craft"]]
                for x in craft_items:
                    user_item = self.get_user_item(authordata["items"].run(self.db), x[0])
                    if user_item["amount"] < x[1]:
                        return await ctx.send("You do not have enough `{}` to craft this pickaxe :no_entry:".format(x[0]))
                items = self.add_mats(authordata["items"].run(self.db), [(rod["name"], 1)], {"upgrades": 0, "rand_min": rod["rand_min"], "rand_max": rod["rand_max"], "durability": rod["durability"], "price": rod["price"]})
                items = self.remove_mats(items, craft_items) 
                await ctx.send("You have crafted a {} with {} :ok_hand:".format(rod["name"], ", ".join(["{} {}".format(x[1], x[0]) for x in craft_items])))
                authordata.update({"items": items, "roddur": rod["durability"]}).run(self.db, durability="soft")
            else:
                return await ctx.send("This rod is not craftable :no_entry:")
        else:
            return await ctx.send("That is not an item :no_entry:")
            
    @commands.group(usage="<sub command>")
    async def axe(self, ctx):
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            self._set_bank(ctx.author)

    @axe.command()
    async def info(self, ctx, user: str=None):
        if not user:
            user = ctx.author 
        else:
            user = arg.get_server_member(ctx, user)
            if not user:
                return await ctx.send("I could not find that user :no_entry:")
        
        userdata = r.table("bank").get(str(user.id))
        if userdata.run(self.db):
            if self.has_axe(user):
                item = self.get_user_axe(user)
                if "upgrades" not in item:
                    axe = self.get_exact_item(shop["picitems"], item["name"])
                    item.update({"upgrades": 0, "rand_min": axe["rand_min"], "rand_max": axe["rand_max"], "durability": axe["durability"], "multiplier": axe["multiplier"], "price": axe["price"]})
                s=discord.Embed(colour=user.colour)
                s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                s.add_field(name="Durability", value="{}/{}".format(userdata["axedur"].run(self.db, durability="soft"), item["durability"]), inline=False)
                s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * userdata["axedur"].run(self.db, durability="soft"))), inline=False)
                s.add_field(name="Original Price", value= "$" + str(item["price"]), inline=False)
                s.add_field(name="Upgrades", value=item["upgrades"], inline=False)
                s.set_thumbnail(url="https://www.shareicon.net/data/2016/09/02/823994_ax_512x512.png")
                await ctx.send(embed=s)
            else:
                await ctx.send("That user does not have a axe :no_entry:")
        else:
            await ctx.send("That user does not have a axe :no_entry:")      

    @axe.command(name="buy")
    async def __buy___(self, ctx, axe: str):
        """Buy an axe from the axe shop so you can chop down some trees"""
        item = self.get_item(shop["axes"], axe)
        if not item:
            return await ctx.send("That is not an axe :no_entry:")
        authordata = r.table("bank").get(str(ctx.author.id))
        if self.has_axe(ctx.author):
            return await ctx.send("You already have an axe :no_entry:")
        if authordata["balance"].run(self.db) < item["price"]:
            return await ctx.send("You do not have enough money to buy this axe :no_entry:")
        items = self.add_mats(authordata["items"].run(self.db), [(item["name"], 1)], {"upgrades": 0, "multiplier": item["multiplier"], "durability": item["durability"], "max_mats": item["max_mats"], "price": item["price"]})
        await ctx.send("You just bought a `{}` for **${:,}** :ok_hand:".format(item["name"], item["price"]))
        authordata.update({"balance": r.row["balance"] - item["price"], "items": items, "axedur": item["durability"]}).run(self.db, durability="soft")

    @axe.command(name="shop")
    async def __shop__(self, ctx):
        """View axes from the axe shop"""
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Sx4 shop use your currency in Sx4 to buy items", colour=0xfff90d)
        s.set_author(name="Shop", icon_url=self.bot.user.avatar_url)
        for item in shop["axes"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDurability: {}".format(item["price"], item["durability"]))
        try:    
            s.set_footer(text="Use s?axe buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run(self.db, durability="soft")))
        except:
            s.set_footer(text="Use s?axe buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @commands.command()
    async def chop(self, ctx):
        """Chop some trees down with your current axe to gain some wood"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        self._set_bank(author)
        authordata = r.table("bank").get(str(author.id))
        if self.has_axe(author):
            axe = self.get_user_axe(author)
            array = []
            items = authordata["items"].run(self.db)
            if not authordata["axetime"].run(self.db):
                for x in range(axe["max_mats"]):
                    for w in wood["wood"]:
                        number = round(w["rand_max"] / axe["multiplier"]) if round(w["rand_max"] / axe["multiplier"]) > 0 else 1
                        chance = randint(0, number)
                        if chance == 0:
                            if w["name"] in map(lambda x: x["name"], array):
                                current = list(filter(lambda x: x["name"] == w["name"], array))[0]
                                array.remove(current)
                                current["amount"] += 1
                                array.append(current)
                            else:
                                array.append({"name": w["name"], "amount": 1}) 
                            items = self.add_mats(items, [(w["name"], 1)])
                if authordata["axedur"].run(self.db, durability="soft") - 1 > 0:
                    s=discord.Embed(description="You chopped down some trees and found the following wood: {}".format(", ".join(["{}x {}".format(x["amount"], x["name"]) for x in sorted(array, key=lambda x: x["amount"], reverse=True)]) if array else "Absolutely nothing"), colour=colour)
                else:
                    s=discord.Embed(description="You chopped down some trees and found the following wood: {}\n\nYour axe broke in the process".format(", ".join(["{}x {}".format(x["amount"], x["name"]) for x in sorted(array, key=lambda x: x["amount"], reverse=True)]) if array else "Absolutely nothing"), colour=colour)
                    items = self.remove_mats(items, [(axe["name"], 1)])
                s.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.send(embed=s)
                authordata.update({"items": items, "axedur": r.row["axedur"] - 1, "axetime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft")
            elif ctx.message.created_at.timestamp() - authordata["axetime"].run(self.db, durability="soft") <= 600:
                time = dateify.get(authordata["axetime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 600)
                return await ctx.send("You are too early, come back to chop trees in {}".format(time))
            else:
                for x in range(axe["max_mats"]):
                    for w in wood["wood"]:
                        number = round(w["rand_max"] / axe["multiplier"]) if round(w["rand_max"] / axe["multiplier"]) > 0 else 1
                        chance = randint(0, number)
                        if chance == 0:
                            if w["name"] in map(lambda x: x["name"], array):
                                current = list(filter(lambda x: x["name"] == w["name"], array))[0]
                                array.remove(current)
                                current["amount"] += 1
                                array.append(current)
                            else:
                                array.append({"name": w["name"], "amount": 1}) 
                            items = self.add_mats(items, [(w["name"], 1)])
                if authordata["axedur"].run(self.db, durability="soft") - 1 > 0:
                    s=discord.Embed(description="You chopped down some trees and found the following wood: {}".format(", ".join(["{}x {}".format(x["amount"], x["name"]) for x in sorted(array, key=lambda x: x["amount"], reverse=True)]) if array else "Absolutely nothing"), colour=colour)
                else:
                    s=discord.Embed(description="You chopped down some trees and found the following wood: {}\n\nYour axe broke in the process".format(", ".join(["{}x {}".format(x["amount"], x["name"]) for x in sorted(array, key=lambda x: x["amount"], reverse=True)]) if array else "Absolutely nothing"), colour=colour)
                    items = self.remove_mats(items, [(axe["name"], 1)])
                s.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.send(embed=s)
                authordata.update({"items": items, "axedur": r.row["axedur"] - 1, "axetime": ctx.message.created_at.timestamp()}).run(self.db, durability="soft")
        else:
            return await ctx.send("You do not have an axe, you can buy one in `{}axe shop` :no_entry:".format(ctx.prefix))
                    
    @commands.command()
    async def mine(self, ctx): 
        """If you have a pickaxe use this to mine with it"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        materials = ""
        self._set_bank(author)
        authordata = r.table("bank").get(str(author.id))
        if "picktime" not in authordata.run(self.db):
            authordata.update({"picktime": None}).run(self.db, durability="soft", noreply=True)
        if not self.has_pickaxe(author):
            return await ctx.send("You do not own a pickaxe, you can buy one at the `{}pickaxe shop`".format(ctx.prefix))
        item = self.get_user_pickaxe(author)
        if "upgrades" not in item:
            pick = self.get_exact_item(shop["picitems"], item["name"])
            item.update({"upgrades": 0, "rand_min": pick["rand_min"], "rand_max": pick["rand_max"], "durability": pick["durability"], "multiplier": pick["multiplier"], "price": pick["price"]})

        amount = randint(item["rand_min"], item["rand_max"])
        if not authordata["pickdur"].run(self.db, durability="soft"):
            await ctx.send("It seems you've came across a bug where your pick durabilty doesn't exist report this to my owner, your pick has been removed from your items and you should be able to buy a new one.")
            items = self.remove_mats(authordata["items"].run(self.db), [(item["name"], 1)])
            authordata.update({"items": items}).run(self.db, durability="soft", noreply=True)
            return
        if not authordata["picktime"].run(self.db, durability="soft"):
            items = authordata["items"].run(self.db)
            for item2 in mine["items"]:
                if round(item2["rand_max"] / item["multiplier"]) <= 0:
                    number = 1
                else:
                    number = round(item2["rand_max"] / item["multiplier"])
                chance = randint(0, number)
                if chance == 0:
                    items = self.add_mats(items, [(item2["name"], 1)])
                    materials += item2["name"] + item2["emote"] + ", "
            materials = materials[:-2]
            if materials == "":
                materials = "Absolutely nothing"
                        
                    
            if authordata["pickdur"].run(self.db, durability="soft") - 1 > 0:
                s=discord.Embed(description="You mined resources and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
            else:
                s=discord.Embed(description="You mined resources and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                items = self.remove_mats(items, [(item["name"], 1)])        
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            authordata.update({"items": items, "picktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + amount, "pickdur": r.row["pickdur"] - 1}).run(self.db, durability="soft", noreply=True)
        elif ctx.message.created_at.timestamp() - authordata["picktime"].run(self.db, durability="soft") <= 900:   
            time = dateify.get(authordata["picktime"].run(self.db, durability="soft") - ctx.message.created_at.timestamp() + 900)
            return await ctx.send("You are too early, come back to mine in {}".format(time))
        else:
            items = authordata["items"].run(self.db)
            for item2 in mine["items"]:
                if round(item2["rand_max"] / item["multiplier"]) <= 0:
                    number = 1
                else:
                    number = round(item2["rand_max"] / item["multiplier"])
                chance = randint(0, number)
                if chance == 0:
                    items = self.add_mats(items, [(item2["name"], 1)])
                    materials += item2["name"] + item2["emote"] + ", "
            materials = materials[:-2]
            if materials == "":
                materials = "Absolutely nothing"
            if authordata["pickdur"].run(self.db, durability="soft") - 1 > 0:
                s=discord.Embed(description="You mined resources and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
            else:
                s=discord.Embed(description="You mined resources and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                items = self.remove_mats(items, [(item["name"], 1)])   
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            authordata.update({"items": items, "picktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + amount, "pickdur": r.row["pickdur"] - 1}).run(self.db, durability="soft", noreply=True)
        
    @commands.command(aliases=["inventory"])
    async def items(self, ctx, *, user: discord.Member=None): 
        """View your current items"""
        if not user:
            user = ctx.author   
        userdata = r.table("bank").get(str(user.id)).run(self.db, durability="soft")
        if not userdata:
            bal = 0
            item = None
        else:
            bal = userdata["balance"]
            items = sorted(userdata["items"], key=lambda x: x["amount"], reverse=True)
            if not items:
                item = None
            else:
                item = {"tools": [], "factories": [], "miners": [], "materials": [], "wood": [], "boosters": [], "crates": []}
                for x in items:
                    if self.get_exact_item(shop["roditems"], x["name"]):
                        item["tools"].append("{} x{} ({:,} Durability)".format(x["name"], x["amount"], userdata["roddur"]))
                    elif self.get_exact_item(shop["picitems"], x["name"]):
                        item["tools"].append("{} x{} ({:,} Durability)".format(x["name"], x["amount"], userdata["pickdur"]))
                    elif self.get_exact_item(shop["axes"], x["name"]):
                        item["tools"].append("{} x{} ({:,} Durability)".format(x["name"], x["amount"], userdata["axedur"]))
                    elif self.get_exact_item(factories_all["factory"], x["name"]):
                        item["factories"].append("{} x{}".format(x["name"], x["amount"]))
                    elif self.get_exact_item(shop["crates"], x["name"]):
                        item["crates"].append("{} x{}".format(x["name"], x["amount"]))
                    elif self.get_exact_item(shop["miners"], x["name"]):
                        item["miners"].append("{} x{}".format(x["name"], x["amount"]))
                    elif self.get_exact_item(mine_all["items"], x["name"]):
                        item["materials"].append("{} x{}".format(x["name"], x["amount"]))
                    elif self.get_exact_item(wood["wood"], x["name"]):
                        item["wood"].append("{} x{}".format(x["name"], x["amount"]))
                    elif self.get_exact_item(shop["boosters"], x["name"]):
                        item["boosters"].append("{} x{}".format(x["name"], x["amount"]))
        if item:
            s=discord.Embed(colour=user.colour)
            for x in sorted(item.items(), key=lambda x: len(x[1])):
                if x[1]:
                    s.add_field(name=x[0].title(), value="\n".join(x[1]))
        else:
            s=discord.Embed(description="This user has no items", colour=user.colour)
        s.set_author(name=user.name +"'s Items", icon_url=user.avatar_url)
        s.set_footer(text="If a category isn't shown it means you have no items in that category | Balance: ${:,}".format(bal))
        await ctx.send(embed=s)
            
    def _set_bank(self, author):
        if author.bot:
            return
        r.table("bank").insert({"id": str(author.id), "rep": 0, "balance": 0, "streak": 0, "streaktime": None,
        "reptime": None, "items": [], "pickdur": None, "roddur": None, "axedur": None, "axetime": None, "minertime": None, "winnings": 0,
        "fishtime": None, "factorytime": None, "picktime": None}).run(self.db, durability="soft")

    @commands.group(aliases=["lb"])  
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def leaderboard(self, ctx):
        """See where you're ranked"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            pass

    @leaderboard.command(usage="[month/all] [page] | [page]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def votes(self, ctx, option: str="month", *, page: int=None):
        """View the leaderboard for most votes"""
        if not page:
            page = 1
        counter = Counter()
        
        votesjockie = requests.get("http://localhost:8080/411916947773587456/votes" + ("?ids=true" if option.lower() == "all" else "")).json()["votes"]
        votessx4 = requests.get("http://localhost:8080/440996323156819968/votes" + ("?ids=true" if option.lower() == "all" else "")).json()["votes"]
        if option.lower() not in ["all", "month"]:
            try:
                page = int(option)
            except ValueError:
                return await ctx.send("Invalid option :no_entry:")
            option = "month"
        if option.lower() == "all":
            for x in votessx4.items():
                counter[x[0]] += len(x[1]["votes"])
            for x in votesjockie.items():
                counter[x[0]] += len(x[1]["votes"])
        elif option.lower() == "month":
            for x in votessx4.items():
                for y in x[1]["votes"]:
                    if datetime.datetime.fromtimestamp(y["time"]).month == datetime.date.today().month and datetime.datetime.fromtimestamp(y["time"]).year == datetime.date.today().year:
                        counter[x[0]] += 1
            for x in votesjockie.items():
                for y in x[1]["votes"]:
                    if datetime.datetime.fromtimestamp(y["time"]).month == datetime.date.today().month and datetime.datetime.fromtimestamp(y["time"]).year == datetime.date.today().year:
                        counter[x[0]] += 1
        votes = counter.most_common()
        if page < 1 or page > math.ceil(len(votes)/10):
            return await ctx.send("Invalid Page :no_entry:")
        entries = []
        data = votes
        for user_data in data:
            user = self.bot.get_user(int(user_data[0]))
            if not user:
                continue
            entry = {}
            entry["votes"] = user_data[1]
            entry["user"] = user
            entries.append(entry)
        votes = sorted([x for x in entries if x["votes"] != 0], key=lambda x: x["votes"], reverse=True)
        i, msg, n = page*10-10, "", 0
        for n, entry in enumerate(votes, start=1):
            if entry["user"].id == ctx.author.id:
                break
        else:
            n = None
        for x in votes[page*10-10:page*10]:
            i += 1
            msg += "{}. `{}` - {} {}\n".format(i, x["user"], x["votes"], "vote" if x["votes"] == 1 else "votes")
        s=discord.Embed(title="Votes Leaderboard {}".format("" if option.lower() == "all" else "for " + datetime.datetime.utcnow().strftime("%B")), description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(votes)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)

    @leaderboard.command(name="items")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _items(self, ctx, item: str, page: int=None):
        """View the leaderboard for a specific item and who has the most of it"""
        if not page:
            page = 1
        all_items = shop["items"] + mine_all["items"] + shop["miners"] + shop["boosters"] + factories_all["factory"] + shop["picitems"] + shop["roditems"] + shop["crates"] + wood["wood"]
        try:
            item = list(filter(lambda x: x["name"].lower() == item.lower(), all_items))[0]
        except:
            return await ctx.send("Invalid Item :no_entry:")
        counter = Counter()
        data = r.table("bank").filter(lambda x: x["items"] != [])
        for y in data.run(self.db, durability="soft"):
            item2 = self.get_user_item(y["items"], item["name"])
            if item2["amount"] != 0:
                counter[y["id"]] += item2["amount"]
        if len(counter) == 0:
            return await ctx.send("No one has that item :no_entry:")
        users = counter.most_common()
        entries = []
        for user_data in users:
            user2 = self.bot.get_user(int(user_data[0]))
            if not user2:
                continue
            entry = {}
            entry["items"] = user_data[1]
            entry["user"] = user2
            entries.append(entry)
        users = sorted(entries, key=lambda x: x["items"], reverse=True)
        userspg = users[page*10-10:page*10]
        if page < 1 or page > math.ceil(len(users)/10):
            return await ctx.send("Invalid Page :no_entry:")
        i, msg, n = page*10-10, "", 0
        for n, entry in enumerate(users, start=1):
            if entry["user"].id == ctx.author.id:
                break
        else:
            n = None
        for x in userspg:
            i += 1
            msg += "{}. `{}` - {:,} {}\n".format(i, x["user"], x["items"], item["name"])
        s=discord.Embed(title="{} Leaderboard".format(item["name"]), description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(users)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command(aliases=["rep"])
    async def reputation(self, ctx, page: int=None):
        """Leaderboard for most reputation"""
        if not page:
            page = 1
        data = r.table("bank")
        list = data.filter(lambda x: x["rep"] != 0).order_by(r.desc("rep")).run(self.db, durability="soft")
        if page - 1 > len(list) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""   
        i = page*10-10
        n = 0
        sortedrep2 = list
        sortedrep = list[page*10-10:page*10]
        if str(ctx.author.id) in map(lambda x: x["id"], sortedrep2):
            for x in sortedrep2:
                n = n + 1
                if str(ctx.author.id) == x["id"]:
                    break    
        else:
            n = None
        for x in sortedrep:
            i = i + 1
            user = self.bot.get_user(int(x["id"]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - {} reputation\n".format(i, user, x["rep"])
        s=discord.Embed(title="Reputation Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(list)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def winnings(self, ctx, page: int=None):
        """Leaderboard for most winnings"""
        if not page:
            page = 1
        entries = []
        data = r.table("bank").run(self.db, durability="soft")
        for user_data in data:
            user = self.bot.get_user(int(user_data["id"]))
            if not user:
                continue
            entry = {}
            entry["winnings"] = user_data["winnings"]
            entry["user"] = user
            entries.append(entry)
        list = sorted([x for x in entries if x["winnings"] != 0], key=lambda x: x["winnings"], reverse=True)
        if page - 1 > len(list) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        
        sortedwin = list[page*10-10:page*10]
        for n, entry in enumerate(list, start=1):
            if entry["user"].id == ctx.author.id:
                break
        else:
            n = None
        for i, x in enumerate(sortedwin, start=page*10-9):
            msg += "{}. `{}` - ${:,}\n".format(i, x["user"], x["winnings"])
        s=discord.Embed(title="Winnings Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(list)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def bank(self, ctx, page: int=None):
        """Leaderboard for most money"""
        if not page:
            page = 1
        entries = []
        data = r.table("bank").run(self.db, durability="soft")
        for user_data in data:
            user = self.bot.get_user(int(user_data["id"]))
            if not user:
                continue
            entry = {}
            entry["balance"] = user_data["balance"]
            entry["user"] = user
            entries.append(entry)
        list = sorted([x for x in entries if x["balance"] != 0], key=lambda x: x["balance"], reverse=True)
        if page - 1 > len(list) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10
        
        sortedbank = list[page*10-10:page*10]
        for n, entry in enumerate(list, start=1):
            if entry["user"].id == ctx.author.id:
                break
        else:
            n = None
        for x in sortedbank:
            i += 1
            msg += "{}. `{}` - ${:,}\n".format(i, x["user"], x["balance"])
        s=discord.Embed(title="Bank Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(list)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command(hidden=True)
    @checks.is_main_owner()
    async def moneyset(self, ctx, amount: str, *, user: str=None):
        if not user:
            user = ctx.author
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                return await ctx.send("Invalid User :no_entry:")
        userdata = r.table("bank").get(str(user.id))
        if not userdata.run(self.db):
            self._set_bank(user)
        if amount[:1] == "+":
            userdata.update({"balance": r.row["balance"] + int(amount[1:len(amount)])}).run(self.db, durability="soft")
            await ctx.send("**{}** has been given an extra **${}**".format(user, amount[1:len(amount)]))
        elif amount[:1] == "-":
            userdata.update({"balance": r.row["balance"] - int(amount[1:len(amount)])}).run(self.db, durability="soft")
            await ctx.send("**{}** has had **${}** taken off their balance".format(user, amount[1:len(amount)]))
        else:
            userdata.update({"balance": int(amount)}).run(self.db, durability="soft")
            await ctx.send("**{}** has had their balance set to **${}**".format(user, amount))

    @commands.command(hidden=True)
    @checks.is_main_owner()
    async def itemset(self, ctx, user: str, *, item: str):
        if not user:
            user = ctx.author
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                return await ctx.send("Invalid User :no_entry:")
        all_items = shop["items"] + mine_all["items"] + shop["miners"] + shop["boosters"] + wood["wood"] + factories_all["factory"] + shop["crates"] + shop["picitems"] + shop["roditems"] + shop["axes"]
        item, amount = self.convert(item)
        actual_item = self.get_item(all_items, item[1:])
        userdata = r.table("bank").get(str(user.id))
        if item[:1] == "+":
            items = self.add_mats(userdata["items"].run(self.db), [(actual_item["name"], amount)])
            userdata.update({"items": items}).run(self.db, durability="soft")
            await ctx.send("**{}** has been given `{} {}`".format(user, amount, actual_item["name"]))
        elif item[:1] == "-":
            items = self.remove_mats(userdata["items"].run(self.db), [(actual_item["name"], amount)])
            userdata.update({"items": items}).run(self.db, durability="soft")
            await ctx.send("**{}** has had `{} {}` taken off them".format(user, amount, actual_item["name"]))
        
    @commands.command()
    async def bankstats(self, ctx):
        """See some of the bank statistics"""
        total = sum(r.table("bank").map(lambda x: x["balance"]).run(self.db, durability="soft"))
        win = sum(r.table("bank").map(lambda x: x["winnings"]).run(self.db, durability="soft"))
        
        sortedloser = r.table("bank").order_by("winnings").run(self.db, durability="soft")[0]
        sortedwinner = r.table("bank").order_by(r.desc("winnings")).run(self.db, durability="soft")[0]
        user = discord.utils.get(self.bot.get_all_members(), id=int(sortedloser["id"]))
        userwinner = discord.utils.get(self.bot.get_all_members(), id=int(sortedwinner["id"]))
        toploser = "${:,} ({})".format(sortedloser["winnings"], user)        
        topwinner= "${:,} ({})".format(sortedwinner["winnings"], userwinner)  
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Bank Stats", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Users", value=r.table("bank").count().run(self.db, durability="soft"))
        s.add_field(name="Total Money", value="${:,}".format(total))
        s.add_field(name="Total Winnings", value="${:,}".format(win))
        s.add_field(name="Biggest Winner", value=topwinner)
        s.add_field(name="Biggest Loser", value=toploser)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def networth(self, ctx, page: int=None):
        """Leaderboard for most networth"""
        msg = ""
        
        author_id = ctx.author.id
        
        entries = []

        if not page:
            page = 1   
        
        all_items = shop["picitems"] + shop["items"] + mine["items"] + shop["roditems"] + shop["miners"] + shop["boosters"] + shop["crates"] + wood["wood"]
        bank_data = r.table("bank").run(self.db, durability="soft")

        for user_data in bank_data:
            try:
                user = self.bot.get_user(int(user_data["id"]))
                if not user:
                    continue
                worth = 0

                items = [item for item in all_items if item["name"] in map(lambda x: x["name"], user_data["items"])]
                for item in items:
                    user_item = self.get_user_item(user_data["items"], item["name"])
                    if "price" in user_item:
                        if self.get_exact_item(shop["picitems"], user_item["name"]):
                            worth += (user_item["price"]/user_item["durability"])*user_data["pickdur"]
                        elif self.get_exact_item(shop["roditems"], user_item["name"]):
                            worth += (user_item["price"]/user_item["durability"])*user_data["roddur"]
                        elif self.get_exact_item(shop["axes"], user_item["name"]):
                            worth += (user_item["price"]/user_item["durability"])*user_data["axedur"]
                        else:
                            worth += user_item["price"] * user_item["amount"]
                    else:
                        if self.get_exact_item(shop["picitems"], user_item["name"]):
                            worth += (item["price"]/item["durability"])*user_data["pickdur"]
                        elif self.get_exact_item(shop["roditems"], user_item["name"]):
                            worth += (item["price"]/item["durability"])*user_data["roddur"]
                        elif self.get_exact_item(shop["axes"], user_item["name"]):
                            worth += (item["price"]/item["durability"])*user_data["axedur"]
                        else:
                            worth += item["price"] * user_item["amount"] 
                for item2 in [item for item in factories["factory"] if item["name"] in map(lambda x: x["name"], user_data["items"])]:
                    user_factory = self.get_user_item(user_data["items"], item2["name"])
                    for item3 in mine["items"]:
                        if item3["name"] == item2["item"]:
                            worth += (item2["price"]*item3["price"]) * user_factory["amount"]
                worth += user_data["balance"]
                worth = round(worth)
                
                entry = {}
                entry["user"] = user
                entry["worth"] = worth
                
                entries.append(entry)
            except:
                pass

        if page - 1 > len([x for x in entries if x["worth"] != 0]) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return          
                
        networth_sorted = sorted([x for x in entries if x["worth"] != 0], key=lambda x: x["worth"], reverse=True)
        
        for index, entry in enumerate(networth_sorted):
            if entry["user"].id == author_id:
                break
        else:
            index = -1
        
        i = page*10-9
        for entry in networth_sorted[page*10-10:page*10]:
            msg += "{}. `{}` - ${:,}\n".format(i, entry["user"], entry["worth"])
            
            i += 1
        
        embed = discord.Embed(title="Networth Leaderboard", description = msg, colour = 0xfff90d)
        
        if index != -1:
            embed.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.author.name, index + 1, page, math.ceil(len([x for x in entries if x["worth"] != 0])/10)), icon_url = ctx.author.avatar_url)
        else:
            embed.set_footer(text = "{} does not have a rank | Page {}/{}".format(ctx.author.name, page, math.ceil(len([x for x in entries if x["worth"] != 0])/10)), icon_url = ctx.author.avatar_url)
        await ctx.send(embed=embed)
        del entries
            
        
    @leaderboard.command()
    async def streak(self, ctx, page: int=None):
        """Leaderboard for biggest streak"""
        if not page:
            page = 1
        data = r.table("bank").run(self.db, durability="soft")
        list = sorted(data, key=lambda x: x["streak"], reverse=True)
        if page - 1 > len(list) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10;
        n = 0;
        
        sortedstreak2 = list
        sortedstreak = list[page*10-10:page*10]
        for x in sortedstreak2:
            n = n + 1
            if str(ctx.author.id) == x["id"]:
                break            
        for x in sortedstreak:
            i = i + 1
            user = self.bot.get_user(int(x["id"]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - {} day streak\n".format(i, user, x["streak"])
        s=discord.Embed(title="Streak Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.author.name, n, page, math.ceil(len(list)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command()
    async def marry(self, ctx, user: discord.Member):
        """Marry other uses"""
        author = ctx.author
        server = ctx.guild
        if user.bot:
            await ctx.send("You can't marry bots :no_entry:")
            return
        r.table("marriage").insert({"id": str(author.id), "marriedto": []}).run(self.db, durability="soft")
        r.table("marriage").insert({"id": str(user.id), "marriedto": []}).run(self.db, durability="soft")
        authormarriage = r.table("marriage").get(str(author.id))
        usermarriage = r.table("marriage").get(str(user.id))
        if authormarriage["marriedto"].run(self.db, durability="soft"):
            if len(authormarriage["marriedto"].run(self.db, durability="soft")) >= 5:
                await ctx.send("You are married to the max amount of users possible (5 users) you need to divorce someone to marry this user :no_entry:")
                return
        if usermarriage["marriedto"].run(self.db, durability="soft"):
            if len(usermarriage["marriedto"].run(self.db, durability="soft")) >= 5:
                await ctx.send("This user is married to the max amount of users possible (5 users) they need to divorce someone to marry you :no_entry:")
                return
        if str(user.id) in authormarriage["marriedto"].run(self.db, durability="soft"):
            await ctx.send("Don't worry, You're already married to that user.")
            return
        if user == author:
            await ctx.send("So you want to be lonely, that's fine.\nJust say **yes** well you can say **no** but are you going to reject yourself?")
        else:
            await ctx.send("{}, **{}** would like to marry you!\n**Do you accept?**\nType **yes** or **no** to choose.".format(user.mention, author.name))
        try:
            def marry(m):
                return m.author == user and m.channel == ctx.channel
            msg = await self.bot.wait_for("message", check=marry, timeout=1800)
        except asyncio.TimeoutError:
            return await ctx.send("{}, You can always try someone else. (Response timed out :stopwatch:)".format(author.mention))
        if ("yes" in msg.content.lower()):
            if str(user.id) in authormarriage["marriedto"].run(self.db):
                return await ctx.send("You are already married to this user :no_entry:")
            if len(usermarriage["marriedto"].run(self.db, durability="soft")) >= 5:
                await ctx.send("This user is married to the max amount of users possible (5 users) they need to divorce someone to marry you :no_entry:")
                return
            if len(authormarriage["marriedto"].run(self.db, durability="soft")) >= 5:
                await ctx.send("You are married to the max amount of users possible (5 users) you need to divorce someone to marry this user :no_entry:")
                return
            if user == author:
                await self._create_marriage_user(ctx, user)
            else:
                await self._create_marriage_user(ctx, user)
                await self._create_marriage_author(ctx, user)
            await ctx.send("Congratulations **{}** and **{}** :heart: :tada:".format(author.name, user.name))
        else:
            await ctx.send("{}, You can always try someone else.".format(author.mention))
            
    @commands.command() 
    async def divorce(self, ctx, *, user: str=None):
        """Divorce someone you've married"""
        author = ctx.author
        authormarriage = r.table("marriage").get(str(author.id))
        if not authormarriage.run(self.db) or not authormarriage["marriedto"].run(self.db):
            return await ctx.send("You are not married to that user :no_entry:")
        if not user:
            event = await paged.page(ctx, authormarriage["marriedto"].run(self.db), selectable=True, function=lambda x: self.bot.get_user(int(x)) if self.bot.get_user(int(x)) else x)
            if event:
                user_id = event["object"]
                user = await arg.get_member(ctx, user_id)
                usermarriage = r.table("marriage").get(user_id)
                await ctx.send("Feels bad **{}**, Argument?".format(user.name if user else user_id))
                if author == user:
                    authormarriage.update({"marriedto": r.row["marriedto"].difference([user_id])}).run(self.db, durability="soft")
                else:
                    try:
                        authormarriage.update({"marriedto": r.row["marriedto"].difference([user_id])}).run(self.db, durability="soft")
                    except:
                        pass
                    try:
                        usermarriage.update({"marriedto": r.row["marriedto"].difference([str(author.id)])}).run(self.db, durability="soft")
                    except: 
                        pass
        else:
            user = await arg.get_member(ctx, user)
            if not user:
                await ctx.send("I could not find that user :no_entry:")
                return
            usermarriage = r.table("marriage").get(str(user.id))
            if str(user.id) in authormarriage["marriedto"].run(self.db, durability="soft"):
                await ctx.send("Feels bad **{}**, Argument?".format(user.name))
                if author == user:
                    authormarriage.update({"marriedto": r.row["marriedto"].difference([str(user.id)])}).run(self.db, durability="soft")
                else:
                    try:
                        authormarriage.update({"marriedto": r.row["marriedto"].difference([str(user.id)])}).run(self.db, durability="soft")
                    except:
                        pass
                    try:
                        usermarriage.update({"marriedto": r.row["marriedto"].difference([str(author.id)])}).run(self.db, durability="soft")
                    except: 
                        pass
            else:
                await ctx.send("You are not married to that user :no_entry:")

    @commands.command()
    async def married(self, ctx, user: discord.Member=None):
        """Check who you're married to"""
        if not user:
            user = ctx.author
        usermarriage = r.table("marriage").get(str(user.id)).run(self.db, durability="soft")
        list = []
        if usermarriage:
            for x in usermarriage["marriedto"]:
                user2 = self.bot.get_user(int(x))
                list.append((str(user2) + " " if user2 else "") + "({})".format(x))
        else:
            return await ctx.send("That user is not married to anyone :no_entry:")
        await ctx.send(embed=discord.Embed(description="\n".join(list) if list != [] else "No one :(").set_author(name=str(user), icon_url=user.avatar_url))
            
    @commands.command(aliases=["mdivorce"]) 
    async def massdivorce(self, ctx):
        """Divorce everyone""" 
        author = ctx.author
        data = r.table("marriage").get(str(author.id))
        if not data.run(self.db):
            return await ctx.send("You are not married to anyone :no_entry:")
        if not data["marriedto"].run(self.db):
            return await ctx.send("You are not married to anyone :no_entry:")
        data.update({"marriedto": []}).run(self.db, durability="soft")
        await ctx.send("You are now divorced from everyone previously you were married to <:done:403285928233402378>")
            
    async def _create_marriage_user(self, ctx, user):
        author = ctx.author
        r.table("marriage").get(str(user.id)).update({"marriedto": r.row["marriedto"].append(str(author.id))}).run(self.db, durability="soft")
    
    async def _create_marriage_author(self, ctx, user):
        author = ctx.message.author
        r.table("marriage").get(str(author.id)).update({"marriedto": r.row["marriedto"].append(str(user.id))}).run(self.db, durability="soft")
        
    @commands.group(name="set")
    async def _set(self, ctx):
        """Set aspects about yourself"""
        author = ctx.author
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("userprofile").insert({"id": str(author.id), "birthday": None, "height": None, "description": None, "colour": None}).run(self.db, durability="soft")
            
    @_set.command()
    async def height(self, ctx, feet: int, inches: int):
        """set your height on the profile
        example: s?set height 5 4
        height = 5'4"""
        author = ctx.author
        if feet == 8 and inches >= 4: 
            await ctx.send("You're not taller than the tallest man :no_entry:")
            return
        if feet >= 9: 
            await ctx.send("You're not taller than the tallest man :no_entry:")
            return
        if inches >= 12:
            await ctx.send("There's 12 inches in a foot you should know that :no_entry:")
            return
        if feet <= 0 and inches <= 0:
            await ctx.send("You have to be a height :no_entry:")
            return
        cm = inches * 2.54
        cm2 = feet * 30.48
        total = round(cm2 + cm)
        r.table("userprofile").get(str(author.id)).update({"height": "{}'{} ({}cm)".format(feet, inches, total)}).run(self.db, durability="soft")
        await ctx.send("Your height has been set to {}'{} ({}cm)".format(feet, inches, total))
    
    @_set.command()
    async def birthday(self, ctx, birthday: str):
        """set your birthday
        example: s?set birthday 01/07/2002"""
        author = ctx.author
        birthdates = birthday.split("/")
        try:
            day = int(birthdates[0])
            month = int(birthdates[1])
        except:
            return await ctx.send("Invalid Birthday :no_entry:")
        try:
            year = int(birthdates[2])
        except:
            year = None
        if day > monthrange(2016, int(month))[1] or day < 1:
            return await ctx.send("Invalid Birthday :no_entry:")
        if month > 12 or month < 1:
            return await ctx.send("Invalid Birthday :no_entry:")
        elif year is not None and (year > int(datetime.datetime.utcnow().strftime("%Y")) - 1 or year < int(datetime.datetime.utcnow().strftime("%Y")) - 100):
            return await ctx.send("Invalid Birthday :no_entry:")
        else:
            r.table("userprofile").get(str(author.id)).update({"birthday": "%02d/%02d" % (day, month) + ("/" + str(year) if year else "")}).run(self.db, durability="soft")
        await ctx.send("Your birthday has been set to the {}".format(r.table("userprofile").get(str(author.id))["birthday"].run(self.db, durability="soft")))
        
    @_set.command(aliases=["desc"])
    async def description(self, ctx, *, description):
        """Set your decription about yourself"""
        author = ctx.author
        if len(str(description)) > 300:
            await ctx.send("Descriptions are limited to 300 characters :no_entry:")
            return
        r.table("userprofile").get(str(author.id)).update({"description": description}).run(self.db, durability="soft")
        await ctx.send("Your description has been set it'll now be on your profile")
        
    @_set.command()
    async def background(self, ctx, image_url=None): 
        """Set your background on your profile to make it shine a bit more (Ideal resolution: 2560x1440)"""
        author = ctx.author
        if not image_url:
            if ctx.message.attachments:
                try: 
                    image_url = ctx.message.attachments[0].url.replace(".gif", ".png").replace(".webp", ".png")
                    try:
                        with open("profile-images/{}.png".format(ctx.author.id), "wb") as f:
                            f.write(requests.get(image_url).content)
                        image = Image.open("profile-images/{}.png".format(ctx.author.id))
                        image = image.resize((2560, 1440))
                        image.save("profile-images/{}.png".format(ctx.author.id))
                        return await ctx.send("Your background has been set.")
                    except:
                        return await ctx.send("I failed to download that image, I recommend a discord image or imgur as they are bound to work :no_entry:")
                except:
                    pass
            try:
                os.remove("profile-images/{}.png".format(ctx.author.id))
            except:
                pass
            await ctx.send("Your background has been reset.")
            return
        image_url = image_url.replace(".gif", ".png").replace(".webp", ".png")
        try:
            with open("profile-images/{}.png".format(ctx.author.id), "wb") as f:
                f.write(requests.get(image_url).content)
            image = Image.open("profile-images/{}.png".format(ctx.author.id))
            image = image.resize((2560, 1440))
            image.save("profile-images/{}.png".format(ctx.author.id))
            await ctx.send("Your background has been set.")
        except:
            return await ctx.send("I failed to download that image, I recommend a discord image or imgur as they are bound to work :no_entry:")
    
    @_set.command(aliases=["color"])
    async def colour(self, ctx, colour: discord.Colour): 
        """Set the accent colour of your profile"""
        author = ctx.author
        userdata = r.table("userprofile").get(str(author.id))
        if not userdata.run(self.db, durability="soft"):
            r.table("userprofile").insert({"id": str(author.id), "birthday": None, "description": None, "height": None, "birthday": None}).run(self.db, durability="soft")
        image = Image.new('RGBA', (273, 10), (colour.r, colour.g, colour.b))
        file = img.get_file(image)
        userdata.update({"colour": str(colour)}).run(self.db, durability="soft")
        await ctx.send(file=file, content="The text colour on your profile has been set.")
    

    @commands.command()
    async def birthdays(self, ctx):
        """See who's birthdays are upcoming within the next 30 days"""
        today = datetime.date.today()
        birthdays = r.table("userprofile").filter(lambda x: x["birthday"] != None).run(self.db, durability="soft")

        def get(data):
            date = data.split("/")
            return datetime.date(today.year, int(date[1]), int(date[0]))

        birthdays = {data["id"]: get(data["birthday"]) for data in birthdays}

        next_month = today + datetime.timedelta(days=30)
        birthdays = sorted(list(filter(lambda data: data[1] >= today and data[1] <= next_month, birthdays.items())), key=lambda x: time.mktime(x[1].timetuple()))

        msg = ""

        additionals = ctx.message.content[len(ctx.prefix + str(ctx.command)):].split(" ")
        
        if "--server" in additionals:
            members = self._get(ctx.guild.members)
        else:
            members = self._get(self.bot.get_all_members())

        for x in birthdays:
            try:
                user = members[int(x[0])]
                msg += "{} - {} {}\n".format(user, self.suffix(x[1].day) + " " + x[1].strftime("%B"), ":birthday:" if today == x[1] else "")
            except: 
                pass

        await ctx.send(embed=discord.Embed(title="Upcoming Birthdays 🍰", description=msg if msg != "" else "No one has an upcoming birthday", colour=0xffff00))

    def get_item(self, array, user_input: str):
        try:
            item = list(filter(lambda x: x["name"].lower() == user_input.lower(), array))[0]
        except IndexError:
            try:
                item = list(filter(lambda x: x["name"].lower().startswith(user_input), array))[0]
            except IndexError:
                try:
                    item = list(filter(lambda x: user_input.lower() in x["name"].lower(), array))[0]
                except IndexError:
                    return None
        return item

    def get_exact_item(self, array, item: str):
        try:
            item = list(filter(lambda x: x["name"].lower() == item.lower(), array))[0]
        except IndexError:
            return None
        return item

    def suffix(self, number: int):
        suffix = ""
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

    def _get(self, object):
        return {obj.id: obj for obj in object}

    def _vote_time(self, timestamp):
        m, s = divmod(timestamp - datetime.datetime.now().timestamp() + 43200, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if h < 0:
            time = None
        return time

    def convert(self, item):
        if item[:1].isdigit():
            index = item.find(" ")
            amount = item[:index]
            if amount.isdigit():
                amount = int(amount)
                item = item[index + 1:]
            else:
                amount = 1
        else:
            index = item.rfind(" ")
            amount = item[index + 1:]
            if amount.isdigit():
                amount = int(amount)
                item = item[:index]
            else:
                amount = 1
        return item, amount

    def upgrade_item(self, items, item, update: dict):
        items.remove(item)
        for key, value in update.items():
            item[key] += value
        items.append(item) 
        return items

    def add_mats(self, items, tuples, additional: dict=None):
        for item, amount in tuples:
            if item.title() in map(lambda x: x["name"], items):
                current = list(filter(lambda x: x["name"] == item.title(), items))[0]
                items.remove(current)
                current["amount"] += amount
                updated = current
            else:
                updated = {"name": item.title(), "amount": amount}
            if additional:
                updated.update(additional)
            items.append(updated)
        return items

    def remove_mats(self, items, tuples):
        for item, amount in tuples:
            current = list(filter(lambda x: x["name"] == item.title(), items))[0]
            items.remove(current)
            current["amount"] -= amount
            updated = current
            if updated["amount"] > 0:
                items.append(updated)
        return items

    def replace_item(self, items, item, new_item):
        items.remove(item)
        items.append(new_item)
        return items

    def update_item(self, items, item_name, additional: dict):
        item = list(filter(lambda x: x["name"] == item_name, items))[0]
        items.remove(item)
        item.update(additional)
        items.append(item)
        return items       

    def get_user_item(self, items, item_name):
        try:
            return list(filter(lambda x: x["name"] == item_name, items))[0]
        except IndexError:
            return {"name": item_name, "amount": 0}

    def get_user_pickaxe(self, user):
        items = r.table("bank").get(str(user.id))["items"].run(self.db)
        for x in items:
            if x["name"] in map(lambda x: x["name"], shop["picitems"]):
                return x
        return None

    def get_user_rod(self, user):
        items = r.table("bank").get(str(user.id))["items"].run(self.db)
        for x in items:
            if x["name"] in map(lambda x: x["name"], shop["roditems"]):
                return x
        return None

    def get_user_axe(self, user):
        items = r.table("bank").get(str(user.id))["items"].run(self.db)
        for x in items:
            if x["name"] in map(lambda x: x["name"], shop["axes"]):
                return x
        return None

    def has_pickaxe(self, user):
        items = r.table("bank").get(str(user.id))["items"].run(self.db)
        for x in items:
            if x["name"] in map(lambda x: x["name"], shop["picitems"]):
                return True
        return False

    def has_rod(self, user):
        items = r.table("bank").get(str(user.id))["items"].run(self.db)
        for x in items:
            if x["name"] in map(lambda x: x["name"], shop["roditems"]):
                return True
        return False

    def has_axe(self, user):
        items = r.table("bank").get(str(user.id))["items"].run(self.db)
        for x in items:
            if x["name"] in map(lambda x: x["name"], shop["axes"]):
                return True
        return False

def setup(bot, connection): 
    bot.add_cog(economy(bot, connection))