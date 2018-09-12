import discord
from discord.ext import commands
import os
from copy import deepcopy
from utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import choice as randchoice
from random import randint
from utils import arghelp
from copy import deepcopy
from utils import checks
from enum import Enum
from collections import Counter
import time
import logging
import re
import datetime
import math
from cogs import general
from PIL import Image, ImageDraw, ImageFont, ImageOps
from urllib.request import Request, urlopen
import json
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

class economy:
    """Make money"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/fun/marriage.json"
        self.data = dataIO.load_json(self.file_path)
        self.JSON = 'data/economy/birthday.json'
        self.settingss = dataIO.load_json(self.JSON)
        self.location = 'data/economy/bank.json'
        self.settings = dataIO.load_json(self.location)
        self._shop_file = 'data/economy/shop.json'
        self._shop = dataIO.load_json(self._shop_file)
        self._auction_file = 'data/economy/auction.json'
        self._auction = dataIO.load_json(self._auction_file) 
        self._mine_file = 'data/economy/materials.json'
        self._mine = dataIO.load_json(self._mine_file) 
        self._slots_file = 'data/economy/slots.json'
        self._slots = dataIO.load_json(self._slots_file)
        self._factories_file = 'data/economy/factory.json'
        self._factories = dataIO.load_json(self._factories_file)
        self._colour_file = 'data/economy/colour.json'
        self._colour = dataIO.load_json(self._colour_file)
        
        if "picitems" not in self._shop:
            self._shop["picitems"] = []
            dataIO.save_json(self._shop_file, self._shop)

        if "roditems" not in self._shop:
            self._shop["roditems"] = []
            dataIO.save_json(self._shop_file, self._shop)
            
        if "items" not in self._shop:
            self._shop["items"] = []
            dataIO.save_json(self._shop_file, self._shop)
    
        if "items" not in self._auction:
            self._auction["items"] = []
            dataIO.save_json(self._auction_file, self._auction)
            
        if "items" not in self._mine:
            self._mine["items"] = []
            dataIO.save_json(self._mine_file, self._mine)
            
        if "wins" not in self._slots:
            self._slots["wins"] = []
            dataIO.save_json(self._slots_file, self._slots)
            
        if "factory" not in self._factories:
            self._factories["factory"] = []
            dataIO.save_json(self._factories_file, self._factories)

        if "tax" not in self.settings:
            self.settings["tax"] = 0
            dataIO.save_json(self.location, self.settings)

    @commands.command()
    async def tax(self, ctx):
        s=discord.Embed(description="Their Balance: **${:,}**".format(self.settings["tax"]), colour=0xffff00)
        s.set_author(name="Sx4 the tax bot", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def resettax(self, ctx):
        self.settings["tax"] = 0
        dataIO.save_json(self.location, self.settings)
        await ctx.send("Done")
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def parse(self, ctx):
        code = ctx.message.content[8:]
        code = "    " + code.replace("\n", "\n    ")
        code = "async def __eval_function__():\n" + code

        additional = {}
        additional["self"] = self
        additional["ctx"] = ctx
        additional["channel"] = ctx.channel
        additional["author"] = ctx.author
        additional["server"] = ctx.guild

        try:
            exec(code, {**globals(), **additional}, locals())

            await locals()["__eval_function__"]()
        except Exception as e:
            await ctx.send(str(e))
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code):
        author = ctx.author
        server = ctx.guild
        channel = ctx.channel
        try:
            await ctx.send(str(await eval(code))) 
        except:
            try:
                await ctx.send(str(eval(code))) 
            except Exception as e:
                await ctx.send(str(e))

    @commands.command()
    async def trade(self, ctx, *, user: discord.Member):
        author = ctx.author
        if author == user:
            return await ctx.send("You can't trade with yourself :no_entry:")
        if user in filter(lambda x: x.bot, self.bot.get_all_members()):
            return await ctx.send("You can't trade with a bot :no_entry:")
        await self._set_bank(author)
        await self._set_bank_user(user)
        await ctx.send("What are you offering to the user? Respond below in this format "
        "`amount_of_money | amount_of_materials name_of_material, amount_of_materials name_of_material,... etc` "
        "If you're not trading money just put 0 and if you're not trading materials don't put the dash. Respond with cancel to cancel the trade (The user you want to trade with has to be online to accept your trade)",
        embed=discord.Embed(title="Example").set_image(url="https://cdn.discordapp.com/attachments/344091594972069888/481118196481523712/2018-08-20_16-10-29.gif"))
        tradeableitems = self._factories["factory"] + self._shop["miners"] + self._mine["items"] + self._shop["boosters"]
        def user_check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            response = await self.bot.wait_for("message", check=user_check, timeout=300)
            if response.content.lower() == "cancel":
                return await ctx.send("Cancelled.")
            if "|" in response.content:
                responsesplit = response.content.split("|")
                material = responsesplit[1]
                material = material.split(", " if ", " in response.content else ",")
                materials = [x[1:] if x.startswith(" ") else x for x in material]
                materials2 = []
                for x in materials:
                    result = re.search('(.*)"(.*)"', str(x))
                    if result:
                        try:
                            amount = int(result.group(1))
                            materialname = result.group(2)
                        except:
                            return await ctx.send("Follow the format given above :no_entry:")
                    else:
                        try:
                            amount = int(x.split(" ")[0])
                            materialname = x.split(" ")[1]
                        except:
                            return await ctx.send("Follow the format given above :no_entry:")
                    if amount > 0:
                        i = 0
                        for x in tradeableitems:
                            if materialname.lower() == x["name"].lower():
                                i += 1    
                                useramount = self.settings["user"][str(author.id)]["items"].count(x["name"])
                                if useramount < amount:
                                    return await ctx.send("You don't have that much `{}` to trade :no_entry:".format(x["name"])) 
                                materials2.append("{} {}".format(amount, x["name"]))
                        if i == 0:
                            return await ctx.send("One of the materials you offered doesn't exist check your spelling :no_entry:")
                try:
                    money = int(responsesplit[0])
                except:
                    return await ctx.send("Invalid money amount :no_entry:")
                if money > self.settings["user"][str(author.id)]["balance"]:
                    return await ctx.send("You don't have that much money :no_entry:")
                if money <= 0:
                    money = None
                if not money and materials2 == []:
                    return await ctx.send("You have to offer something :no_entry:")
                usergetsmoney = money if money else None
                usergetsmaterials = materials2
                await ctx.send(content="What would you like from the the user? Respond below in this format "
                "`amount_of_money | amount_of_materials name_of_material, amount_of_materials name_of_material,... etc` "
                "If you're not trading money just put 0 and if you're not trading materials don't put the dash. (The user you want to trade with has to be online to accept your trade)",
                embed=discord.Embed(title="What you're offering", description="{}\n{}".format("$" + str(money) if money else "", "\n".join(materials2))))
            else:
                try:
                    money = int(response.content)
                except:
                    return await ctx.send("Follow the format given above :no_entry:")
                if money > self.settings["user"][str(author.id)]["balance"]:
                    return await ctx.send("You don't have that much money :no_entry:")
                if money <= 0:
                    return await ctx.send("You need to give some money at least :no_entry:")
                usergetsmaterials = None
                usergetsmoney = money
                await ctx.send(content="What would you like from the the user? Respond below in this format "
                "`amount_of_money | amount_of_materials name_of_material, amount_of_materials name_of_material,... etc` "
                "If you're not trading money just put 0 and if you're not trading materials don't put the dash. (The user you want to trade with has to be online to accept your trade)",
                embed=discord.Embed(title="What you're offering", description="${}".format(money)))
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")
        try:
            response = await self.bot.wait_for("message", check=user_check, timeout=300)
            if response.content.lower() == "cancel":
                return await ctx.send("Cancelled.")
            if "|" in response.content:
                responsesplit = response.content.split("|")
                material = responsesplit[1]
                material = material.split(", " if ", " in response.content else ",")
                materials = [x[1:] if x.startswith(" ") else x for x in material]
                materials2 = []
                for x in materials:
                    result = re.search('(.*)"(.*)"', str(x))
                    if result:
                        try:
                            amount = int(result.group(1))
                            materialname = result.group(2)
                        except:
                            return await ctx.send("Follow the format given above :no_entry:")
                    else:
                        try:
                            amount = int(x.split(" ")[0])
                            materialname = x.split(" ")[1]
                        except:
                            return await ctx.send("Follow the format given above :no_entry:")
                    if amount > 0:
                        i = 0
                        for x in tradeableitems:
                            if materialname.lower() == x["name"].lower():
                                i += 1    
                                useramount = self.settings["user"][str(user.id)]["items"].count(x["name"])
                                if useramount < amount:
                                    return await ctx.send("The user doesn't have that much `{}` to trade :no_entry:".format(x["name"])) 
                                materials2.append("{} {}".format(amount, x["name"]))
                        if i == 0:
                            return await ctx.send("One of the materials you offered doesn't exist check your spelling :no_entry:")
                try:
                    money = int(responsesplit[0])
                except:
                    return await ctx.send("Invalid money amount :no_entry:")
                if money > self.settings["user"][str(user.id)]["balance"]:
                    return await ctx.send("The user doesn't have that much money :no_entry:")
                if money <= 0:
                    money = None
                if not money and materials2 == []:
                    return await ctx.send("You have to offer something :no_entry:")
                authorgetsmoney = money if money else None
                authorgetsmaterials = materials2
                await ctx.send(embed=discord.Embed(title="The Final Trade").add_field(name="{} Gets".format(user), value="{}\n{}".format("$" + str(usergetsmoney) if usergetsmoney else "", "\n".join(usergetsmaterials) if usergetsmaterials else ""),
                inline=False).add_field(name="{} Gets".format(author), value="{}\n{}".format("$" + str(authorgetsmoney) if authorgetsmoney else "", "\n".join(authorgetsmaterials) if authorgetsmaterials else "")).set_footer(
                text="{} needs to type yes to accept the trade or it will be declined".format(user)))
            else:
                try:
                    money = int(response.content)
                except:
                    return await ctx.send("Follow the format given above :no_entry:")
                if money > self.settings["user"][str(user.id)]["balance"]:
                    return await ctx.send("The user doesn't have that much money :no_entry:")
                if money <= 0:
                    return await ctx.send("You need to give some money at least :no_entry:")
                if not usergetsmaterials:
                    return await ctx.send("You can't trade just money :no_entry:")
                authorgetsmaterials = None
                authorgetsmoney = money
                await ctx.send(embed=discord.Embed(title="The Final Trade").add_field(name="{} Gets".format(user), value="{}\n{}".format("$" + str(usergetsmoney) if usergetsmoney else "", "\n".join(usergetsmaterials) if usergetsmaterials else ""),
                inline=False).add_field(name="{} Gets".format(author), value="{}\n{}".format("$" + str(authorgetsmoney) if authorgetsmoney else "", "\n".join(authorgetsmaterials) if authorgetsmaterials else "")).set_footer(
                text="{} needs to type yes to accept the trade or it will be declined".format(user)))
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")
        try:
            def check(m):
                return m.author == user and m.channel == ctx.channel
            userresponse = await self.bot.wait_for("message", check=check, timeout=60)
            if userresponse.content.lower() == "yes":
                if authorgetsmoney:
                    if self.settings["user"][str(user.id)]["balance"] < authorgetsmoney:
                        return await ctx.send("The user no longer has enough money to give like shown in the deal :no_entry:")
                if usergetsmoney:
                    if self.settings["user"][str(author.id)]["balance"] < usergetsmoney:
                        return await ctx.send("You no longer have enough money to give like shown in the deal :no_entry:")
                if usergetsmaterials:
                    for x in usergetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        if self.settings["user"][str(author.id)]["items"].count(item) < int(amount):
                            return await ctx.send("You no longer have enough materials to continue the deal :no_entry:")
                if authorgetsmaterials:
                    for x in authorgetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        if self.settings["user"][str(user.id)]["items"].count(item) < int(amount):
                            return await ctx.send("The user longer has enough materials to continue the deal :no_entry:")
                if usergetsmaterials:
                    for x in usergetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        for x in range(int(amount)):
                            self.settings["user"][str(user.id)]["items"].append(item)
                            self.settings["user"][str(author.id)]["items"].remove(item)
                if authorgetsmaterials:
                    for x in authorgetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        for x in range(int(amount)):
                            self.settings["user"][str(user.id)]["items"].remove(item)
                            self.settings["user"][str(author.id)]["items"].append(item)
                if authorgetsmoney:
                    self.settings["user"][str(author.id)]["balance"] += authorgetsmoney
                    self.settings["user"][str(user.id)]["balance"] -= authorgetsmoney
                if usergetsmoney:
                    self.settings["user"][str(author.id)]["balance"] -= usergetsmoney
                    self.settings["user"][str(user.id)]["balance"] += usergetsmoney
                dataIO.save_json(self.location, self.settings)
                await ctx.send("All items and money have been transferred <:done:403285928233402378>")
            else:
                await ctx.send("Trade Declined.")
        except asyncio.TimeoutError:
            return await ctx.send("Timed out :stopwatch:")

    @commands.group()
    async def booster(self, ctx):
        """Buy and activate boosters here"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            await self._set_bank(ctx.author)

    @booster.command(name="shop")
    async def _shop_(self, ctx):
        """Check what boosters you can buy"""
        s=discord.Embed(description="You can buy boosters to avoid annoying things like cooldowns on commands", colour=0xfff90d)
        s.set_author(name="Booster Shop", icon_url=self.bot.user.avatar_url)
        for item in self._shop["boosters"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDescription: {}".format(item["price"], item["description"]))
        try:    
            s.set_footer(text="Use s?booster buy <item> to buy an item. | Your balance: ${:,}".format(self.settings["user"][str(ctx.author.id)]["balance"]))
        except:
            s.set_footer(text="Use s?booster buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @booster.command(name="buy")
    async def _buy_(self, ctx, *, booster):
        """Buy booster here"""
        for x in self._shop["boosters"]:
            if x["name"].lower() == booster.lower():
                if x["price"] <= self.settings["user"][str(ctx.author.id)]["balance"]:
                    self.settings["user"][str(ctx.author.id)]["balance"] -= x["price"]
                    self.settings["user"][str(ctx.author.id)]["items"].append(x["name"])
                    dataIO.save_json(self.location, self.settings)
                    return await ctx.send("You just bought the booster `{}` for **${:,}** :ok_hand:".format(x["name"], x["price"]))
                else:
                    return await ctx.send("You don't have enough money to buy that booster :no_entry:")
        await ctx.send("That booster does not exist :no_entry:")

    @booster.command()
    async def activate(self, ctx, *, booster):
        """Activate booster which say they needed to be activated here"""
        if booster.lower() == "lended pickaxe":
            if booster.title() in self.settings["user"][str(ctx.author.id)]["items"]:
                has_pick = False
                for item in self.settings["user"][str(ctx.author.id)]["items"]:
                    for pick in self._shop["picitems"]:
                        if pick["name"] == item:
                            has_pick = True
                            break
                if has_pick:
                    self.settings["user"][str(ctx.author.id)]["picktime"] = None
                    self.settings["user"][str(ctx.author.id)]["items"].remove(booster.title())
                    await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster.title()))
                else:
                    await ctx.send("You do not own a pickaxe you should probably own one to use this booster :no_entry:")
            else:
                await ctx.send("You do not own that booster :no_entry:")
        elif booster.lower() == "miner repair":
            if booster.title() in self.settings["user"][str(ctx.author.id)]["items"]:
                has_miner = False
                for item in self.settings["user"][str(ctx.author.id)]["items"]:
                    for miner in self._shop["miners"]:
                        if miner["name"] == item:
                            has_miner = True
                            break
                if has_miner:
                    self.settings["user"][str(ctx.author.id)]["minertime"] = None
                    self.settings["user"][str(ctx.author.id)]["items"].remove(booster.title())
                    await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster.title()))
                else:
                    await ctx.send("You do not own a miner you should probably own one to use this booster :no_entry:")
            else:
                await ctx.send("You do not own that booster :no_entry:")
        else:
            await ctx.send("That booster doesn't exist or isn't activatable :no_entry:")
        dataIO.save_json(self.location, self.settings)

    @commands.command(aliases=["referralurl"])
    async def referral(self, ctx, user: discord.Member=None):
        """Get given your referral urls for votes"""
        if not user:
            user = ctx.author
        await ctx.send("__**{}'s** referral urls__\n<https://discordbots.org/bot/440996323156819968/vote?referral={}> (Sx4)\n<https://discordbots.org/bot/411916947773587456/vote?referral={}> (Jockie Music)".format(user, user.id, user.id))
 
    @commands.command()
    async def votebonus(self, ctx):
        """Get some extra credits by simply upvoting the bot on dbl"""
        author = ctx.author
        try:
            request = requests.get("http://localhost:8080/440996323156819968/votes/user/{}/unused/use".format(author.id), headers={"Authorization": Token.jockie()}).json()
            requestjockie = requests.get("http://localhost:8080/411916947773587456/votes/user/{}/unused/use".format(author.id), headers={"Authorization": Token.jockie_music()}).json()
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
                        money += 500 if vote["weekend"] else 250
                        if "referral" in vote["query"]:
                            if type(vote["query"]["referral"]) == str:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"]))
                            elif type(vote["query"]["referral"]) == list:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"][0]))
                            else:
                                return await ctx.send("No clue what you've done there to cause this, report this to the Sx4 Support Server or add Joakim#9814 and spam his dms telling him you found this. Thank you!")
                            if user and user != author and not user.bot:
                                if str(user.id) in self.settings["user"]:
                                    self.settings["user"][str(user.id)]["balance"] += 200 if vote["weekend"] else 100
                                    referred.append(user)
                if votes2:
                    for vote in votes2:
                        money += 300 if vote["weekend"] else 150
                        if "referral" in vote["query"]:
                            if type(vote["query"]["referral"]) == str:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"]))
                            elif type(vote["query"]["referral"]) == list:
                                user = discord.utils.get(self.bot.get_all_members(), id=int(vote["query"]["referral"][0]))
                            else:
                                return await ctx.send("No clue what you've done there to cause this, report this to the Sx4 Support Server or add Joakim#9814 and spam his dms telling him you found this. Thank you!")
                            if user and user != author and not user.bot:
                                if str(user.id) in self.settings["user"]:
                                    self.settings["user"][str(user.id)]["balance"] += 150 if vote["weekend"] else 75
                                    referred.append(user)
                    
                await ctx.send("You have voted for the bots **{}** {} since you last used the command gathering you a total of **${:,}**, Vote for the bots again in 12 hours for more money. Referred users: {}".format(
                amount, "time" if amount == 1 else "times", money, ", ".join(map(lambda x: str(x), list(set(referred)))) if referred != [] else "None"))
                await self._set_bank(author)
                self.settings["user"][str(author.id)]["balance"] += money
                dataIO.save_json(self.location, self.settings)
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
                s.add_field(name="Sx4", value="{}".format("**[You have voted recently you can vote for the bot again in {}](https://discordbots.org/bot/440996323156819968/vote)**".format(timesx4)
                if timesx4 else "**[You can vote for Sx4 for an extra ${}](https://discordbots.org/bot/440996323156819968/vote)**".format(500 if weekend else 250)), inline=False)
                s.add_field(name="Jockie Music", value="{}".format("**[You have voted recently you can vote for the bot again in {}](https://discordbots.org/bot/411916947773587456/vote)**".format(timejockie)
                if timejockie else "**[You can vote for Jockie Music for an extra ${}](https://discordbots.org/bot/411916947773587456/vote)**".format(300 if weekend else 150)), inline=False)
                await ctx.send(embed=s)
            else:
                await ctx.send("Ops, something unexpected happened")

    @commands.command()
    async def badges(self, ctx):
        s=discord.Embed(title="Badges", description=("<:server_owner:441255213450526730> - Be an owner of a server in which Sx4 is in\n"
        "<:developer:441255213068845056> - Be a developer of Sx4\n<:helper:441255213131628554> - You have at some point contributed to the bot\n"
        "<:donator:441255213224034325> - Donate to Sx4 either through PayPal or Patreon\n<:profile_editor:441255213207126016> - Edit your profile"
		"\n<:married:441255213106593803> - Be married to someone on the bot\n<:playing:441255213513572358> - Have a playing status\n<:streaming:441255213106724865> - Have a streaming status"
        "\n<:insx4server:472895584856965132> - Be in the Sx4 Support Server"))
        await ctx.send(embed=s)
        

    @commands.command(no_pm=True)
    async def profile(self, ctx, *, user: discord.Member=None):
        """Lists aspects about you on discord with Sx4. Defaults to author."""
        author = ctx.author
        server = ctx.guild
        if not user:
            user = author
        if user.bot:
            await ctx.send("Bots don't have profiles :no_entry:")
            return
        if "user" not in self.settings: 
            self.settings["user"] = {} 
            dataIO.save_json(self.location, self.settings)
        if str(user.id) not in self.settings["user"]: 
            self.settings["user"][str(user.id)] = {}
            dataIO.save_json(self.location, self.settings)
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(user.id) not in self.data["user"]:
            self.data["user"][str(user.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][str(user.id)]:
            self.data["user"][str(user.id)]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(user.id) not in self.settingss:
            self.settingss[str(user.id)] = {}
            dataIO.save_json(self.JSON, self.settingss)
        if "BIRTHDAY" not in self.settingss[str(user.id)]:
            self.settingss[str(user.id)]["BIRTHDAY"] = None 
            dataIO.save_json(self.JSON, self.settingss)
        if "DESCRIPTION" not in self.settingss[str(user.id)]:
            self.settingss[str(user.id)]["DESCRIPTION"] = None
            dataIO.save_json(self.JSON, self.settingss)
        if "HEIGHT" not in self.settingss[str(user.id)]:
            self.settingss[str(user.id)]["HEIGHT"] = None
            dataIO.save_json(self.JSON, self.settingss)
        if str(user.id) not in self._colour:
            self._colour[str(user.id)] = {}
            dataIO.save_json(self._colour_file, self._colour)
        await self._set_bank_user(user)
        msg = await self._list_marriage(user)
        if self._colour[str(user.id)] != {}:
            colour = discord.Colour(self._colour[str(user.id)])
            colour = (colour.r, colour.g, colour.b)
        else:
            colour = (255, 255, 255)
        try:
            image = Image.open("profile-images/{}.png".format(user.id))
        except:
            image = Image.new("RGBA", (2560, 1440), (114, 137, 218))
        if not self.settingss[str(user.id)]["BIRTHDAY"]:
            self.settingss[str(user.id)]["BIRTHDAY"] = "Not set"
        if not self.settingss[str(user.id)]["DESCRIPTION"]:
            self.settingss[str(user.id)]["DESCRIPTION"] = "Not set"
        if not self.settingss[str(user.id)]["HEIGHT"]:
            self.settingss[str(user.id)]["HEIGHT"] = "Not set"
        with open("avatar.png", "wb") as f:
            f.write(requests.get(user.avatar_url).content)
        avatar = Image.open("avatar.png")
        avatar = avatar.resize((450, 450))
        size = (avatar.size[0] * 6, avatar.size[1] * 6)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + size, fill=255)
        mask = mask.resize(avatar.size)
        avatar.putalpha(mask)
        output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        outline = Image.new("RGBA", (470, 470), colour)
        size = (outline.size[0] * 6, outline.size[1] * 6)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + size, fill=255)
        mask = mask.resize(outline.size)
        outline.putalpha(mask)
        output2 = ImageOps.fit(outline, mask.size, centering=(0.5, 0.5))
        output2.putalpha(mask)
        nameplate = Image.new("RGBA", (2000, 500), (35, 39, 42))
        statsplate = Image.new("RGBA", (2000, 150), (44, 47, 51))
        badgeplate = Image.new("RGBA", (560, 650), (44, 47, 51))
        whiteborderlong = Image.new("RGBA", (2000, 10), colour)
        whiteborderlong2 = Image.new("RGBA", (2560, 10), colour)
        whiteborderheight = Image.new("RGBA", (10, 510), colour)
        smallwhiteborder = Image.new("RGBA", (10, 150), colour)
        boxborderside = Image.new("RGBA", (10, 600), colour)
        boxborderheight = Image.new("RGBA", (1010, 10), colour)
        transdesc = Image.new("RGBA", (1000, 600), (0, 0, 0, 175))
        image.paste(nameplate, (0, 0), nameplate)
        image.paste(output2, (15, 15), output2)
        image.paste(output, (25, 25), output)
        image.paste(statsplate, (0, 500), statsplate)
        image.paste(badgeplate, (2000, 0), badgeplate)
        image.paste(transdesc, (70, 750), transdesc)
        image.paste(transdesc, (1490, 750), transdesc)
        x = 0
        y = 0
        if [x for x in self.bot.guilds if user == x.owner]:
            serverowner = Image.open("badges/server_owner.png") 
            serverowner = serverowner.resize((100, 100))
            image.paste(serverowner, (2030 + x, 130 + y), serverowner)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if [x for x in self.bot.get_guild(330399610273136641).members if user == x and discord.utils.get(self.bot.get_guild(330399610273136641).roles, id=330400064541425664) in x.roles]:
            developer = Image.open("badges/developer.png") 
            developer = developer.resize((100, 100))
            image.paste(developer, (2030 + x, 130 + y), developer)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if user.id == 153286414212005888 or user.id == 285451236952768512 or user.id == 388424304678666240 or user.id == 250815960250974209 or user.id == 223424602150273024:
            helper = Image.open("badges/helper.png") 
            helper = helper.resize((100, 100))
            image.paste(helper, (2030 + x, 130 + y), helper)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if [x for x in self.bot.get_guild(330399610273136641).members if user == x and discord.utils.get(self.bot.get_guild(330399610273136641).roles, id=355083059336314881) in x.roles]:
            donator = Image.open("badges/donator.png") 
            donator = donator.resize((100, 100))
            image.paste(donator, (2030 + x, 130 + y), donator)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if not self.settingss[str(user.id)]["BIRTHDAY"] and not self.settingss[str(user.id)]["DESCRIPTION"] and not self.settingss[str(user.id)]["HEIGHT"]:
            pass
        elif self.settingss[str(user.id)]["BIRTHDAY"] == "Not set" and self.settingss[str(user.id)]["DESCRIPTION"] == "Not set" and self.settingss[str(user.id)]["HEIGHT"] == "Not set":
            pass
        else:
            profileeditor = Image.open("badges/profile_editor.png") 
            profileeditor = profileeditor.resize((100, 100))
            image.paste(profileeditor, (2030 + x, 130 + y), profileeditor)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if user in self.bot.get_guild(330399610273136641).members:
            insx4 = Image.open("badges/sx4-circle.png") 
            insx4 = insx4.resize((100, 100))
            image.paste(insx4, (2030 + x, 130 + y), insx4)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if msg != "No-one\nMarry someone to get a free badge":
            married = Image.open("badges/married.png") 
            married = married.resize((100, 100))
            image.paste(married, (2030 + x, 130 + y), married)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        if not user.activity:
            pass
        elif user.activity:
            playing = Image.open("badges/playing.png") 
            playing = playing.resize((100, 100))
            image.paste(playing, (2030 + x, 130 + y), playing)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        elif user.activity.url:
            streaming = Image.open("badges/streaming.png") 
            streaming = streaming.resize((100, 100))
            image.paste(streaming, (2030 + x, 130 + y), streaming)
            x += 130
            if x >= 520:
                y += 120
                x = 0
        image.paste(boxborderside, (70, 750), boxborderside)
        image.paste(boxborderside, (1070, 750), boxborderside)
        image.paste(boxborderside, (1490, 750), boxborderside)
        image.paste(boxborderside, (2490, 750), boxborderside)
        image.paste(boxborderheight, (70, 750), boxborderheight)
        image.paste(boxborderheight, (70, 1350), boxborderheight)
        image.paste(boxborderheight, (1490, 750), boxborderheight)
        image.paste(boxborderheight, (1490, 1350), boxborderheight)
        image.paste(whiteborderlong, (0, 500), whiteborderlong)
        image.paste(whiteborderlong2, (0, 650), whiteborderlong2)
        image.paste(whiteborderheight, (2000, 0), whiteborderheight)
        image.paste(smallwhiteborder, (495, 500), smallwhiteborder)
        image.paste(smallwhiteborder, (995, 500), smallwhiteborder)
        image.paste(smallwhiteborder, (1495, 500), smallwhiteborder)
        image.paste(smallwhiteborder, (2000, 510), smallwhiteborder)
        draw = ImageDraw.Draw(image)
        fontsize = 216
        left = 720
        down = 90
        i = 0
        for x in range(len(str(user))):
            fontsize -= 4
            left -= 5
            i += 1
            down += 2
            if i >= 12 and i <= 18:
                fontsize -= 3
                down += 1
            if i >= 28:
                left -= 1
                down += 1
                fontsize += 2
        n = 0
        m = 46
        times = 0 
        description = ""
        for x in range(math.ceil(len(str(self.settingss[str(user.id)]["DESCRIPTION"]))/46)+1):
            if [x for x in self.settingss[str(user.id)]["DESCRIPTION"] if " " in x]:
                for x in range(len([x for x in self.settingss[str(user.id)]["DESCRIPTION"] if " " in x])+1):
                    while self.settingss[str(user.id)]["DESCRIPTION"][m-1:m] != " " and m != 0 and m != len(str(self.settingss[str(user.id)]["DESCRIPTION"])):
                        m -= 1
                    times += 46
                    if m == 0:
                        n = times - 46
                        m = times
            description += self.settingss[str(user.id)]["DESCRIPTION"][n:m] + "\n"
            n = m
            m += 50
        font = ImageFont.truetype("exo.regular.otf", fontsize)
        fontstats = ImageFont.truetype("exo.regular.otf", 45)
        fontbig = ImageFont.truetype("exo.regular.otf", 70)
        draw.text((left, down), str(user), colour, font=font)
        draw.text((20, 545), "Reputation: {}".format(self.settings["user"][str(user.id)]["rep"]), colour, font=fontstats)
        draw.text((520, 545), "Balance: ${}".format(self.settings["user"][str(user.id)]["balance"]), colour, font=fontstats)
        draw.text((1020, 545), "Birthday: {}".format(self.settingss[str(user.id)]["BIRTHDAY"]), colour, font=fontstats)
        draw.text((1520, 545), "Height: {}".format(self.settingss[str(user.id)]["HEIGHT"]), colour, font=fontstats)
        draw.text((2160, 20), "Badges", colour, font=fontbig)
        draw.text((95, 770), "Description", colour, font=fontbig)
        draw.text((95, 870), description, colour, font=fontstats)
        draw.text((1515, 770), "Partners", colour, font=fontbig)
        draw.text((1515, 870), msg, colour, font=fontstats)
        image.save("test.png")
        await ctx.send(file=discord.File("test.png", "test.png"))
        try:
            os.remove("test.png")
        except:
            pass
        try:
            os.remove("avatar.png")
        except: 
            pass
        
    @commands.command(aliases=["pd", "payday"])
    async def daily(self, ctx):
        """Collect your daily money"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        await self._set_bank(author)
        if not self.settings["user"][str(author.id)]["streaktime"]:
            self.settings["user"][str(author.id)]["streaktime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + 100
            self.settings["user"][str(author.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            dataIO.save_json(self.location, self.settings)
            return
        m, s = divmod(self.settings["user"][str(author.id)]["streaktime"] - ctx.message.created_at.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["streaktime"] <= 86400:
            await ctx.send("You are too early, come collect your money again in {}".format(time))
            return
        elif ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["streaktime"] <= 172800:
            self.settings["user"][str(author.id)]["streaktime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["streak"] = self.settings["user"][str(author.id)]["streak"] + 1
            if  self.settings["user"][str(author.id)]["streak"] == 1:
                money = 120
            if self.settings["user"][str(author.id)]["streak"] == 2:
                money = 145
            if self.settings["user"][str(author.id)]["streak"] == 3:
                money = 170
            if self.settings["user"][str(author.id)]["streak"] == 4:
                money = 200
            if self.settings["user"][str(author.id)]["streak"] >= 5:
                money = 250
            self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + money
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You have collected your daily money! (**+${}**)\nYou had a bonus of ${} for having a {} day streak.".format(money, (money-100), self.settings["user"][str(author.id)]["streak"]), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            
            dataIO.save_json(self.location, self.settings)
            return
        else: 
            self.settings["user"][str(author.id)]["streaktime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + 100
            self.settings["user"][str(author.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
    @commands.command()
    async def rep(self, ctx, user: discord.Member):
        """Give reputation to another user"""
        server = ctx.guild
        author = ctx.author
        if user.bot:
            await ctx.send("Bots are useless unless it's me, so no reputation for them :no_entry:")
            return
        await self._set_bank(author)
        await self._set_bank_user(user)
        if user == author:
            await ctx.send("You can not give reputation to yourself :no_entry:")
            return
        if not self.settings["user"][str(author.id)]["reptime"]:
            self.settings["user"][str(author.id)]["reptime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(user.id)]["rep"] = self.settings["user"][str(user.id)]["rep"] + 1
            dataIO.save_json(self.location, self.settings)
            await ctx.send("**+1**, {} has gained reputation".format(user.name))
            return
        m, s = divmod(self.settings["user"][str(author.id)]["reptime"] - ctx.message.created_at.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["reptime"] <= 86400:
            await ctx.send("You are too early, give out your reputation in {}".format(time))
            return
        else:
            self.settings["user"][str(author.id)]["reptime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(user.id)]["rep"] = self.settings["user"][str(user.id)]["rep"] + 1
            dataIO.save_json(self.location, self.settings)
            await ctx.send("**+1**, {} has gained reputation".format(user.name))
            return
            
    @commands.command(aliases=["bal"])
    async def balance(self, ctx, *, user: discord.Member=None):
        """Check how much money you have"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if not user or user == ctx.author:
            user = ctx.author
            if user.bot:
                return await ctx.send("Bots can't make money :no_entry:")
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Your balance: **${:,}**".format(self.settings["user"][str(user.id)]["balance"]), colour=colour)
            except:
                s=discord.Embed(description="Your balance: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            if user.bot:
                return await ctx.send("Bots can't make money :no_entry:")
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Their balance: **${:,}**".format(self.settings["user"][str(user.id)]["balance"]), colour=colour)
            except:
                s=discord.Embed(description="Their balance: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(name="winnings")
    async def _winnings(self, ctx, user: discord.Member=None):
        if not user or user == ctx.author:
            user = ctx.author
            if user.bot:
                return await ctx.send("Bots can't gamble :no_entry:")
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Your winnings: **${:,}**".format(self.settings["user"][str(user.id)]["winnings"]), colour=user.colour)
            except:
                s=discord.Embed(description="Your winnings: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            if user.bot:
                return await ctx.send("Bots can't gamble :no_entry:")
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Their winnings: **${:,}**".format(self.settings["user"][str(user.id)]["winnings"]), colour=user.colour)
            except:
                s=discord.Embed(description="Their winnings: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(name="networth")
    async def _networth(self, ctx, *, user: discord.Member=None):
        check = False
        if not user:
            user = ctx.author
            check = True
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        all_items = self._shop["picitems"] + self._shop["items"] + self._mine["items"] + self._shop["roditems"] + self._shop["miners"] + self._shop["boosters"]
        if str(user.id) in self.settings["user"]:
            user_data = self.settings["user"][str(user.id)] 
            worth = 0
            items = [item for item in all_items if item["name"] in user_data["items"]]
            for item in items:
                if "durability" in item and item["name"].split(" ")[1] == "Pickaxe":
                    worth += round((item["price"]/item["durability"]) * user_data["pickdur"])
                elif "durability" in item and item["name"].split(" ")[1] == "Rod":
                    worth += round((item["price"]/item["durability"]) * user_data["roddur"])
                else:
                    worth += item["price"] * user_data["items"].count(item["name"])
            for item2 in [item for item in self._factories["factory"] if item["name"] in user_data["items"]]:
                for item3 in self._mine["items"]:
                    if item3["name"] == item2["item"]:
                        worth += item2["price"]*item3["price"]
            worth += user_data["balance"]
        if check is True or user == ctx.author:
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Your networth: **${:,}**".format(worth), colour=colour)
            except:
                s=discord.Embed(description="Your networth: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            await self._set_bank_user(user)
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
        if self.settings["user"][str(author.id)]["balance"] <= 0:
            await ctx.send("You don't have enough money to do double or nothing :no_entry:")
            ctx.command.reset_cooldown(ctx)
            return
        msg = await ctx.send("This will bet **${:,}**, are you sure you want to bet this?\nYes or No".format(self.settings["user"][str(author.id)]["balance"]))
        try:
            def don(m):
                return m.author == ctx.author
            response = await self.bot.wait_for("message", check=don, timeout=30)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("The bet has been canceled.")
            ctx.command.reset_cooldown(ctx)
            return
        if "yes" in response.content.lower():
            await msg.delete()
        else:
            await msg.delete()
            await ctx.send("The bet has been canceled.")
            ctx.command.reset_cooldown(ctx)
            return
        number = randint(0, 1)
        message = await ctx.send("You just put **${:,}** on the line and...".format(self.settings["user"][str(author.id)]["balance"]))
        await asyncio.sleep(2)
        if number == 0:
            await message.edit(content="You lost it all! **-${:,}**".format(self.settings["user"][str(author.id)]["balance"]))
            self.settings["user"][str(author.id)]["winnings"] -= self.settings["user"][str(author.id)]["balance"]
            self.settings["user"][str(author.id)]["balance"] = 0
        if number == 1:
            await message.edit(content="You double your money! **+${:,}**".format(self.settings["user"][str(author.id)]["balance"]))
            self.settings["user"][str(author.id)]["winnings"] += self.settings["user"][str(author.id)]["balance"]
            self.settings["user"][str(author.id)]["balance"] *= 2
        dataIO.save_json(self.location, self.settings) 
        ctx.command.reset_cooldown(ctx)
            
    @commands.command()
    async def shop(self, ctx):    
        """Check what you can buy"""
        s=discord.Embed(description="Sx4 shop use your currency in Sx4 to buy items", colour=0xfff90d)
        s.set_author(name="Shop", icon_url=self.bot.user.avatar_url)
        for item in self._shop["roditems"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDurability: {}".format(item["price"], item["durability"]))
        for item in self._shop["picitems"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDurability: {}".format(item["price"], item["durability"]))
        try:    
            s.set_footer(text="Use s?shopbuy <item> to buy an item. | Your balance: ${:,}".format(self.settings["user"][str(ctx.author.id)]["balance"]))
        except:
            s.set_footer(text="Use s?shopbuy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @commands.group()
    async def miner(self, ctx):
        """Buys miners and get materials every 2 hours"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            await self._set_bank(ctx.author)

    @miner.command(name="shop")
    async def __shop(self, ctx):
        """View the miner shop"""
        s=discord.Embed(description="Buy miners for an easier way to gather materials", colour=0xfff90d)
        s.set_author(name="Miners", icon_url=self.bot.user.avatar_url)
        for item in self._shop["miners"]:
            s.add_field(name=item["name"], value="Price: ${:,}".format(item["price"]))
        try:    
            s.set_footer(text="Use s?miner buy <item> to buy an item. | Your balance: ${:,}".format(self.settings["user"][str(ctx.author.id)]["balance"]))
        except:
            s.set_footer(text="Use s?miner buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @miner.command(name="buy")
    async def _buy(self, ctx, *, miner: str):
        """Buy a miner"""
        for item in self._shop["miners"]:
            if item["name"].lower() == miner.lower():
                if self.settings["user"][str(ctx.author.id)]["balance"] >= item["price"]:
                    self.settings["user"][str(ctx.author.id)]["items"].append(item["name"].title())
                    self.settings["user"][str(ctx.author.id)]["balance"] -= item["price"]
                    await ctx.send("You just bought a `{}` for **${:,}** :ok_hand:".format(item["name"].title(), item["price"])) 
                    return dataIO.save_json(self.location, self.settings)
                else:
                    return await ctx.send("You do not have enough money to buy this miner :no_entry:")
        await ctx.send("That is not a valid miner :no_entry:")

    @miner.command(name="collect")
    async def _collect(self, ctx):
        """Collect money from your miners"""
        i = 0
        author = ctx.author
        for miner in self._shop["miners"]:
            for item in self.settings["user"][str(author.id)]["items"]:
                if item == miner["name"]:
                    i += 1
        if i == 0:
            return await ctx.send("You do not own any miners :no_entry:")
        if not self.settings["user"][str(author.id)]["minertime"]:
            materials = []
            for miner in self._shop["miners"]:
                for item in self.settings["user"][str(author.id)]["items"]:
                    if item == miner["name"]:
                        for x in range(miner["max_mats"]):
                            for mat in self._mine["items"]:
                                if round(mat["rand_max"] * miner["multiplier"]) <= 0:
                                    number = 1
                                else:
                                    number = round(mat["rand_max"] * miner["multiplier"])
                                chance = randint(0, number)
                                if chance == 0:
                                    materials.append({"name": mat["name"], "emote": mat["emote"]})
            msg = ", ".join(set(map(lambda x: x["name"] + " x" + str(list(map(lambda x: x["name"], materials)).count(x["name"])) + x["emote"], materials))) if materials != [] else "Absolutely nothing"
            s=discord.Embed(colour=ctx.author.colour, description="You used your miners and gathered these materials: {}".format(msg)) 
            s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=s)  
            for x in materials:
                self.settings["user"][str(author.id)]["items"].append(x["name"])
            self.settings["user"][str(author.id)]["minertime"] = ctx.message.created_at.timestamp()
            dataIO.save_json(self.location, self.settings)
        else:
            m, s = divmod(self.settings["user"][str(author.id)]["minertime"] - ctx.message.created_at.timestamp() + 7200, 60)
            h, m = divmod(m, 60)
            if h == 0:
                time = "%d minutes %d seconds" % (m, s)
            elif h == 0 and m == 0:
                time = "%d seconds" % (s)
            else:
                time = "%d hours %d minutes %d seconds" % (h, m, s)
            if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["minertime"] <= 7200:
                await ctx.send("You are too early, come back to your miner in {}".format(time))
                return
            else:
                materials = []
                for miner in self._shop["miners"]:
                    for item in self.settings["user"][str(author.id)]["items"]:
                        if item == miner["name"]:
                            for x in range(miner["max_mats"]):
                                for mat in self._mine["items"]:
                                    if round(mat["rand_max"] * miner["multiplier"]) <= 0:
                                        number = 1
                                    else:
                                        number = round(mat["rand_max"] * miner["multiplier"])
                                    if randint(0, number) == 0:
                                        materials.append({"name": mat["name"], "emote": mat["emote"]})
                msg = ", ".join(set(map(lambda x: x["name"] + " x" + str(list(map(lambda x: x["name"], materials)).count(x["name"])) + x["emote"], materials))) if materials != [] else "Absolutely nothing"
                s=discord.Embed(colour=ctx.author.colour, description="You used your miners and gathered these materials: {}".format(msg)) 
                s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=s)    
                for x in materials:
                    self.settings["user"][str(author.id)]["items"].append(x["name"])
                self.settings["user"][str(author.id)]["minertime"] = ctx.message.created_at.timestamp()
                dataIO.save_json(self.location, self.settings)


        
    @commands.command(aliases=["pick"])
    async def pickaxe(self, ctx, *, user: discord.Member=None):
        """Displays your pickaxe if you have one"""
        if not user:
            user = ctx.author 
        msg = ""
        try:
            for item in self._shop["picitems"]:
                if item["name"] in self.settings["user"][str(user.id)]["items"]:
                    s=discord.Embed(colour=user.colour)
                    s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                    s.add_field(name="Durability", value=str(self.settings["user"][str(user.id)]["pickdur"]), inline=False)
                    s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * self.settings["user"][str(user.id)]["pickdur"])), inline=False)
                    s.add_field(name="Original Price", value= "$" + str(item["price"]), inline=False)
                    s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/131/pick_26cf.png")
                    await ctx.send(embed=s)
                    return
            await ctx.send("That user does not have a pickaxe :no_entry:")
        except:
            await ctx.send("That user does not have a pickaxe :no_entry:")
        
        
    @commands.command()
    async def repair(self, ctx, durability: int=None):
        """Repair your pickaxe with recourses"""
        author = ctx.author
        if not durability: 
            for item in self._shop["picitems"]:
                if item["name"] in self.settings["user"][str(author.id)]["items"]:
                    if self.settings["user"][str(author.id)]["pickdur"] >= item["durability"]:
                        await ctx.send("You already have full durability on your pickaxe :no_entry:")
                        return
                    material = item["name"][:-8]
                    for mat in self._mine["items"]:
                        if material == mat["name"]:
                            calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * (item["durability"] - self.settings["user"][str(author.id)]["pickdur"]))
                            if calc > self.settings["user"][str(author.id)]["items"].count(material):
                                await ctx.send("You do not have enough materials to fix this pickaxe :no_entry:")
                            else:
                                msg = await ctx.send("It will cost you **{} {}** to fix your pickaxe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                                try:
                                    def repair(m):
                                        return m.author == ctx.author
                                    response = await self.bot.wait_for("message", timeout=60, check=repair)
                                except asyncio.TimeoutError:
                                    await msg.delete()
                                    return
                                if response.content.lower() == "yes": 
                                    await msg.delete()
                                    for x in range(calc):
                                        self.settings["user"][str(author.id)]["items"].remove(material)
                                    self.settings["user"][str(author.id)]["pickdur"] = item["durability"]
                                    dataIO.save_json(self.location, self.settings)
                                    await ctx.send("You have repaired your pickaxe to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], item["durability"]))
                                else:
                                    await msg.delete()
                            return
                    await ctx.send("You cannot repair this pickaxe :no_entry:")
        else:
            for item in self._shop["picitems"]:
                if item["name"] in self.settings["user"][str(author.id)]["items"]:
                    if self.settings["user"][str(author.id)]["pickdur"] >= item["durability"]:
                        await ctx.send("You already have full durability on your pickaxe :no_entry:")
                        return
                    material = item["name"][:-8]
                    for mat in self._mine["items"]:
                        if material == mat["name"]:
                            calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * durability)
                            if calc > self.settings["user"][str(author.id)]["items"].count(material):
                                await ctx.send("You do not have enough materials to fix this pickaxe :no_entry:")
                            else:
                                msg = await ctx.send("It will cost you **{} {}** to fix your pickaxe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                                try:
                                    def repair2(m):
                                        return m.author == ctx.author
                                    response = await self.bot.wait_for("message", timeout=60, check=repair2)
                                except asyncio.TimeoutError:
                                    await msg.delete()
                                    return
                                if response.content.lower() == "yes": 
                                    await msg.delete()
                                    for x in range(calc):
                                        self.settings["user"][str(author.id)]["items"].remove(material)
                                    self.settings["user"][str(author.id)]["pickdur"] += durability
                                    dataIO.save_json(self.location, self.settings)
                                    await ctx.send("You have repaired your pickaxe. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], self.settings["user"][str(author.id)]["pickdur"]))
                                else:
                                    await msg.delete()
                            return
                    await ctx.send("You cannot repair this pickaxe :no_entry:")
                
        
    @commands.command()
    async def give(self, ctx, user: discord.Member, amount):
        """Give someone some money"""
        author = ctx.author
        if user in filter(lambda m: m.bot and m != self.bot.user, self.bot.get_all_members()):
            await ctx.send("Bots can't make money :no_entry:")
            return
        await self._set_bank(author)
        await self._set_bank_user(user)
        if user == author:
            await ctx.send("You can't give yourself money :no_entry:")
            return
        if amount.lower() == "all":
            amount = self.settings["user"][str(author.id)]["balance"]
        else:
            try:
                amount = int(amount)
            except:
                return await ctx.send("Invalid amount :no_entry:")
        if amount > self.settings["user"][str(author.id)]["balance"]:
            await ctx.send("You don't have that much money to give :no_entry:")
            return
        if amount < 1:
            await ctx.send("You can't give them less than a dollar, too mean :no_entry:")
            return
        fullamount = amount
        if self.bot.user != user:
            amount = fullamount if "Tax Avoider" in self.settings["user"][str(author.id)]["items"] else round(amount * 0.95)
            tax = 0 if "Tax Avoider" in self.settings["user"][str(author.id)]["items"] else round(amount * 0.05)
            self.settings["user"][str(user.id)]["balance"] += amount
        else:
            tax = fullamount
            amount = fullamount
        self.settings["tax"] += tax
        self.settings["user"][str(author.id)]["balance"] -= fullamount
        if "Tax Avoider" in self.settings["user"][str(author.id)]["items"]:
            self.settings["user"][str(author.id)]["items"].remove("Tax Avoider")
        dataIO.save_json(self.location, self.settings)
        s=discord.Embed(description="You have gifted **${:,}** to **{}**\n\n{}'s new balance: **${:,}**\n{}'s new balance: **${:,}**".format(amount, user.name, author.name, self.settings["user"][str(author.id)]["balance"], user.name, self.settings["user"][str(user.id)]["balance"] if user != self.bot.user else self.settings["tax"]), colour=author.colour)
        s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://png.kisspng.com/20171216/8cb/5a355146d99f18.7870744715134436548914.png")
        s.set_footer(text="{}".format("${:,} ({}%) tax was taken".format(tax, round((tax/fullamount)*100))))
        await ctx.send(embed=s)
		
    @commands.command(aliases=["givemats"])
    async def givematerials(self, ctx, user: discord.Member, amount: int, *, item: str):
        author = ctx.author
        if user.bot:
            await ctx.send("Bots can't get items :no_entry:")
            return
        await self._set_bank(author)
        await self._set_bank_user(user)
        if user == author:
            await ctx.send("You can't give yourself items :no_entry:")
            return
        for item1 in self._shop["picitems"]:
            if item.lower() == item1["name"].lower():
                await ctx.send("You can't give pickaxes :no_entry:")
                return
        try:
            amountofitem = self.settings["user"][str(author.id)]["items"].count(item.title())
        except:
            await ctx.send("You have any of that item :no_entry:")
            return
        if amountofitem >= amount:
            for x in range(0, amount):
                self.settings["user"][str(author.id)]["items"].remove(item.title())
                self.settings["user"][str(user.id)]["items"].append(item.title())
            usercount = self.settings["user"][str(user.id)]["items"].count(item.title())
            authorcount = self.settings["user"][str(author.id)]["items"].count(item.title())
            s=discord.Embed(description="You have gifted **{} {}** to **{}**\n\n{}'s new {} amount: **{} {}**\n{}'s new {} amount: **{} {}**".format(amount, item.title(), user.name, author.name, item.title(), authorcount, item.title(), user.name, item.title(), usercount, item.title()), colour=author.colour)
            s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://png.kisspng.com/20171216/8cb/5a355146d99f18.7870744715134436548914.png")
            await ctx.send(embed=s)
        else:
            await ctx.send("You don't have enough `{}` to give :no_entry:".format(item.title()))
                

    @commands.command(aliases=["roulette", "rusr"])
    async def russianroulette(self, ctx, bullets: int, bet: int):
        """Risk your money with a revolver to your head with a certain amount of bullets in it, if you get shot you lose if not you win"""
        author = ctx.author
        server = ctx.guild
        await self._set_bank(author)
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if bet < 20:
            await ctx.send("This game requires $20 to play :no_entry:")
            return
        if self.settings["user"][str(author.id)]["balance"] < bet:
            await ctx.send("You don't have that amount to bet :no_entry:")
            return
        if bullets <= 0:
            await ctx.send("Invalid number of bullets :no_entry:")
            return
        if bullets >= 6:
            await ctx.send("Invalid number of bullets :no_entry:")
            return
        self.settings["user"][str(author.id)]["balance"] -= bet
        self.settings["user"][str(author.id)]["winnings"] -= bet
        rr = randint(1, 6)
        winnings = math.ceil((5.7 * bet)/(6 - bullets))
        if bullets >= rr:
            s=discord.Embed(description="You were shot :gun:\nYou lost your bet of **${:,}**".format(bet), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        else:
            self.settings["user"][str(author.id)]["balance"] += winnings
            self.settings["user"][str(author.id)]["winnings"] += winnings
            s=discord.Embed(description="You're lucky, you get to live another day.\nYou Won **${:,}**".format(winnings), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        dataIO.save_json(self.location, self.settings)
        
    @commands.group()
    async def factory(self, ctx):
        """Factorys you can buy with recourses"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            await self._set_bank(ctx.author)

    @factory.command(aliases=["buy"])
    async def purchase(self, ctx, *, factory_name):
        """Buy a factory with your recourses gained by mining"""
        author = ctx.author
        for item in self._factories["factory"]:
            if item["name"].lower() == factory_name.lower():
                for item2 in list(set(self.settings["user"][str(author.id)]["items"])):        
                    itemamount = self.settings["user"][str(author.id)]["items"].count(item2)            
                    if item["item"] == item2:
                        if item["price"] <= itemamount:
                            await ctx.send("You just bought a `{}`".format(item["name"]))
                            for x in range(item["price"]):
                                self.settings["user"][str(author.id)]["items"].remove(item2)
                            self.settings["user"][str(author.id)]["items"].append(item["name"])
                            dataIO.save_json(self._factories_file, self._factories)
                            dataIO.save_json(self.location, self.settings)
                        else:
                            await ctx.send("You don't have enough `{}` to buy this :no_entry:".format(item2))

                        
    @factory.command(aliases=["shop"]) 
    async def market(self, ctx):
        """View factorys you can buy"""
        s=discord.Embed(description="You can buy factories using materials you have gathered", colour=0xfff90d)
        s.set_author(name="Factories", icon_url=self.bot.user.avatar_url)
        
        
        for item2 in self._mine["items"]:
            for item in self._factories["factory"]:
                sortedfactory = sorted(self._factories["factory"], key=lambda x: (x["price"] * item2["price"]), reverse=True)
        for x in sortedfactory:
            s.add_field(name=x["name"], value="Price: {} {}".format(str(x["price"]), x["item"]))
             
        s.set_footer(text="Use s?factory purchase <factory> to buy a factory.")
        
        await ctx.send(embed=s)
        
    @factory.command()
    async def collect(self, ctx):
        """If you have a factory or mutliple use this to collect your money from them every 12 hours"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        number = 0
        factoryc = 0
        for item_ in self.settings["user"][str(author.id)]["items"]:
            for _item in self._factories["factory"]:
                if  _item["name"] == item_:
                    factoryc += 1
        if factoryc == 0:
            await ctx.send("You do not own a factory :no_entry:")
            return
        if not self.settings["user"][str(author.id)]["factorytime"]:
            for item in self.settings["user"][str(author.id)]["items"]:
                for item2 in self._factories["factory"]:
                    if item2["name"] == item:
                        number += randint(item2["rand_min"], item2["rand_max"])
            if number == 0:
                await ctx.send("You don't have any factories :no_entry:")
                return
            self.settings["user"][str(author.id)]["factorytime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] += number
            s=discord.Embed(description="Your factories made you **${}** today".format(str(number)), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            dataIO.save_json(self._factories_file, self._factories)
            dataIO.save_json(self.location, self.settings)
            return
        m, s = divmod(self.settings["user"][str(author.id)]["factorytime"] - ctx.message.created_at.timestamp() + 43200, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["factorytime"] <= 43200:
            await ctx.send("You are too early, come back to your factory in {}".format(time))
            return
        else:
            for item in self.settings["user"][str(author.id)]["items"]:
                for item2 in self._factories["factory"]:
                    if item2["name"] == item:
                        number += randint(item2["rand_min"], item2["rand_max"])
            if number == 0:
                await ctx.send("You don't have any factories :no_entry:")
                return
            self.settings["user"][str(author.id)]["factorytime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] += number
            s=discord.Embed(description="Your factories made you **${}** today".format(str(number)), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            dataIO.save_json(self._factories_file, self._factories)
            dataIO.save_json(self.location, self.settings)
                
                    
    
    @commands.command(hidden=True)
    @checks.is_owner()
    async def additem(self, ctx, name, price, durability = None, rand_min = None, rand_max = None, multiplier = None):
        if not durability and not rand_min and not rand_max and multiplier:
            item = {}
            item["name"] = name
            item["price"] = price
        
            self._shop["items"].append(item)
            dataIO.save_json(self._shop_file, self._shop)
        elif durability and rand_min and rand_max and multiplier:
            item = {}
            item["name"] = name
            
            try:
                item["price"] = int(price)
                item["durability"] = int(durability)
                item["rand_min"] = int(rand_min)
                item["rand_max"] = int(rand_max)
                item["multiplier"] = int(multiplier)
            except:
                await ctx.send("You fucked up")
                
                return
            
            self._shop["picitems"].append(item)
            dataIO.save_json(self._shop_file, self._shop)
            await ctx.send("You have created the item `{}`".format(name))
        else:
            await ctx.send("You fucked up")
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def addfactory(self, ctx, name, price, item2, rand_min, rand_max):
        item = {}
        item["name"] = name 
        item["price"] = int(price)
        item["item"] = item2
        item["rand_min"] = int(rand_min)
        item["rand_max"] = int(rand_max)
        self._factories["factory"].append(item)
        dataIO.save_json(self._factories_file, self._factories)
        await ctx.send("You have created the `{}`".format(name))
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def addmat(self, ctx, name, value, chance, emote):
        item = {}
        item["name"] = name 
        item["price"] = int(value)
        item["rand_max"] = int(chance)
        item["emote"] = emote
        self._mine["items"].append(item)
        dataIO.save_json(self._mine_file, self._mine)
        await ctx.send("You have created the material `{}`".format(name))
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def delitem(self, ctx, *, name: str):
        for item in self._shop["picitems"]:
            if item["name"] == name:
                self._shop["picitems"].remove(item)
                dataIO.save_json(self._shop_file, self._shop)
                await ctx.send("I have deleted that item")
        
    @commands.group()
    async def auction(self, ctx):
        """The Sx4 Auction house"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            pass
        
    @auction.command()
    async def refund(self, ctx):
        author = ctx.author
        await self._set_bank(author)
        filtered = filter(lambda x: x["ownerid"] == str(author.id), self._auction["items"]) 
        filtered = sorted(filtered, key=lambda x: x["price"])
        if not filtered:
            await ctx.send("You have no items for sale on the auction house :no_entry:")
            return
        server = ctx.guild
        channel = ctx.channel
        author = ctx.author
        
        if server.id not in PagedResultData.paged_results:
            PagedResultData.paged_results[server.id] = dict()
        
        if channel.id not in PagedResultData.paged_results[server.id]:
            PagedResultData.paged_results[server.id][channel.id] = dict()
            
        paged_result = PagedResult(filtered, lambda item: "\n**Name:** " + item["name"] + "\n**Price:** " + str(item["price"]) + "\n" + ("**Durability:** " + str(item["durability"]) + "\n" if "durability" in item else "") + ("**Amount:** " + str(item["amount"]) + "\n" if "amount" in item else "**Amount:** 1"))
        paged_result.list_indexes = True
        paged_result.selectable = True
        async def selected2(event):
            item = event.entry
            i = 0
            items = [item1 for item1 in self._shop["picitems"] if item1["name"] in self.settings["user"][str(author.id)]["items"]]
            for item2 in self._shop["picitems"]:
                if item2["name"].lower() == item["name"].lower():
                    for item3 in items:
                        i = i + 1
                    if i >= 1:
                        await channel.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                        return
            if item not in self._auction["items"]:
                await channel.send("That item was recently bought :no_entry:")
                return
            self._auction["items"].remove(item)
                
            try:
                if item["durability"]:
                    self.settings["user"][str(author.id)]["pickdur"] = item["durability"]
            except:
                pass
                
            try:
                if item["amount"]:
                    pass
            except:
                item["amount"] = 1
                    
            for x in range(0, item["amount"]):
                self.settings["user"][str(author.id)]["items"].append(item["name"].title())
                    
            await channel.send("You just refunded your `{}`.".format(item["name"]))
            
            dataIO.save_json(self._auction_file, self._auction)
            dataIO.save_json(self.location, self.settings)
        
        paged_result.on_select = selected2

        message = await channel.send(embed=paged_result.get_current_page_embed())

        paged_result.message_id = message.id

        PagedResultData.paged_results[server.id][channel.id][author.id] = paged_result
        
    @auction.command()
    async def sell(self, ctx, item: str, price: int, amount: int=None):
        """Sell items on the auction house"""
        author = ctx.author
        if amount == None:
            amount = 1
        if amount <= 0:
            await ctx.send("You can't sell no items, we're not ebay :no_entry:")
            return
        if price < 0:
            await ctx.send("You can't sell something for less than $0 :no_entry:")
            return
        await self._set_bank(author)
        item3 = [x.lower() for x in self.settings["user"][str(author.id)]["items"]]
        if item3.count(item.lower()) < amount:
            await ctx.send("You don't have that amount of `{}` to sell :no_entry:".format(item))
            return            
        if item.lower() in item3:
            auction = {}
            for item2 in self._shop["picitems"]:
                if item.lower() == item2["name"].lower():
                    auction["durability"] = self.settings["user"][str(author.id)]["pickdur"]
                    self.settings["user"][str(author.id)]["pickdur"] = None
            for item2 in self._shop["roditems"]:
                if item.lower() == item2["name"].lower():
                    auction["durability"] = self.settings["user"][str(author.id)]["roddur"]
                    self.settings["user"][str(author.id)]["roddur"] = None
            for item2 in self._shop["items"] + self._mine["items"]:
                if item.lower() == item2["name"].lower():
                    auction["durability"] = None
            auction["name"] = item.title()
            auction["ownerid"] = str(author.id)
            auction["price"] = price
            auction["amount"] = amount
            for x in range(0, amount):
                self.settings["user"][str(author.id)]["items"].remove(item.title())
            self._auction["items"].append(auction)
            dataIO.save_json(self._auction_file, self._auction)
            dataIO.save_json(self.location, self.settings)
            await ctx.send("Your item has been put on the auction house <:done:403285928233402378>")
        else:
            await ctx.send("You don't own that item :no_entry:")
            
    @auction.command()
    async def buy(self, ctx, *, auction_item: str):
        """Buy items on the auction house"""
        author = ctx.author
        await self._set_bank(author)
        i = 0;
        items = [item for item in self._shop["picitems"] if item["name"] in self.settings["user"][str(author.id)]["items"]]
        itemsrod = [item for item in self._shop["roditems"] if item["name"] in self.settings["user"][str(author.id)]["items"]]
        for item2 in self._shop["picitems"]:
            if item2["name"].lower() == auction_item.lower():
                for item in items:
                    i = i + 1
                if i >= 1:
                    await ctx.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                    return
        for item2 in self._shop["roditems"]:
            if item2["name"].lower() == auction_item.lower():
                for item in itemsrod:
                    i = i + 1
                if i >= 1:
                    await ctx.send("You already own a rod, sell your rod and try again :no_entry:")
                    return
        filtered = filter(lambda x: x["name"].lower() == auction_item.lower(), self._auction["items"]) 
        filtered = sorted(filtered, key=lambda x: x["price"])
        if not filtered:
            await ctx.send("There is no `{}` on the auction house :no_entry:".format(auction_item.title()))
            return
        server = ctx.guild
        channel = ctx.channel
        author = ctx.author
        
        if server.id not in PagedResultData.paged_results:
            PagedResultData.paged_results[server.id] = dict()
        
        if channel.id not in PagedResultData.paged_results[server.id]:
            PagedResultData.paged_results[server.id][channel.id] = dict()
            
        paged_result = PagedResult(filtered, lambda item: "\n**Name:** " + item["name"] + "\n**Price:** " + str(item["price"]) + "\n" + ("**Durability:** " + str(item["durability"]) + "\n" if "durability" in item else "") + ("**Amount:** " + str(item["amount"]) + "\n" if "amount" in item else "**Amount:** 1"))
        paged_result.list_indexes = True
        paged_result.selectable = True
        
        async def selected(event):
            item = event.entry
            if item not in self._auction["items"]:
                await channel.send("That item was recently bought :no_entry:")
                return
            owner = discord.utils.get(self.bot.get_all_members(), id=int(item["ownerid"]))
            if owner == ctx.message.author:
                await channel.send("You can't buy your own items :no_entry:")
                return
            if item["price"] > self.settings["user"][str(author.id)]["balance"]:
                await channel.send("You don't have enough money for that item :no_entry:")
                return
            self._auction["items"].remove(item)
            
            self.settings["user"][str(author.id)]["balance"] -= item["price"]
            self.settings["user"][str(owner.id)]["balance"] += item["price"]
                
            try:
                if item["durability"]:
                    self.settings["user"][str(author.id)]["pickdur"] = item["durability"]
            except:
                pass
                
            try:
                if item["amount"]:
                    pass
            except:
                item["amount"] = 1
                    
            for x in range(0, item["amount"]):
                self.settings["user"][str(author.id)]["items"].append(item["name"].title())
            try:
                await channel.send("You just bought `{} {}` for **${:,}** :tada:".format(item["amount"], item["name"], item["price"]))
            except:
                await channel.send("You just bought `1 {}` for **${:,}** :tada:".format(item["name"], item["price"]))
            try:
                await owner.send("Your `{}` just got bought on the auction house, it was sold for **${:,}** :tada:".format(item["name"], item["price"]))
            except:
                pass
            
            dataIO.save_json(self._auction_file, self._auction)
            dataIO.save_json(self.location, self.settings)
        
        paged_result.on_select = selected

        message = await channel.send(embed=paged_result.get_current_page_embed())

        paged_result.message_id = message.id

        PagedResultData.paged_results[server.id][channel.id][author.id] = paged_result

    @commands.command(aliases=["rod", "fishing_rod"])
    async def fishingrod(self, ctx, user: discord.Member=None):
        if not user:
            user = ctx.author 
        msg = ""
        try:
            for item in self._shop["roditems"]:
                if item["name"] in self.settings["user"][str(user.id)]["items"]:
                    s=discord.Embed(colour=user.colour)
                    s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                    s.add_field(name="Durability", value=str(self.settings["user"][str(user.id)]["roddur"]), inline=False)
                    s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * self.settings["user"][str(user.id)]["roddur"])), inline=False)
                    s.add_field(name="Original Price", value= "$" + str(item["price"]), inline=False)
                    s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/147/fishing-pole-and-fish_1f3a3.png")
                    await ctx.send(embed=s)
                    return
            await ctx.send("That user does not have a fishing rod :no_entry:")
        except:
            await ctx.send("That user does not have a fishing rod :no_entry:")
          
    @commands.command()
    async def fish(self, ctx):
        """Fish for some extra money"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        msg, i = "", 0
        await self._set_bank(author)
        if not self.settings["user"][str(author.id)]["fishtime"]:
            for rod in self._shop["roditems"]:
                if rod["name"] in self.settings["user"][str(author.id)]["items"]:
                    money = randint(rod["rand_min"], rod["rand_max"])
                    self.settings["user"][str(author.id)]["roddur"] -= 1
                    msg = "Your fishing rod broke in the process" if self.settings["user"][str(author.id)]["roddur"] == 0 else ""
                    if self.settings["user"][str(author.id)]["roddur"] == 0:
                        self.settings["user"][str(author.id)]["items"].remove(rod["name"])
                    i += 1
            if i != 1:
                money = randint(2, 15)
            self.settings["user"][str(author.id)]["fishtime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] += money
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n{}".format(money, msg), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            dataIO.save_json(self.location, self.settings)
            return
        m, s = divmod(self.settings["user"][str(author.id)]["fishtime"] - ctx.message.created_at.timestamp() + 300, 60)
        if m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d minutes %d seconds" % (m, s)
        if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["fishtime"] <= 300:
            await ctx.send("You are too early, come collect your money again in {}".format(time))
            return
        else:
            for rod in self._shop["roditems"]:
                if rod["name"] in self.settings["user"][str(author.id)]["items"]:
                    money = randint(rod["rand_min"], rod["rand_max"])
                    self.settings["user"][str(author.id)]["roddur"] -= 1
                    msg = "Your fishing rod broke in the process" if self.settings["user"][str(author.id)]["roddur"] == 0 else ""
                    if self.settings["user"][str(author.id)]["roddur"] == 0:
                        self.settings["user"][str(author.id)]["items"].remove(rod["name"])
                    i += 1
            if i != 1:
                money = randint(2, 15)
            self.settings["user"][str(author.id)]["fishtime"] = ctx.message.created_at.timestamp()
            self.settings["user"][str(author.id)]["balance"] += money
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n{}".format(money, msg), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            dataIO.save_json(self.location, self.settings)
        
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def slot(self, ctx, bet: int=None):
        """Bid your money into slots with a chance of winning big"""
        author = ctx.author
        if bet:
            await self._set_bank(author)
            if self.settings["user"][str(author.id)]["balance"] < bet:
                await ctx.send("You don't have that much to bet :no_entry:")
                return
            if bet <= 0:
                await ctx.send("At least bet a dollar :no_entry:")
                return
            self.settings["user"][str(author.id)]["balance"] -= bet
            self.settings["user"][str(author.id)]["winnings"] -= bet
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
                        self.settings["user"][str(author.id)]["balance"] += winnings
                        self.settings["user"][str(author.id)]["winnings"] += winnings
                        win = {}
                        win["userid"] = str(author.id)
                        win["username"] = author.name + "#" + author.discriminator
                        win["chance"] = str(slot["percentage"]) + "%"
                        win["multiplier"] = round((100/slot["percentage"]) * 0.5)
                        win["bet"] = bet
                        win["icon"] = slot["icon"]
                        win["winnings"] = winnings
                        self._slots["wins"].append(win)
                        dataIO.save_json(self.location, self.settings)
                        dataIO.save_json(self._slots_file, self._slots)
                    else:
                        msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou would have won **{:,}x** your bet!".format(round((100/slot["percentage"]) * 0.5))
        else:
            msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou {} won **nothing**!".format("would have" if not bet else "")
        s=discord.Embed(description=msg, colour=0xfff90d)
        s.set_author(name="🎰 Slot Machine 🎰")
        s.set_thumbnail(url="https://images.emojiterra.com/twitter/512px/1f3b0.png")
        s.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        dataIO.save_json(self.location, self.settings)
        
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
        if itemnamesearch == True:
            type = sorted(filter(lambda x: x["name"].lower() == itemname.lower(), self._auction["items"]), key=lambda x: x["price"])
        else:
            type = sorted(self._auction["items"], key=lambda x: x["price"])
        if page < 1:
            await ctx.send("Invalid Page :no_entry:")
            return
        if page - 1 > len(type) / 10:
            await ctx.send("Invalid Page :no_entry:")
            return
        msg = ""
        for item in type[page*10-10:page*10]:
            owner = discord.utils.get(self.bot.get_all_members(), id=int(item["ownerid"]))
            try:
                if item["durability"]:
                    try:
                        if item["amount"]:
                            msg += "**__{}__**\nOwner: `{}` ({})\nPrice: ${}\nDurability: {}\nAmount: {}\n\n".format(item["name"], owner, item["ownerid"], item["price"], item["durability"], item["amount"])
                    except:
                        item["amount"] = 1
                        msg += "**__{}__**\nOwner: `{}` ({})\nPrice: ${}\nDurability: {}\nAmount: {}\n\n".format(item["name"], owner, item["ownerid"], item["price"], item["durability"], item["amount"])
                else:
                    try:
                        if item["amount"]:
                            msg += "**__{}__**\nOwner: `{}` ({})\nPrice: ${}\nDurability: {}\nAmount: {}\n\n".format(item["name"], owner, item["ownerid"], item["price"], item["durability"], item["amount"])
                    except:
                        item["amount"] = 1
                        msg += "**__{}__**\nOwner: `{}` ({})\nPrice: ${}\nDurability: {}\nAmount: {}\n\n".format(item["name"], owner, item["ownerid"], item["price"], item["durability"], item["amount"])
            except:
                try:
                    if item["amount"]:
                        msg += "**__{}__**\nOwner: `{}` ({})\nPrice: ${}\nAmount: {}\n\n".format(item["name"], owner, item["ownerid"], item["price"], item["amount"])
                except:
                    item["amount"] = 1
                    msg += "**__{}__**\nOwner: `{}` ({})\nPrice: ${}\nAmount: {}\n\n".format(item["name"], owner, item["ownerid"], item["price"], item["amount"])
        if not msg and itemnamesearch == True:
            await ctx.send("There are none of that item on the auction house :no_entry:")
            return
        if not msg and itemnamesearch == False:
            await self.bot.say("There are no items for sale on the auction house :no_entry:")
            return
        s = discord.Embed(description=msg, colour=0xfff90d, timestamp=datetime.datetime.utcnow())
        s.set_author(name="Auction House", icon_url=self.bot.user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(type)/10)))
        await ctx.send(embed=s) 
            
    @commands.command(aliases=["buy"])
    async def shopbuy(self, ctx, *, buyable_item: str):
        """Buy something from the shop"""
        author = ctx.author
        through = False
        await self._set_bank(author)
        i, n = 0, 0
        for item in self._shop["picitems"]:
            if buyable_item.lower() == item["name"].lower():
                items = [item for item in self._shop["picitems"] if item["name"] in self.settings["user"][str(author.id)]["items"]]
                for item in items:
                    i = i + 1
                if i >= 1:
                    await ctx.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                    return
                await self._set_bank(author)
                
                if buyable_item.lower() in [x.lower() for x in self.settings["user"][str(author.id)]["items"]]:
                    await ctx.send("You already own this item :no_entry:") 
                    return
                    
                author_data = self.settings["user"][str(author.id)]
                
                if author_data["balance"] >= item["price"]:
                    author_data["balance"] -= item["price"]
                    author_data["items"].append(buyable_item.title())
                    author_data["pickdur"] = item["durability"]
                    
                    dataIO.save_json(self.location, self.settings)
                    
                    await ctx.send("You just bought a {} for **${:,}** :ok_hand:".format(item["name"], item["price"]))
                    through = True
                else:
                    await ctx.send("You don't have enough money to buy that item :no_entry:")
                    through = True
        for item in self._shop["roditems"]:
            if buyable_item.lower() == item["name"].lower():
                rods = [item for item in self._shop["roditems"] if item["name"] in self.settings["user"][str(author.id)]["items"]]
                for rod in rods:
                    n += 1
                if n >= 1:
                    await ctx.send("You already own a fishing rod use the rest of it then buy a new one :no_entry:")
                    return
                await self._set_bank(author)
                
                if buyable_item.lower() in [x.lower() for x in self.settings["user"][str(author.id)]["items"]]:
                    await ctx.send("You already own this item :no_entry:")
                    return
                    
                author_data = self.settings["user"][str(author.id)]
                
                if author_data["balance"] >= item["price"]:
                    author_data["balance"] -= item["price"]
                    author_data["items"].append(buyable_item.title())
                    author_data["roddur"] = item["durability"]
                    
                    dataIO.save_json(self.location, self.settings)
                    
                    await ctx.send("You just bought a {} for **${:,}** :ok_hand:".format(item["name"], item["price"]))
                    through = True
                else:
                    await ctx.send("You don't have enough money to buy that item :no_entry:")
                    through = True
        if not through:
            await ctx.send("That is not an item :no_entry:")
                    
    @commands.command()
    async def mine(self, ctx): 
        """If you have a pickaxe use this to mine with it"""
        author = ctx.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        materials = ""
        await self._set_bank(author)
        for item in self._shop["picitems"]:
            if item["name"] in self.settings["user"][str(author.id)]["items"]:
                amount = randint(item["rand_min"], item["rand_max"])
                if "picktime" not in self.settings["user"][str(author.id)]:
                    self.settings["user"][str(author.id)]["picktime"] = None
                if not self.settings["user"][str(author.id)]["pickdur"]:
                    await ctx.send("It seems you've came across a bug where your pick durabilty doesn't exist report this to my owner")
                    return
                if not self.settings["user"][str(author.id)]["picktime"]:
                    author_data = self.settings["user"][str(author.id)]
                    author_data["picktime"] = ctx.message.created_at.timestamp()
                    author_data["balance"] += amount
                    author_data["pickdur"] -= 1
                    for item2 in self._mine["items"]:
                        if round(item2["rand_max"] * item["multiplier"]) <= 0:
                            number = 1
                        else:
                            number = round(item2["rand_max"] * item["multiplier"])
                        chance = randint(0, number)
                        if chance == 0:
                            author_data["items"].append(item2["name"])
                            materials += item2["name"] + item2["emote"] + ", "
                    materials = materials[:-2]
                    if materials == "":
                        materials = "Absolutely nothing"
                        
                    
                    if author_data["pickdur"] > 0:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
                    else:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                        author_data["items"].remove(item["name"])
                        
                    s.set_author(name=author.name, icon_url=author.avatar_url)
                    await ctx.send(embed=s)
                    dataIO.save_json(self.location, self.settings)
                    return
                
                m, s = divmod(self.settings["user"][str(author.id)]["picktime"] - ctx.message.created_at.timestamp() + 900, 60)
                h, m = divmod(m, 60)
                if h == 0:
                    time = "%d minutes %d seconds" % (m, s)
                elif h == 0 and m == 0:
                    time = "%d seconds" % (s)
                else:
                    time = "%d hours %d minutes %d seconds" % (h, m, s)
                if ctx.message.created_at.timestamp() - self.settings["user"][str(author.id)]["picktime"] <= 900:
                    await ctx.send("You are too early, come back to mine in {}".format(time))
                    return
                else:
                    self.settings["user"][str(author.id)]["picktime"] = ctx.message.created_at.timestamp()
                    author_data = self.settings["user"][str(author.id)]
                    self.settings["user"][str(author.id)]["balance"] = self.settings["user"][str(author.id)]["balance"] + amount
                    self.settings["user"][str(author.id)]["pickdur"] = self.settings["user"][str(author.id)]["pickdur"] - 1
                    for item2 in self._mine["items"]:
                        if round(item2["rand_max"] * item["multiplier"]) <= 0:
                            number = 1
                        else:
                            number = round(item2["rand_max"] * item["multiplier"])
                        chance = randint(0, number)
                        if chance == 0:
                            author_data["items"].append(item2["name"])
                            materials += item2["name"] + item2["emote"] + ", "
                    materials = materials[:-2]
                    if materials == "":
                        materials = "Absolutely nothing"
                    if author_data["pickdur"] > 0:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
                    else:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                        author_data["items"].remove(item["name"])
                    s.set_author(name=author.name, icon_url=author.avatar_url)
                    await ctx.send(embed=s)
                    dataIO.save_json(self.location, self.settings)
                
                return
        
        await ctx.send("You don't have a pickaxe, buy one at the shop.")
        
    @commands.command(aliases=["inventory"])
    async def items(self, ctx, *, user: discord.Member=None): 
        """View your current items"""
        counter = Counter()
        if not user:
            user = ctx.author
        for item in self.settings["user"][str(user.id)]["items"]:
            counter[item] += 1
        items = counter.most_common()
        items = "\n".join(["{} x{}".format(x[0], x[1]) for x in items])
        if items == "":
            items = "None"
        s=discord.Embed(description=items, colour=user.colour)
        s.set_author(name=user.name +"'s Items", icon_url=user.avatar_url)
        await ctx.send(embed=s)
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def updatedata(self, ctx, input, output: int=None): 
        if not output:
            output = []
        i = 0;
        for userid in self.settings["user"]:
            i = i + 1
            self.settings["user"][userid]["{}".format(input)] = output
            dataIO.save_json(self.location, self.settings)
        await ctx.send("Updated data for {}/{} users".format(i, len(self.settings["user"])))
        
    @commands.command(hidden=True)
    @checks.is_owner()
    async def deletedata(self, ctx, data, hidden=True):
        i = 0;
        for userid in self.settings["user"]:
            i = i + 1
            del self.settings["user"][userid]["{}".format(data)]
            dataIO.save_json(self.location, self.settings)
        await ctx.send("Deleted data for {}/{} users".format(i, len(self.settings["user"])))
        
    async def _set_bank_user(self, user):
        if user.bot:
            return
        if "user" not in self.settings: 
            self.settings["user"] = {} 
            dataIO.save_json(self.location, self.settings)
        if str(user.id) not in self.settings["user"]: 
            self.settings["user"][str(user.id)] = {}
            dataIO.save_json(self.location, self.settings)
        if "rep" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["rep"] = 0
            dataIO.save_json(self.location, self.settings)
        if "balance" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["balance"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streak" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streaktime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["streaktime"] = None
            dataIO.save_json(self.location, self.settings)
        if "reptime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["reptime"] = None
            dataIO.save_json(self.location, self.settings)
        if "items" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["items"] = []
            dataIO.save_json(self.location, self.settings)
        if "pickdur" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["pickdur"] = None
            dataIO.save_json(self.location, self.settings)
        if "roddur" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["roddur"] = None
            dataIO.save_json(self.location, self.settings)
        if "minertime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["minertime"] = None
            dataIO.save_json(self.location, self.settings)
        if "winnings" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["winnings"] = 0
            dataIO.save_json(self.location, self.settings)
        if "fishtime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["fishtime"] = None
            dataIO.save_json(self.location, self.settings)
        if "factorytime" not in self.settings["user"][str(user.id)]:
            self.settings["user"][str(user.id)]["factorytime"] = None
            dataIO.save_json(self.location, self.settings)
            
    async def _set_bank(self, author):
        if author.bot:
            return
        if "user" not in self.settings: 
            self.settings["user"] = {} 
            dataIO.save_json(self.location, self.settings)
        if str(author.id) not in self.settings["user"]: 
            self.settings["user"][str(author.id)] = {}
            dataIO.save_json(self.location, self.settings)
        if "rep" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["rep"] = 0
            dataIO.save_json(self.location, self.settings)
        if "balance" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["balance"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streak" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streaktime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["streaktime"] = None
            dataIO.save_json(self.location, self.settings)
        if "reptime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["reptime"] = None
            dataIO.save_json(self.location, self.settings)
        if "items" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["items"] = []
            dataIO.save_json(self.location, self.settings)
        if "pickdur" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["pickdur"] = None
            dataIO.save_json(self.location, self.settings)
        if "roddur" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["roddur"] = None
            dataIO.save_json(self.location, self.settings)
        if "minertime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["minertime"] = None
            dataIO.save_json(self.location, self.settings)
        if "winnings" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["winnings"] = 0
            dataIO.save_json(self.location, self.settings)
        if "fishtime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["fishtime"] = None
            dataIO.save_json(self.location, self.settings)
        if "factorytime" not in self.settings["user"][str(author.id)]:
            self.settings["user"][str(author.id)]["factorytime"] = None
            dataIO.save_json(self.location, self.settings)
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def byebots(self, ctx):
        i = 0;

        for userid in sorted(self.settings["user"])[:len(self.settings["user"])]:
            if userid in list(map(lambda m: m.id, filter(lambda m: m.bot, self.bot.get_all_members()))):
                del self.settings["user"][userid]
                dataIO.save_json(self.location, self.settings)
                i = i + 1
        await ctx.send("**{}** bots have been removed from the economy data".format(i))

    @commands.group(aliases=["lb"])  
    async def leaderboard(self, ctx):
        """See where you're ranked"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            pass

    @leaderboard.command(name="items")
    async def _items(self, ctx, item: str, page: int=None):
        if not page:
            page = 1
        counter = Counter()
        for y in self.settings["user"]:
            for item in [x for x in self.settings["user"][y]["items"] if x.lower() == item.lower()]:
                counter[y] += 1
        if len(counter) == 0:
            return await ctx.send("No one has that item or it doesn't exist :no_entry:")
        users = counter.most_common()
        userspg = counter.most_common()[page*10-10:page*10]
        if page < 1 or page > math.ceil(len(users)/10):
            return await ctx.send("Invalid Page :no_entry:")
        i, msg, n = page*10-10, "", 0
        for x in users:
            n += 1
            if str(ctx.author.id) == x[0]:
                break
        for x in userspg:
            i += 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg += "{}. `{}` - {:,} {}\n".format(i, user, x[1], item.title())
        s=discord.Embed(title="{} Leaderboard".format(item.title()), description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n != len(users) else "Unranked", page, math.ceil(len(users)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command(aliases=["rep"])
    async def reputation(self, ctx, page: int=None):
        """Leaderboard for most reputation"""
        if not page:
            page = 1
        if page - 1 > len([x for x in self.settings["user"].items() if x[1]["rep"] != 0]) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10
        n = 0
        sortedrep2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["rep"], reverse=True)
        sortedrep = sorted([x for x in self.settings["user"].items() if x[1]["rep"] != 0], key=lambda x: x[1]["rep"], reverse=True)[page*10-10:page*10]
        for x in sortedrep2:
            n = n + 1
            if str(ctx.author.id) == x[0]:
                break    
        for x in sortedrep:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - {} reputation\n".format(i, user, x[1]["rep"])
        s=discord.Embed(title="Reputation Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n != len(sortedrep2) else "Unranked", page, math.ceil(len([x for x in self.settings["user"].items() if x[1]["rep"] != 0])/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def winnings(self, ctx, page: int=None):
        """Leaderboard for most winnings"""
        if not page:
            page = 1
        if page - 1 > len(self.settings["user"]) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10;
        n = 0;
        sortedwin2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["winnings"], reverse=True)
        sortedwin = sorted(self.settings["user"].items(), key=lambda x: x[1]["winnings"], reverse=True)[page*10-10:page*10]
        for x in sortedwin2:
            n = n + 1
            if str(ctx.author.id) == x[0]:
                break    
        for x in sortedwin:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - ${:,}\n".format(i, user, x[1]["winnings"])
        s=discord.Embed(title="Winnings Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n != len(sortedwin2) else "Unranked", page, math.ceil(len(self.settings["user"])/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def bank(self, ctx, page: int=None):
        """Leaderboard for most money"""
        if not page:
            page = 1
        if page - 1 > len([x for x in self.settings["user"].items() if x[1]["balance"] != 0]) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10;
        n = 0;
        sortedbank2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["balance"], reverse=True)
        sortedbank = sorted([x for x in self.settings["user"].items() if x[1]["balance"] != 0], key=lambda x: x[1]["balance"], reverse=True)[page*10-10:page*10]
        for x in sortedbank2:
            n = n + 1
            if str(ctx.author.id) == x[0]:
                break    
        for x in sortedbank:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - ${:,}\n".format(i, user, x[1]["balance"])
        s=discord.Embed(title="Bank Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n != len(sortedbank2) else "Unranked", page, math.ceil(len([x for x in self.settings["user"].items() if x[1]["balance"] != 0])/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command(hidden=True)
    @checks.is_main_owner()
    async def moneyset(self, ctx, amount: str, *, user: discord.Member=None):
        if not user:
            user = ctx.author
        if amount[0:1] == "+":
            self.settings["user"][str(user.id)]["balance"] += int(amount[1:len(amount)])
            await ctx.send("**{}** has been given an extra **${}**".format(user, amount[1:len(amount)]))
        elif amount[0:1] == "-":
            self.settings["user"][str(user.id)]["balance"] -= int(amount[1:len(amount)])
            await ctx.send("**{}** has had **${}** taken off their balance".format(user, amount[1:len(amount)]))
        else:
            self.settings["user"][str(user.id)]["balance"] = int(amount)
            await ctx.send("**{}** has had their balance set to **${}**".format(user, amount))
        dataIO.save_json(self.location, self.settings)
        
    @commands.command()
    async def bankstats(self, ctx):
        """See some of the bank statistics"""
        msg = 0
        win = 0
        for userid in self.settings["user"]:
            msg += self.settings["user"][userid]["balance"]
            win += self.settings["user"][userid]["winnings"]
        sortedslot = sorted(self._slots["wins"], key=lambda x: x["winnings"], reverse=True)[:1]
        sortedloser = sorted(self.settings["user"].items(), key=lambda x: x[1]["winnings"])[:1]
        for x in sortedloser:
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            toploser = "${:,} ({})".format(x[1]["winnings"], user)
        for x in sortedslot:
            topwin = "${:,} ({})".format(x["winnings"], x["username"])            
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Bank Stats", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Users", value=len(self.settings["user"]))
        s.add_field(name="Total Money", value="${:,}".format(msg))
        s.add_field(name="Total Winnings", value="${:,}".format(win))
        s.add_field(name="Biggest Win (Slot)", value=topwin)
        s.add_field(name="Biggest Loser", value=toploser)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def networth(self, ctx, page: int=None):
        """Leaderboard for most networth"""
        msg = ""
        
        author_id = ctx.author.id
        
        entries = []
        
        all_items = self._shop["picitems"] + self._shop["items"] + self._mine["items"] + self._shop["roditems"] + self._shop["miners"] + self._shop["boosters"]
        for member in list(set(self.bot.get_all_members())):
            if str(member.id) in self.settings["user"]:
                user_data = self.settings["user"][str(member.id)]
            
                worth = 0
                
                items = [item for item in all_items if item["name"] in user_data["items"]]
                for item in items:
                    if "durability" in item and item["name"].split(" ")[1] == "Pickaxe":
                        worth += round((item["price"]/item["durability"]) * user_data["pickdur"])
                    elif "durability" in item and item["name"].split(" ")[1] == "Rod":
                        worth += round((item["price"]/item["durability"]) * user_data["roddur"])
                    else:
                        worth += item["price"] * user_data["items"].count(item["name"])
                for item2 in [item for item in self._factories["factory"] if item["name"] in user_data["items"]]:
                    for item3 in self._mine["items"]:
                        if item3["name"] == item2["item"]:
                            worth += item2["price"]*item3["price"]
                
                worth += user_data["balance"]
                
                entry = {}
                entry["user"] = member
                entry["worth"] = worth
                
                entries.append(entry)
        if not page:
            page = 1
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
        if page - 1 > len(self.settings["user"]) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10;
        n = 0;
        sortedstreak2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["streak"], reverse=True)
        sortedstreak = sorted(self.settings["user"].items(), key=lambda x: x[1]["streak"], reverse=True)[page*10-10:page*10]
        for x in sortedstreak2:
            n = n + 1
            if str(ctx.author.id) == x[0]:
                break            
        for x in sortedstreak:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - {} day streak\n".format(i, user, x[1]["streak"])
        s=discord.Embed(title="Streak Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.author.name, n, page, math.ceil(len(self.settings["user"])/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command()
    async def marry(self, ctx, user: discord.Member):
        """Marry other uses"""
        author = ctx.author
        server = ctx.guild
        if user.bot:
            await ctx.send("You can't marry bots :no_entry:")
            return
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(author.id) not in self.data["user"]:
            self.data["user"][str(author.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][str(author.id)]:
            self.data["user"][str(author.id)]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if len(self.data["user"][str(author.id)]["marriedto"]) >= 5:
            await ctx.send("You are married to the max amount of users possible (5 users) you need to divorce someone to marry this user :no_entry:")
            return
        try:
            if len(self.data["user"][str(user.id)]["marriedto"]) >= 5:
                await ctx.send("This user is married to the max amount of users possible (5 users) they need to divorce someone to marry you :no_entry:")
                return
        except: 
            pass
        if str(user.id) in self.data["user"][str(author.id)]["marriedto"]:
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
            await ctx.send("Congratulations **{}** and **{}** :heart: :tada:".format(author.name, user.name))
            await self._create_marriage_user(ctx, user)
            await self._create_marriage_author(ctx, user)
        else:
            await ctx.send("{}, You can always try someone else.".format(author.mention))
            
    @commands.command() 
    async def divorce(self, ctx, user: str):
        """Divorce someone you've married"""
        author = ctx.author
        if "<" in user and "@" in user:
            user = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            user = discord.utils.get(self.bot.get_all_members(), id=int(user))
        elif "#" in user:
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            user = discord.utils.get(self.bot.get_all_members(), name=user[:usernum], discriminator=user[usernum + 1:len(user)])
        else:
            try:
                user2 = await self.bot.get_user_info(int(user))
                if not user2:
                    try:
                        del self.data["user"][str(author.id)]["marriedto"][user]
                        try:
                            del self.data["user"][user]["marriedto"][str(author.id)]
                        except: 
                            pass
                        return await ctx.send("I could not find that user but i found the id in your married list, they have now been deleted from it.")
                    except:
                        user = user2
                else:
                    user = user2
            except:
                user = discord.utils.get(self.bot.get_all_members(), name=user)
        if not user:
            await ctx.send("I could not find that user :no_entry:")
            return
        try:
            self.data["user"][str(user.id)]
            self.data["user"][str(author.id)]
        except:
            await ctx.send("I could not find that user :no_entry:")
            try:
                del self.data["user"][str(author.id)]["marriedto"][str(user.id)]
                await ctx.send("The ID was found in your marriage data though, so it has been removed :thumbsup:")
            except:
                pass
            return
        if str(user.id) in self.data["user"][str(author.id)]["marriedto"]:
            if author == user:
                del self.data["user"][str(user.id)]["marriedto"][str(author.id)]
            else:
                try:
                    del self.data["user"][str(user.id)]["marriedto"][str(author.id)]
                except:
                    pass
                try:
                    del self.data["user"][str(author.id)]["marriedto"][str(user.id)]
                except: 
                    pass
            dataIO.save_json(self.file_path, self.data)
            await ctx.send("Feels bad **{}**, Argument?".format(user.name))
        else:
            await ctx.send("You are not married to that user :no_entry:")

    @commands.command()
    async def married(self, ctx, user: discord.Member=None):
        if not user:
            user = ctx.author
        list = []
        try:
            for x in self.data["user"][str(user.id)]["marriedto"]:
                user2 = await self.bot.get_user_info(x)
                if user2:
                    list.append(str(user2) + " ({})".format(x))
                else:
                    list.append(x)
        except:
            return await ctx.send("That user is not married to anyone :no_entry:")
        await ctx.send(embed=discord.Embed(description="\n".join(list)).set_author(name=str(user), icon_url=user.avatar_url))
            
    @commands.command(aliases=["mdivorce"]) 
    async def massdivorce(self, ctx):
        """Divorce everyone""" 
        author = ctx.author
        for userid in list(self.data["user"][str(author.id)]["marriedto"])[:len(self.data["user"][str(author.id)]["marriedto"])]:
            if str(author.id) == userid:
                del self.data["user"][userid]["marriedto"][str(author.id)]
            else:
                try:
                    del self.data["user"][userid]["marriedto"][str(author.id)]
                except:
                    continue
                try:
                    del self.data["user"][str(author.id)]["marriedto"][userid]
                except:
                    continue
        dataIO.save_json(self.file_path, self.data) 
        await ctx.send("You are now divorced from everyone previously you were married to <:done:403285928233402378>")
            
    async def _create_marriage_user(self, ctx, user):
        author = ctx.author
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(user.id) not in self.data["user"]:
            self.data["user"][str(user.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][str(user.id)]:
            self.data["user"][str(user.id)]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(author.id) not in self.data["user"][str(user.id)]["marriedto"]:
            self.data["user"][str(user.id)]["marriedto"][str(author.id)] = {}
            dataIO.save_json(self.file_path, self.data)
    
    async def _create_marriage_author(self, ctx, user):
        author = ctx.message.author
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(author.id) not in self.data["user"]:
            self.data["user"][str(author.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][str(author.id)]:
            self.data["user"][str(author.id)]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(user.id) not in self.data["user"][str(author.id)]["marriedto"]:
            self.data["user"][str(author.id)]["marriedto"][str(user.id)] = {}
            dataIO.save_json(self.file_path, self.data)
            
    async def _list_marriage(self, user):
        msg = ""    
        for userid in self.data["user"][str(user.id)]["marriedto"]:
            user = discord.utils.get(self.bot.get_all_members(), id=int(userid))
            if user:
                msg += "• {}\n\n".format(user)
        
        if msg == "":
            msg = "No-one\nMarry someone to get a free badge"
        return msg
        
    @commands.group()
    async def set(self, ctx):
        """Set aspects about yourself"""
        author = ctx.author
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            if str(author.id) not in self.settingss:
                self.settingss[str(author.id)] = {}
                dataIO.save_json(self.JSON, self.settingss)
            if "BIRTHDAY" not in self.settingss[str(author.id)]:
                self.settingss[str(author.id)]["BIRTHDAY"] = None
                dataIO.save_json(self.JSON, self.settingss)
            if "DESCRIPTION" not in self.settingss[str(author.id)]:
                self.settingss[str(author.id)]["DESCRIPTION"] = None
                dataIO.save_json(self.JSON, self.settingss)
            if "HEIGHT" not in self.settingss[str(author.id)]:
                self.settingss[str(author.id)]["HEIGHT"] = None
                dataIO.save_json(self.JSON, self.settingss)
            
    @set.command()
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
        self.settingss[str(author.id)]["HEIGHT"] = "{}'{} ({}cm)".format(feet, inches, total)
        dataIO.save_json(self.JSON, self.settingss)
        await ctx.send("Your height has been set to {}'{} ({}cm)".format(feet, inches, total))
    
    @set.command()
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
        if day > 31 or day < 1:
            return await ctx.send("Invalid Birthday :no_entry:")
        if month > 12 or month < 1:
            return await ctx.send("Invalid Birthday :no_entry:")
        elif day > 28 and month == 2:
            return await ctx.send("Invalid Birthday :no_entry:")
        elif day == 31 and (month % 2) == 0:
            return await ctx.send("Invalid Birthday :no_entry:")
        elif year is not None and (year > int(datetime.datetime.utcnow().strftime("%Y")) - 1 or year < int(datetime.datetime.utcnow().strftime("%Y")) - 100):
            return await ctx.send("Invalid Birthday :no_entry:")
        else:
            self.settingss[str(author.id)]["BIRTHDAY"] = "%02d/%02d" % (day, month) + ("/" + str(year) if year else "")
        await ctx.send("Your birthday has been set to the {}".format(self.settingss[str(author.id)]["BIRTHDAY"]))
        dataIO.save_json(self.JSON, self.settingss)
        
    @set.command(aliases=["desc"])
    async def description(self, ctx, *, description):
        """Set your decription about yourself"""
        author = ctx.author
        if len(str(description)) > 250:
            await ctx.send("Descriptions are limited to 250 characters :no_entry:")
            return
        self.settingss[str(author.id)]["DESCRIPTION"] = description
        dataIO.save_json(self.JSON, self.settingss)
        await ctx.send("Your description has been set it'll now be on your profile")
        
    @set.command()
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
    
    @set.command(aliases=["color"])
    async def colour(self, ctx, colour: discord.Colour): 
        author = ctx.author
        if str(author.id) not in self._colour:
            self._colour[str(author.id)] = {}
            dataIO.save_json(self._colour_file, self._colour)
        self._colour[str(author.id)] = colour.value
        dataIO.save_json(self._colour_file, self._colour)
        image = Image.new('RGBA', (273, 10), (colour.r, colour.g, colour.b))
        image.save("result.png")
        await ctx.send(file=discord.File("result.png", "result.png"), content="The text colour on your profile has been set.")
        try:
            os.remove("result.png")
        except:
            pass

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
    
def check_folders():
    if not os.path.exists("data/economy"):
        print("Creating data/economy folder...")
        os.makedirs("data/economy")
    if not os.path.exists("data/fun"):
        print("Creating data/fun folder...")
        os.makedirs("data/fun")


def check_files():
    f = 'data/economy/birthday.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default birthday.json...')
    f = 'data/fun/marriage.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default marriage.json...')
    f = 'data/economy/bank.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default bank.json...')
    f = 'data/economy/shop.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default shop.json...') 
    f = 'data/economy/auction.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default auction.json...')
    f = 'data/economy/materials.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default materials.json...')
    f = 'data/economy/slots.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default slots.json...')
    f = 'data/economy/factory.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default factory.json...')
    f = 'data/economy/colour.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default colour.json...')


def setup(bot): 
    global logger
    check_folders()
    check_files()
    bot.add_cog(economy(bot))