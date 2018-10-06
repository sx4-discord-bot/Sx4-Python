import discord
from discord.ext import commands
import rethinkdb as r
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
import logging
import asyncio
import random
#from utils import arghelp
import time

reinvite = "(?:https://|http://|[\s \S]*|)discord.gg/(?:[\s \S]|[0-9]){1,7}"


class antiad:

    def __init__(self, bot):
        self.bot = bot
		
    @commands.group()
    async def antiinvite(self, ctx):
        """Block out those discord invite advertisers"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("antiad").insert({"id": str(server.id), "toggle": False, "modtoggle": True, "admintoggle": False, "bottoggle": True, "channels": []}).run()
		
    @antiinvite.command()
    @checks.has_permissions("manage_messages")
    async def toggle(self, ctx):
        """Toggle antiinvite on or off"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["toggle"].run() == True:
            data.update({"toggle": False}).run()
            await ctx.send("Anti-invite has been **Disabled**")
            return
        if data["toggle"].run() == False:
            data.update({"toggle": True}).run()
            await ctx.send("Anti-invite has been **Enabled**")
            return
		
    @antiinvite.command() 
    @checks.has_permissions("manage_guild")
    async def modtoggle(self, ctx):
        """Choose whether you want your mods to be able to send invites or not (manage_message and above are classed as mods)"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["modtoggle"].run() == True:
            data.update({"modtoggle": False}).run()
            await ctx.send("Mods will now not be affected by anti-invite.")
            return
        if data["modtoggle"].run() == False:
            data.update({"modtoggle": True}).run()
            await ctx.send("Mods will now be affected by anti-invite.")
            return
			
    @antiinvite.command() 
    @checks.has_permissions("manage_guild")
    async def admintoggle(self, ctx):
        """Choose whether you want your admins to be able to send invites or not (administrator perms are classed as admins)"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["admintoggle"].run() == True:
            data.update({"admintoggle": False}).run()
            await ctx.send("Admins will now not be affected by anti-invite.")
            return
        if data["admintoggle"].run() == False:
            data.update({"admintoggle": True}).run()
            await ctx.send("Admins will now be affected by anti-invite.")
            return
			
    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def togglebot(self, ctx):
        """Choose whether bots can send invites or not"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["bottoggle"].run() == True:
            data.update({"bottoggle": False}).run()
            await ctx.send("Bots will now not be affected by anti-invite.")
            return
        if data["bottoggle"].run() == False:
            data.update({"bottoggle": True}).run()
            await ctx.send("Bots will now be affected by anti-invite.")
            return
			
    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def togglechannel(self, ctx, channel: discord.TextChannel=None):
        """Choose what channels you want to count towards antiinvite"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if not channel:
           channel = ctx.channel 
        if str(channel.id) in data["channels"].run():
            data.update({"channels": r.row["channels"].difference([str(channel.id)])}).run()
            await ctx.send("Anti-invite is now enabled in <#{}>".format(str(channel.id)))
        else: 
            data.update({"channels": r.row["channels"].append(str(channel.id))}).run()
            await ctx.send("Anti-invite is now disabled in <#{}>".format(str(channel.id)))
		 
    @antiinvite.command()
    async def stats(self, ctx):  
        """View the settings of the antiinvite in your server"""
        serverid=ctx.guild.id
        server=ctx.guild
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Anti-invite Settings", icon_url=self.bot.user.avatar_url)
        data = r.table("antiad").get(str(server.id))
        msg = ""
        if data["toggle"].run() == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        if data["modtoggle"].run() == False:
            mod = "Mods **Can** send links"
        else:
            mod = "Mods **Can't** send links"
        if data["bottoggle"].run() == False:
            bottoggle = "Bots **Can** send links"
        else:
            bottoggle = "Bots **Can't** send links"
        if data["admintoggle"].run() == False:
            admin = "Admins **Can** send links"
        else:
            admin = "Admins **Can't** send links"
        s.add_field(name="Status", value=toggle)
        s.add_field(name="Mod Perms", value=mod)
        s.add_field(name="Admin Perms", value=admin)
        s.add_field(name="Bots", value=bottoggle)
        for channelid in data["channels"].run():
            channel = discord.utils.get(server.channels, id=int(channelid))
            msg += channel.mention + "\n"
        s.add_field(name="Disabled Channels", value=msg if msg != "" else "None")
        await ctx.send(embed=s)
		
	
    async def on_message(self, message): 
        serverid = message.guild.id
        author = message.author
        channel = message.channel
        data = r.table("antiad").get(str(serverid))
        if author == self.bot.user:
            return
        if data["modtoggle"].run() == False:
            if channel.permissions_for(author).manage_messages:
                return
        if data["admintoggle"].run() == False:
            if channel.permissions_for(author).administrator:
                return
        if data["bottoggle"].run() == False:
            if author.bot:
                return
        if str(channel.id) in data["channels"].run():
            return
        if data["toggle"].run() == True:
            if re.match(reinvite, message.content):
                await message.delete()
                await channel.send("{}, You are not allowed to send invite links here :no_entry:".format(author.mention))
				
    async def on_message_edit(self, before, after): 
        serverid = before.guild.id
        author = before.author
        channel = before.channel
        data = r.table("antiad").get(str(serverid))
        if author == self.bot.user:
            return
        if data["modtoggle"].run() == False:
            if channel.permissions_for(author).manage_messages:
                return
        if data["admintoggle"].run() == False:
            if channel.permissions_for(author).administrator:
                return
        if data["bottoggle"].run() == False:
            if author.bot:
                return
        try:
            if str(channel.id) in data["channels"].run():
                return
        except:
            pass
        if data["toggle"].run() == True:
            if re.match(reinvite, after.content):
                await after.delete()
                await channel.send("{}, You are not allowed to send invite links here :no_entry:".format(author.mention))

def setup(bot): 
    bot.add_cog(antiad(bot))