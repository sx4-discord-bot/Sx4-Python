import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
import math
import logging
import asyncio
import random
import time
from utils.dataIO import fileIO


settings = {"toggle": False, "channel": None, "message": "{user.mention}, Welcome to **{server}**. Enjoy your time here! The server now has {server.members} members.", "message-leave": "**{user.name}** has just left **{server}**. Bye **{user.name}**!", "dm": False}

class welcomer:
    """Shows when a user joins and leaves a server"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/welcomer/settings.json"
        self.settings = dataIO.load_json(self.file_path)
        self.settings = defaultdict(lambda: settings, self.settings)
		
    @commands.group(pass_context=True)
    async def welcomer(self, ctx):
        """Make the bot welcome people for you"""
        pass
		
    @welcomer.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def toggle(self, ctx): 
        """Toggle welcomer on or off"""
        server = ctx.message.server
        if self.settings[server.id]["toggle"] == True:
            self.settings[server.id]["toggle"] = False
            await self.bot.say("Welcomer has been **Disabled**")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[server.id]["toggle"] == False:
            self.settings[server.id]["toggle"] = True
            await self.bot.say("Welcomer has been **Enabled**")
            dataIO.save_json(self.file_path, self.settings)
            return
			
    @welcomer.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def dmtoggle(self, ctx): 
        """Toggle whether you want the bot to dm the user or not"""
        server = ctx.message.server
        if self.settings[server.id]["dm"] == True:
            self.settings[server.id]["dm"] = False
            await self.bot.say("Welcome messages will now be sent in the welcomer channel.")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[server.id]["dm"] == False:
            self.settings[server.id]["dm"] = True
            await self.bot.say("Welcome messages will now be sent in dms.")
            dataIO.save_json(self.file_path, self.settings)
            return
	
    @welcomer.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def joinmessage(self, ctx, *, message: str=None):
        """Set the joining message"""
        if not message:
            desc = """{server} = Your server name
{user.mention} = Mentions the user who joins
{user.name} = The username of the person who joined
{user} = The username + discriminator
{server.members} = The amount of members in your server
**Make sure you keep the {} brackets in the message**

Example: `s?welcomer message {user.mention}, Welcome to **{server}**. We now have **{server.members}** members :tada:`"""
            s=discord.Embed(description=desc, colour=ctx.message.author.colour)
            s.set_author(name="Examples on setting your message", icon_url=self.bot.user.avatar_url)
            await self.bot.say(embed=s)
            return
        self.settings[ctx.message.server.id]["message"] = message
        dataIO.save_json(self.file_path, self.settings)
        await self.bot.say("Your message has been set <:done:403285928233402378>")
		
    @welcomer.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def leavemessage(self, ctx, *, message: str=None):
        """Set the leaving message"""
        if not message:
            desc = """{server} = Your server name
{user.mention} = Mentions the user who joins
{user.name} = The username of the person who joined
{user} = The username + discriminator
{server.members} = The amount of members in your server
**Make sure you keep the {} brackets in the message**

Example: `s?welcomer leavemessage {user.mention}, Goodbye!`"""
            s=discord.Embed(description=desc, colour=ctx.message.author.colour)
            s.set_author(name="Examples on setting your message", icon_url=self.bot.user.avatar_url)
            await self.bot.say(embed=s)
            return
        self.settings[ctx.message.server.id]["message-leave"] = message
        dataIO.save_json(self.file_path, self.settings)
        await self.bot.say("Your message has been set <:done:403285928233402378>")
		
    @welcomer.command(pass_context=True)
    async def preview(self, ctx):
        """Look at the preview of your welcomer"""
        message = self.settings[ctx.message.server.id]["message"]
        await self.bot.say(message.format(ctx.message.server, ctx.message.author, len(ctx.message.server.members)))
        await self.bot.say("**{}** just left **{}**. Goodbye **{}**!".format(ctx.message.author.name, ctx.message.server, ctx.message.author.name))
			
    @welcomer.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def channel(self, ctx, channel: discord.Channel):
        """Set the channel of where you want the bot to welcome people"""
        server = ctx.message.server
        self.settings[server.id]["channel"] = channel.id    
        dataIO.save_json(self.file_path, self.settings)		
        await self.bot.say("<#{}> has been set as the join-leave channel".format(channel.id))
		
    @welcomer.command(pass_context=True)
    async def stats(self, ctx): 
        """Look at the settings of your welcomer"""
        server = ctx.message.server
        message = self.settings[server.id]["message"]
        message2 = self.settings[server.id]["message-leave"]
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Welcomer Settings", icon_url=self.bot.user.avatar_url)
        if self.settings[server.id]["toggle"] == True:
            msg = "Enabled"
        if self.settings[server.id]["toggle"] == False:
            msg = "Disabled"
        if self.settings[server.id]["dm"] == True:
            msg2 = "Enabled"
        if self.settings[server.id]["dm"] == False:
            msg2 = "Disabled"
        s.add_field(name="Welcomer status", value=msg)
        s.add_field(name="Welcomer channel", value="<#{}>".format(self.settings[server.id]["channel"]))
        s.add_field(name="DM Welcomer", value=msg2)
        s.add_field(name="Join message", value="`" + message + "`", inline=False)
        s.add_field(name="Leave message", value= "`" + message2 + "`", inline=False)
        await self.bot.say(embed=s)
        
		
    async def on_member_join(self, member): 
        server = member.server
        message = self.settings[server.id]["message"]
        channel = self.settings[server.id]["channel"]
        message = message.replace("{server}", server.name)
        message = message.replace("{user.mention}", member.mention)
        message = message.replace("{user.name}", member.name)
        message = message.replace("{user}", str(member))
        message = message.replace("{server.members}", str(len(server.members))) 
        if self.settings[server.id]["toggle"] == True:
            if self.settings[server.id]["dm"] == True:
                await self.bot.send_message(member, message)
            else:
                await self.bot.send_message(server.get_channel(channel), message)
        else:
            pass
			
    async def on_member_remove(self, member):
        server = member.server
        if self.settings[server.id]["dm"] == True:
            return
        channel = self.settings[server.id]["channel"]
        message = self.settings[server.id]["message-leave"]
        if self.settings[server.id]["toggle"] == True:
            message = message.replace("{server}", server.name)
            message = message.replace("{user.mention}", member.mention)
            message = message.replace("{user.name}", member.name)
            message = message.replace("{user}", str(member))
            message = message.replace("{server.members}", str(len(server.members))) 
            await self.bot.send_message(server.get_channel(channel), message)
        else:
            pass

def check_folders():
    if not os.path.exists("data/welcomer"):
        print("Creating data/welcomer folder...")
        os.makedirs("data/welcomer")


def check_files():
    s = "data/welcomer/settings.json"
    if not dataIO.is_valid_json(s):
        print("Creating empty settings.json...")
        dataIO.save_json(s, {})

def setup(bot): 
    check_folders()
    check_files() 
    bot.add_cog(welcomer(bot))