import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
from utils import arghelp
import math
import logging
import rethinkdb as r
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
import asyncio
import random
import time
from utils.dataIO import fileIO

class welcomer:
    """Shows when a user joins and leaves a server"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @checks.has_permissions("manage_messages")
    async def imgwelcomer(self, ctx):
        """Make the bot welcome people for you with an image"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("welcomer").insert({"id": str(ctx.guild.id), "toggle": False, "channel": None,
            "message": "{user.mention}, Welcome to **{server}**. Enjoy your time here! The server now has {server.members} members.",
            "message-leave": "**{user.name}** has just left **{server}**. Bye **{user.name}**!", "dm": False, "imgwelcomertog": False, 
            "banner": None, "leavetoggle": True}).run()

    @imgwelcomer.command(name="toggle")
    @checks.has_permissions("manage_messages")
    async def _toggle(self, ctx):
        "toggle image welcomer on or off"
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["imgwelcomertog"].run() == True:
            data.update({"imgwelcomertog": False}).run()
            await ctx.send("Image Welcomer has been **Disabled**")
            return
        if data["imgwelcomertog"].run() == False:
            data.update({"imgwelcomertog": True}).run()
            await ctx.send("Image Welcomer has been **Enabled**")
            return

    @imgwelcomer.command()
    @checks.has_permissions("manage_messages")
    async def banner(self, ctx, banner: str=None):
        """Adds a banner to the image welcomer, when added the image welcomer changes resolution to 2560 x 1440 so a banner that size would be ideal"""
        author = ctx.author
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if not banner:
            if ctx.message.attachments:
                try: 
                    banner = ctx.message.attachments[0].url.replace(".gif", ".png").replace(".webp", ".png")
                    data.update({"banner": banner}).run()
                    await ctx.send("Your banner for image welcomer has been set.")
                    return
                except:
                    pass
            data.update({"banner": None}).run()
            await ctx.send("Your banner for image welcomer has been reset.")
            return
        banner = banner.replace(".gif", ".png").replace(".webp", ".png")
        if "https://" in banner or "http://" in banner:
            if ".png" in banner or ".jpg" in banner:
                if "cdn.discordapp.com" in banner or "i.imgur.com" in banner:
                    data.update({"banner": banner}).run()
                    await ctx.send("Your banner for image welcomer has been set.")
                else:
                    await ctx.send("Invalid image url, has to be an imgur or discord image :no_entry:")
            else:
                await ctx.send("Invalid image url, has to be a jpeg or png image :no_entry:")
        else:
            await ctx.send("Invalid image url, needs to be an actual link :no_entry:")

        
    @commands.group()
    async def welcomer(self, ctx):
        """Make the bot welcome people for you"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("welcomer").insert({"id": str(ctx.guild.id), "toggle": False, "channel": None,
            "message": "{user.mention}, Welcome to **{server}**. Enjoy your time here! The server now has {server.members} members.",
            "message-leave": "**{user.name}** has just left **{server}**. Bye **{user.name}**!", "dm": False, "imgwelcomertog": False, 
            "banner": None, "leavetoggle": True}).run()
        
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def toggle(self, ctx): 
        """Toggle welcomer on or off"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["toggle"].run() == True:
            data.update({"toggle": False}).run()
            await ctx.send("Welcomer has been **Disabled**")
            return
        if data["toggle"].run() == False:
            data.update({"toggle": True}).run()
            await ctx.send("Welcomer has been **Enabled**")
            return
            
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def dmtoggle(self, ctx): 
        """Toggle whether you want the bot to dm the user or not"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["dm"].run() == True:
            data.update({"dm": False}).run()
            await ctx.send("Welcome messages will now be sent in the welcomer channel.")
            return
        if data["dm"].run() == False:
            data.update({"dm": True}).run()
            await ctx.send("Welcome messages will now be sent in dms.")
            return

    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def leavetoggle(self, ctx):
        """Toggle if you want the leave message or not"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if data["leavetoggle"].run() == True:
            data.update({"leavetoggle": False}).run()
            await ctx.send("Leave messages are now disabled.")
            return
        if data["leavetoggle"].run() == False:
            data.update({"leavetoggle": True}).run()
            await ctx.send("Leave messages are now enabled.")
            return
    
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def joinmessage(self, ctx, *, message: str=None):
        """Set the joining message"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if not message:
            desc = """{server} = Your server name
{user.mention} = Mentions the user who joins
{user.name} = The username of the person who joined
{user} = The username + discriminator
{server.members} = The amount of members in your server
{server.members.prefix} = The amount of members plus a prefix ex 232nd
**Make sure you keep the {} brackets in the message**

Example: `s?welcomer joinmessage {user.mention}, Welcome to **{server}**. We now have **{server.members}** members :tada:`"""
            s=discord.Embed(description=desc, colour=ctx.message.author.colour)
            s.set_author(name="Examples on setting your message", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=s)
            return
        data.update({"message": message}).run()
        await ctx.send("Your message has been set <:done:403285928233402378>")
        
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def leavemessage(self, ctx, *, message: str=None):
        """Set the leaving message"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        if not message:
            desc = """{server} = Your server name
{user.mention} = Mentions the user who joins
{user.name} = The username of the person who joined
{user} = The username + discriminator
{server.members} = The amount of members in your server
{server.members.prefix} = The amount of members plus a prefix ex 232nd
**Make sure you keep the {} brackets in the message**

Example: `s?welcomer leavemessage {user.mention}, Goodbye!`"""
            s=discord.Embed(description=desc, colour=ctx.message.author.colour)
            s.set_author(name="Examples on setting your message", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=s)
            return
        data.update({"message-leave": message}).run()
        await ctx.send("Your message has been set <:done:403285928233402378>")
        
    @welcomer.command()
    async def preview(self, ctx):
        """Look at the preview of your welcomer"""
        server = ctx.guild
        author = ctx.author
        data = r.table("welcomer").get(str(server.id)).run()
        message = data["message"]
        message = message.replace("{server}", server.name)
        message = message.replace("{user.mention}", author.mention)
        message = message.replace("{user.name}", author.name)
        message = message.replace("{user}", str(author))
        message = message.replace("{server.members}", str(len(server.members)))  
        message = message.replace("{server.members.prefix}", await self.prefixfy(server)) 
        message2 = data["message-leave"]
        message2 = message2.replace("{server}", server.name)
        message2 = message2.replace("{user.mention}", author.mention)
        message2 = message2.replace("{user.name}", author.name)
        message2 = message2.replace("{user}", str(author))
        message2 = message2.replace("{server.members}", str(len(server.members))) 
        message = message.replace("{server.members.prefix}", await self.prefixfy(server)) 
        if data["imgwelcomertog"]:
            await ctx.send(content=message, file=await self.image_welcomer(author, server))
        else:
            await ctx.send(message)
        await ctx.send(message2)
            
    @welcomer.command()
    @checks.has_permissions("manage_messages")
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel of where you want the bot to welcome people"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id))
        data.update({"channel": str(channel.id)}).run()       
        await ctx.send("<#{}> has been set as the join-leave channel".format(channel.id))
        
    @welcomer.command()
    async def stats(self, ctx): 
        """Look at the settings of your welcomer"""
        server = ctx.guild
        data = r.table("welcomer").get(str(server.id)).run()
        message = "`" + data["message"] + "`"
        message2 = "`" + data["message-leave"] + "`"  
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Welcomer Settings", icon_url=self.bot.user.avatar_url)
        if data["toggle"] == True:
            msg = "Enabled"
        if data["toggle"] == False:
            msg = "Disabled"
        if data["dm"] == True:
            msg2 = "Enabled"
        if data["dm"] == False:
            msg2 = "Disabled"
        if data["imgwelcomertog"] == True:
            img = "Enabled"
        else:
            img = "Disabled"
        if data["leavetoggle"] == False:
            message2 = "Disabled"
        s.add_field(name="Welcomer status", value=msg)
        if not data["channel"]:
            channel = "Not set"
        else:
            channel = "<#{}>".format(data["channel"])
        s.add_field(name="Welcomer channel", value=channel)
        s.add_field(name="DM Welcomer", value=msg2)
        s.add_field(name="Image Welcomer", value=img)
        s.add_field(name="Join message", value=message, inline=False)
        s.add_field(name="Leave message", value=message2, inline=False)
        await ctx.send(embed=s)
        
    async def prefixfy(self, server):
        number = str(len(server.members))
        num = len(number) - 2
        num2 = len(number) - 1
        if int(number[num:]) < 11 or int(number[num:]) > 13:
            if int(number[num2:]) == 1:
                prefix = "st"
            elif int(number[num2:]) == 2:
                prefix = "nd"
            elif int(number[num2:]) == 3:
                prefix = "rd"
            else:
                prefix = "th"
        else:
            prefix = "th"
        return number + prefix
        
        
    async def on_member_join(self, member): 
        server = member.guild
        author = member
        data = r.table("welcomer").get(str(server.id)).run()
        message = data["message"]
        channel = data["channel"]
        message = message.replace("{server}", server.name)
        message = message.replace("{user.mention}", member.mention)
        message = message.replace("{user.name}", member.name)
        message = message.replace("{user}", str(member))
        message = message.replace("{server.members}", str(len(server.members))) 
        message = message.replace("{server.members.prefix}", await self.prefixfy(server)) 
        if data["toggle"] == True:
            if data["dm"] == True and data["imgwelcomertog"] == True:
                await member.send(content=message, file=await self.image_welcomer(author, server))
            elif data["dm"] == True and data["imgwelcomertog"] == False:
                await member.send(content=message)
            elif data["imgwelcomertog"] == True and data["dm"] == False:
                await server.get_channel(int(channel)).send(content=message, file=await self.image_welcomer(author, server))
            else:
                await server.get_channel(int(channel)).send(message)
        else:
            pass
            
    async def on_member_remove(self, member):
        server = member.guild
        data = r.table("welcomer").get(str(server.id)).run()
        if data["dm"] == True:
            return
        if data["leavetoggle"] == False:
            return
        channel = data["channel"]
        message = data["message-leave"]
        if data["toggle"] == True:
            message = message.replace("{server}", server.name)
            message = message.replace("{user.mention}", member.mention)
            message = message.replace("{user.name}", member.name)
            message = message.replace("{user}", str(member))
            message = message.replace("{server.members}", str(len(server.members))) 
            message = message.replace("{server.members.prefix}", await self.prefixfy(server)) 
            await server.get_channel(int(channel)).send(message)
        else:
            pass

    async def image_welcomer(self, author, server):
        data = r.table("welcomer").get(str(server.id)).run()
        left = 654
        down = 600
        fontsize = 170
        i = 0
        for x in range(len(str(author.name))):
            i += 1
            if i >= 20:
                fontsize -= 2
            else:
                fontsize -= 3
            left -= 4
            down += 1
        with open("image.png", "wb") as f:
            f.write(requests.get(author.avatar_url).content)
        im = Image.open('image.png')
        im = im.resize((500, 500))
        size = (im.size[0] * 6, im.size[1] * 6)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + size, fill=255)
        mask = mask.resize(im.size)
        im.putalpha(mask)
        output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        x = 50
        if data["banner"]:
            with open("backgroundwelcomer.png", "wb") as f:
                f.write(requests.get(data["banner"]).content)
            try:
                image = Image.open("backgroundwelcomer.png")
                image = image.resize((2560, 1440))
                background = Image.new('RGBA', (2560, 600), (0, 0, 0, 200))
                image.paste(background, (0, 425), background)
                x += 425
            except:
                image = Image.new('RGBA', (2560, 600), (0, 0, 0, 100))
                down -= 425
        else:
            image = Image.new('RGBA', (2560, 600), (0, 0, 0, 100))
            down -= 425
        image.paste(output, (25, x), output)
        draw2 = ImageDraw.Draw(image)
        font = ImageFont.truetype("exo.regular.otf", fontsize)
        draw2.text((left, down), "Welcome {}".format(author), (255, 255, 255), font=font)
        image.save("output.png")
        try:
            os.remove("image.png")
            os.remove("backgroundwelcomer.png")
        except:
            pass
        file = discord.File("output.png", "output.png")
        return file

def setup(bot): 
    bot.add_cog(welcomer(bot))
