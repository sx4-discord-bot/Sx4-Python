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
import aiohttp
import urllib.request
from utils import data
import requests
import random
from random import choice
import asyncio
from difflib import get_close_matches

colours = data.read_json("data/colours/colournames.json")

class image:
    """Fun image commands"""
      
    def __init__(self, bot, connection):  
        self.bot = bot
        self.db = connection

    @commands.command(aliases=["htg"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def howtogoogle(self, ctx, *, text):
        """Shows someone how to use google"""
        if len(text) > 50:
            return await ctx.send("You can only use **50** characters :no_entry:")
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8443/api/google?{}".format(urllib.parse.urlencode({"q": text}))) as f:
                    if f.status == 200:
                        await ctx.send(file=discord.File(f.content, "google.{}".format(f.headers["Content-Type"].split("/")[1])))
                    elif f.status == 400:
                        await ctx.send(await f.text())
                    else:
                        await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hot(self, ctx, user_or_image: str=None):
        """The specified user/image will be called hot by will smith"""
        if ctx.message.attachments and not user_or_image:
            url = ctx.message.attachments[0].url
        elif not ctx.message.attachments and not user_or_image:
            url = get_avatar_url(ctx.author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/hot?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "hot.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(name="discord", usage="<user> <text>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _discord(self, ctx, user: str, *, discord_text: str):
        """Recreate a message from discord using this command"""
        user = arg.get_server_member(ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        if discord_text.lower().endswith(" --white"):
            white = True
            discord_text = discord_text[:-8]
        else: 
            white = False
        url = "http://localhost:8443/api/discord?image={}&theme={}&{}&colour={}&{}&bot={}".format(get_avatar_url(user), "dark" if not white else "white", urllib.parse.urlencode({"text": discord_text}),
        str(user.colour)[1:], urllib.parse.urlencode({"name": user.display_name}), user.bot)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "discord.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def flag(self, ctx, flag_initial: str, *, user: discord.Member=None):
        """Put a flag on top of your profile picture"""
        if not user:
            user = ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/flag?image={}&flag={}".format(get_avatar_url(user), flag_initial.lower())) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "flag.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def christmas(self, ctx, *, user_or_image: str=None):
        """Turn an image into a christmas themed one"""
        if not user_or_image:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(ctx.author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/christmas?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "christmas.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def halloween(self, ctx, *, user_or_image: str=None):
        """Turn an image into a halloween themed one"""
        if not user_or_image:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(ctx.author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/halloween?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "halloween.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
        
    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def trash(self, ctx, user_or_imagelink: str=None):
        """Make someone look like trash"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = ctx.author.avatar_url_as(format="png")
        else:
            user = arg.get_server_member(ctx, user_or_imagelink)
            if not user:
                url = user_or_imagelink
            else:
                url = user.avatar_url_as(format="png")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/trash?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "trash.png"))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(aliases=["www"], usage="[user | image] [user | image]") 
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whowouldwin(self, ctx, user_or_imagelink: str, user_or_imagelink2: str=None):
        """Who would win out of 2 images"""
        channel = ctx.channel
        author = ctx.author
        user = arg.get_server_member(ctx, user_or_imagelink)
        if not user:
            url1 = user_or_imagelink
        else:
            url1 = user.avatar_url_as(format="png")
        if not user_or_imagelink2:
            url2 = author.avatar_url_as(format="png")
        else: 
            user = arg.get_server_member(ctx, user_or_imagelink2)
            if not user:
                url2 = user_or_imagelink2
            else:
                url2 = user.avatar_url_as(format="png")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/www?firstImage={}&secondImage={}".format(url1, url2)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "www.png"))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
            
    @commands.command(usage="[user | image]") 
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def fear(self, ctx, user_or_imagelink: str=None):
        """Make someone look feared of"""
        channel = ctx.channel
        author = ctx.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(author)
        else:
            user = arg.get_server_member(ctx, user_or_imagelink)
            if not user:
                url = user_or_imagelink
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/fear?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "fear.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
        
    @commands.command(usage="[user | image]") 
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def emboss(self, ctx, user_or_image: str=None):
        """Make a profile picture emboss"""
        channel = ctx.channel
        author = ctx.author
        if not user_or_image:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/emboss?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "emboss.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    await ctx.send(await f.text())
                else:
                    await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
            
    @commands.command(usage="<user> [user]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ship(self, ctx, user1: str, *, user2: str=None):
        """Ship 2 users"""
        if not user2:
            user2 = arg.get_server_member(ctx, user1)
            user1 = ctx.author
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
        u1avatar = user1.avatar_url_as(format="png")
        u2avatar = user2.avatar_url_as(format="png")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/ship?firstImage={}&secondImage={}".format(u1avatar, u2avatar)) as f:
                if f.status == 200:
                    await ctx.send(content="Ship Name: **{}**\nLove Percentage: **{}%**".format(shipname, number), file=discord.File(f.content, "ship.png"))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vr(self, ctx, user_or_image: str=None):
        """Make someone feel emotional in vr"""	
        channel = ctx.channel
        author = ctx.author
        if not user_or_image:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/vr?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "vr.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
					
            
    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shit(self, ctx, user_or_image: str=None):
        """Choose who you want to be shit"""
        channel = ctx.channel
        author = ctx.author
        if not user_or_image:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/shit?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "shit.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command(usage="[user | image]")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def beautiful(self, ctx, user_or_image: str=None):
        """Turn something to a masterpiece"""
        channel = ctx.channel
        author = ctx.author
        if not user_or_image:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(author)
        else:
            user = arg.get_server_member(ctx, user_or_image)
            if not user:
                url = user_or_image
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/beautiful?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "beautiful.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
            
    @commands.command(usage="[user | image]")
    async def gay(self, ctx, user_or_imagelink: str=None):
        """Turn someone or yourself gay"""
        channel = ctx.message.channel
        author = ctx.message.author
        if not user_or_imagelink:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                url = get_avatar_url(author)
        else:
            user = arg.get_server_member(ctx, user_or_imagelink)
            if not user:
                url = user_or_imagelink
            else:
                url = get_avatar_url(user)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/gay?image={}".format(url)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "gay.{}".format(f.headers["Content-Type"].split("/")[1])))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def trumptweet(self, ctx, *, text: str):
        """Make trump say something on twitter"""
        channel = ctx.channel
        author = ctx.author
        if len(text) > 250:
            await ctx.send("No more than 250 characters :no_entry:")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8443/api/trump?text={}".format(text)) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "trump.png"))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tweet(self, ctx, user: str, *, text: commands.clean_content(fix_channel_mentions=True)):
        """Tweet from your or another users account"""
        await ctx.channel.trigger_typing()
        user = arg.get_server_member(ctx, user)
        if not user:
            return await ctx.send("I could not find that user :no_entry:")
        if len(text) > 250:
            await ctx.send("No more than 250 characters :no_entry:")
            return
        retweets = randint(1, ctx.guild.member_count)
        likes = randint(1, ctx.guild.member_count)
        urls = list(map(lambda x: x.avatar_url_as(format="png", size=64), random.sample(ctx.guild.members, min(ctx.guild.member_count, 10, likes))))
        data = {"displayName": user.display_name, "name": user.name, "avatarUrl": user.avatar_url_as(format="png", size=128), "urls": urls, "likes": likes, "retweets": retweets, "text": text}
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8443/api/tweet", json=data, headers={"Content-Type": "application/json"}) as f:
                if f.status == 200:
                    await ctx.send(file=discord.File(f.content, "tweet.png"))
                elif f.status == 400:
                    return await ctx.send(await f.text())
                else:
                    return await ctx.send("Oops something went wrong! Status code: {}".format(f.status))

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
        times = 0 
        size = 20
        description = ""
        if (math.ceil(len(str(text))/char)+1) >=6:
            for x in range((math.ceil(len(str(text))/char)+1) - 6):
                size -= 3
                char += 1
        for x in range(math.ceil(len(str(text))/char)+1):
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
            
    @commands.command(aliases=["color", "hex"])
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
        img2 = getImage(user.avatar_url.replace("gif", "png").replace("webp", "png"))
        img2 = img2.resize((23, 23))
        img.paste(img2, (270, 335))
        await send_file(ctx, img)

    @commands.command(usage="[user | image]")
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

    
def get_avatar_url(user):
    if ".gif" in user.avatar_url:
        return user.avatar_url
    else:
        return user.avatar_url_as(format="png")


async def send_file(ctx, img):
    temp = BytesIO()
    img.save(temp, "png")
    temp.seek(0)
    await ctx.send(file=discord.File(temp, "result.png"))

def get_file(img):
    temp = BytesIO()
    img.save(temp, "png")
    temp.seek(0)
    return discord.File(temp, "result.png")

def get_file_gif(img, frames):
    temp = BytesIO()
    img.save(temp, "gif", save_all=True, append_images=frames)
    temp.seek(0)
    return discord.File(temp, "result.gif")

def getImage(url):
    r = requests.get(url, stream=True, timeout=3)
    img = Image.open(r.raw).convert('RGBA')
    return img
        
def setup(bot, connection):
    bot.add_cog(image(bot, connection))
