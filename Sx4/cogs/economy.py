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
from utils import checks
from enum import Enum
from collections import Counter
from utils import arg
import time
import logging
import rethinkdb as r
import re
from calendar import monthrange
import datetime
import math
from cogs import general
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
mine = data.read_json("data/economy/materials.json")
factories = data.read_json("data/economy/factory.json")

class economy:
    """Make money"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tax(self, ctx):
        s=discord.Embed(description="Their Balance: **${:,}**".format(r.table("tax").get("tax")["tax"].run()), colour=0xffff00)
        s.set_author(name="Sx4 the tax bot", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=s)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def resettax(self, ctx):
        r.table("tax").get("tax").update({"tax": 0}).run()
        await ctx.send("Done")
            
    @commands.command(hidden=True)
    @checks.is_owner()
    async def parse(self, ctx):
        code = ctx.message.content[7:]
        if not code:
            with open("parse.txt", "wb") as f:
                f.write(requests.get(ctx.message.attachments[0].url).content)
            with open("parse.txt", "rb") as f:
                code = f.read().decode()
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
        try:
            os.remove("parse.txt")
        except: 
            pass
            
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
        
        
        
        authordata = r.table("bank").get(str(author.id))
        userdata = r.table("bank").get(str(user.id))
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
        tradeableitems = factories["factory"] + shop["miners"] + mine["items"] + shop["boosters"]
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
                                useramount = authordata["items"].run().count(x["name"])
                                if useramount < amount:
                                    return await ctx.send("You don't have that much `{}` to trade :no_entry:".format(x["name"])) 
                                materials2.append("{} {}".format(amount, x["name"]))
                        if i == 0:
                            return await ctx.send("One of the materials you offered doesn't exist check your spelling :no_entry:")
                try:
                    money = int(responsesplit[0])
                except:
                    return await ctx.send("Invalid money amount :no_entry:")
                if money > authordata["balance"].run():
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
                if money > authordata["balance"].run():
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
                                useramount = userdata["items"].run().count(x["name"])
                                if useramount < amount:
                                    return await ctx.send("The user doesn't have that much `{}` to trade :no_entry:".format(x["name"])) 
                                materials2.append("{} {}".format(amount, x["name"]))
                        if i == 0:
                            return await ctx.send("One of the materials you offered doesn't exist check your spelling :no_entry:")
                try:
                    money = int(responsesplit[0])
                except:
                    return await ctx.send("Invalid money amount :no_entry:")
                if money > userdata["balance"].run():
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
                if money > userdata["balance"].run():
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
                    if userdata["balance"].run() < authorgetsmoney:
                        return await ctx.send("The user no longer has enough money to give like shown in the deal :no_entry:")
                if usergetsmoney:
                    if authordata["balance"].run() < usergetsmoney:
                        return await ctx.send("You no longer have enough money to give like shown in the deal :no_entry:")
                if usergetsmaterials:
                    for x in usergetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        if authordata["items"].run().count(item) < int(amount):
                            return await ctx.send("You no longer have enough materials to continue the deal :no_entry:")
                if authorgetsmaterials:
                    for x in authorgetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        if userdata["items"].run().count(item) < int(amount):
                            return await ctx.send("The user longer has enough materials to continue the deal :no_entry:")
                if usergetsmaterials:
                    for x in usergetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        list = authordata["items"].run()
                        for x in range(int(amount)):
                            list.remove(item)
                        authordata.update({"items": list}).run()
                        userdata.update({"items": r.row["items"] + [item] * int(amount)}).run()
                if authorgetsmaterials:
                    for x in authorgetsmaterials:
                        amount = x.split(" ", 1)[0]
                        item = x.split(" ", 1)[1]
                        list = userdata["items"].run()
                        for x in range(int(amount)):
                            list.remove(item)
                        userdata.update({"items": list})
                        authordata.update({"items": r.row["items"] + [item] * int(amount)}).run()
                if authorgetsmoney:
                    authordata.update({"balance": r.row["balance"] + authorgetsmoney}).run()
                    userdata.update({"balance": r.row["balance"] - authorgetsmoney}).run()
                if usergetsmoney:
                    authordata.update({"balance": r.row["balance"] - usergetsmoney}).run()
                    userdata.update({"balance": r.row["balance"] + usergetsmoney}).run()
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
        
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="You can buy boosters to avoid annoying things like cooldowns on commands", colour=0xfff90d)
        s.set_author(name="Booster Shop", icon_url=self.bot.user.avatar_url)
        for item in shop["boosters"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDescription: {}".format(item["price"], item["description"]))
        try:    
            s.set_footer(text="Use s?booster buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run()))
        except:
            s.set_footer(text="Use s?booster buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @booster.command(name="buy")
    async def _buy_(self, ctx, *, booster):
        """Buy booster here"""
        
        authordata = r.table("bank").get(str(ctx.author.id))
        for x in shop["boosters"]:
            if x["name"].lower() == booster.lower():
                if x["price"] <= authordata["balance"].run():
                    authordata.update({"balance": r.row["balance"] - x["price"]}).run()
                    authordata.update({"items": r.row["items"].append(x["name"])}).run()
                    return await ctx.send("You just bought the booster `{}` for **${:,}** :ok_hand:".format(x["name"], x["price"]))
                else:
                    return await ctx.send("You don't have enough money to buy that booster :no_entry:")
        await ctx.send("That booster does not exist :no_entry:")

    @booster.command()
    async def activate(self, ctx, *, booster):
        """Activate booster which say they needed to be activated here"""
        authordata = r.table("bank").get(str(ctx.author.id))
        
        if booster.lower() == "lended pickaxe":
            if booster.title() in authordata["items"].run():
                has_pick = False
                for item in authordata["items"].run():
                    for pick in shop["picitems"]:
                        if pick["name"] == item:
                            has_pick = True
                            break
                if has_pick:
                    list = authordata["items"].run()
                    list.remove(booster.title())
                    authordata.update({"items": list, "picktime": None}).run()
                    await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster.title()))
                else:
                    await ctx.send("You do not own a pickaxe you should probably own one to use this booster :no_entry:")
            else:
                await ctx.send("You do not own that booster :no_entry:")
        elif booster.lower() == "miner repair":
            if booster.title() in authordata["items"].run():
                has_miner = False
                for item in authordata["items"].run():
                    for miner in shop["miners"]:
                        if miner["name"] == item:
                            has_miner = True
                            break
                if has_miner:
                    list = authordata["items"].run()
                    list.remove(booster.title())
                    authordata.update({"items": list, "minertime": None}).run()
                    await ctx.send("Your booster `{}` has been activated :ok_hand:".format(booster.title()))
                else:
                    await ctx.send("You do not own a miner you should probably own one to use this booster :no_entry:")
            else:
                await ctx.send("You do not own that booster :no_entry:")
        else:
            await ctx.send("That booster doesn't exist or isn't activatable :no_entry:")

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
        authordata = r.table("bank").get(str(ctx.author.id))
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
                                if r.table("bank").get(str(user.id)).run():
                                    r.table("bank").get(str(user.id)).update({"balance": r.row["balance"] + 200 if vote["weekend"] else 100}).run()
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
                                if r.table("bank").get(str(user.id)).run():
                                    r.table("bank").get(str(user.id)).update({"balance": r.row["balance"] + 150 if vote["weekend"] else 75}).run()
                                    referred.append(user)
                    
                await ctx.send("You have voted for the bots **{}** {} since you last used the command gathering you a total of **${:,}**, Vote for the bots again in 12 hours for more money. Referred users: {}".format(
                amount, "time" if amount == 1 else "times", money, ", ".join(map(lambda x: str(x) + " x" + str(referred.count(x)), list(set(referred)))) if referred != [] else "None"))
                await self._set_bank(author)
                authordata.update({"balance": r.row["balance"] + money}).run()
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
                if timesx4 else "**[You can vote for Sx4 for an extra ${}](https://discordbots.org/bot/440996323156819968/vote)**".format(500 if weekend else 250), inline=False)
                s.add_field(name="Jockie Music", value="**[You have voted recently you can vote for the bot again in {}](https://discordbots.org/bot/411916947773587456/vote)**".format(timejockie)
                if timejockie else "**[You can vote for Jockie Music for an extra ${}](https://discordbots.org/bot/411916947773587456/vote)**".format(300 if weekend else 150), inline=False)
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
        r.table("userprofile").insert({"id": str(author.id), "birthday": None, "description": None, "height": None, "colour": None}).run()
        r.table("marriage").insert({"id": str(author.id), "marriedto": []}).run()
        await self._set_bank_user(user)
        userdata = r.table("bank").get(str(user.id))
        usermarriage = r.table("marriage").get(str(user.id))
        userprofile = r.table("userprofile").get(str(user.id))
        msg = await self._list_marriage(user)
        if userprofile["colour"].run():
            colour = discord.Colour(userprofile["colour"].run())
            colour = (colour.r, colour.g, colour.b)
        else:
            colour = (255, 255, 255)
        try:
            image = Image.open("profile-images/{}.png".format(user.id))
        except:
            image = Image.new("RGBA", (2560, 1440), (114, 137, 218))
        if not userprofile["birthday"].run():
            birthday = "Not set"
        else:
            birthday = userprofile["birthday"].run()
        if not userprofile["description"].run():
            description = "Not set"
        else:
            description = userprofile["description"].run()
        if not userprofile["height"].run():
            height = "Not set"
        else:
            height = userprofile["height"].run()
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
        if not userprofile["birthday"].run() and not userprofile["description"].run() and not userprofile["height"].run():
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
        descriptioncheck = description 
        description = ""
        for x in range(math.ceil(len(str(descriptioncheck))/46)+1):
            if [x for x in descriptioncheck if " " in x]:
                for x in range(len([x for x in descriptioncheck if " " in x])+1):
                    while descriptioncheck[m-1:m] != " " and m != 0 and m != len(str(descriptioncheck)):
                        m -= 1
                    times += 46
                    if m == 0:
                        n = times - 46
                        m = times
            description += descriptioncheck[n:m] + "\n"
            n = m
            m += 50
        font = ImageFont.truetype("exo.regular.otf", fontsize)
        fontstats = ImageFont.truetype("exo.regular.otf", 45)
        fontbig = ImageFont.truetype("exo.regular.otf", 70)
        draw.text((left, down), str(user), colour, font=font)
        draw.text((20, 545), "Reputation: {}".format(userdata["rep"].run()), colour, font=fontstats)
        draw.text((520, 545), "Balance: ${}".format(userdata["balance"].run()), colour, font=fontstats)
        draw.text((1020, 545), "Birthday: {}".format(birthday), colour, font=fontstats)
        draw.text((1520, 545), "Height: {}".format(height), colour, font=fontstats)
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
        authordata = r.table("bank").get(str(author.id))
        await self._set_bank(author)
        if not authordata["streaktime"].run():
            authordata.update({"streaktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + 100, "streak": 0}).run()
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        m, s = divmod(authordata["streaktime"].run() - ctx.message.created_at.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - authordata["streaktime"].run() <= 86400:
            await ctx.send("You are too early, come collect your money again in {}".format(time))
            return
        elif ctx.message.created_at.timestamp() - authordata["streaktime"].run() <= 172800:
            if authordata["streak"].run() == 1:
                money = 120
            if authordata["streak"].run() == 2:
                money = 145
            if authordata["streak"].run() == 3:
                money = 170
            if authordata["streak"].run() == 4:
                money = 200
            if authordata["streak"].run() >= 5:
                money = 250
            authordata.update({"streaktime": ctx.message.created_at.timestamp(), "streak": r.row["streak"] + 1, "balance": r.row["balance"] + money}).run()
            s=discord.Embed(description="You have collected your daily money! (**+${}**)\nYou had a bonus of ${} for having a {} day streak.".format(money, (money-100), authordata["streak"].run()), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        else: 
            authordata.update({"streaktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + 100, "streak": 0}).run()
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
        userdata = r.table("bank").get(str(user.id))
        authordata = r.table("bank").get(str(author.id))
        if user == author:
            await ctx.send("You can not give reputation to yourself :no_entry:")
            return
        if not authordata["reptime"].run():
            authordata.update({"reptime": ctx.message.created_at.timestamp()}).run()
            userdata.update({"rep": r.row["rep"] + 1}).run()
            await ctx.send("**+1**, {} has gained reputation".format(user.name))
            return
        m, s = divmod(authordata["reptime"].run() - ctx.message.created_at.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - authordata["reptime"].run() <= 86400:
            await ctx.send("You are too early, give out your reputation in {}".format(time))
            return
        else:
            authordata.update({"reptime": ctx.message.created_at.timestamp()}).run()
            userdata.update({"rep": r.row["rep"] + 1}).run()
            await ctx.send("**+1**, {} has gained reputation".format(user.name))
            return
            
    @commands.command(aliases=["bal"])
    async def balance(self, ctx, *, user=None):
        """Check how much money you have"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if not user or await arg.get_member(self.bot, ctx, user) == ctx.author:
            user = ctx.author
            if user.bot:
                return await ctx.send("Bots can't make money :no_entry:")
            await self._set_bank_user(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Your balance: **${:,}**".format(userdata["balance"].run() if userdata["balance"].run() else 0), colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            user = await arg.get_member(self.bot, ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
            if user.bot:
                return await ctx.send("Bots can't make money :no_entry:")
            await self._set_bank_user(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Their balance: **${:,}**".format(userdata["balance"].run() if userdata["balance"].run() else 0), colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(name="winnings")
    async def _winnings(self, ctx, user=None):
        if not user or await arg.get_member(self.bot, ctx, user) == ctx.author:
            user = ctx.author
            if user.bot:
                return await ctx.send("Bots can't gamble :no_entry:")
            await self._set_bank_user(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Your winnings: **${:,}**".format(userdata["winnings"].run() if userdata["winnings"].run() else 0), colour=user.colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)
        else:
            user = await arg.get_member(self.bot, ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
            if user.bot:
                return await ctx.send("Bots can't gamble :no_entry:")
            await self._set_bank_user(user)
            userdata = r.table("bank").get(str(user.id))
            s=discord.Embed(description="Their winnings: **${:,}**".format(userdata["winnings"].run() if userdata["winnings"].run() else 0), colour=user.colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await ctx.send(embed=s)

    @commands.command(name="networth")
    async def _networth(self, ctx, *, user=None):
        check = False
        if not user:
            user = ctx.author
            check = True
        else:
            user = await arg.get_member(self.bot, ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        userdata = r.table("bank").get(str(user.id))
        
        
        
        all_items = shop["picitems"] + shop["items"] + mine["items"] + shop["roditems"] + shop["miners"] + shop["boosters"]
        if userdata.run():
            user_data = userdata.run()
            worth = 0
            items = [item for item in all_items if item["name"] in user_data["items"]]
            for item in items:
                if "durability" in item and item["name"].split(" ")[1] == "Pickaxe":
                    worth += round((item["price"]/item["durability"]) * user_data["pickdur"])
                elif "durability" in item and item["name"].split(" ")[1] == "Rod":
                    worth += round((item["price"]/item["durability"]) * user_data["roddur"])
                else:
                    worth += item["price"] * user_data["items"].count(item["name"])
            for item2 in [item for item in factories["factory"] if item["name"] in user_data["items"]]:
                for item3 in mine["items"]:
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
        authordata = r.table("bank").get(str(author.id))
        if authordata["balance"].run() <= 0:
            await ctx.send("You don't have enough money to do double or nothing :no_entry:")
            ctx.command.reset_cooldown(ctx)
            return
        msg = await ctx.send("This will bet **${:,}**, are you sure you want to bet this?\nYes or No".format(authordata["balance"].run()))
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
        message = await ctx.send("You just put **${:,}** on the line and...".format(authordata["balance"].run()))
        await asyncio.sleep(2)
        if number == 0:
            await message.edit(content="You lost it all! **-${:,}**".format(authordata["balance"].run()))
            authordata.update({"winnings": r.row["winnings"] - r.row["balance"], "balance": 0}).run()
        if number == 1:
            await message.edit(content="You double your money! **+${:,}**".format(authordata["balance"].run()))
            authordata.update({"winnings": r.row["winnings"] + r.row["balance"], "balance": r.row["balance"] * 2}).run()
        ctx.command.reset_cooldown(ctx)
            
    @commands.command()
    async def shop(self, ctx):    
        """Check what you can buy"""
        
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Sx4 shop use your currency in Sx4 to buy items", colour=0xfff90d)
        s.set_author(name="Shop", icon_url=self.bot.user.avatar_url)
        for item in shop["roditems"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDurability: {}".format(item["price"], item["durability"]))
        for item in shop["picitems"]:
            s.add_field(name=item["name"], value="Price: ${:,}\nDurability: {}".format(item["price"], item["durability"]))
        try:    
            s.set_footer(text="Use s?shopbuy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run()))
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
        
        authordata = r.table("bank").get(str(ctx.author.id))
        s=discord.Embed(description="Buy miners for an easier way to gather materials", colour=0xfff90d)
        s.set_author(name="Miners", icon_url=self.bot.user.avatar_url)
        for item in shop["miners"]:
            s.add_field(name=item["name"], value="Price: ${:,}".format(item["price"]))
        try:    
            s.set_footer(text="Use s?miner buy <item> to buy an item. | Your balance: ${:,}".format(authordata["balance"].run()))
        except:
            s.set_footer(text="Use s?miner buy <item> to buy an item. | Your balance: $0")
        
        await ctx.send(embed=s)

    @miner.command(name="buy")
    async def _buy(self, ctx, *, miner: str):
        """Buy a miner"""
        
        authordata = r.table("bank").get(str(ctx.author.id))
        for item in shop["miners"]:
            if item["name"].lower() == miner.lower():
                if authordata["balance"].run() >= item["price"]:
                    authordata.update({"items": r.row["items"].append(item["name"].title()), "balance": r.row["balance"] - item["price"]}).run()
                    await ctx.send("You just bought a `{}` for **${:,}** :ok_hand:".format(item["name"].title(), item["price"])) 
                    return
                else:
                    return await ctx.send("You do not have enough money to buy this miner :no_entry:")
        await ctx.send("That is not a valid miner :no_entry:")

    @miner.command(name="collect")
    async def _collect(self, ctx):
        """Collect money from your miners"""
        i = 0
        author = ctx.author
        
        
        authordata = r.table("bank").get(str(author.id))
        for miner in shop["miners"]:
            for item in authordata["items"].run():
                if item == miner["name"]:
                    i += 1
        if i == 0:
            return await ctx.send("You do not own any miners :no_entry:")
        if not authordata["minertime"].run():
            counter = Counter()
            for miner in shop["miners"]:
                for item in authordata["items"].run():
                    if item == miner["name"]:
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
                for entry in counter.most_common():
                    msg += ", " + entry[0] + " x" + str(entry[1]) + emote[entry[0]]
                msg = msg[2:]
            else:
                msg = "Absolutely nothing"

            s=discord.Embed(colour=ctx.author.colour, description="You used your miners and gathered these materials: {}".format(msg)) 
            s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(embed=s)
            authordata.update({"items": r.row["items"] + list(counter.elements()), "minertime": ctx.message.created_at.timestamp()}).run()
        else:
            m, s = divmod(authordata["minertime"].run() - ctx.message.created_at.timestamp() + 7200, 60)
            h, m = divmod(m, 60)
            if h == 0:
                time = "%d minutes %d seconds" % (m, s)
            elif h == 0 and m == 0:
                time = "%d seconds" % (s)
            else:
                time = "%d hours %d minutes %d seconds" % (h, m, s)
            if ctx.message.created_at.timestamp() - authordata["minertime"].run() <= 7200:
                await ctx.send("You are too early, come back to your miner in {}".format(time))
                return
            else:
                counter = Counter()
                for miner in shop["miners"]:
                    for item in authordata["items"].run():
                        if item == miner["name"]:
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
                    for entry in counter.most_common():
                        msg += ", " + entry[0] + " x" + str(entry[1]) + emote[entry[0]]
                    msg = msg[2:]
                else:
                    msg = "Absolutely nothing"

                s=discord.Embed(colour=ctx.author.colour, description="You used your miners and gathered these materials: {}".format(msg)) 
                s.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

                await ctx.send(embed=s)
                authordata.update({"items": r.row["items"] + list(counter.elements()), "minertime": ctx.message.created_at.timestamp()}).run()


        
    @commands.command(aliases=["pick"])
    async def pickaxe(self, ctx, *, user: discord.Member=None):
        """Displays your pickaxe if you have one"""
        if not user:
            user = ctx.author 
        
        userdata = r.table("bank").get(str(user.id))
        msg = ""
        try:
            for item in shop["picitems"]:
                if item["name"] in userdata["items"].run():
                    s=discord.Embed(colour=user.colour)
                    s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                    s.add_field(name="Durability", value=str(userdata["pickdur"].run()), inline=False)
                    s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * userdata["pickdur"].run())), inline=False)
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
        authordata = r.table("bank").get(str(author.id))
        
        
        if not durability: 
            for item in shop["picitems"]:
                if item["name"] in authordata["items"].run():
                    if authordata["pickdur"].run() >= item["durability"]:
                        await ctx.send("You already have full durability on your pickaxe :no_entry:")
                        return
                    material = item["name"][:-8]
                    for mat in mine["items"]:
                        if material == mat["name"]:
                            calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * (item["durability"] - authordata["pickdur"].run()))
                            if calc > authordata["items"].run().count(material):
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
                                    list = authordata["items"].run()
                                    for x in range(calc):
                                        list.remove(material)
                                    authordata.update({"items": list, "pickdur": item["durability"]}).run()
                                    await ctx.send("You have repaired your pickaxe to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], item["durability"]))
                                else:
                                    await msg.delete()
                            return
                    await ctx.send("You cannot repair this pickaxe :no_entry:")
        else:
            for item in shop["picitems"]:
                if item["name"] in authordata["items"].run():
                    if authordata["pickdur"].run() >= item["durability"]:
                        await ctx.send("You already have full durability on your pickaxe :no_entry:")
                        return
                    material = item["name"][:-8]
                    for mat in mine["items"]:
                        if material == mat["name"]:
                            calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * durability)
                            if calc > authordata["items"].run().count(material):
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
                                    list = authordata["items"].run()
                                    for x in range(calc):
                                        list.remove(material)
                                    authordata.update({"items": list, "pickdur": r.row["pickdur"] + durability}).run()
                                    await ctx.send("You have repaired your pickaxe. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], authordata["pickdur"].run()))
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
        authordata = r.table("bank").get(str(author.id))
        userdata = r.table("bank").get(str(user.id))
        taxdata = r.table("tax").get("tax")
        if user == author:
            await ctx.send("You can't give yourself money :no_entry:")
            return
        if amount.lower() == "all":
            amount = authordata["balance"].run()
        else:
            try:
                amount = int(amount)
            except:
                return await ctx.send("Invalid amount :no_entry:")
        if amount > authordata["balance"].run():
            await ctx.send("You don't have that much money to give :no_entry:")
            return
        if amount < 1:
            await ctx.send("You can't give them less than a dollar, too mean :no_entry:")
            return
        fullamount = amount
        if self.bot.user != user:
            amount = fullamount if "Tax Avoider" in authordata["items"].run() else round(amount * 0.95)
            tax = fullamount - amount
            userdata.update({"balance": r.row["balance"] + amount}).run()
        else:
            tax = fullamount
            amount = fullamount
        taxdata.update({"tax": r.row["tax"] + tax}).run()
        authordata.update({"balance": r.row["balance"] - fullamount}).run()
        if "Tax Avoider" in authordata["items"].run():
            list = authordata["items"].run()
            list.remove("Tax Avoider")
            authordata.update({"items": list}).run()
        s=discord.Embed(description="You have gifted **${:,}** to **{}**\n\n{}'s new balance: **${:,}**\n{}'s new balance: **${:,}**".format(amount, user.name, author.name, authordata["balance"].run(), user.name, userdata["balance"].run() if user != self.bot.user else taxdata["tax"].run()), colour=author.colour)
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
        
        authordata = r.table("bank").get(str(author.id))
        userdata = r.table("bank").get(str(user.id))
        if user == author:
            await ctx.send("You can't give yourself items :no_entry:")
            return
        for item1 in shop["picitems"]:
            if item.lower() == item1["name"].lower():
                await ctx.send("You can't give pickaxes :no_entry:")
                return
        try:
            amountofitem = authordata["items"].run().count(item.title())
        except:
            await ctx.send("You have any of that item :no_entry:")
            return
        if amountofitem >= amount:
            usercount = userdata["items"].run().count(item.title()) + amount
            authorcount = authordata["items"].run().count(item.title()) - amount
            s=discord.Embed(description="You have gifted **{} {}** to **{}**\n\n{}'s new {} amount: **{} {}**\n{}'s new {} amount: **{} {}**".format(amount, item.title(), user.name, author.name, item.title(), authorcount, item.title(), user.name, item.title(), usercount, item.title()), colour=author.colour)
            s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://png.kisspng.com/20171216/8cb/5a355146d99f18.7870744715134436548914.png")
            await ctx.send(embed=s)
            list = authordata["items"].run()
            for x in range(amount):
                list.remove(item.title())
            authordata.update({"items": list}).run()
            userdata.update({"items": r.row["items"] + [item.title()] * amount}).run()
        else:
            await ctx.send("You don't have enough `{}` to give :no_entry:".format(item.title()))
                

    @commands.command(aliases=["roulette", "rusr"])
    async def russianroulette(self, ctx, bullets: int, bet: int):
        """Risk your money with a revolver to your head with a certain amount of bullets in it, if you get shot you lose if not you win"""
        author = ctx.author
        server = ctx.guild
        await self._set_bank(author)
        authordata = r.table("bank").get(str(author.id))
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if bet < 20:
            await ctx.send("This game requires $20 to play :no_entry:")
            return
        if authordata["balance"].run() < bet:
            await ctx.send("You don't have that amount to bet :no_entry:")
            return
        if bullets <= 0:
            await ctx.send("Invalid number of bullets :no_entry:")
            return
        if bullets >= 6:
            await ctx.send("Invalid number of bullets :no_entry:")
            return
        authordata.update({"balance": r.row["balance"] - bet, "winnings": r.row["winnings"] - bet}).run()
        rr = randint(1, 6)
        winnings = math.ceil((5.7 * bet)/(6 - bullets))
        if bullets >= rr:
            s=discord.Embed(description="You were shot :gun:\nYou lost your bet of **${:,}**".format(bet), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        else:
            authordata.update({"balance": r.row["balance"] + winnings, "winnings": r.row["winnings"] + winnings}).run()
            s=discord.Embed(description="You're lucky, you get to live another day.\nYou Won **${:,}**".format(winnings), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
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
        
        authordata = r.table("bank").get(str(author.id))
        for item in factories["factory"]:
            if item["name"].lower() == factory_name.lower():
                for item2 in list(set(authordata["items"].run())):        
                    itemamount = authordata["items"].run().count(item2)            
                    if item["item"] == item2:
                        if item["price"] <= itemamount:
                            await ctx.send("You just bought a `{}`".format(item["name"]))
                            list = authordata["items"].run()
                            for x in range(item["price"]):
                                list.remove(item2)
                            list.append(item["name"])
                            authordata.update({"items": list}).run()
                        else:
                            await ctx.send("You don't have enough `{}` to buy this :no_entry:".format(item2))

                        
    @factory.command(aliases=["shop"]) 
    async def market(self, ctx):
        """View factorys you can buy"""
        
        
        s=discord.Embed(description="You can buy factories using materials you have gathered", colour=0xfff90d)
        s.set_author(name="Factories", icon_url=self.bot.user.avatar_url)
        
        
        for item2 in mine["items"]:
            for item in factories["factory"]:
                sortedfactory = sorted(factories["factory"], key=lambda x: (x["price"] * item2["price"]), reverse=True)
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
        
        authordata = r.table("bank").get(str(author.id))
        number = 0
        factoryc = 0
        for item_ in authordata["items"].run():
            for _item in factories["factory"]:
                if  _item["name"] == item_:
                    factoryc += 1
        if factoryc == 0:
            await ctx.send("You do not own a factory :no_entry:")
            return
        if not authordata["factorytime"].run():
            for item in authordata["items"].run():
                for item2 in factories["factory"]:
                    if item2["name"] == item:
                        number += randint(item2["rand_min"], item2["rand_max"])
            if number == 0:
                await ctx.send("You don't have any factories :no_entry:")
                return
            authordata.update({"factorytime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + number}).run()
            s=discord.Embed(description="Your factories made you **${}** today".format(str(number)), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        m, s = divmod(authordata["factorytime"].run() - ctx.message.created_at.timestamp() + 43200, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.created_at.timestamp() - authordata["factorytime"].run() <= 43200:
            await ctx.send("You are too early, come back to your factory in {}".format(time))
            return
        else:
            for item in authordata["items"].run():
                for item2 in factories["factory"]:
                    if item2["name"] == item:
                        number += randint(item2["rand_min"], item2["rand_max"])
            if number == 0:
                await ctx.send("You don't have any factories :no_entry:")
                return
            authordata.update({"factorytime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + number}).run()
            s=discord.Embed(description="Your factories made you **${}** today".format(str(number)), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
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
        auctiondata = r.table("auction")
        authordata = r.table("bank").get(str(author.id))
        filtered = auctiondata.filter({"ownerid": str(author.id)}).run()
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
            items = [item for item in shop["picitems"] if item["name"] in authordata["items"].run()]
            itemsrod = [item for item in shop["roditems"] if item["name"] in authordata["items"].run()]
            for item2 in shop["picitems"]:
                if item2["name"].lower() == item["name"].lower():
                    for item in items:
                        i = i + 1
                    if i >= 1:
                        await channel.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                        return
            for item2 in shop["roditems"]:
                if item2["name"].lower() == item["name"].lower():
                    for item in itemsrod:
                        i = i + 1
                    if i >= 1:
                        await channel.send("You already own a rod, sell your rod and try again :no_entry:")
                        return
            if item not in auctiondata.run():
                await channel.send("That item was recently bought :no_entry:")
                return
            auctiondata.get(item["id"]).delete().run()
                
            try:
                if item["durability"]:
                    authordata.update({"pickdur": item["durability"]}).run()
            except:
                pass
                
            try:
                if item["amount"]:
                    pass
            except:
                item["amount"] = 1
                    
            for x in range(item["amount"]):
                authordata.update({"items": r.row["items"].append(item["name"].title())}).run()
                    
            await channel.send("You just refunded your `{}`.".format(item["name"]))
        
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
        auctiondata = r.table("auction")
        authordata = r.table("bank").get(str(author.id))
        
        
        item3 = [x.lower() for x in authordata["items"].run()]
        if item3.count(item.lower()) < amount:
            await ctx.send("You don't have that amount of `{}` to sell :no_entry:".format(item))
            return            
        if item.lower() in item3:
            for item2 in shop["picitems"]:
                if item.lower() == item2["name"].lower():
                    durability = authordata["pickdur"].run()
            for item2 in shop["roditems"]:
                if item.lower() == item2["name"].lower():
                    durability = authordata["roddur"].run()
            for item2 in shop["items"] + mine["items"]:
                if item.lower() == item2["name"].lower():
                    durability = None
            name = item.title()
            ownerid = str(author.id)
            list = authordata["items"].run()
            for x in range(amount):
                list.remove(item.title())
            authordata.update({"items": list}).run()
            auctiondata.insert({"name": name, "ownerid": ownerid, "price": str(price), "amount": amount, "durability": durability}).run()
            await ctx.send("Your item has been put on the auction house <:done:403285928233402378>")
        else:
            await ctx.send("You don't own that item :no_entry:")
            
    @auction.command()
    async def buy(self, ctx, *, auction_item: str):
        """Buy items on the auction house"""
        author = ctx.author
        await self._set_bank(author)
        auctiondata = r.table("auction")
        authordata = r.table("bank").get(str(author.id))
        
        i = 0;
        items = [item for item in shop["picitems"] if item["name"] in authordata["items"].run()]
        itemsrod = [item for item in shop["roditems"] if item["name"] in authordata["items"].run()]
        for item2 in shop["picitems"]:
            if item2["name"].lower() == auction_item.lower():
                for item in items:
                    i = i + 1
                if i >= 1:
                    await ctx.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                    return
        for item2 in shop["roditems"]:
            if item2["name"].lower() == auction_item.lower():
                for item in itemsrod:
                    i = i + 1
                if i >= 1:
                    await ctx.send("You already own a rod, sell your rod and try again :no_entry:")
                    return
        filtered = filter(lambda x: x["name"].lower() == auction_item.lower(), auctiondata.run()) 
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
            if item not in auctiondata.run():
                await channel.send("That item was recently bought :no_entry:")
                return
            owner = discord.utils.get(self.bot.get_all_members(), id=int(item["ownerid"]))
            if owner == ctx.message.author:
                await channel.send("You can't buy your own items :no_entry:")
                return
            if int(item["price"]) > authordata["balance"].run():
                await channel.send("You don't have enough money for that item :no_entry:")
                return
            auctiondata.get(item["id"]).delete().run()
            
            authordata.update({"balance": r.row["balance"] - int(item["price"])}).run()
            r.table("bank").get(str(owner.id)).update({"balance": r.row["balance"] + int(item["price"])}).run()
                
            try:
                for item2 in hop["picitems"]:
                    if item["name"].lower() == item2["name"].lower():
                        authordata.update({"pickdur": item["durability"]}).run()
                for item2 in shop["roditems"]:
                    if item["name"].lower() == item2["name"].lower():
                        authordata.update({"roddur": item["durability"]}).run()
            except:
                pass
                
            try:
                if item["amount"]:
                    pass
            except:
                item["amount"] = 1
                    
            for x in range(item["amount"]):
                authordata.update({"items": r.row["items"].append(item["name"].title())}).run()
            try:
                await channel.send("You just bought `{} {}` for **${:,}** :tada:".format(item["amount"], item["name"], int(item["price"])))
            except:
                await channel.send("You just bought `1 {}` for **${:,}** :tada:".format(item["name"], int(item["price"])))
            try:
                await owner.send("Your `{}` just got bought on the auction house, it was sold for **${:,}** :tada:".format(item["name"], int(item["price"])))
            except:
                pass
        
        paged_result.on_select = selected

        message = await channel.send(embed=paged_result.get_current_page_embed())

        paged_result.message_id = message.id

        PagedResultData.paged_results[server.id][channel.id][author.id] = paged_result

    @commands.command(aliases=["rod", "fishing_rod"])
    async def fishingrod(self, ctx, user: discord.Member=None):
        if not user:
            user = ctx.author 
        msg = ""
        
        userdata = r.table("bank").get(str(user.id))
        try:
            for item in shop["roditems"]:
                if item["name"] in userdata["items"].run():
                    s=discord.Embed(colour=user.colour)
                    s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                    s.add_field(name="Durability", value=str(userdata["roddur"].run()), inline=False)
                    s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * userdata["roddur"].run())), inline=False)
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
        
        authordata = r.table("bank").get(str(author.id))
        await self._set_bank(author)
        if not authordata["fishtime"].run():
            for rod in shop["roditems"]:
                if rod["name"] in authordata["items"].run():
                    money = randint(rod["rand_min"], rod["rand_max"])
                    authordata.update({"roddur": r.row["roddur"] - 1}).run()
                    msg = "Your fishing rod broke in the process" if authordata["roddur"].run() <= 0 else ""
                    if authordata["roddur"].run() <= 0:
                        authordata.update({"items": r.row["items"].difference([rod["name"]])}).run()
                    i += 1
            if i != 1:
                money = randint(2, 15)
            authordata.update({"fishtime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + money}).run()
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n{}".format(money, msg), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
            return
        m, s = divmod(authordata["fishtime"].run() - ctx.message.created_at.timestamp() + 300, 60)
        if m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d minutes %d seconds" % (m, s)
        if ctx.message.created_at.timestamp() - authordata["fishtime"].run() <= 300:
            await ctx.send("You are too early, come collect your money again in {}".format(time))
            return
        else:
            for rod in shop["roditems"]:
                if rod["name"] in authordata["items"].run():
                    money = randint(rod["rand_min"], rod["rand_max"])
                    authordata.update({"roddur": r.row["roddur"] - 1}).run()
                    msg = "Your fishing rod broke in the process" if authordata["roddur"].run() <= 0 else ""
                    if authordata["roddur"].run() <= 0:
                        authordata.update({"items": r.row["items"].difference([rod["name"]])}).run()
                    i += 1
            if i != 1:
                money = randint(2, 15)
            authordata.update({"fishtime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + money}).run()
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n{}".format(money, msg), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await ctx.send(embed=s)
        
    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def slot(self, ctx, bet: int=None):
        """Bid your money into slots with a chance of winning big"""
        author = ctx.author
        if bet:
            await self._set_bank(author)
            authordata = r.table("bank").get(str(author.id))
            if authordata["balance"].run() < bet:
                await ctx.send("You don't have that much to bet :no_entry:")
                return
            if bet <= 0:
                await ctx.send("At least bet a dollar :no_entry:")
                return
            authordata.update({"balance": r.row["balance"] - bet, "winnings": r.row["winnings"] - bet}).run()
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
                        authordata.update({"balance": r.row["balance"] + winnings, "winnings": r.row["winnings"] + winnings}).run()
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
        if itemnamesearch == True:
            type = sorted(filter(lambda x: x["name"].lower() == itemname.lower(), auctiondata.run()), key=lambda x: x["price"])
        else:
            type = sorted(auctiondata.run(), key=lambda x: x["price"])
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
        authordata = r.table("bank").get(str(author.id))
        
        for item in shop["picitems"]:
            if buyable_item.lower() == item["name"].lower():
                items = [item for item in shop["picitems"] if item["name"] in authordata["items"].run()]
                for item in items:
                    i = i + 1
                if i >= 1:
                    await ctx.send("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                    return
                await self._set_bank(author)
                
                if buyable_item.lower() in [x.lower() for x in authordata["items"].run()]:
                    await ctx.send("You already own this item :no_entry:") 
                    return
                    
                author_data = authordata.run()
                
                if author_data["balance"] >= item["price"]:
                    authordata.update({"balance": r.row["balance"] - item["price"], "items": r.row["items"].append(buyable_item.title()), "pickdur": item["durability"]}).run()
                    
                    await ctx.send("You just bought a {} for **${:,}** :ok_hand:".format(item["name"], item["price"]))
                    through = True
                else:
                    await ctx.send("You don't have enough money to buy that item :no_entry:")
                    through = True
        for item in shop["roditems"]:
            if buyable_item.lower() == item["name"].lower():
                rods = [item for item in shop["roditems"] if item["name"] in authordata["items"].run()]
                for rod in rods:
                    n += 1
                if n >= 1:
                    await ctx.send("You already own a fishing rod use the rest of it then buy a new one :no_entry:")
                    return
                await self._set_bank(author)
                
                if buyable_item.lower() in [x.lower() for x in authordata["items"].run()]:
                    await ctx.send("You already own this item :no_entry:")
                    return
                    
                author_data = authordata.run()
                
                if author_data["balance"] >= item["price"]:
                    authordata.update({"balance": r.row["balance"] - item["price"], "items": r.row["items"].append(buyable_item.title()), "roddur": item["durability"]}).run()
                    
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
        authordata = r.table("bank").get(str(author.id))
        
        
        for item in shop["picitems"]:
            if item["name"] in authordata["items"].run():
                amount = randint(item["rand_min"], item["rand_max"])
                if not authordata["pickdur"].run():
                    await ctx.send("It seems you've came across a bug where your pick durabilty doesn't exist report this to my owner, your pick has been removed from your items and you should be able to buy a new one.")
                    authordata.update({"items": r.row["items"].difference([item["name"]])}).run()
                    return
                if not authordata["picktime"].run():
                    authordata.update({"picktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + amount, "pickdur": r.row["pickdur"] - 1}).run()
                    for item2 in mine["items"]:
                        if round(item2["rand_max"] * item["multiplier"]) <= 0:
                            number = 1
                        else:
                            number = round(item2["rand_max"] * item["multiplier"])
                        chance = randint(0, number)
                        if chance == 0:
                            authordata.update({"items": r.row["items"].append(item2["name"])}).run()
                            materials += item2["name"] + item2["emote"] + ", "
                    materials = materials[:-2]
                    if materials == "":
                        materials = "Absolutely nothing"
                        
                    
                    if authordata["pickdur"].run() > 0:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
                    else:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                        authordata.update({"items": r.row["items"].difference([item["name"]])}).run()          
                    s.set_author(name=author.name, icon_url=author.avatar_url)
                    await ctx.send(embed=s)
                    return
                
                m, s = divmod(authordata["picktime"].run() - ctx.message.created_at.timestamp() + 900, 60)
                h, m = divmod(m, 60)
                if h == 0:
                    time = "%d minutes %d seconds" % (m, s)
                elif h == 0 and m == 0:
                    time = "%d seconds" % (s)
                else:
                    time = "%d hours %d minutes %d seconds" % (h, m, s)
                if ctx.message.created_at.timestamp() - authordata["picktime"].run() <= 900:
                    await ctx.send("You are too early, come back to mine in {}".format(time))
                    return
                else:
                    authordata.update({"picktime": ctx.message.created_at.timestamp(), "balance": r.row["balance"] + amount, "pickdur": r.row["pickdur"] - 1}).run()
                    for item2 in mine["items"]:
                        if round(item2["rand_max"] * item["multiplier"]) <= 0:
                            number = 1
                        else:
                            number = round(item2["rand_max"] * item["multiplier"])
                        chance = randint(0, number)
                        if chance == 0:
                            authordata.update({"items": r.row["items"].append(item2["name"])}).run()
                            materials += item2["name"] + item2["emote"] + ", "
                    materials = materials[:-2]
                    if materials == "":
                        materials = "Absolutely nothing"
                    if authordata["pickdur"].run() > 0:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
                    else:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                        authordata.update({"items": r.row["items"].difference([item["name"]])}).run()    
                    s.set_author(name=author.name, icon_url=author.avatar_url)
                    await ctx.send(embed=s)
                
                return
        
        await ctx.send("You don't have a pickaxe, buy one at the shop.")
        
    @commands.command(aliases=["inventory"])
    async def items(self, ctx, *, user: discord.Member=None): 
        """View your current items"""
        if not user:
            user = ctx.author
        userdata = r.table("bank").get(str(user.id)).run()
        counter = Counter(userdata["items"])
        items = counter.most_common()
        items = "\n".join(["{} x{}".format(x[0], x[1]) for x in items])
        if items == "":
            items = "None"
        s=discord.Embed(description=items, colour=user.colour)
        s.set_author(name=user.name +"'s Items", icon_url=user.avatar_url)
        await ctx.send(embed=s)
        
    async def _set_bank_user(self, user):
        if user.bot:
            return
        r.table("bank").insert({"id": str(user.id), "rep": 0, "balance": 0, "streak": 0, "streaktime": None,
        "reptime": None, "items": [], "pickdur": None, "roddur": None, "minertime": None, "winnings": 0,
        "fishtime": None, "factorytime": None}).run()
            
    async def _set_bank(self, author):
        if author.bot:
            return
        r.table("bank").insert({"id": str(author.id), "rep": 0, "balance": 0, "streak": 0, "streaktime": None,
        "reptime": None, "items": [], "pickdur": None, "roddur": None, "minertime": None, "winnings": 0,
        "fishtime": None, "factorytime": None}).run()

    @commands.group(aliases=["lb"])  
    async def leaderboard(self, ctx):
        """See where you're ranked"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            pass

    @leaderboard.command()
    async def votes(self, ctx, page: int=None):
        if not page:
            page = 1
        counter = Counter()
        
        votesjockie = requests.get("http://localhost:8080/411916947773587456/votes?ids=true").json()["votes"]
        votessx4 = requests.get("http://localhost:8080/440996323156819968/votes?ids=true").json()["votes"]
        for x in votessx4.items():
            counter[x[0]] += len(x[1]["votes"])
        for x in votesjockie.items():
            counter[x[0]] += len(x[1]["votes"])
        votes = counter.most_common()
        if page < 1 or page > math.ceil(len(votes)/10):
            return await ctx.send("Invalid Page :no_entry:")
        i, msg, n = page*10-10, "", 0
        for x in votes:
            if str(ctx.author.id) in map(lambda x: x[0], votes):
                n += 1
                if str(ctx.author.id) == x[0]:
                    break
            else:
                n = None
        for x in votes[page*10-10:page*10]:
            i += 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown user"
            msg += "{}. `{}` - {} {}\n".format(i, user, x[1], "vote" if x[1] == 1 else "votes")
        s=discord.Embed(title="Votes Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(votes)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)

    @leaderboard.command(name="items")
    async def _items(self, ctx, item: str, page: int=None):
        if not page:
            page = 1
        counter = Counter()
        data = r.table("bank")
        for y in data.run():
            counter[y["id"]] += len(list(filter(lambda x: x.lower() == item.lower(), data.get(y["id"])["items"].run())))
        if len(counter) == 0:
            return await ctx.send("No one has that item or it doesn't exist :no_entry:")
        users = counter.most_common()
        userspg = counter.most_common()[page*10-10:page*10]
        if page < 1 or page > math.ceil(len(users)/10):
            return await ctx.send("Invalid Page :no_entry:")
        i, msg, n = page*10-10, "", 0
        if str(ctx.author.id) in map(lambda x: x[0], users):
            for x in users:
                n += 1
                if str(ctx.author.id) == x[0]:
                    break
        else:
            n = None
        for x in userspg:
            i += 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x[0]))
            if not user:
                user = "Unknown User"
            msg += "{}. `{}` - {:,} {}\n".format(i, user, x[1], item.title())
        s=discord.Embed(title="{} Leaderboard".format(item.title()), description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(users)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command(aliases=["rep"])
    async def reputation(self, ctx, page: int=None):
        """Leaderboard for most reputation"""
        if not page:
            page = 1
        data = r.table("bank")
        list = data.filter(lambda x: x["rep"] != 0).order_by(r.desc("rep")).run()
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
            user = discord.utils.get(self.bot.get_all_members(), id=int(x["id"]))
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
        data = r.table("bank").run()
        list = sorted(data, key=lambda x: x["winnings"], reverse=True)
        if page - 1 > len(list) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        n = 0
        
        sortedwin2 = list
        sortedwin = list[page*10-10:page*10]
        if str(ctx.author.id) in map(lambda x: x["id"], sortedwin2):
            for x in sortedwin2:
                n = n + 1
                if str(ctx.author.id) == x["id"]:
                    break    
        else:
            n = None
        for i, x in enumerate(sortedwin, start=page*10-9):
            user = discord.utils.get(self.bot.get_all_members(), id=int(x["id"]))
            if not user:
                user = "Unknown User"
            msg += "{}. `{}` - ${:,}\n".format(i, user, x["winnings"])
        s=discord.Embed(title="Winnings Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(list)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @leaderboard.command()
    async def bank(self, ctx, page: int=None):
        """Leaderboard for most money"""
        if not page:
            page = 1
        data = r.table("bank").run()
        list = sorted(data, key=lambda x: x["balance"], reverse=True)
        if page - 1 > len(list) / 10: 
            await ctx.send("Invalid page :no_entry:") 
            return    
        if page <= 0: 
            await ctx.send("Invalid page :no_entry:") 
            return                
        msg = ""
        i = page*10-10;
        n = 0;
        
        sortedbank2 = list
        sortedbank = list[page*10-10:page*10]
        if str(ctx.author.id) in map(lambda x: x["id"], sortedbank2):
            for x in sortedbank2:
                n = n + 1
                if str(ctx.author.id) == x["id"]:
                    break    
        else:
            n = None
        for x in sortedbank:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=int(x["id"]))
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - ${:,}\n".format(i, user, x["balance"])
        s=discord.Embed(title="Bank Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: {} | Page {}/{}".format(ctx.author.name, "#{}".format(n) if n else "Unranked", page, math.ceil(len(list)/10)), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=s)
        
    @commands.command(hidden=True)
    @checks.is_main_owner()
    async def moneyset(self, ctx, amount: str, *, user: discord.Member=None):
        if not user:
            user = ctx.author
        userdata = r.table("bank").get(str(user.id))
        if amount[0:1] == "+":
            userdata.update({"balance": r.row["balance"] + int(amount[1:len(amount)])}).run()
            await ctx.send("**{}** has been given an extra **${}**".format(user, amount[1:len(amount)]))
        elif amount[0:1] == "-":
            userdata.update({"balance": r.row["balance"] - int(amount[1:len(amount)])}).run()
            await ctx.send("**{}** has had **${}** taken off their balance".format(user, amount[1:len(amount)]))
        else:
            userdata.update({"balance": int(amount)}).run()
            await ctx.send("**{}** has had their balance set to **${}**".format(user, amount))
        
    @commands.command()
    async def bankstats(self, ctx):
        """See some of the bank statistics"""
        total = sum(r.table("bank").map(lambda x: x["balance"]).run())
        win = sum(r.table("bank").map(lambda x: x["winnings"]).run())
        
        sortedloser = r.table("bank").order_by("winnings").run()[0]
        user = discord.utils.get(self.bot.get_all_members(), id=int(sortedloser["id"]))
        toploser = "${:,} ({})".format(sortedloser["winnings"], user)        
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Bank Stats", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Users", value=r.table("bank").count().run())
        s.add_field(name="Total Money", value="${:,}".format(total))
        s.add_field(name="Total Winnings", value="${:,}".format(win))
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
        
        all_items = shop["picitems"] + shop["items"] + mine["items"] + shop["roditems"] + shop["miners"] + shop["boosters"]
        bank_data = r.table("bank").run()
        users = {user.id: user for user in self.bot.get_all_members()}

        for user_data in bank_data:
            try:
                user = users[int(user_data["id"])]
                worth = 0

                items = [item for item in all_items if item["name"] in user_data["items"]]
                for item in items:
                    if "durability" in item and item["name"].split(" ")[1] == "Pickaxe":
                        worth += round((item["price"]/item["durability"]) * user_data["pickdur"])
                    elif "durability" in item and item["name"].split(" ")[1] == "Rod":
                        worth += round((item["price"]/item["durability"]) * user_data["roddur"])
                    else:
                        worth += item["price"] * user_data["items"].count(item["name"])
                
                for item2 in [item for item in factories["factory"] if item["name"] in user_data["items"]]:
                    for item3 in mine["items"]:
                        if item3["name"] == item2["item"]:
                            worth += item2["price"] * item3["price"]
                
                worth += user_data["balance"]
                
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
        data = r.table("bank").run()
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
            user = discord.utils.get(self.bot.get_all_members(), id=int(x["id"]))
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
        r.table("marriage").insert({"id": str(author.id), "marriedto": []}).run()
        r.table("marriage").insert({"id": str(user.id), "marriedto": []}).run()
        authormarriage = r.table("marriage").get(str(author.id))
        usermarriage = r.table("marriage").get(str(user.id))
        if authormarriage["marriedto"].run():
            if len(authormarriage["marriedto"].run()) >= 5:
                await ctx.send("You are married to the max amount of users possible (5 users) you need to divorce someone to marry this user :no_entry:")
                return
        if usermarriage["marriedto"].run():
            if len(usermarriage["marriedto"].run()) >= 5:
                await ctx.send("This user is married to the max amount of users possible (5 users) they need to divorce someone to marry you :no_entry:")
                return
        if str(user.id) in authormarriage["marriedto"].run():
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
            if user == author:
                await self._create_marriage_user(ctx, user)
            else:
                await self._create_marriage_user(ctx, user)
                await self._create_marriage_author(ctx, user)
        else:
            await ctx.send("{}, You can always try someone else.".format(author.mention))
            
    @commands.command() 
    async def divorce(self, ctx, user: str):
        """Divorce someone you've married"""
        author = ctx.author
        user = await arg.get_member(self.bot, ctx, user)
        if not user:
            await ctx.send("I could not find that user :no_entry:")
            return
        authormarriage = r.table("marriage").get(str(author.id))
        usermarriage = r.table("marriage").get(str(user.id))
        if str(user.id) in authormarriage["marriedto"].run():
            if author == user:
                authormarriage.update({"marriedto": r.row["marriedto"].difference([str(user.id)])}).run()
            else:
                try:
                    authormarriage.update({"marriedto": r.row["marriedto"].difference([str(user.id)])}).run()
                except:
                    pass
                try:
                    usermarriage.update({"marriedto": r.row["marriedto"].difference([str(author.id)])}).run()
                except: 
                    pass
            await ctx.send("Feels bad **{}**, Argument?".format(user.name))
        else:
            await ctx.send("You are not married to that user :no_entry:")

    @commands.command()
    async def married(self, ctx, user: discord.Member=None):
        if not user:
            user = ctx.author
        usermarriage = r.table("marriage").get(str(user.id))
        if usermarriage.run():
            user = await self.bot.get_user_info(x)
            list = [str(user) + " ({})".format(x) for x in usermarriage["marriedto"].run()]
        else:
            return await ctx.send("That user is not married to anyone :no_entry:")
        await ctx.send(embed=discord.Embed(description="\n".join(list) if list != [] else "No one :(").set_author(name=str(user), icon_url=user.avatar_url))
            
    @commands.command(aliases=["mdivorce"]) 
    async def massdivorce(self, ctx):
        """Divorce everyone""" 
        author = ctx.author
        r.table("marriage").get(str(author.id)).delete().run()
        await ctx.send("You are now divorced from everyone previously you were married to <:done:403285928233402378>")
            
    async def _create_marriage_user(self, ctx, user):
        author = ctx.author
        r.table("marriage").get(str(user.id)).update({"marriedto": r.row["marriedto"].append(str(author.id))}).run()
    
    async def _create_marriage_author(self, ctx, user):
        author = ctx.message.author
        r.table("marriage").get(str(author.id)).update({"marriedto": r.row["marriedto"].append(str(user.id))}).run()
            
    async def _list_marriage(self, user):
        msg = ""    
        for x in r.table("marriage").get(str(user.id))["marriedto"].run():
            user = discord.utils.get(self.bot.get_all_members(), id=int(x))
            if user:
                msg += "• {}\n\n".format(user)
        
        if msg == "":
            msg = "No-one\nMarry someone to get a free badge"
        return msg
        
    @commands.group(name="set")
    async def _set(self, ctx):
        """Set aspects about yourself"""
        author = ctx.author
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("userprofile").insert({"id": str(author.id), "birthday": None, "height": None, "description": None, "colour": None}).run()
            
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
        r.table("userprofile").get(str(author.id)).update({"height": "{}'{} ({}cm)".format(feet, inches, total)}).run()
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
            r.table("userprofile").get(str(author.id)).update({"birthday": "%02d/%02d" % (day, month) + ("/" + str(year) if year else "")}).run()
        await ctx.send("Your birthday has been set to the {}".format(r.table("userprofile").get(str(author.id))["birthday"].run()))
        
    @_set.command(aliases=["desc"])
    async def description(self, ctx, *, description):
        """Set your decription about yourself"""
        author = ctx.author
        if len(str(description)) > 300:
            await ctx.send("Descriptions are limited to 300 characters :no_entry:")
            return
        r.table("userprofile").get(str(author.id)).update({"description": description}).run()
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
        author = ctx.author
        userdata = r.table("userprofile").get(str(author.id))
        if not userdata.run():
            r.table("userprofile").insert({"id": str(author.id), "birthday": None, "description": None, "height": None, "birthday": None}).run()
        image = Image.new('RGBA', (273, 10), (colour.r, colour.g, colour.b))
        image.save("result.png")
        await ctx.send(file=discord.File("result.png", "result.png"), content="The text colour on your profile has been set.")
        try:
            os.remove("result.png")
        except:
            pass

    @commands.command()
    async def birthdays(self, ctx, *additionals):
        today = datetime.date.today()
        birthdays = r.table("userprofile").filter(lambda x: x["birthday"] != None).run()

        def get(data):
            date = data.split("/")
            return datetime.date(today.year, int(date[1]), int(date[0]))

        birthdays = {data["id"]: get(data["birthday"]) for data in birthdays}

        next_month = today + datetime.timedelta(days=30)
        birthdays = sorted(list(filter(lambda data: data[1] >= today and data[1] <= next_month, birthdays.items())), key=lambda x: time.mktime(x[1].timetuple()))

        msg = ""
        
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

def setup(bot): 
    bot.add_cog(economy(bot))