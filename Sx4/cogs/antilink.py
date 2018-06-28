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


class antilink:

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/antiad/antilink.json"
        self.settings = dataIO.load_json(self.file_path)
		
    @commands.group()
    async def antilink(self, ctx):
        """Block out those advertisers"""
        server = ctx.guild
        if str(server.id) not in self.settings:
            self.settings[str(server.id)] = {}
            dataIO.save_json(self.file_path, self.settings)
        if "toggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["toggle"] = False
            dataIO.save_json(self.file_path, self.settings)
        if "modtoggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["modtoggle"] = True
            dataIO.save_json(self.file_path, self.settings)
        if "admintoggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["admintoggle"] = False
            dataIO.save_json(self.file_path, self.settings)
        if "bottoggle" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["bottoggle"] = True
            dataIO.save_json(self.file_path, self.settings)
        if "channels" not in self.settings[str(server.id)]:
            self.settings[str(server.id)]["channels"] = {}
            dataIO.save_json(self.file_path, self.settings)
		
    @antilink.command()
    @checks.admin_or_permissions(manage_messages=True)
    async def toggle(self, ctx):
        """Toggle antilink on or off"""
        server = ctx.guild
        if self.settings[str(server.id)]["toggle"] == True:
            self.settings[str(server.id)]["toggle"] = False
            await ctx.send("Anti-link has been **Disabled**")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[str(server.id)]["toggle"] == False:
            self.settings[str(server.id)]["toggle"] = True
            await ctx.send("Anti-link has been **Enabled**")
            dataIO.save_json(self.file_path, self.settings)
            return
		
    @antilink.command() 
    @checks.admin_or_permissions(manage_guild=True)
    async def modtoggle(self, ctx):
        """Choose whether you want your mods to be able to send links or not (manage_message and above are classed as mods)"""
        server = ctx.guild
        if self.settings[str(server.id)]["modtoggle"] == True:
            self.settings[str(server.id)]["modtoggle"] = False
            await ctx.send("Mods will now not be affected by anti-link.")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[str(server.id)]["modtoggle"] == False:
            self.settings[str(server.id)]["modtoggle"] = True
            await ctx.send("Mods will now be affected by anti-link.")
            dataIO.save_json(self.file_path, self.settings)
            return
			
    @antilink.command() 
    @checks.admin_or_permissions(manage_guild=True)
    async def admintoggle(self, ctx):
        """Choose whether you want your admins to be able to send links or not (administrator perms are classed as admins)"""
        server = ctx.guild
        if self.settings[str(server.id)]["admintoggle"] == True:
            self.settings[str(server.id)]["admintoggle"] = False
            await ctx.send("Admins will now not be affected by anti-link.")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[str(server.id)]["admintoggle"] == False:
            self.settings[str(server.id)]["admintoggle"] = True
            await ctx.send("Admins will now be affected by anti-link.")
            dataIO.save_json(self.file_path, self.settings)
            return
			
    @antilink.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def togglebot(self, ctx):
        """Choose whether bots can send links or not"""
        server = ctx.guild
        if self.settings[str(server.id)]["bottoggle"] == True:
            self.settings[str(server.id)]["bottoggle"] = False
            await ctx.send("Bots will now not be affected by anti-link.")
            dataIO.save_json(self.file_path, self.settings)
            return
        if self.settings[str(server.id)]["bottoggle"] == False:
            self.settings[str(server.id)]["bottoggle"] = True
            await ctx.send("Bots will now be affected by anti-link.")
            dataIO.save_json(self.file_path, self.settings)
            return
			
    @antilink.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def togglechannel(self, ctx, channel: discord.TextChannel=None): 
        """Choose what channels you want to count towards antilink"""
        server = ctx.guild
        if not channel:
           channel = ctx.channel 
        if self.settings[str(server.id)]["channels"] == None:
            self.settings[str(server.id)]["channels"][str(channel.id)] = {}
            await ctx.send("Anti-link is now disabled in <#{}>".format(str(channel.id)))
            dataIO.save_json(self.file_path, self.settings)
            return
        elif str(channel.id) not in self.settings[str(server.id)]["channels"]:
            self.settings[str(server.id)]["channels"][str(channel.id)] = {}
            await ctx.send("Anti-link is now disabled in <#{}>".format(str(channel.id)))
            dataIO.save_json(self.file_path, self.settings)
            return
        else: 
            del self.settings[str(server.id)]["channels"][str(channel.id)]
            await ctx.send("Anti-link is now enabled in <#{}>".format(str(channel.id)))
            dataIO.save_json(self.file_path, self.settings)
            return
		 
    @antilink.command()
    async def stats(self, ctx): 
        """View the settings of the antilink in your server"""
        serverid=ctx.guild.id
        server=ctx.guild
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Anti-link Settings", icon_url=self.bot.user.avatar_url)
        if self.settings[str(server.id)]["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        if self.settings[str(server.id)]["bottoggle"] == False:
            bottoggle = "Bots **Can** send links"
        else:
            bottoggle = "Bots **Can't** send links"
        if self.settings[str(serverid)]["modtoggle"] == False:
            mod = "Mods **Can** send links"
        else:
            mod = "Mods **Can't** send links"
        if self.settings[str(serverid)]["admintoggle"] == False:
            admin = "Admins **Can** send links"
        else:
            admin = "Admins **Can't** send links"
        s.add_field(name="Status", value=toggle)
        s.add_field(name="Mod Perms", value=mod)
        s.add_field(name="Admin Perms", value=admin)
        s.add_field(name="Bots", value=bottoggle)
        try:
            msg = ""
            for channelid in self.settings[str(server.id)]["channels"]:
                channel = discord.utils.get(server.channels, id=int(channelid))
                msg += channel.name + "\n"
            if msg == "":
                s.add_field(name="Disabled Channels", value="None")
                await ctx.send(embed=s)
                return
            else:
                s.add_field(name="Disabled Channels", value=msg)
        except:
            s.add_field(name="Disabled Channels", value="None")
        await ctx.send(embed=s)
		
	
    async def on_message(self, message): 
        serverid = message.guild.id
        author = message.author
        channel = message.channel
        if self.settings[str(serverid)]["modtoggle"] == False:
            if channel.permissions_for(author).manage_messages:
                return
        if self.settings[str(serverid)]["admintoggle"] == False:
            if channel.permissions_for(author).administrator:
                return
        if self.settings[str(serverid)]["bottoggle"] == False:
            if author.bot:
                return
        try:
            if str(channel.id) in self.settings[str(serverid)]["channels"]:
                return
        except:
            pass
        if self.settings[str(serverid)]["toggle"] == True:
            if ("http://" in message.content.lower()) or ("https://" in message.content.lower()):
                await message.delete()
                await channel.send("{}, You are not allowed to send links here :no_entry:".format(author.mention))
				
    async def on_message_edit(self, before, after): 
        serverid = before.guild.id
        author = before.author
        channel = before.channel
        if self.settings[str(serverid)]["modtoggle"] == False:
            if channel.permissions_for(author).manage_messages:
                return
        if self.settings[str(serverid)]["admintoggle"] == False:
            if channel.permissions_for(author).administrator:
                return
        if self.settings[str(serverid)]["bottoggle"] == False:
            if author.bot:
                return
        try:
            if str(channel.id) in self.settings[str(serverid)]["channels"]:
                return
        except:
            pass
        if self.settings[str(serverid)]["toggle"] == True:
            if ("http://" in after.content.lower()) or ("https://" in after.content.lower()):
                await after.delete()
                await channel.send("{}, You are not allowed to send links here :no_entry:".format(author.mention))

		
def check_folders():
    if not os.path.exists("data/antiad"):
        print("Creating data/antiad folder...")
        os.makedirs("data/antiad")


def check_files():
    s = "data/antiad/antilink.json"
    if not dataIO.is_valid_json(s):
        print("Creating empty antilink.json...")
        dataIO.save_json(s, {})

def setup(bot): 
    check_folders()
    check_files() 
    bot.add_cog(antilink(bot))