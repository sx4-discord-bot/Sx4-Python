import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import random
from utils import checks
import os
from random import choice
from utils.dataIO import dataIO
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
from enum import Enum
import asyncio
from difflib import get_close_matches

class selfroles:
    def __init__(self, bot):
        self.bot = bot
        self.file_path = 'data/general/selfroles.json'
        self.data = dataIO.load_json(self.file_path)
	
    @commands.group(pass_context=True)
    async def selfrole(self, ctx): 
        """Make it so users can self assign roles without perms"""
        server = ctx.message.server
        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.file_path, self.data)
        if "role" not in self.data[server.id]:
            self.data[server.id]["role"] = {}
            dataIO.save_json(self.file_path, self.data)
			
    @selfrole.command(pass_context=True) 
    @checks.admin_or_permissions(manage_roles=True)
    async def add(self, ctx, *, role: discord.Role):
        """Add a role to be self assignable"""
        server = ctx.message.server
        try:
            if role.id in self.data[server.id]["role"]:
                await self.bot.say("That role is already a self role :no_entry:")
                return
        except: 
            pass
        await self._create_role(server, role)
        dataIO.save_json(self.file_path, self.data)
        await self.bot.say("Added **{}** to the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command(pass_context=True) 
    @checks.admin_or_permissions(manage_roles=True)
    async def remove(self, ctx, *, role: discord.Role): 
        """Remove a role to be self assignable"""
        server = ctx.message.server
        if role.id not in self.data[server.id]["role"]:
            await self.bot.say("That role isn't a self role :no_entry:")
            return
        del self.data[server.id]["role"][role.id]
        dataIO.save_json(self.file_path, self.data)
        await self.bot.say("Removed **{}** from the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command(pass_context=True) 
    @checks.admin_or_permissions(manage_roles=True)
    async def reset(self, ctx):
        """Reset all the selfroles"""
        server = ctx.message.server
        self.data[server.id] = {}
        dataIO.save_json(self.file_path, self.data)
        await self.bot.say("All self roles have been deleted <:done:403285928233402378>")
		
    @selfrole.command(pass_context=True) 
    async def list(self, ctx): 
        """List all the selfroles"""
        server = ctx.message.server
        s = await self._list(server)
        try:
            await self.bot.say(embed=s)
        except:
            await self.bot.say("This server has no Self Roles :no_entry:")
			
    @commands.command(pass_context=True)
    async def role(self, ctx, *, role: discord.Role):
        """Self assign a role in the selfrole list"""
        author = ctx.message.author
        server = ctx.message.server
        if role.id in self.data[server.id]["role"]:
            if role in author.roles:
                await self.bot.remove_roles(author, role)
                await self.bot.say("{}, You no longer have **{}**".format(author.mention, role.name))
                return
            if not role in author.roles:
                await self.bot.add_roles(author, role)
                await self.bot.say("{}, You now have **{}**".format(author.mention, role.name))
                return
        else:
            await self.bot.say("That role is not self assignable :no_entry:")
			
    async def _create_role(self, server, role):
        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.file_path, self.data)
        if "role" not in self.data[server.id]:
            self.data[server.id]["role"] = {}
            dataIO.save_json(self.file_path, self.data)
        if role.id not in self.data[server.id]["role"]:
            self.data[server.id]["role"][role.id] = {}
            dataIO.save_json(self.file_path, self.data)
			
    async def _list(self, server):   
        msg = ""	
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        for roleid in self.data[server.id]["role"]:
            role = discord.utils.get(server.roles, id=roleid)
            try:
                msg += "\n{}".format(role.name)
            except:
                pass
        s.add_field(name="Self Roles ({})".format(len(self.data[server.id]["role"])), value=msg)
        return s
		 
    async def on_server_role_delete(self, role):
        server = role.server
        if role.id in self.data[server.id]["role"]:
            del self.data[server.id]["role"][role.id]

			
def check_files():
    f = 'data/general/selfroles.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default selfroles.json...')
		
def setup(bot):
    check_files()
    bot.add_cog(selfroles(bot))