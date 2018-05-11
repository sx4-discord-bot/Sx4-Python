import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
import logging
import asyncio
import random
import time


class antiad:

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/antiad/settings.json"
        self.settings = dataIO.load_json(self.file_path)
		
    @commands.group(pass_context=True)
    async def antiinvite(self, ctx):
        """Block out those discord invite advertisers"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {}
            dataIO.save_json(self.file_path, self.settings)
        if "toggle" not in self.settings[server.id]:
            self.settings[server.id]["toggle"] = False
            dataIO.save_json(self.file_path, self.settings)
        if "modtoggle" not in self.settings[server.id]:
            self.settings[server.id]["modtoggle"] = True
            dataIO.save_json(self.file_path, self.settings)
        if "admintoggle" not in self.settings[server.id]:
            self.settings[server.id]["admintoggle"] = False
            dataIO.save_json(self.file_path, self.settings)
        if "channels" not in self.settings[server.id]:
            self.settings[server.id]["channels"] = {}
            dataIO.save_json(self.file_path, self.settings)
		
    @antiinvite.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def toggle(self, ctx):
        """Toggle antiinvite on or off"""
        server = ctx.message.server
        if self.settings[server.id]["toggle"] == True:
            self.settings[server.id]["toggle"] = False
            await self.bot.say("Anti-invite has been **Disabled**")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[server.id]["toggle"] == False:
            self.settings[server.id]["toggle"] = True
            await self.bot.say("Anti-invite has been **Enabled**")
            dataIO.save_json(self.file_path, self.settings)
            return
		
    @antiinvite.command(pass_context=True) 
    @checks.admin_or_permissions(manage_server=True)
    async def modtoggle(self, ctx):
        """Choose whether you want your mods to be able to send invites or not (manage_message and above are classed as mods)"""
        server = ctx.message.server
        if self.settings[server.id]["modtoggle"] == True:
            self.settings[server.id]["modtoggle"] = False
            await self.bot.say("Mods will now not be affected by anti-invite.")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[server.id]["modtoggle"] == False:
            self.settings[server.id]["modtoggle"] = True
            await self.bot.say("Mods will now be affected by anti-invite.")
            dataIO.save_json(self.file_path, self.settings)
            return
			
    @antiinvite.command(pass_context=True) 
    @checks.admin_or_permissions(manage_server=True)
    async def admintoggle(self, ctx):
        """Choose whether you want your admins to be able to send invites or not (administrator perms are classed as admins)"""
        server = ctx.message.server
        if self.settings[server.id]["admintoggle"] == True:
            self.settings[server.id]["admintoggle"] = False
            await self.bot.say("Admins will now not be affected by anti-invite.")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[server.id]["admintoggle"] == False:
            self.settings[server.id]["admintoggle"] = True
            await self.bot.say("Admins will now be affected by anti-invite.")
            dataIO.save_json(self.file_path, self.settings)
            return
			
    @antiinvite.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def togglechannel(self, ctx, channel: discord.Channel=None):
        """Choose what channels you want to count towards antiinvite"""
        server = ctx.message.server
        if not channel:
           channel = ctx.message.channel 
        if self.settings[server.id]["channels"] == None:
            self.settings[server.id]["channels"][channel.id] = {}
            await self.bot.say("Anti-invite is now disabled in <#{}>".format(channel.id))
            dataIO.save_json(self.file_path, self.settings)
            return
        elif channel.id not in self.settings[server.id]["channels"]:
            self.settings[server.id]["channels"][channel.id] = {}
            await self.bot.say("Anti-invite is now disabled in <#{}>".format(channel.id))
            dataIO.save_json(self.file_path, self.settings)
            return
        else: 
            del self.settings[server.id]["channels"][channel.id]
            await self.bot.say("Anti-invite is now enabled in <#{}>".format(channel.id))
            dataIO.save_json(self.file_path, self.settings)
            return
		 
    @antiinvite.command(pass_context=True)
    async def stats(self, ctx):  
        """View the settings of the antiinvite in your server"""
        serverid=ctx.message.server.id
        server=ctx.message.server
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Anti-invite Settings", icon_url=self.bot.user.avatar_url)
        if self.settings[server.id]["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        if self.settings[serverid]["modtoggle"] == False:
            mod = "Mods **Can** send links"
        else:
            mod = "Mods **Can't** send links"
        if self.settings[serverid]["admintoggle"] == False:
            admin = "Admins **Can** send links"
        else:
            admin = "Admins **Can't** send links"
        s.add_field(name="Status", value=toggle)
        s.add_field(name="Mod Perms", value=mod)
        s.add_field(name="Admin Perms", value=admin)
        try:
            msg = ""
            for channelid in self.settings[server.id]["channels"]:
                channel = discord.utils.get(server.channels, id=channelid)
                msg += channel.name + "\n"
            if msg == "":
                s.add_field(name="Disabled Channels", value="None")
                await self.bot.say(embed=s)
                return
            s.add_field(name="Disabled Channels", value=msg)
        except:
            s.add_field(name="Disabled Channels", value="None")
        await self.bot.say(embed=s)
		
	
    async def on_message(self, message): 
        serverid = message.server.id
        author = message.author
        channel = message.channel
        if self.settings[serverid]["modtoggle"] == False:
            if channel.permissions_for(author).manage_messages:
                return
        if self.settings[serverid]["admintoggle"] == False:
            if channel.permissions_for(author).administrator:
                return
        try:
            if channel.id in self.settings[serverid]["channels"]:
                return
        except:
            pass
        if self.settings[serverid]["toggle"] == True:
            if ("discord.me/" in message.content.lower()) or ("discord.gg/" in message.content.lower()):
                await self.bot.delete_message(message)
                await self.bot.send_message(channel, "{}, You are not allowed to send invite links here :no_entry:".format(author.mention))
				
    async def on_message_edit(self, before, after): 
        serverid = before.server.id
        author = before.author
        channel = before.channel
        if self.settings[serverid]["modtoggle"] == False:
            if channel.permissions_for(author).manage_messages:
                return
        if self.settings[serverid]["admintoggle"] == False:
            if channel.permissions_for(author).administrator:
                return
        try:
            if channel.id in self.settings[serverid]["channels"]:
                return
        except:
            pass
        if self.settings[serverid]["toggle"] == True:
            if ("discord.me" in after.content.lower()) or ("discord.gg" in after.content.lower()):
                await self.bot.delete_message(after)
                await self.bot.send_message(channel, "{}, You are not allowed to send invite links here :no_entry:".format(author.mention))

		
def check_folders():
    if not os.path.exists("data/antiad"):
        print("Creating data/antiad folder...")
        os.makedirs("data/antiad")


def check_files():
    s = "data/antiad/settings.json"
    if not dataIO.is_valid_json(s):
        print("Creating empty settings.json...")
        dataIO.save_json(s, {})

def setup(bot): 
    check_folders()
    check_files() 
    bot.add_cog(antiad(bot))