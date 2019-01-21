import discord
from discord.ext import commands
import os
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import randint
from copy import deepcopy
from io import BytesIO, StringIO
from utils import checks
from enum import Enum
import time
import logging
import datetime
import math
from utils import arg
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageSequence
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
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def hot(self, ctx, user_or_image: str=None):
        """The specified user/image will be called hot by will smith"""
        if ctx.message.attachments and not user_or_image:
            url = ctx.message.attachments[0].url
        elif not ctx.message.attachments and not user_or_image:
            url = ctx.author.avatar_url
        else:
            user = await arg.get_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = user.avatar_url
        try:
            avatar = getImage(url).resize((400, 300))
        except:
            return await ctx.send("Invalid user/image :no_entry:")
        image = Image.open("thats-hot-meme.png").resize((419, 493))
        main = Image.new('RGBA', (419, 493), (255, 255, 255, 0))
        main.paste(avatar, (8, 213), avatar)
        main.paste(image, (0, 0), image)
        await send_file(ctx, main)

    @commands.command(name="discord")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def _discord(self, ctx, user: str, *, discord_text: str):
        if len(discord_text) > 2000:
            return await ctx.send("You can not have more than 2000 characters :no_entry:")
        user = await arg.get_member(ctx, user)
        if not user:
            return await ctx.send("Invalid User :no_entry:")
        if discord_text.lower().endswith(" --white"):
            white = True
            discord_text = discord_text[:-8]
        else: 
            white = False
        bot = getImage("https://cdn.discordapp.com/emojis/441255212582174731.png").resize((60, 60))
        breaks = len([x for x in discord_text if x == "\n"])
        length = 66 if user.bot else 0
        text = ImageFont.truetype("whitney/whitney-book.otf", 34)
        textsize = text.getsize(discord_text)
        times = math.ceil(len(discord_text)/50)
        height = (times * 36) + (breaks * 36)
        n, m, final_text = 0, 50, ""
        for x in range(times):
            if n != 0:
                while discord_text[n-1:n] != " " and len(discord_text) != n:
                    if n != 0:
                        n -= 1
                    else:
                        n = ((x + 1) * 50) - 50
                        break
            while discord_text[m-1:m] != " " and len(discord_text) != m:
                if m != 0:
                    m -= 1
                else:
                    m = (x + 1) * 50
                    break
            final_text += discord_text[n:m] + "\n"
            n += 50
            m += 50
        def circlefy(image):
            size = (image.size[0] * 6, image.size[1] * 6)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + size, fill=255)
            mask = mask.resize(image.size)
            image.putalpha(mask)
            return image
        avatar = getImage(user.avatar_url).resize((100, 100))
        background = Image.new("RGBA", (1000, 115 + height), (54, 57, 63) if not white else (255, 255, 255))
        draw = ImageDraw.Draw(background)
        name = ImageFont.truetype("whitney/Whitney-Medium.ttf", 40)
        time = ImageFont.truetype("whitney/WhitneyLight.ttf", 24)
        background.paste(circlefy(avatar), (20, 10), circlefy(avatar))
        namesize = name.getsize(user.display_name)
        if user.bot:
            background.paste(bot, (160 + namesize[0] + 10, 2), bot)
        draw.text((160, 6), user.display_name, (user.colour.r, user.colour.g, user.colour.b), font=name)
        draw.text((170 + namesize[0] + length, (namesize[1]/2) - 2), "Today at " + datetime.datetime.utcnow().strftime("%H:%M"), (122, 125, 130), font=time)
        draw.text((160, namesize[1] + 20), final_text, (116, 127, 141) if white else (255, 255, 255), font=text)
        await send_file(ctx, background)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def flag(self, ctx, flag_initial: str, *, user: discord.Member=None):
        if not user:
            user = ctx.author
        try:
            flag = getImage("http://www.geonames.org/flags/x/{}.gif".format(flag_initial))
        except:
            return await ctx.send("Invalid flag initial :no_entry:")
        avatar = getImage(user.avatar_url)
        avatar = avatar.resize((200, 200))
        flag = flag.resize((200, 200))
        flag.putalpha(100)
        avatar.paste(flag, (0, 0), flag)
        await send_file(ctx, avatar)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def christmas(self, ctx, user_or_image: str=None, enhance: int=None):
        """Turn an image into a christmas themed one"""
        if not user_or_image:
            if ctx.message.attachments:
                try:
                    r = requests.get(ctx.message.attachments[0].url, stream=True)
                    url = ctx.message.attachments[0].url
                    if ".gif" in url:
                        gif = True 
                    else:
                        gif = False
                except:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("Invalid user/image :no_entry:")
            else:
                user = ctx.author
                r = requests.get(user.avatar_url, stream=True)
                url = user.avatar_url
                if ".gif" in user.avatar_url:
                    gif = True 
                else:
                    gif = False
        else:
            user = await arg.get_member(ctx, user_or_image)
            if not user:
                try: 
                    r = requests.get(user_or_image, stream=True)
                    url = user_or_image
                    if ".gif" in user_or_image:
                        gif = True 
                    else:
                        gif = False
                except:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("Invalid user/image :no_entry:")
            else:
                r = requests.get(user.avatar_url, stream=True)
                url = user.avatar_url
                if ".gif" in user.avatar_url:
                    gif = True 
                else:
                    gif = False
        if not gif:
            img = Image.open(r.raw)
            if enhance:
                img = img.convert(mode='L')
                img = ImageEnhance.Contrast(img).enhance(enhance)
            img = img.convert("RGBA")
            basewidth = 400
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            white = Image.new("RGBA", (basewidth, hsize), (255, 255, 255))
            img = img.resize((basewidth, hsize))

            pixels = img.load()

            for y in range(img.height):
                for x in range(img.width):
                    r, g, b, a = img.getpixel((x, y))
                    o = math.sqrt(0.299*r**2 + 0.587*g**2 + 0.114*b**2)
                    o *= ((o - 102) / 128)
                    o = 255 - o
                    pixels[x, y] = (255, 0, 0, int(o))
            white.paste(img, (0, 0), img)
            await send_file(ctx, white)
        else:
            with open("avatar.gif", "wb") as f:
                f.write(requests.get(url).content)
            img = Image.open("avatar.gif")
            basewidth = 128
            new = []
            frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
            try:
                for frame in frames:
                    if enhance:
                        frame = frame.convert(mode='L')
                        frame = ImageEnhance.Contrast(frame).enhance(enhance)
                    wpercent = (basewidth/float(img.size[0]))
                    hsize = int((float(img.size[1])*float(wpercent)))
                    white = Image.new("RGBA", (basewidth, hsize), (255, 255, 255))
                    frame = frame.convert("RGBA").resize((basewidth, hsize))
                    pixels = frame.load()
                    for y in range(frame.height):
                        for x in range(frame.width):
                            r, g, b, a = pixels[x, y]
                            o = math.sqrt(0.299*r**2 + 0.587*g**2 + 0.114*b**2)
                            o *= ((o - 102) / 128)
                            o = 255 - o
                            pixels[x, y] = (255, 0, 0, int(o))
                    white.paste(frame, (0, 0), frame)
                    new.append(white)
            except EOFError:
                pass
            await ctx.send(file=get_file_gif(new[0], new[1:]))
            try:
                os.remove("avatar.gif")
            except:
                pass

    @commands.command(hidden=True)
    @checks.is_owner()
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def halloween(self, ctx, user_or_image: str=None, enhance: int=None):
        """Turn an image into a halloween themed one"""
        if not user_or_image:
            if ctx.message.attachments:
                try:
                    r = requests.get(ctx.message.attachments[0].url, stream=True)
                    url = ctx.message.attachments[0].url
                    if ".gif" in url:
                        gif = True 
                    else:
                        gif = False
                except:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("Invalid user/image :no_entry:")
            else:
                user = ctx.author
                r = requests.get(user.avatar_url, stream=True)
                url = user.avatar_url
                if ".gif" in user.avatar_url:
                    gif = True 
                else:
                    gif = False
        else:
            user = await arg.get_member(ctx, user_or_image)
            if not user:
                try: 
                    r = requests.get(user_or_image, stream=True)
                    url = user_or_image
                    if ".gif" in user_or_image:
                        gif = True 
                    else:
                        gif = False
                except:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("Invalid user/image :no_entry:")
            else:
                r = requests.get(user.avatar_url, stream=True)
                url = user.avatar_url
                if ".gif" in user.avatar_url:
                    gif = True 
                else:
                    gif = False
        if not gif:
            img = Image.open(r.raw)
            if enhance:
                img = img.convert(mode='L')
                img = ImageEnhance.Contrast(img).enhance(enhance)
            img = img.convert("RGBA")
            basewidth = 400
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize))

            pixels = img.load()

            for y in range(img.height):
                for x in range(img.width):
                    r, g, b, a = img.getpixel((x, y))
                    o = math.sqrt(0.299*r**2 + 0.587*g**2 + 0.114*b**2)
                    o *= ((o - 102) / 128)
                    pixels[x, y] = (int(o), int((o - 10) / 2), 0, a)
            await send_file(ctx, img)
        else:
            with open("avatar.gif", "wb") as f:
                f.write(requests.get(url).content)
            img = Image.open("avatar.gif")
            new = []
            frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
            try:
                for frame in frames:
                    if enhance:
                        frame = frame.convert(mode='L')
                        frame = ImageEnhance.Contrast(frame).enhance(enhance)
                    basewidth = 128
                    wpercent = (basewidth/float(img.size[0]))
                    hsize = int((float(img.size[1])*float(wpercent)))
                    frame = frame.convert("RGBA").resize((basewidth, hsize))
                    pixels = frame.load()
                    for y in range(frame.height):
                        for x in range(frame.width):
                            r, g, b, a = pixels[x, y]
                            o = math.sqrt(0.299*r**2 + 0.587*g**2 + 0.114*b**2)
                            o *= ((o - 102) / 128)
                            pixels[x, y] = (int(o), int((o - 10) / 2), 0, a)
                    new.append(frame)
            except EOFError:
                pass
            await ctx.send(file=get_file_gif(new[0], new[1:]))
            try:
                os.remove("avatar.gif")
            except:
                pass
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
            img2 = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img = Image.open("trash-meme.jpg")
            img2 = img2.resize((385, 384))
            img2 = img2.filter(ImageFilter.GaussianBlur(radius=7.0))
            img.paste(img2, (384, 0))
            await send_file(ctx, img)
        except:
            await ctx.send("Not a valid user or image url :no_entry:")

    @commands.command(aliases=["www"]) 
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def whowouldwin(self, ctx, user_or_imagelink: str, user_or_imagelink2: str=None):
        """Who would win out of 2 images"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            url1 = ctx.message.author.avatar_url
        elif "<" in user_or_imagelink and "@" in user_or_imagelink:
            userid = user_or_imagelink.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            try:
                user = discord.utils.get(ctx.message.guild.members, id=int(userid))
                if not user:
                    return await ctx.send("Invalid user :no_entry:")
            except:
                await ctx.send("Invalid user :no_entry:")
                return
            url1 = user.avatar_url
        else:
            try:
                user = ctx.message.guild.get_member_named(user_or_imagelink)
                if not user:
                    return await ctx.send("Invalid user :no_entry:")
                url1 = user.avatar_url
            except:
                try:
                    user = discord.utils.get(ctx.message.guild.members, id=int(user_or_imagelink))
                    if not user:
                        return await ctx.send("Invalid user :no_entry:")
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
            img2 = getImage(url1.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img3 = getImage(url2.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img = Image.open("whowouldwin.png").convert("RGBA")
            img2 = img2.resize((400, 400))
            img3 = img3.resize((400, 400))
            img.paste(img2, (30, 180), img2)
            img.paste(img3, (510, 180), img3)
            await send_file(ctx, img)
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command() 
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
            img = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img2 = Image.open("fear-meme.png")
            img = img.resize((251, 251))
            img2.paste(img, (260, 517))
            img2.save("result.png")
            await send_file(ctx, img2)
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
        
    @commands.command() 
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
            im = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            image = im.filter(ImageFilter.EMBOSS) 
            image = ImageEnhance.Contrast(image).enhance(4.0)
            image = image.filter(ImageFilter.SMOOTH)
            await send_file(ctx, image)
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def ship(self, ctx, user1: str, *, user2: str=None):
        """Ship 2 users"""
        if not user2:
            user2 = arg.get_server_member(ctx, user1)
            user1 = ctx.message.author
        else:
            user1 = arg.get_server_member(ctx, user1)
            user2 = arg.get_server_member(ctx, user2)
        if not user1 or not user2:
            return await ctx.send("Invalid user :no_entry:")
        shipname = str(user1.name[:math.ceil(len(user1.name)/2)]) + str(user2.name[math.ceil(len(user2.name)/2):])
        state = random.getstate()
        random.seed(user2.id + user1.id)
        number = randint(0, 100)
        random.setstate(state)
        u1avatar = user1.avatar_url
        u2avatar = user2.avatar_url
        user1 = getImage(u1avatar.replace("gif", "png").replace("webp", "png"))
        user2 = getImage(u2avatar.replace("gif", "png").replace("webp", "png"))
        user1 = user1.resize((280, 280))
        user2 = user2.resize((280, 280))
        heart = Image.open("heart.png")
        image = Image.new('RGBA', (880, 280), (255, 255, 255, 0))
        image.paste(user1, (0, 0))
        image.paste(heart, (280, 0))
        image.paste(user2, (600, 0))
        temp = BytesIO()
        image.save(temp, "png")
        temp.seek(0)
        await ctx.send(content="Ship Name: **{}**\nLove Percentage: **{}%**".format(shipname, number), file=discord.File(temp, "result.png"))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
            img2 = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img = Image.open("vr.png").convert("RGBA")
            img = img.resize((493, 511))
            image = Image.new('RGBA', (493, 511), (255, 255, 255, 0))
            img2 = img2.resize((225, 150))
            img2.convert('RGBA')
            image.paste(img2, (15, 310), img2)
            image.paste(img, (0, 0), img)
            await send_file(ctx, image)
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
					
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
            img2 = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img = Image.open("shit-meme.png").convert("RGBA")
            image = Image.new('RGBA', (763, 1080), (255, 255, 255, 0))
            img2 = img2.resize((185, 185))
            img2 = img2.rotate(50, expand=True)
            img2.convert('RGBA')
            image.paste(img2, (215, 675), img2)
            image.paste(img, (0, 0), img)
            await send_file(ctx, image)
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
            img2 = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
            img = Image.open("beautiful.png").convert("RGBA")
            img2 = img2.resize((90, 104))
            img2 = img2.rotate(1, expand=True)
            img2.convert('RGBA')
            img.paste(img2, (253, 25), img2)
            img.paste(img2, (256, 222), img2)
            await send_file(ctx, img)
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
        else:
            user = await arg.get_member(ctx, user_or_imagelink)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
            else:
                url = user.avatar_url
        try:
            img = getImage(url.replace("gif", "png").replace("webp", "png").replace("<", "").replace(">", ""))
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
            await send_file(ctx, img)
        except:
            await ctx.send("Not a valid user or image url :no_entry:")
            
    @commands.command(aliases=["tweet"])
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
        await send_file(ctx, img)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
        await send_file(ctx, img)
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
    @commands.cooldown(1, 5, commands.BucketType.guild)
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
        img2 = getImage(user.avatar_url.replace("gif", "png").replace("webp", "png"))
        img2 = img2.resize((23, 23))
        img.paste(img2, (270, 335))
        await send_file(ctx, img)

    @commands.command()
    async def commoncolour(self, ctx, user_or_imagelink: str=None):
        """Returns the most common colour from an image"""
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.author.avatar_url
        else:
            user = await arg.get_member(ctx, user_or_imagelink)
            if not user:
                url = user_or_imagelink
            else:
                url = user.avatar_url
        try:
            image = getImage(url).convert("RGB")
        except:
            return await ctx.send("Invalid Image/User :no_entry:")
        pixdata = image.load()
        entries = {}
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                if pixdata[x, y] not in entries:
                    entries[pixdata[x, y]] = 1
                else:
                    entries[pixdata[x, y]] += 1
        image = Image.new("RGBA", (300, 50), sorted(entries.items(), key=lambda x: x[1], reverse=True)[0][0])
        hex = '%02x%02x%02x' % sorted(entries.items(), key=lambda x: x[1], reverse=True)[0][0]
        await ctx.send(file=get_file(image), embed=discord.Embed(title="Most Common Colour: #{}".format(hex.upper()), description="RGB: {}".format(sorted(entries.items(), key=lambda x: x[1], reverse=True)[0][0]), colour=discord.Colour(int(hex, 16))).set_image(url="attachment://result.png").set_thumbnail(url=url))
        del entries


async def send_file(ctx, image):
    temp = BytesIO()
    image.save(temp, "png")
    temp.seek(0)
    await ctx.send(file=discord.File(temp, "result.png"))

def get_file(image):
    temp = BytesIO()
    image.save(temp, "png")
    temp.seek(0)
    return discord.File(temp, "result.png")

def get_file_gif(image, frames):
    temp = BytesIO()
    image.save(temp, "gif", save_all=True, append_images=frames)
    temp.seek(0)
    return discord.File(temp, "result.gif")

def getImage(url):
    r = requests.get(url, stream=True, timeout=3)
    img = Image.open(r.raw).convert('RGBA')
    return img
        
def setup(bot):
    bot.add_cog(image(bot))
