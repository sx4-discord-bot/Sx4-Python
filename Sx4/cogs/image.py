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
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from urllib.request import Request, urlopen
import re
import json
import urllib.request
from utils import data
import requests
from utils.PagedResult import PagedResult
from utils.PagedResult import PagedResultData
import random
from random import choice
import asyncio
from difflib import get_close_matches

colours = data.read_json("data/colours/colournames.json")

class image:
    """Fun image commands"""
      
    def __init__(self, bot):  
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def flag(self, ctx, flag_initial: str, *, user: discord.Member=None):
        if not user:
            user = ctx.author
        request = requests.get("http://www.geonames.org/flags/x/{}.gif".format(flag_initial))
        with open("flag.png", "wb") as f:
            f.write(request.content)
        with open("avatar.png", "wb") as f:
            f.write(requests.get(user.avatar_url).content)
        try:
            flag = Image.open("flag.png").convert("RGBA")
        except:
            return await ctx.send("Invalid flag initial :no_entry:")
        avatar = Image.open("avatar.png").convert("RGBA")
        avatar = avatar.resize((200, 200))
        flag = flag.resize((200, 200))
        flag.putalpha(100)
        avatar.paste(flag, (0, 0), flag)
        avatar.save("flag.png")
        await ctx.send(file=discord.File("flag.png", "flag.png"))
        try:
            os.remove("avatar.png")
            os.remove("flag.png")
        except:
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rip(self, ctx, *, user: discord.Member=None):
        if not user:
            user = ctx.author
        with open("avatar.png", "wb") as f:
            f.write(requests.get(user.avatar_url).content)
        image = Image.open("rip.jpg").convert("RGBA")
        avatar = Image.open("avatar.png").convert("RGBA")
        avatar = avatar.resize((260, 260))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 30)
        left = 355
        for x in range(len(user.name)):
            left -= 8
        draw.text((left, 410), "Here lies {}".format(user.name), (0, 0, 0), font=font)
        image.paste(avatar, (285, 145), avatar)
        image.save("image.png")
        await ctx.send(file=discord.File("image.png", "image.png"))
        try:
            os.remove("avatar.png")
            os.remove("image.png")
        except:
            pass
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def trash(self, ctx, user_or_imagelink: str=None):
        """Make someone look like trash"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open('image.jpg', 'wb') as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("trash-meme.jpg")
            img2 = Image.open("image.jpg")
            img2 = img2.resize((385, 384))
            img2 = img2.filter(ImageFilter.GaussianBlur(radius=7.0))
            img.paste(img2, (384, 0))
            img.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")

    @commands.command(aliases=["www"]) 
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whowouldwin(self, ctx, user_or_imagelink: str, user_or_imagelink2: str):
        """Who would win out of 2 images"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            url1 = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url1 = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url1 = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url1 = user.avatar_url
                except:
                    url1 = user_or_imagelink
        if not user_or_imagelink2:
            url2 = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink2 and "@" in user_or_imagelink2:
            userid = user_or_imagelink2.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url2 = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink2)
                url2 = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink2))
                    url2 = user.avatar_url
                except:
                    url2 = user_or_imagelink2
        try:
            with open('image1.jpg', 'wb') as f:
                f.write(requests.get(url1.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            with open('image2.jpg', 'wb') as f:
                f.write(requests.get(url2.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("whowouldwin.png").convert("RGBA")
            img2 = Image.open("image1.jpg").convert("RGBA")
            img3 = Image.open("image2.jpg").convert("RGBA")
            img2 = img2.resize((400, 400))
            img3 = img3.resize((400, 400))
            img.paste(img2, (30, 180), img2)
            img.paste(img3, (510, 180), img3)
            img.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image1.jpg")
                os.remove("image1.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command() 
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def fear(self, ctx, user_or_imagelink: str=None):
        """Make someone look feared of"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open('image.jpg', 'wb') as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("image.jpg")
            img2 = Image.open("fear-meme.png")
            img = img.resize((251, 251))
            img2.paste(img, (260, 517))
            img2.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
        
    @commands.command() 
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def emboss(self, ctx, user_or_imagelink: str=None):
        """Make a profile picture emboss"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open('image.jpg', 'wb') as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            im = Image.open("image.jpg")
            image = im.filter(ImageFilter.EMBOSS) 
            image = ImageEnhance.Contrast(image).enhance(4.0)
            image = image.filter(ImageFilter.SMOOTH)
            image.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member=None):
        """Ship 2 users"""
        if not user2:
            user2 = user1
            user1 = ctx.message.author
        shipname = str(user1.name[:math.ceil(len(user1.name)/2)]) + str(user2.name[math.ceil(len(user2.name)/2):])
        state = random.getstate()
        random.seed(user2.id + user1.id)
        number = randint(0, 100)
        random.setstate(state)
        if user1.id + user2.id == 581253343411044352:
            number = 100
        u1avatar = user1.avatar_url
        u2avatar = user2.avatar_url
        with open('image.jpg', 'wb') as f:
            f.write(requests.get(u1avatar.replace("gif", "png").replace("webp", "png")).content)
        with open('image2.jpg', 'wb') as f:
            f.write(requests.get(u2avatar.replace("gif", "png").replace("webp", "png")).content)
        user1 = Image.open("image.jpg").convert("RGBA")
        user2 = Image.open("image2.jpg").convert("RGBA")
        user1 = user1.resize((280, 280))
        user2 = user2.resize((280, 280))
        heart = Image.open("heart.png")
        image = Image.new('RGBA', (880, 280), (255, 255, 255, 0))
        image.paste(user1, (0, 0))
        image.paste(heart, (280, 0))
        image.paste(user2, (600, 0))
        image.save("result.png")
        await ctx.send(content="Ship Name: **{}**\nLove Percentage: **{}%**".format(shipname, number), file=discord.File("result.png", "result.png"))
        try:
            os.remove("result.png")
            os.remove("image.jpg")
            os.remove("image2.jpg")
        except:
            pass        

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vr(self, ctx, user_or_imagelink: str=None):
        """Make someone feel emotional in vr"""	
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open('image.jpg', 'wb') as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("vr.png").convert("RGBA")
            img = img.resize((493, 511))
            img2 = Image.open("image.jpg").convert("RGBA")
            image = Image.new('RGBA', (493, 511), (255, 255, 255, 0))
            img2 = img2.resize((225, 150))
            img2.convert('RGBA')
            image.paste(img2, (15, 310), img2)
            image.paste(img, (0, 0), img)
            image.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
					
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shit(self, ctx, user_or_imagelink: str=None):
        """Choose who you want to be shit"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open('image.jpg', 'wb') as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("shit-meme.png").convert("RGBA")
            img2 = Image.open("image.jpg").convert("RGBA")
            image = Image.new('RGBA', (763, 1080), (255, 255, 255, 0))
            img2 = img2.resize((185, 185))
            img2 = img2.rotate(50, expand=True)
            img2.convert('RGBA')
            image.paste(img2, (215, 675), img2)
            image.paste(img, (0, 0), img)
            image.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")

    @commands.command()
    async def beautiful(self, ctx, user_or_imagelink: str=None):
        """Turn something to a masterpiece"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open('image.jpg', 'wb') as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("beautiful.png").convert("RGBA")
            img2 = Image.open("image.jpg").convert("RGBA")
            img2 = img2.resize((90, 104))
            img2 = img2.rotate(1, expand=True)
            img2.convert('RGBA')
            img.paste(img2, (253, 25), img2)
            img.paste(img2, (256, 222), img2)
            img.save("result.png")
            await ctx.send(file=discord.File("result.png", "result.png"))
            try:
                os.remove("result.png")
                os.remove("image.jpg")
            except:
                pass
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command()
    async def gay(self, ctx, user_or_imagelink: str=None):
        """Turn someone or yourself gay"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                url = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    url = user.avatar_url
                except:
                    url = user_or_imagelink
        try:
            with open("image.jpg", "wb") as f:
                f.write(requests.get(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", "")).content)
            img = Image.open("image.jpg").convert("RGBA")
            img = img.resize((600, 600))
            red = Image.new("RGBA", (600, 100), (255, 0, 0, 125))
            orange = Image.new("RGBA", (600, 100), (255, 69, 0, 125))
            yellow = Image.new("RGBA", (600, 100), (255, 220, 0, 125))
            green = Image.new("RGBA", (600, 100), (0, 100, 0, 125))
            blue = Image.new("RGBA", (600, 100), (0, 0, 220, 125))
            purple = Image.new("RGBA", (600, 100), (138, 43, 226, 125))
            img.paste(red, (0, 0), red)
            img.paste(orange, (0, 100), orange)
            img.paste(yellow, (0, 200), yellow)
            img.paste(green, (0, 300), green)
            img.paste(blue, (0, 400), blue)
            img.paste(purple, (0, 500), purple)
            img.save("image.png")
            await ctx.send(file=discord.File("image.png", "image.png"))
            os.remove("image.png")
            os.remove("image.jpg")
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command(aliases=["tweet"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def trumptweet(self, ctx, *, text: str):
        """Make trump say something on twitter"""
        channel = ctx.message.channel
        author = ctx.message.author
        if len(text) > 280:
            await ctx.send("No more than 280 characters (Twitters limit) :no_entry:")
            return
        img = Image.open("trumptweet-meme.png")
        draw = ImageDraw.Draw(img)
        n = 0
        m = 70
        number = 0
        times = 0 
        size = 25
        description = ""
        for x in range(math.ceil(len(str(text))/70)+1):
            number += 1
            if [x for x in text if " " in x]:
                for x in range(len([x for x in text if " " in x])+1):
                    while text[m-1:m] != " " and m != 0 and m != len(str(text)):
                        m -= 1
                    times += 70
                    if m == 0:
                        n = times - 70
                        m = times
            description += text[n:m] + "\n"
            n = m
            m += 70
        font = ImageFont.truetype("arial.ttf", size)
        draw.text((60, 125), description, (0, 0, 0), font=font)
        img.save("result.png")
        await ctx.send(file=discord.File("result.png", "result.png"))
        try:
            os.remove("result.png")
            os.remove("image.jpg")
        except:
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def scroll(self, ctx, *, text: str):
        """The terrible truth"""
        channel = ctx.message.channel
        author = ctx.message.author
        if len(text) > 80:
            await ctx.send("No more than 80 characters :no_entry:")
            return
        img = Image.open("scroll-meme.png")
        draw = ImageDraw.Draw(img)
        n = 0
        m = 12
        char = 12
        number = 0
        times = 0 
        size = 20
        description = ""
        if (math.ceil(len(str(text))/12)+1) >=6:
            for x in range((math.ceil(len(str(text))/12)+1) - 6):
                size -= 3
                char += 1
        for x in range(math.ceil(len(str(text))/char)+1):
            number += 1
            if [x for x in text if " " in x]:
                for x in range(len([x for x in text if " " in x])+1):
                    while text[m-1:m] != " " and m != 0 and m != len(str(text)):
                        m -= 1
                    times += char
                    if m == 0:
                        n = times - char
                        m = times
            description += text[n:m] + "\n"
            n = m
            m += char
        font = ImageFont.truetype("arial.ttf", size)
        draw.text((95, 285), description, (0, 0, 0), font=font)
        img.save("result.png")
        await ctx.send(file=discord.File("result.png", "result.png"))
        try:
            os.remove("result.png")
            os.remove("image.jpg")
        except:
            pass
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def colour(self, ctx, *, colour: str=None):
        """View a colours hex code and RGB and a image with the colour, if a colour is not specified it will get a random one"""
        if not colour:
            colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
            colour = discord.Colour(int(colour, 16))
            colourname = str(colour)
            for x in colours:
                if str(colour).lower() == colours[x].lower():
                    if not re.match("(?:[a-f A-F]|[0-9]){6}" if "#" not in colour else "#(?:[a-f A-F]|[0-9]){6}", colour):
                        return await ctx.send("Invalid hex :no_entry:")
                    colourname = x.title()
            image = Image.new('RGBA', (100, 100), (colour.r, colour.g, colour.b))
            image.save("result.png")
            s=discord.Embed(colour=colour, description="Hex: {}\nRGB: ({}, {}, {})".format(str(colour), colour.r, colour.g, colour.b))
            s.set_image(url="attachment://result.png")
            s.set_author(name=colourname, icon_url="attachment://result.png")
            await ctx.send(file=discord.File("result.png", "result.png"), embed=s)
            try:
                os.remove("result.png")
            except:
                pass
            return
        colourname = colour
        for x in colours:
            if x.title() == colour.title():
                colourname = colours[x].lower()
                colour = colours[x].lower()
            elif "#" + str(colour).replace("#", "").lower() == colours[x].lower():
                if not re.match("(?:[a-f A-F]|[0-9]){6}" if "#" not in colour else "#(?:[a-f A-F]|[0-9]){6}", colour):
                    return await ctx.send("Invalid hex :no_entry:")
                colourname = x.title()
        if not re.match("(?:[a-f A-F]|[0-9]){6}" if "#" not in colour else "#(?:[a-f A-F]|[0-9]){6}", colour):
            return await ctx.send("Invalid hex :no_entry:")
        image = Image.new('RGBA', (100, 100), (discord.Colour(int(colour.replace("#", ""), 16)).r, discord.Colour(int(colour.replace("#", ""), 16)).g, discord.Colour(int(colour.replace("#", ""), 16)).b))
        image.save("result.png")
        s=discord.Embed(colour=discord.Colour(int(colour.replace("#", ""), 16)), description="Hex: {}\nRGB: ({}, {}, {})".format("#" + str(colour).replace("#", ""), discord.Colour(int(colour.replace("#", ""), 16)).r, discord.Colour(int(colour.replace("#", ""), 16)).g, discord.Colour(int(colour.replace("#", ""), 16)).b))
        s.set_image(url="attachment://result.png")
        s.set_author(name=colourname, icon_url="attachment://result.png")
        await ctx.send(file=discord.File("result.png", "result.png"), embed=s)
        try:
            os.remove("result.png")
        except:
            pass
         
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def drift(self, ctx, user: discord.Member, textleft: str, textright: str=None):
        """Drift away from something, any words over 10 characters will be ignored"""
        channel = ctx.message.channel
        author = ctx.message.author
        try:
            if len(textright) > 50:
                await ctx.send("No more than 50 characters on the right sign :no_entry:")
                return
        except:
            pass
        if len(textleft) > 50:
            await ctx.send("No more than 50 characters on the left sign :no_entry:")
            return
        img = Image.open("drift-meme.png")
        draw = ImageDraw.Draw(img)
        n = 0
        m = 10
        number = 0
        times = 0 
        size = 20
        description = ""
        for x in range(math.ceil(len(str(textleft))/10)+1):
            number += 1
            if [x for x in textleft if " " in x]:
                for x in range(len([x for x in textleft if " " in x])+1):
                    while textleft[m-1:m] != " " and m != 0 and m != len(str(textleft)):
                        m -= 1
                    times += 10
                    if m == 0:
                        n = times - 10
                        m = times
            if number > 4:
                size -= 3
            description += textleft[n:m] + "\n"
            n = m
            m += 10
        a = 0
        b = 13
        number2 = 0
        times2 = 0
        size2 = 20
        description2 = ""
        if textright:
            for x in range(math.ceil(len(str(textright))/13)+1):
                number2 += 1
                if [x for x in textright if " " in x]:
                    for x in range(len([x for x in textright if " " in x])+1):
                        while textright[b-1:b] != " " and b != 0 and b != len(str(textright)):
                            b -= 1
                        times += 13
                        if b == 0:
                            a = times - 13
                            b = times
                if number2 > 5:
                    size2 -= 3
                description2 += textright[a:b] + "\n"
                a = b
                b += 13
        font = ImageFont.truetype("arial.ttf", size)
        font2 = ImageFont.truetype("arial.ttf", size2)
        draw.text((125, 60), description, (255, 255, 255), font=font)
        if description2 != "":
            draw.text((265, 60), description2, (255, 255, 255), font=font2)
        with open('image.jpg', 'wb') as f:
            if user.avatar_url != "":
                f.write(requests.get(user.avatar_url.replace("gif", "png").replace("webp", "png")).content)
            else:
                f.write(requests.get(user.default_avatar_url.replace("gif", "png").replace("webp", "png")).content)
        img2 = Image.open("image.jpg")
        img2 = img2.resize((23, 23))
        img.paste(img2, (270, 335))
        img.save("result.png")
        await ctx.send(file=discord.File("result.png", "result.png"))
        try:
            os.remove("result.png")
            os.remove("image.jpg")
        except:
            pass
        
def setup(bot):
    bot.add_cog(image(bot))