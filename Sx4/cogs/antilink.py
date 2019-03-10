import discord
from discord.ext import commands
import rethinkdb as r
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
from utils import arghelp
import re
import logging
import asyncio
import random
import time


class antilink:

    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
		
    @commands.group(usage="<sub command>")
    async def antilink(self, ctx):
        """Block out those advertisers"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("antilink").insert({"id": str(server.id), "toggle": False, "modtoggle": True, "admintoggle": False, "bottoggle": True, "channels": []}).run(self.db, durability="soft")
		
    @antilink.command()
    @checks.has_permissions("manage_messages")
    async def toggle(self, ctx):
        """Toggle antilink on or off"""
        server = ctx.guild
        data = r.table("antilink").get(str(server.id))
        if data["toggle"].run(self.db, durability="soft") == True:
            data.update({"toggle": False}).run(self.db, durability="soft")
            await ctx.send("Anti-link has been **Disabled**")
            return
        if data["toggle"].run(self.db, durability="soft") == False:
            data.update({"toggle": True}).run(self.db, durability="soft")
            await ctx.send("Anti-link has been **Enabled**")
            return
		
    @antilink.command() 
    @checks.has_permissions("manage_guild")
    async def modtoggle(self, ctx):
        """Choose whether you want your mods to be able to send links or not (manage_message and above are classed as mods)"""
        server = ctx.guild
        data = r.table("antilink").get(str(server.id))
        if data["modtoggle"].run(self.db, durability="soft") == True:
            data.update({"modtoggle": False}).run(self.db, durability="soft")
            await ctx.send("Mods will now not be affected by anti-link.")
            return
        if data["modtoggle"].run(self.db, durability="soft") == False:
            data.update({"modtoggle": True}).run(self.db, durability="soft")
            await ctx.send("Mods will now be affected by anti-link.")
            return
			
    @antilink.command() 
    @checks.has_permissions("manage_guild")
    async def admintoggle(self, ctx):
        """Choose whether you want your admins to be able to send links or not (administrator perms are classed as admins)"""
        server = ctx.guild
        data = r.table("antilink").get(str(server.id))
        if data["admintoggle"].run(self.db, durability="soft") == True:
            data.update({"admintoggle": False}).run(self.db, durability="soft")
            await ctx.send("Admins will now not be affected by anti-link.")
            return
        if data["admintoggle"].run(self.db, durability="soft") == False:
            data.update({"admintoggle": True}).run(self.db, durability="soft")
            await ctx.send("Admins will now be affected by anti-link.")
            return
			
    @antilink.command()
    @checks.has_permissions("manage_guild")
    async def togglebot(self, ctx):
        """Choose whether bots can send links or not"""
        server = ctx.guild
        data = r.table("antilink").get(str(server.id))
        if data["bottoggle"].run(self.db, durability="soft") == True:
            data.update({"bottoggle": False}).run(self.db, durability="soft")
            await ctx.send("Bots will now not be affected by anti-link.")
            return
        if data["bottoggle"].run(self.db, durability="soft") == False:
            data.update({"bottoggle": True}).run(self.db, durability="soft")
            await ctx.send("Bots will now be affected by anti-link.")
            return
			
    @antilink.command()
    @checks.has_permissions("manage_guild")
    async def togglechannel(self, ctx, channel: discord.TextChannel=None): 
        """Choose what channels you want to count towards antilink"""
        server = ctx.guild
        data = r.table("antilink").get(str(server.id))
        if not channel:
           channel = ctx.channel 
        if str(channel.id) in data["channels"].run(self.db, durability="soft"):
            data.update({"channels": r.row["channels"].difference([str(channel.id)])}).run(self.db, durability="soft")
            await ctx.send("Anti-link is now enabled in <#{}>".format(str(channel.id)))
            return
        else: 
            data.update({"channels": r.row["channels"].append(str(channel.id))}).run(self.db, durability="soft")
            await ctx.send("Anti-link is now disabled in <#{}>".format(str(channel.id)))
            return
		 
    @antilink.command()
    async def stats(self, ctx): 
        """View the settings of the antilink in your server"""
        serverid=ctx.guild.id
        server=ctx.guild
        data = r.table("antilink").get(str(server.id))
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Anti-link Settings", icon_url=self.bot.user.avatar_url)
        msg = ""
        if data["toggle"].run(self.db, durability="soft") == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        if data["modtoggle"].run(self.db, durability="soft") == False:
            mod = "Mods **Can** send links"
        else:
            mod = "Mods **Can't** send links"
        if data["bottoggle"].run(self.db, durability="soft") == False:
            bottoggle = "Bots **Can** send links"
        else:
            bottoggle = "Bots **Can't** send links"
        if data["admintoggle"].run(self.db, durability="soft") == False:
            admin = "Admins **Can** send links"
        else:
            admin = "Admins **Can't** send links"
        s.add_field(name="Status", value=toggle)
        s.add_field(name="Mod Perms", value=mod)
        s.add_field(name="Admin Perms", value=admin)
        s.add_field(name="Bots", value=bottoggle)
        for channelid in data["channels"].run(self.db, durability="soft"):
            channel = discord.utils.get(server.channels, id=int(channelid))
            if channel:
                msg += channel.mention + "\n"
        s.add_field(name="Disabled Channels", value=msg if msg != "" else "None")
        await ctx.send(embed=s)
		
	
    async def on_message(self, message): 
        serverid = message.guild.id
        author = message.author
        channel = message.channel
        data = r.table("antilink").get(str(serverid))
        if data["modtoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).manage_messages:
                return
        if data["admintoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).administrator:
                return
        if data["bottoggle"].run(self.db, durability="soft") == False:
            if author.bot:
                return
        if str(channel.id) in data["channels"].run(self.db, durability="soft"):
            return
        if data["toggle"].run(self.db, durability="soft") == True:
            if ("http://" in message.content.lower()) or ("https://" in message.content.lower()):
                await message.delete()
                await channel.send("{}, You are not allowed to send links here :no_entry:".format(author.mention))
				
    async def on_message_edit(self, before, after): 
        serverid = before.guild.id
        author = before.author
        channel = before.channel
        data = r.table("antilink").get(str(serverid))
        if data["modtoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).manage_messages:
                return
        if data["admintoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).administrator:
                return
        if data["bottoggle"].run(self.db, durability="soft") == False:
            if author.bot:
                return
        if str(channel.id) in data["channels"].run(self.db, durability="soft"):
            return
        if data["toggle"].run(self.db, durability="soft") == True:
            if ("http://" in after.content.lower()) or ("https://" in after.content.lower()):
                await after.delete()
                await channel.send("{}, You are not allowed to send links here :no_entry:".format(author.mention))

def setup(bot, connection): 
    bot.add_cog(antilink(bot, connection))