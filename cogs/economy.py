import discord
from discord.ext import commands
import os
from copy import deepcopy
from utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import randint
from copy import deepcopy
from utils import checks
from enum import Enum
import time
import logging
import datetime
import math
from urllib.request import Request, urlopen
import json
from utils.PagedResult import PagedResult
from utils.PagedResult import PagedResultData
import random
from random import choice
import asyncio
from difflib import get_close_matches
                    

class Economy:
    """Make money"""

    def __init__(self, bot):
        global default_settings
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
        
        if "picitems" not in self._shop:
            self._shop["picitems"] = []
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
            
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def parse(self, ctx):
        code = ctx.message.content[8:]
        code = "    " + code.replace("\n", "\n    ")
        code = "async def __eval_function__():\n" + code

        additional = {}
        additional["self"] = self
        additional["ctx"] = ctx
        additional["channel"] = ctx.message.channel
        additional["author"] = ctx.message.author
        additional["server"] = ctx.message.server

        try:
            exec(code, {**globals(), **additional}, locals())

            await locals()["__eval_function__"]()
        except Exception as e:
            await self.bot.say(str(e))
			
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code):
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        try:
            await self.bot.say(str(await eval(code))) 
        except:
            try:
                await self.bot.say(str(eval(code))) 
            except Exception as e:
                await self.bot.say(str(e))
 
        
    @commands.command(pass_context=True)
    async def votebonus(self, ctx):
        """Get some extra credits by simply upvoting the bot on dbl"""
        try:
            m, s = divmod(self.settings["user"][ctx.message.author.id]["votetime"] - ctx.message.timestamp.timestamp() + 86400, 60)
            h, m = divmod(m, 60)
            if h == 0:
                time = "%d minutes %d seconds" % (m, s)
            elif h == 0 and m == 0:
                time = "%d seconds" % (s)
            else:
                time = "%d hours %d minutes %d seconds" % (h, m, s)
            if ctx.message.timestamp.timestamp() - self.settings["user"][ctx.message.author.id]["votetime"] <= 86400:
                await self.bot.say("You are too early, come collect your vote bonus again in {}".format(time))
                return
        except:
            pass
        if has_voted(ctx.message.author.id):
            self.settings["user"][ctx.message.author.id]["balance"] += 250
            await self.bot.say("Thanks for voting! Here's **$250**. Come back and vote in 24 hours for another **$250**!")
            self.settings["user"][ctx.message.author.id]["votetime"] = ctx.message.timestamp.timestamp()
            dataIO.save_json(self.location, self.settings)
        else:
            await self.bot.say("You need to upvote the bot to use this command you can do that here: https://discordbots.org/bot/440996323156819968")


    @commands.command(pass_context=True, no_pm=True)
    async def profile(self, ctx, *, user: discord.Member=None):
        """Lists aspects about you on discord with Sx4. Defaults to author."""
        author = ctx.message.author
        server = ctx.message.server
        if not user:
            user = author
        if "user" not in self.settings: 
            self.settings["user"] = {} 
            dataIO.save_json(self.location, self.settings)
        if user.id not in self.settings["user"]: 
            self.settings["user"][user.id] = {}
            dataIO.save_json(self.location, self.settings)
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if user.id not in self.data["user"]:
            self.data["user"][user.id] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][user.id]:
            self.data["user"][user.id]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if user.id not in self.settingss:
            self.settingss[user.id] = {}
            dataIO.save_json(self.JSON, self.settingss)
        if "BIRTHDAY" not in self.settingss[user.id]:
            self.settingss[user.id]["BIRTHDAY"] = "`[p]set birthday`" 
            dataIO.save_json(self.JSON, self.settingss)
        if "DESCRIPTION" not in self.settingss[user.id]:
            self.settingss[user.id]["DESCRIPTION"] = "`[p]set description`" 
            dataIO.save_json(self.JSON, self.settingss)
        if "HEIGHT" not in self.settingss[user.id]:
            self.settingss[user.id]["HEIGHT"] = "`[p]set height`" 
            dataIO.save_json(self.JSON, self.settingss)
        await self._set_bank_user(user)
        msg2 = ""
        for item2 in self._mine["items"]:
            for item in list(set(self.settings["user"][user.id]["items"])):
                if item == item2["name"]:
                    msg2 += item2["emote"] + "x" + str(self.settings["user"][user.id]["items"].count(item)) + ", "
        msg2 = msg2[:-2]
        if msg2 == "":
            msg2 = "None"
        msg = await self._list_marriage(user)
        bots = list(map(lambda m: m.id, filter(lambda m: m.bot, self.bot.get_all_members())))
        badges = ""
        if user == server.owner:
            badges += "<:server_owner:441255213450526730>"
        if user.id == "151766611097944064" or user.id == "153286414212005888" or user.id == "190551803669118976" or user.id == "402557516728369153":
            badges += "<:developer:441255213068845056>"
        if user.id == "153286414212005888" or user.id == "285451236952768512" or user.id == "388424304678666240":
            badges += "<:helper:441255213131628554> "
        if user.id in bots:
            badges += "<:bot:441255212582174731>"
        if user.id == "230533871119106049" or user.id == "181355725790904320" or user.id == "358115593343467521":
            badges += "<:donator:441255213224034325>"
        if self.settingss[user.id]["BIRTHDAY"] == "`[p]set birthday`":
            self.settingss[user.id]["BIRTHDAY"] = "`{}set birthday`".format(ctx.prefix)
        if self.settingss[user.id]["DESCRIPTION"] == "`[p]set description`":
            self.settingss[user.id]["DESCRIPTION"] = "`{}set description`".format(ctx.prefix)
        if self.settingss[user.id]["HEIGHT"] == "`[p]set height`":
            self.settingss[user.id]["HEIGHT"] = "`{}set height`".format(ctx.prefix)
        if self.settingss[user.id]["BIRTHDAY"] == "`{}set birthday`".format(ctx.prefix) and self.settingss[user.id]["DESCRIPTION"] == "`{}set description`".format(ctx.prefix) and self.settingss[user.id]["HEIGHT"] == "`{}set height`".format(ctx.prefix):
            pass
        else:
            badges += "<:profile_editor:441255213207126016>"
        if msg != "No-one":
            badges += "<:married:441255213106593803>"
        if user.game is None:
            pass
        elif user.game.url is None:
            badges += "<:playing:441255213513572358>"
        else:
            badges += "<:streaming:441255213106724865>"
        if badges == "":
            badges = "None"
        em=discord.Embed(colour=user.colour)
        em.add_field(name="Description", value="{}".format(self.settingss[user.id]["DESCRIPTION"]), inline=False)
        em.add_field(name="Badges", value=badges)
        em.add_field(name="Birthday", value="{}".format(self.settingss[user.id]["BIRTHDAY"]))
        em.add_field(name="Height", value=self.settingss[user.id]["HEIGHT"])
        em.add_field(name="Items", value=msg2)
        try:
            em.add_field(name="Reputation", value=self.settings["user"][user.id]["rep"])
        except:
            em.add_field(name="Reputation", value="0")
        try:
            em.add_field(name="Balance", value="${}" .format(self.settings["user"][user.id]["balance"]))
        except:
            em.add_field(name="Balance", value="$0")
        em.add_field(name="Married to", value=msg)
        em.set_author(name="{}'s Profile".format(user.name), icon_url=user.avatar_url)
        em.set_thumbnail(url=user.avatar_url)
        em.set_footer(text="Profile on {}".format(server.name), icon_url=server.icon_url)
        await self.bot.say(embed=em)
        return
        
    @commands.command(pass_context=True, aliases=["pd", "payday"])
    async def daily(self, ctx):
        """Collect your daily money"""
        author = ctx.message.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        await self._set_bank(author)
        if not self.settings["user"][author.id]["streaktime"]:
            self.settings["user"][author.id]["streaktime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["balance"] = self.settings["user"][author.id]["balance"] + 100
            self.settings["user"][author.id]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
            dataIO.save_json(self.location, self.settings)
            return
        m, s = divmod(self.settings["user"][author.id]["streaktime"] - ctx.message.timestamp.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.timestamp.timestamp() - self.settings["user"][author.id]["streaktime"] <= 86400:
            await self.bot.say("You are too early, come collect your money again in {}".format(time))
            return
        elif ctx.message.timestamp.timestamp() - self.settings["user"][author.id]["streaktime"] <= 172800:
            self.settings["user"][author.id]["streaktime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["streak"] = self.settings["user"][author.id]["streak"] + 1
            if  self.settings["user"][author.id]["streak"] == 1:
                money = 120
            if self.settings["user"][author.id]["streak"] == 2:
                money = 145
            if self.settings["user"][author.id]["streak"] == 3:
                money = 170
            if self.settings["user"][author.id]["streak"] == 4:
                money = 200
            if self.settings["user"][author.id]["streak"] >= 5:
                money = 250
            self.settings["user"][author.id]["balance"] = self.settings["user"][author.id]["balance"] + money
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You have collected your daily money! (**+${}**)\nYou had a bonus of ${} for having a {} day streak.".format(money, (money-100), self.settings["user"][author.id]["streak"]), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
            
            dataIO.save_json(self.location, self.settings)
            return
        else: 
            self.settings["user"][author.id]["streaktime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["balance"] = self.settings["user"][author.id]["balance"] + 100
            self.settings["user"][author.id]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You have collected your daily money! (**+$100**)", colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def rep(self, ctx, user: discord.Member):
        """Give reputation to another user"""
        server = ctx.message.server
        author = ctx.message.author
        await self._set_bank(author)
        await self._set_bank_user(user)
        if user == author:
            await self.bot.say("You can not give reputation to yourself :no_entry:")
            return
        if not self.settings["user"][author.id]["reptime"]:
            self.settings["user"][author.id]["reptime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][user.id]["rep"] = self.settings["user"][user.id]["rep"] + 1
            dataIO.save_json(self.location, self.settings)
            await self.bot.say("**+1**, {} has gained reputation".format(user.name))
            return
        m, s = divmod(self.settings["user"][author.id]["reptime"] - ctx.message.timestamp.timestamp() + 86400, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.timestamp.timestamp() - self.settings["user"][author.id]["reptime"] <= 86400:
            await self.bot.say("You are too early, give out your reputation in {}".format(time))
            return
        else:
            self.settings["user"][author.id]["reptime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][user.id]["rep"] = self.settings["user"][user.id]["rep"] + 1
            dataIO.save_json(self.location, self.settings)
            await self.bot.say("**+1**, {} has gained reputation".format(user.name))
            return
            
    @commands.command(pass_context=True, aliases=["bal"])
    async def balance(self, ctx, user: discord.Member=None):
        """Check how much money you have"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if not user:
            user = ctx.message.author
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Your balance: **${}**".format(self.settings["user"][user.id]["balance"]), colour=colour)
            except:
                s=discord.Embed(description="Your balance: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await self.bot.say(embed=s)
        else:
            await self._set_bank_user(user)
            try:
                s=discord.Embed(description="Their balance: **${}**".format(self.settings["user"][user.id]["balance"]), colour=colour)
            except:
                s=discord.Embed(description="Their balance: **$0**", colour=colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            await self.bot.say(embed=s)
			
    @commands.command(pass_context=True, aliases=["don", "allin", "dn"])
    @commands.cooldown(1, 40, commands.BucketType.user) 
    async def doubleornothing(self, ctx):
        """You double your money or lose it all it's that simple"""
        author = ctx.message.author
        if self.settings["user"][author.id]["balance"] <= 0:
            await self.bot.say("You don't have enough money to do double or nothing :no_entry:")
            ctx.command.reset_cooldown(ctx)
            return
        msg = await self.bot.say("This will bet **${}**, are you sure you want to bet this?\nYes or No".format(self.settings["user"][author.id]["balance"]))
        response = await self.bot.wait_for_message(author=author, timeout=30)
        if "yes" in response.content.lower():
            await self.bot.delete_message(msg)
        elif not response:
            await self.bot.delete_message(msg)
            await self.bot.say("The bet has been canceled.")
            ctx.command.reset_cooldown(ctx)
            return
        else:
            await self.bot.delete_message(msg)
            await self.bot.say("The bet has been canceled.")
            ctx.command.reset_cooldown(ctx)
            return
        number = randint(0, 1)
        message = await self.bot.say("You just put **${}** on the line and...".format(self.settings["user"][author.id]["balance"]))
        await asyncio.sleep(2)
        if number == 0:
            await self.bot.edit_message(message, "You lost it all! **-${}**".format(self.settings["user"][author.id]["balance"]))
            self.settings["user"][author.id]["winnings"] -= self.settings["user"][author.id]["balance"]
            self.settings["user"][author.id]["balance"] = 0
        if number == 1:
            await self.bot.edit_message(message, "You double your money! **+${}**".format(self.settings["user"][author.id]["balance"]))
            self.settings["user"][author.id]["winnings"] += self.settings["user"][author.id]["balance"]
            self.settings["user"][author.id]["balance"] *= 2
        dataIO.save_json(self.location, self.settings) 
        ctx.command.reset_cooldown(ctx)
            
    @commands.command(pass_context=True)
    async def shop(self, ctx):    
        """Check what you can buy"""
        s=discord.Embed(description="Sx4 shop use your currency in Sx4 to buy items", colour=0xfff90d)
        s.set_author(name="Shop", icon_url=self.bot.user.avatar_url)
        
        for item in self._shop["picitems"]:
            s.add_field(name=item["name"], value="Price: ${}\nDurability: {}".format(item["price"], item["durability"]))
            
        s.set_footer(text="Use s?shopbuy <item> to buy an item.")
        
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True, aliases=["pick"])
    async def pickaxe(self, ctx, user: discord.Member=None):
        """Displays your pickaxe if you have one"""
        if not user:
            user = ctx.message.author 
        msg = ""
        for item in self._shop["picitems"]:
            if item["name"] in self.settings["user"][user.id]["items"]:
                s=discord.Embed(colour=user.colour)
                s.set_author(name="{}'s {}".format(user.name, item["name"], icon_url=user.avatar_url), icon_url=user.avatar_url)
                s.add_field(name="Durability", value=str(self.settings["user"][user.id]["pickdur"]), inline=False)
                s.add_field(name="Current Price", value="$" + str(round(item["price"]/item["durability"] * self.settings["user"][user.id]["pickdur"])), inline=False)
                s.add_field(name="Original Price", value= "$" + str(item["price"]), inline=False)
                s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/131/pick_26cf.png")
                await self.bot.say(embed=s)
                return
        await self.bot.say("You do not have a pickaxe buy one at the shop :no_entry:")
        
        
    @commands.command(pass_context=True)
    async def repair(self, ctx, durability: int=None):
        """Repair your pickaxe with recourses"""
        author = ctx.message.author
        if not durability: 
            for item in self._shop["picitems"]:
                if item["name"] in self.settings["user"][author.id]["items"]:
                    if self.settings["user"][author.id]["pickdur"] == item["durability"]:
                        await self.bot.say("You already have full durability on your pickaxe :no_entry:")
                        return
                    material = item["name"][:-8]
                    for mat in self._mine["items"]:
                        if material == mat["name"]:
                            calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * (item["durability"] - self.settings["user"][author.id]["pickdur"]))
                            if calc > self.settings["user"][author.id]["items"].count(material):
                                await self.bot.say("You do not have enough materials to fix this pickaxe :no_entry:")
                            else:
                                msg = await self.bot.say("It will cost you **{} {}** to fix your pickaxe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                                response = await self.bot.wait_for_message(timeout=60, author=author)
                                if not response:
                                    await self.bot.delete_message(msg)
                                elif response.content.lower() == "yes": 
                                    await self.bot.delete_message(msg)
                                    for x in range(calc):
                                        self.settings["user"][author.id]["items"].remove(material)
                                    self.settings["user"][author.id]["pickdur"] += durability
                                    dataIO.save_json(self.location, self.settings)
                                    await self.bot.say("You have repaired your pickaxe to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], durability))
                                else:
                                    await self.bot.delete_message(msg)
                            return
                    await self.bot.say("You cannot repair this pickaxe :no_entry:")
        else:
            for item in self._shop["picitems"]:
                if item["name"] in self.settings["user"][author.id]["items"]:
                    if self.settings["user"][author.id]["pickdur"] == item["durability"]:
                        await self.bot.say("You already have full durability on your pickaxe :no_entry:")
                        return
                    material = item["name"][:-8]
                    for mat in self._mine["items"]:
                        if material == mat["name"]:
                            calc = math.ceil(((item["price"] / mat["price"]) / item["durability"]) * durability)
                            if calc > self.settings["user"][author.id]["items"].count(material):
                                await self.bot.say("You do not have enough materials to fix this pickaxe :no_entry:")
                            else:
                                msg = await self.bot.say("It will cost you **{} {}** to fix your pickaxe in it's current state, would you like to repair it?\n**yes** or **no**".format(calc, material))
                                response = await self.bot.wait_for_message(timeout=60, author=author)
                                if not response:
                                    await self.bot.delete_message(msg)
                                elif response.content.lower() == "yes": 
                                    await self.bot.delete_message(msg)
                                    for x in range(calc):
                                        self.settings["user"][author.id]["items"].remove(material)
                                    self.settings["user"][author.id]["pickdur"] += durability
                                    dataIO.save_json(self.location, self.settings)
                                    await self.bot.say("You have repaired your pickaxe to full durability. Your `{}` now has **{}** durability <:done:403285928233402378>".format(item["name"], durability))
                                else:
                                    await self.bot.delete_message(msg)
                            return
                    await self.bot.say("You cannot repair this pickaxe :no_entry:")
                
        
    @commands.command(pass_context=True)
    async def give(self, ctx, user: discord.Member, amount: int):
        """Give someone some money"""
        author = ctx.message.author
        await self._set_bank(author)
        await self._set_bank_user(user)
        if user == author:
            await self.bot.say("You can't give yourself money :no_entry:")
            return
        if amount > self.settings["user"][author.id]["balance"]:
            await self.bot.say("You don't have that much money to give :no_entry:")
            return
        if amount < 1:
            await self.bot.say("You can't give them less than a dollar, too mean :no_entry:")
            return
        self.settings["user"][user.id]["balance"] += amount
        self.settings["user"][author.id]["balance"] -= amount
        dataIO.save_json(self.location, self.settings)
        s=discord.Embed(description="You have gifted **${}** to **{}**\n\n{}'s new balance: **${}**\n{}'s new balance: **${}**".format(amount, user.name, author.name, self.settings["user"][author.id]["balance"], user.name, self.settings["user"][user.id]["balance"]), colour=author.colour)
        s.set_author(name="{} → {}".format(author.name, user.name), icon_url="https://png.kisspng.com/20171216/8cb/5a355146d99f18.7870744715134436548914.png")
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True, no_pm=True, aliases=["roulette", "rusr"])
    async def russianroulette(self, ctx, bullets: int, bet: int):
        """Risk your money with a revolver to your head with a certain amount of bullets in it, if you get shot you lose if not you win"""
        author = ctx.message.author
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if bet < 20:
            await self.bot.say("This game requires $20 to play :no_entry:")
            return
        if self.settings["user"][author.id]["balance"] < bet:
            await self.bot.say("You don't have that amount to bet :no_entry:")
            return
        if bullets <= 0:
            await self.bot.say("Invalid number of bullets :no_entry:")
            return
        if bullets >= 6:
            await self.bot.say("Invalid number of bullets :no_entry:")
            return
        self.settings["user"][author.id]["balance"] -= bet
        self.settings["user"][author.id]["winnings"] -= bet
        rr = randint(1, 6)
        winnings = math.ceil(bet * (100/((6 - bullets) / 6 * 100)* 0.95))
        if bullets >= rr:
            s=discord.Embed(description="You were shot :gun:\nYou lost your bet of **${}**".format(bet), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
        else:
            self.settings["user"][author.id]["balance"] += winnings
            self.settings["user"][author.id]["winnings"] += winnings
            s=discord.Embed(description="You're lucky, you get to live another day.\nYou Won **${}**".format(winnings), colour=discord.Colour(value=colour))
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
        dataIO.save_json(self.location, self.settings)
        
    @commands.group(pass_context=True)
    async def factory(self, ctx):
        """Factorys you can buy with recourses"""
        await self._set_bank(ctx.message.author)

    @factory.command(pass_context=True, aliases=["buy"])
    async def purchase(self, ctx, *, factory_name):
        """Buy a factory with your recourses gained by mining"""
        author = ctx.message.author
        for item in self._factories["factory"]:
            if item["name"].lower() == factory_name.lower():
                for item2 in list(set(self.settings["user"][author.id]["items"])):        
                    itemamount = self.settings["user"][author.id]["items"].count(item2)            
                    if item["item"] == item2:
                        if item["price"] <= itemamount:
                            await self.bot.say("You just bought a `{}`".format(item["name"]))
                            for x in range(item["price"]):
                                self.settings["user"][author.id]["items"].remove(item2)
                            self.settings["user"][author.id]["items"].append(item["name"])
                            dataIO.save_json(self._factories_file, self._factories)
                            dataIO.save_json(self.location, self.settings)
                        else:
                            await self.bot.say("You don't have enough `{}` to buy this :no_entry:".format(item2))

                        
    @factory.command(pass_context=True, aliases=["shop"]) 
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
        
        await self.bot.say(embed=s)
        
    @factory.command(pass_context=True)
    async def collect(self, ctx):
        """If you have a factory or mutliple use this to collect your money from them every 12 hours"""
        author = ctx.message.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        number = 0
        factoryc = 0
        for item_ in self.settings["user"][author.id]["items"]:
            for _item in self._factories["factory"]:
                if  _item["name"] == item_:
                    factoryc += 1
        if factoryc == 0:
            await self.bot.say("You do not own a factory :no_entry:")
            return
        if not self.settings["user"][author.id]["factorytime"]:
            for item in self.settings["user"][author.id]["items"]:
                for item2 in self._factories["factory"]:
                    if item2["name"] == item:
                        number += randint(item2["rand_min"], item2["rand_max"])
            if number == 0:
                await self.bot.say("You don't have any factories :no_entry:")
                return
            self.settings["user"][author.id]["factorytime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["balance"] += number
            s=discord.Embed(description="Your factories made you **${}** today".format(str(number)), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
            dataIO.save_json(self._factories_file, self._factories)
            dataIO.save_json(self.location, self.settings)
            return
        m, s = divmod(self.settings["user"][author.id]["factorytime"] - ctx.message.timestamp.timestamp() + 43200, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        if ctx.message.timestamp.timestamp() - self.settings["user"][author.id]["factorytime"] <= 43200:
            await self.bot.say("You are too early, come back to your factory in {}".format(time))
            return
        else:
            for item in self.settings["user"][author.id]["items"]:
                for item2 in self._factories["factory"]:
                    if item2["name"] == item:
                        number += randint(item2["rand_min"], item2["rand_max"])
            if number == 0:
                await self.bot.say("You don't have any factories :no_entry:")
                return
            self.settings["user"][author.id]["factorytime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["balance"] += number
            s=discord.Embed(description="Your factories made you **${}** today".format(str(number)), colour=colour)
            s.set_author(name=author.name, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
            dataIO.save_json(self._factories_file, self._factories)
            dataIO.save_json(self.location, self.settings)
                
                    
    
    @commands.command(pass_context=True, hidden=True)
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
                await self.bot.say("You fucked up")
                
                return
            
            self._shop["picitems"].append(item)
            dataIO.save_json(self._shop_file, self._shop)
            await self.bot.say("You have created the item `{}`".format(name))
        else:
            await self.bot.say("You fucked up")
            
    @commands.command(pass_context=True, hidden=True)
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
        await self.bot.say("You have created the `{}`".format(name))
            
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def addmat(self, ctx, name, value, chance, emote):
        item = {}
        item["name"] = name 
        item["price"] = int(value)
        item["rand_max"] = int(chance)
        item["emote"] = emote
        self._mine["items"].append(item)
        dataIO.save_json(self._mine_file, self._mine)
        await self.bot.say("You have created the material `{}`".format(name))
            
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def delitem(self, ctx, *, name: str):
        for item in self._shop["picitems"]:
            if item["name"] == name:
                self._shop["picitems"].remove(item)
                dataIO.save_json(self._shop_file, self._shop)
                await self.bot.say("I have deleted that item")
        
    @commands.group(pass_context=True)
    async def auction(self, ctx):
        """The Sx4 Auction house"""
        pass
        
    @auction.command(pass_context=True)
    async def sell(self, ctx, item: str, price: int, amount: int=None):
        """Sell items on the auction house"""
        author = ctx.message.author
        if amount == None:
            amount = 1
        if amount <= 0:
            await self.bot.say("You can't sell no items, we're not ebay :no_entry:")
            return
        if price < 0:
            await self.bot.say("You can't sell something for less than $0 :no_entry:")
            return
        await self._set_bank(author)
        item3 = [x.lower() for x in self.settings["user"][author.id]["items"]]
        if item3.count(item.lower()) < amount:
            await self.bot.say("You don't have that amount of `{}` to sell :no_entry:".format(item))
            return            
        if item.lower() in item3:
            auction = {}
            for item2 in self._shop["picitems"]:
                if item.lower() == item2["name"].lower():
                    auction["durability"] = self.settings["user"][author.id]["pickdur"]
                    self.settings["user"][author.id]["pickdur"] = None
            for item2 in self._shop["items"] + self._mine["items"]:
                if item.lower() == item2["name"].lower():
                    auction["durability"] = None
            auction["name"] = item.title()
            auction["ownerid"] = ctx.message.author.id
            auction["price"] = price
            auction["amount"] = amount
            for x in range(0, amount):
                self.settings["user"][author.id]["items"].remove(item.title())
            self._auction["items"].append(auction)
            dataIO.save_json(self._auction_file, self._auction)
            dataIO.save_json(self.location, self.settings)
            await self.bot.say("Your item has been put on the auction house <:done:403285928233402378>")
        else:
            await self.bot.say("You don't own that item :no_entry:")
            
    @auction.command(pass_context=True)
    async def buy(self, ctx, *, auction_item: str):
        """Buy items on the auction house"""
        author = ctx.message.author
        await self._set_bank(author)
        i = 0;
        items = [item for item in self._shop["picitems"] if item["name"] in self.settings["user"][author.id]["items"]]
        for item2 in self._shop["picitems"]:
            if item2["name"].lower() == auction_item.lower():
                for item in items:
                    i = i + 1
                if i >= 1:
                    await self.bot.say("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
                    return
        filtered = filter(lambda x: x["name"].lower() == auction_item.lower(), self._auction["items"]) 
        filtered = sorted(filtered, key=lambda x: x["price"])
        if not filtered:
            await self.bot.say("There is no `{}` on the auction house :no_entry:".format(auction_item.title()))
            return
        server = ctx.message.server
        channel = ctx.message.channel
        author = ctx.message.author
        
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
                await self.bot.send_message(channel, "That item was recently bought :no_entry:")
                return
            owner = await self.bot.get_user_info(item["ownerid"])
            if owner == ctx.message.author:
                await self.bot.send_message(channel, "You can't buy your own items :no_entry:")
                return
            if item["price"] > self.settings["user"][author.id]["balance"]:
                await self.bot.send_message(channel, "You don't have enough money for that item :no_entry:")
                return
            self._auction["items"].remove(item)
            
            self.settings["user"][author.id]["balance"] -= item["price"]
            self.settings["user"][owner.id]["balance"] += item["price"]
                
            try:
                if item["durability"]:
                    self.settings["user"][author.id]["pickdur"] = item["durability"]
            except:
                pass
                
            try:
                if item["amount"]:
                    pass
            except:
                item["amount"] = 1
                    
            for x in range(0, item["amount"]):
                self.settings["user"][author.id]["items"].append(item["name"].title())
                    
            await self.bot.send_message(channel, "You just bought a `{}` for **${}** :tada:".format(item["name"], item["price"]))
            await self.bot.send_message(owner, "Your `{}` just got bought on the auction house, it was sold for **${}** :tada:".format(item["name"], item["price"]))
            
            dataIO.save_json(self._auction_file, self._auction)
            dataIO.save_json(self.location, self.settings)
        
        paged_result.on_select = selected

        message = await self.bot.send_message(channel, embed=paged_result.get_current_page_embed())

        paged_result.message_id = message.id

        PagedResultData.paged_results[server.id][channel.id][author.id] = paged_result
          
    @commands.command(pass_context=True)
    async def fish(self, ctx):
        """Fish for some extra money"""
        author = ctx.message.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        await self._set_bank(author)
        money = randint(2, 15)
        if not self.settings["user"][author.id]["fishtime"]:
            self.settings["user"][author.id]["fishtime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["balance"] += money
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n".format(money), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
            dataIO.save_json(self.location, self.settings)
            return
        m, s = divmod(self.settings["user"][author.id]["fishtime"] - ctx.message.timestamp.timestamp() + 300, 60)
        if m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d minutes %d seconds" % (m, s)
        if ctx.message.timestamp.timestamp() - self.settings["user"][author.id]["fishtime"] <= 300:
            await self.bot.say("You are too early, come collect your money again in {}".format(time))
            return
        else:
            self.settings["user"][author.id]["fishtime"] = ctx.message.timestamp.timestamp()
            self.settings["user"][author.id]["balance"] += money
            dataIO.save_json(self.location, self.settings)
            s=discord.Embed(description="You fish for 5 minutes and sell your fish! (**+${}**) :fish:\n".format(money), colour=colour)
            s.set_author(name=author, icon_url=author.avatar_url)
            await self.bot.say(embed=s)
            dataIO.save_json(self.location, self.settings)
        
    @commands.command(pass_context=True)
    async def slot(self, ctx, bet: int):
        """Bid your money into slots with a chance of winning big"""
        author = ctx.message.author
        await self._set_bank(author)
        if self.settings["user"][author.id]["balance"] < bet:
            await self.bot.say("You don't have that much to bet :no_entry:")
            return
        if bet <= 0:
            await self.bot.say("At least bet a dollar :no_entry:")
            return
        self.settings["user"][author.id]["balance"] -= bet
        self.settings["user"][author.id]["winnings"] -= bet
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
                    winnings = bet * round((100/slot["percentage"]) * 0.5)
                    msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou won **${}**!".format(winnings)
                    self.settings["user"][author.id]["balance"] += winnings
                    self.settings["user"][author.id]["winnings"] += winnings
                    win = {}
                    win["userid"] = author.id
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
            msg = slots[number1a-1]["icon"] + slots[number2a-1]["icon"] + slots[number3a-1]["icon"] + "\n" + slot1 + slot2 + slot3 + "\n" + slots[number1b-1]["icon"] + slots[number2b-1]["icon"] + slots[number3b-1]["icon"] + "\n\nYou won **nothing**!"
        s=discord.Embed(description=msg, colour=0xfff90d)
        s.set_author(name="🎰 Slot Machine 🎰")
        s.set_thumbnail(url="https://images.emojiterra.com/twitter/512px/1f3b0.png")
        await self.bot.say(embed=s)
        dataIO.save_json(self.location, self.settings)
        
    @auction.command(pass_context=True, aliases=["house"])
    async def list(self, ctx, page: int=None):  
        """See what's in the auction house"""
        if not page:
            page = 1
        if page < 1:
            await self.bot.say("Invalid Page :no_entry:")
            return
        if page - 1 > len(self._auction["items"]) / 10:
            await self.bot.say("Invalid Page :no_entry:")
            return
        msg = ""
        for item in sorted(self._auction["items"], key=lambda x: x["price"])[page*10-10:page*10]:
            owner = discord.utils.get(self.bot.get_all_members(), id=item["ownerid"])
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
        if not msg:
            await self.bot.say("There are no items for sale on the auction house :no_entry:")
            return
        s = discord.Embed(description=msg, colour=0xfff90d, timestamp=datetime.datetime.utcnow())
        s.set_author(name="Auction House", icon_url=self.bot.user.avatar_url)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(self._auction["items"])/10)))
        await self.bot.say(embed=s) 
            
    @commands.command(pass_context=True)
    async def shopbuy(self, ctx, *, buyable_item: str):
        """Buy something from the shop"""
        author = ctx.message.author
        await self._set_bank(author)
        i = 0;
        items = [item for item in self._shop["picitems"] if item["name"] in self.settings["user"][author.id]["items"]]
        for item in items:
            i = i + 1
        if i >= 1:
            await self.bot.say("You already own a pickaxe, sell your pickaxe and try again :no_entry:")
            return
        
        for item in self._shop["picitems"]:
            if buyable_item.lower() == item["name"].lower():
                await self._set_bank(author)
                
                if buyable_item.lower() in [x.lower() for x in self.settings["user"][author.id]["items"]]:
                    await self.bot.say("You already own this item :no_entry:")
                    
                    return
                    
                author_data = self.settings["user"][author.id]
                
                if author_data["balance"] >= item["price"]:
                    author_data["balance"] -= item["price"]
                    author_data["items"].append(buyable_item.title())
                    author_data["pickdur"] = item["durability"]
                    
                    dataIO.save_json(self.location, self.settings)
                    
                    await self.bot.say("You just bought a {} for **${}** :ok_hand:".format(item["name"], item["price"]))
                else:
                    await self.bot.say("You don't have enough money to buy that item :no_entry:")
                    
    @commands.command(pass_context=True)
    async def mine(self, ctx): 
        """If you have a pickaxe use this to mine with it"""
        author = ctx.message.author
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        materials = ""
        await self._set_bank(author)
        for item in self._shop["picitems"]:
            if item["name"] in self.settings["user"][author.id]["items"]:
                amount = randint(item["rand_min"], item["rand_max"])
                if "picktime" not in self.settings["user"][author.id]:
                    self.settings["user"][author.id]["picktime"] = None
                if not self.settings["user"][author.id]["pickdur"]:
                    await self.bot.say("It seems you've came across a bug where you pick durabilty doesn't exist report this to my owner")
                    return
                if not self.settings["user"][author.id]["picktime"]:
                    author_data = self.settings["user"][author.id]
                    author_data["picktime"] = ctx.message.timestamp.timestamp()
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
                            materials += item2["name"] + ", "
                    materials = materials[:-2]
                    if materials == "":
                        materials = "Absolutely nothing"
                        
                    
                    dataIO.save_json(self.location, self.settings)
                    
                    if author_data["pickdur"] > 0:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
                    else:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                        author_data["items"].remove(item["name"])
                        
                    s.set_author(name=author.name, icon_url=author.avatar_url)
                    await self.bot.say(embed=s)

                    return
                
                m, s = divmod(self.settings["user"][author.id]["picktime"] - ctx.message.timestamp.timestamp() + 900, 60)
                h, m = divmod(m, 60)
                if h == 0:
                    time = "%d minutes %d seconds" % (m, s)
                elif h == 0 and m == 0:
                    time = "%d seconds" % (s)
                else:
                    time = "%d hours %d minutes %d seconds" % (h, m, s)
                if ctx.message.timestamp.timestamp() - self.settings["user"][author.id]["picktime"] <= 900:
                    await self.bot.say("You are too early, come back to mine in {}".format(time))
                    return
                else:
                    self.settings["user"][author.id]["picktime"] = ctx.message.timestamp.timestamp()
                    author_data = self.settings["user"][author.id]
                    self.settings["user"][author.id]["balance"] = self.settings["user"][author.id]["balance"] + amount
                    self.settings["user"][author.id]["pickdur"] = self.settings["user"][author.id]["pickdur"] - 1
                    for item2 in self._mine["items"]:
                        if round(item2["rand_max"] * item["multiplier"]) <= 0:
                            number = 1
                        else:
                            number = round(item2["rand_max"] * item["multiplier"])
                        chance = randint(0, number)
                        if chance == 0:
                            author_data["items"].append(item2["name"])
                            materials += item2["name"] + ", "
                    materials = materials[:-2]
                    if materials == "":
                        materials = "Absolutely nothing"
                    dataIO.save_json(self.location, self.settings)
                    if author_data["pickdur"] > 0:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}".format(amount, materials), colour=colour)
                    else:
                        s=discord.Embed(description="You mined recourses and made **${}** :pick:\nMaterials found: {}\nYour pickaxe broke in the process.".format(amount, materials), colour=colour)
                        author_data["items"].remove(item["name"])
                    s.set_author(name=author.name, icon_url=author.avatar_url)
                    await self.bot.say(embed=s)
                
                return
        
        await self.bot.say("You don't have a pickaxe, buy one at the shop.")
        
    @commands.command(pass_context=True)
    async def items(self, ctx, user: discord.Member=None): 
        """View your current items"""
        msg = ""
        if not user:
            user = ctx.message.author
        for item in list(set(self.settings["user"][user.id]["items"])):                
            msg += item + " x" + str(self.settings["user"][user.id]["items"].count(item)) + "\n"
        if not msg:
            msg = "None"
        s=discord.Embed(description=msg, colour=user.colour)
        s.set_author(name=user.name +"'s Items", icon_url=user.avatar_url)
        await self.bot.say(embed=s)
            
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def updatedata(self, ctx, input, output: int=None): 
        if not output:
            output = []
        i = 0;
        for userid in self.settings["user"]:
            i = i + 1
            self.settings["user"][userid]["{}".format(input)] = output
            dataIO.save_json(self.location, self.settings)
        await self.bot.say("Updated data for {}/{} users".format(i, len(self.settings["user"])))
        
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def deletedata(self, ctx, data, hidden=True):
        i = 0;
        for userid in self.settings["user"]:
            i = i + 1
            del self.settings["user"][userid]["{}".format(data)]
            dataIO.save_json(self.location, self.settings)
        await self.bot.say("Deleted data for {}/{} users".format(i, len(self.settings["user"])))
        
    async def _set_bank_user(self, user):
        if user.id in list(map(lambda m: m.id, filter(lambda m: m.bot, self.bot.get_all_members()))):
            return
        if "user" not in self.settings: 
            self.settings["user"] = {} 
            dataIO.save_json(self.location, self.settings)
        if user.id not in self.settings["user"]: 
            self.settings["user"][user.id] = {}
            dataIO.save_json(self.location, self.settings)
        if "rep" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["rep"] = 0
            dataIO.save_json(self.location, self.settings)
        if "balance" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["balance"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streak" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streaktime" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["streaktime"] = None
            dataIO.save_json(self.location, self.settings)
        if "reptime" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["reptime"] = None
            dataIO.save_json(self.location, self.settings)
        if "items" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["items"] = []
            dataIO.save_json(self.location, self.settings)
        if "pickdur" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["pickdur"] = None
            dataIO.save_json(self.location, self.settings)
        if "winnings" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["winnings"] = 0
            dataIO.save_json(self.location, self.settings)
        if "fishtime" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["fishtime"] = None
            dataIO.save_json(self.location, self.settings)
        if "votetime" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["votetime"] = None
            dataIO.save_json(self.location, self.settings)
        if "factorytime" not in self.settings["user"][user.id]:
            self.settings["user"][user.id]["factorytime"] = None
            dataIO.save_json(self.location, self.settings)
            
    async def _set_bank(self, author):
        if author.id in list(map(lambda m: m.id, filter(lambda m: m.bot, self.bot.get_all_members()))):
            return
        if "user" not in self.settings: 
            self.settings["user"] = {} 
            dataIO.save_json(self.location, self.settings)
        if author.id not in self.settings["user"]: 
            self.settings["user"][author.id] = {}
            dataIO.save_json(self.location, self.settings)
            await self.bot.say("Hey, I see that it is your first time using the brand new economy system which came to Sx4 on 1st April. Let me give a brief explanation of it, basically it's now global you compete against **everyone**"
                               ". The command `payday` has also been changed to `daily` which you can get everyday (common sense I know), you can also get streaks from it, snapchat much, come back everyday and get bonuses for doing it!"
                               " You can also check out the shop where you can buy cosmetic items (coming soon!) or items to help you make money like pickaxes which you can find materials from using them, if you get a diamond just"
                               " know you should probably scream, you also make a certain amount of money depending on the pickaxe. Last but not least there is an auction house where you can buy other users items that they've put on the"
                               " market, maybe you can get yourself some *calm* deals, or maybe you want to sell some stuff too because that's possible too, be nice or rip people off, who cares! Thanks for reading the info about the "
                               "new economy system, Lets just say the developers at Sx4 have been working very hard on this one.")
        if "rep" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["rep"] = 0
            dataIO.save_json(self.location, self.settings)
        if "balance" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["balance"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streak" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["streak"] = 0
            dataIO.save_json(self.location, self.settings)
        if "streaktime" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["streaktime"] = None
            dataIO.save_json(self.location, self.settings)
        if "reptime" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["reptime"] = None
            dataIO.save_json(self.location, self.settings)
        if "items" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["items"] = []
            dataIO.save_json(self.location, self.settings)
        if "pickdur" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["pickdur"] = None
            dataIO.save_json(self.location, self.settings)
        if "winnings" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["winnings"] = 0
            dataIO.save_json(self.location, self.settings)
        if "fishtime" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["fishtime"] = None
            dataIO.save_json(self.location, self.settings)
        if "votetime" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["votetime"] = None
            dataIO.save_json(self.location, self.settings)
        if "factorytime" not in self.settings["user"][author.id]:
            self.settings["user"][author.id]["factorytime"] = None
            dataIO.save_json(self.location, self.settings)
            
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def byebots(self, ctx):
        i = 0;

        for userid in sorted(self.settings["user"])[:len(self.settings["user"])]:
            if userid in list(map(lambda m: m.id, filter(lambda m: m.bot, self.bot.get_all_members()))):
                del self.settings["user"][userid]
                dataIO.save_json(self.location, self.settings)
                i = i + 1
        await self.bot.say("**{}** bots have been removed from the economy data".format(i))

    @commands.group(pass_context=True, aliases=["lb"])  
    async def leaderboard(self, ctx):
        """See where you're ranked"""
        pass
        
    @leaderboard.command(pass_context=True, aliases=["rep"])
    async def reputation(self, ctx, page: int=None):
        """Leaderboard for most reputation"""
        if not page:
            page = 1
        if page - 1 > len(self.settings["user"]) / 10: 
            await self.bot.say("Invalid page :no_entry:") 
            return	
        if page <= 0: 
            await self.bot.say("Invalid page :no_entry:") 
            return				
        msg = ""
        i = page*10-10;
        n = 0;
        sortedrep2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["rep"], reverse=True)
        sortedrep = sorted(self.settings["user"].items(), key=lambda x: x[1]["rep"], reverse=True)[page*10-10:page*10]
        for x in sortedrep2:
            n = n + 1
            if ctx.message.author.id == x[0]:
                break    
        for x in sortedrep:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=x[0])
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - {} reputation\n".format(i, user, x[1]["rep"])
        s=discord.Embed(title="Reputation Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.message.author.name, n, page, math.ceil(len(self.settings["user"])/10)), icon_url=ctx.message.author.avatar_url)
        await self.bot.say(embed=s)
        
    @leaderboard.command(pass_context=True, aliases=["slot"])
    async def winnings(self, ctx, page: int=None):
        """Leaderboard for most winnings"""
        if not page:
            page = 1
        if page - 1 > len(self.settings["user"]) / 10: 
            await self.bot.say("Invalid page :no_entry:") 
            return	
        if page <= 0: 
            await self.bot.say("Invalid page :no_entry:") 
            return				
        msg = ""
        i = page*10-10;
        n = 0;
        sortedwin2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["winnings"], reverse=True)
        sortedwin = sorted(self.settings["user"].items(), key=lambda x: x[1]["winnings"], reverse=True)[page*10-10:page*10]
        for x in sortedwin2:
            n = n + 1
            if ctx.message.author.id == x[0]:
                break    
        for x in sortedwin:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=x[0])
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - ${}\n".format(i, user, x[1]["winnings"])
        s=discord.Embed(title="Winnings Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.message.author.name, n, page, math.ceil(len(self.settings["user"])/10)), icon_url=ctx.message.author.avatar_url)
        await self.bot.say(embed=s)
        
    @leaderboard.command(pass_context=True)
    async def bank(self, ctx, page: int=None):
        """Leaderboard for most money"""
        if not page:
            page = 1
        if page - 1 > len([x for x in self.settings["user"].items() if x[1]["balance"] != 0]) / 10: 
            await self.bot.say("Invalid page :no_entry:") 
            return	
        if page <= 0: 
            await self.bot.say("Invalid page :no_entry:") 
            return				
        msg = ""
        i = page*10-10;
        n = 0;
        sortedbank2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["balance"], reverse=True)
        sortedbank = sorted([x for x in self.settings["user"].items() if x[1]["balance"] != 0], key=lambda x: x[1]["balance"], reverse=True)[page*10-10:page*10]
        for x in sortedbank2:
            n = n + 1
            if ctx.message.author.id == x[0]:
                break    
        for x in sortedbank:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=x[0])
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - ${}\n".format(i, user, x[1]["balance"])
        s=discord.Embed(title="Bank Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.message.author.name, n, page, math.ceil(len([x for x in self.settings["user"].items() if x[1]["balance"] != 0])/10)), icon_url=ctx.message.author.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def moneyset(self, ctx, amount: str, user: discord.Member=None):
        if not user:
            user = ctx.message.author
        if amount[0:1] == "+":
            self.settings["user"][user.id]["balance"] += int(amount[1:len(amount)])
            await self.bot.say("**{}** has been given an extra **${}**".format(user, str(amount[1:len(amount)])))
        elif amount[0:1] == "-":
            self.settings["user"][user.id]["balance"] -= int(amount[1:len(amount)])
            await self.bot.say("**{}** has had **${}** taken off their balance".format(user, str(amount[1:len(amount)])))
        else:
            self.settings["user"][user.id]["balance"] = int(amount)
            await self.bot.say("**{}** has had their balance set to **${}**".format(user, amount))
        dataIO.save_json(self.location, self.settings)
        
    @commands.command(pass_context=True)
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
            user = discord.utils.get(self.bot.get_all_members(), id=x[0])
            toploser = "${} ({})".format(x[1]["winnings"], user)
        for x in sortedslot:
            topwin = "${} ({})".format(x["winnings"], x["username"])            
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Bank Stats", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Users", value=len(self.settings["user"]))
        s.add_field(name="Total Money", value="$" + str(msg))
        s.add_field(name="Total Winnings", value="$" + str(win))
        s.add_field(name="Biggest Win (Slot)", value=topwin)
        s.add_field(name="Biggest Loser", value=toploser)
        await self.bot.say(embed=s)
        
    @leaderboard.command(pass_context=True)
    async def networth(self, ctx, page: int=None):
        """Leaderboard for most networth"""
        msg = ""
        
        author_id = ctx.message.author.id
        
        entries = []
        
        all_items = self._shop["picitems"] + self._shop["items"] + self._mine["items"]
        for member in list(set(self.bot.get_all_members())):
            if member.id in self.settings["user"]:
                user_data = self.settings["user"][member.id]
            
                worth = 0
                
                items = [item for item in all_items if item["name"] in user_data["items"]]
                for item in items:
                    if "durability" in item and user_data["pickdur"] is not None:
                        worth += round((item["price"]/item["durability"]) * user_data["pickdur"])
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
            await self.bot.say("Invalid page :no_entry:") 
            return	
        if page <= 0: 
            await self.bot.say("Invalid page :no_entry:") 
            return				
                
        networth_sorted = sorted([x for x in entries if x["worth"] != 0], key=lambda x: x["worth"], reverse=True)
        
        for index, entry in enumerate(networth_sorted):
            if entry["user"].id == author_id:
                break
        else:
            index = -1
        
        i = page*10-9
        for entry in networth_sorted[page*10-10:page*10]:
            msg += "{}. `{}` - ${}\n".format(i, entry["user"], entry["worth"])
            
            i += 1
        
        embed = discord.Embed(title="Networth Leaderboard", description = msg, colour = 0xfff90d)
        
        if index != -1:
            embed.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.message.author.name, index + 1, page, math.ceil(len([x for x in entries if x["worth"] != 0])/10)), icon_url = ctx.message.author.avatar_url)
        else:
            embed.set_footer(text = "{} does not have a rank | Page {}/{}".format(ctx.message.author.name, page, math.ceil(len([x for x in entries if x["worth"] != 0])/10)), icon_url = ctx.message.author.avatar_url)
        await self.bot.say(embed=embed)
        
    @leaderboard.command(pass_context=True)
    async def streak(self, ctx, page: int=None):
        """Leaderboard for biggest streak"""
        if not page:
            page = 1
        if page - 1 > len(self.settings["user"]) / 10: 
            await self.bot.say("Invalid page :no_entry:") 
            return	
        if page <= 0: 
            await self.bot.say("Invalid page :no_entry:") 
            return				
        msg = ""
        i = page*10-10;
        n = 0;
        sortedstreak2 = sorted(self.settings["user"].items(), key=lambda x: x[1]["streak"], reverse=True)
        sortedstreak = sorted(self.settings["user"].items(), key=lambda x: x[1]["streak"], reverse=True)[page*10-10:page*10]
        for x in sortedstreak2:
            n = n + 1
            if ctx.message.author.id == x[0]:
                break            
        for x in sortedstreak:
            i = i + 1
            user = discord.utils.get(self.bot.get_all_members(), id=x[0])
            if not user:
                user = "Unknown User"
            msg+= "{}. `{}` - {} day streak\n".format(i, user, x[1]["streak"])
        s=discord.Embed(title="Streak Leaderboard", description=msg, colour=0xfff90d)
        s.set_footer(text="{}'s Rank: #{} | Page {}/{}".format(ctx.message.author.name, n, page, math.ceil(len(self.settings["user"])/10)), icon_url=ctx.message.author.avatar_url)
        await self.bot.say(embed=s)
        
    @commands.command(pass_context=True)
    async def marry(self, ctx, user: discord.Member):
        """Marry other uses"""
        author = ctx.message.author
        server = ctx.message.server
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if author.id not in self.data["user"]:
            self.data["user"][author.id] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][author.id]:
            self.data["user"][author.id]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if user == self.bot.user:
            await self.bot.say("I'm already taken sorry :cry:")
            return
        if user.id in self.data["user"][author.id]["marriedto"]:
            await self.bot.say("Don't worry, You're already married to that user.")
            return
        await self.bot.say("{}, **{}** would like to marry you!\n**Do you accept?**\nType **yes** or **no** to choose.".format(user.mention, author.name))
        msg = await self.bot.wait_for_message(author=user)
        if ("yes" in msg.content.lower()):
            await self.bot.say("Congratulations **{}** and **{}** :heart: :tada:".format(author.name, user.name))
            await self._create_marriage_user(ctx, user)
            await self._create_marriage_author(ctx, user)
        else:
            await self.bot.say("{}, You can always try someone else.".format(author.mention))
            
    @commands.command(pass_context=True) 
    async def divorce(self, ctx, user: discord.Member):
        """Divorce someone you've married"""
        author = ctx.message.author
        if user.id in self.data["user"][author.id]["marriedto"]:
            if author == user:
                del self.data["user"][user.id]["marriedto"][author.id]
            else:
                del self.data["user"][user.id]["marriedto"][author.id]
                del self.data["user"][author.id]["marriedto"][user.id]
            dataIO.save_json(self.file_path, self.data)
            await self.bot.say("Feels bad **{}**, Argument?".format(user.name))
        else:
            await self.bot.say("You are not married to that user :no_entry:")
			
    @commands.command(pass_context=True, aliases=["mdivorce"]) 
    async def massdivorce(self, ctx):
        """Divorce everyone""" 
        author = ctx.message.author
        for userid in list(self.data["user"][author.id]["marriedto"])[:len(self.data["user"])]:
            if author.id == userid:
                del self.data["user"][userid]["marriedto"][author.id]
            else:
                del self.data["user"][userid]["marriedto"][author.id]
                del self.data["user"][author.id]["marriedto"][userid]
        dataIO.save_json(self.file_path, self.data) 
        await self.bot.say("You are now divorced from everyone previously you were married to <:done:403285928233402378>")
            
    async def _create_marriage_user(self, ctx, user):
        author = ctx.message.author
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if user.id not in self.data["user"]:
            self.data["user"][user.id] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][user.id]:
            self.data["user"][user.id]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if author.id not in self.data["user"][user.id]["marriedto"]:
            self.data["user"][user.id]["marriedto"][author.id] = {}
            dataIO.save_json(self.file_path, self.data)
    
    async def _create_marriage_author(self, ctx, user):
        author = ctx.message.author
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.file_path, self.data)
        if author.id not in self.data["user"]:
            self.data["user"][author.id] = {}
            dataIO.save_json(self.file_path, self.data)
        if "marriedto" not in self.data["user"][author.id]:
            self.data["user"][author.id]["marriedto"] = {}
            dataIO.save_json(self.file_path, self.data)
        if user.id not in self.data["user"][author.id]["marriedto"]:
            self.data["user"][author.id]["marriedto"][user.id] = {}
            dataIO.save_json(self.file_path, self.data)
            
    async def _list_marriage(self, user):
        msg = ""    
        for userid in self.data["user"][user.id]["marriedto"]:
            user = discord.utils.get(self.bot.get_all_members(), id=userid)
            if user:
                msg += "\n{}".format(user)
        if msg == "":
            msg = "No-one"
        return msg
        
    @commands.group(pass_context=True)
    async def set(self, ctx):
        """Set aspects about yourself"""
        author = ctx.message.author
        if author.id not in self.settingss:
            self.settingss[author.id] = {}
            dataIO.save_json(self.JSON, self.settingss)
        if "BIRTHDAY" not in self.settingss[author.id]:
            self.settingss[author.id]["BIRTHDAY"] = "`[p]set birthday`" 
            dataIO.save_json(self.JSON, self.settingss)
        if "DESCRIPTION" not in self.settingss[author.id]:
            self.settingss[author.id]["DESCRIPTION"] = "`[p]set description`" 
            dataIO.save_json(self.JSON, self.settingss)
        if "HEIGHT" not in self.settingss[author.id]:
            self.settingss[author.id]["HEIGHT"] = "`[p]set height`" 
            dataIO.save_json(self.JSON, self.settingss)
            
    @set.command(pass_context=True)
    async def height(self, ctx, feet: int, inches: int):
        """set your height on the profile
        example: s?set height 5 4
        height = 5'4"""
        author = ctx.message.author
        if author.id == "384620517581127681":
            await self.bot.say("Your height is already accurate no need to change it")
            return
        if feet == 8 and inches >= 4: 
            await self.bot.say("You're not taller than the tallest man :no_entry:")
            return
        if feet >= 9: 
            await self.bot.say("You're not taller than the tallest man :no_entry:")
            return
        if inches >= 12:
            await self.bot.say("There's 12 inches in a foot you should know that :no_entry:")
            return
        if feet == 0 and inches == 0:
            await self.bot.say("You have to be a height :no_entry:")
            return
        cm = inches * 2.54
        cm2 = feet * 30.48
        total = round(cm2 + cm)
        self.settingss[author.id]["HEIGHT"] = "{}'{} ({}cm)".format(feet, inches, total)
        dataIO.save_json(self.JSON, self.settingss)
        await self.bot.say("Your height has been set to {}'{} ({}cm)".format(feet, inches, total))
    
    @set.command(pass_context=True)
    async def birthday(self, ctx, day: int, month: int, year: int=None):
        """set your birthday
        example: s?set birthday 1 7 2002
        1st July 2002"""
        author = ctx.message.author
        days = "{}th".format(day)
        if day == 1:
            days = "1st"
        if day == 2:
            days = "2nd"
        if day == 3:
            days = "3rd"
        if day == 21:
            days = "21st"
        if day == 22:
            days = "22nd"
        if day == 23:
            days = "23rd"
        if day == 31:
            days = "31st"
        if day <= 0:
            await self.bot.say("Invalid day :no_entry:")
            return
        if day >= 32:
            await self.bot.say("Invalid day :no_entry:")
            return
        months = ""
        if month == 1:
            months = "January"
        if month == 2:
            months = "February"
            if day >= 30:
                await self.bot.say("Last time i checked February only had 29 days and that's on a leap year :thinking:")
                return
        if month == 3:
            months = "March"
        if month == 4:
            months = "April" 
            if day == 31:
                await self.bot.say("Last time i checked April only had 30 days :thinking:")
                return
        if month == 5:
            months = "May"
        if month == 6:
            months = "June"
            if day == 31:
                await self.bot.say("Last time i checked June only had 30 days :thinking:")
                return
        if month == 7:
            months = "July"
        if month == 8:
            months = "August"
        if month == 9:
            months = "September"
            if day == 31:
                await self.bot.say("Last time i checked September only had 30 days :thinking:")
                return
        if month == 10:
            months = "October"
        if month == 11:
            months = "November"
            if day == 31:
                await self.bot.say("Last time i checked November only had 30 days :thinking:")
                return
        if month == 12:
            months = "December"
        if months == "":
            await self.bot.say("Invalid month :no_entry:")
            return
        if not year:
            year = ""
        if year:
            if year >= int(datetime.datetime.utcnow().strftime("%Y")):
                await self.bot.say("I think we both know you weren't born in {}.".format(year))
                return
        self.settingss[author.id]["BIRTHDAY"] = "{} {} {}".format(days, months, year)
        await self.bot.say("Your birthday has been set to the {}".format(self.settingss[author.id]["BIRTHDAY"]))
        dataIO.save_json(self.JSON, self.settingss)
        
    @set.command(pass_context=True, aliases=["desc"])
    async def description(self, ctx, *, description):
        """Set your decription about yourself"""
        author = ctx.message.author
        if len(str(description)) > 250:
            await self.bot.say("Descriptions are limited to 250 characters :no_entry:")
            return
        self.settingss[author.id]["DESCRIPTION"] = description
        dataIO.save_json(self.JSON, self.settingss)
        await self.bot.say("Your description has been set it'll now be on your profile")
        
endpoint = "https://discordbots.org/api/bots/440996323156819968/check?userId={userId}"
token = "an api key goes here but it's not yours"
        
def has_voted(userId):
    request = Request(endpoint.replace("{userId}", userId))
    request.add_header("Authorization", token) 
    request.add_header('User-Agent', 'Mozilla/5.0')

    data = json.loads(urlopen(request).read().decode())
    return data["voted"] == 1
   
    
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


def setup(bot): 
    global logger
    check_folders()
    check_files()
    bot.add_cog(Economy(bot))
