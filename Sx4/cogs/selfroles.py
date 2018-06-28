import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import random
from utils import checks
import os
import math
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
	
    @commands.group()
    async def selfrole(self, ctx): 
        """Make it so users can self assign roles without perms"""
        server = ctx.message.guild
        if str(server.id) not in self.data:
            self.data[str(server.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "role" not in self.data[str(server.id)]:
            self.data[str(server.id)]["role"] = {}
            dataIO.save_json(self.file_path, self.data)
			
    @selfrole.command() 
    @checks.admin_or_permissions(manage_roles=True)
    async def add(self, ctx, *, role: discord.Role):
        """Add a role to be self assignable"""
        server = ctx.message.guild
        try:
            if str(role.id) in self.data[str(server.id)]["role"]:
                await ctx.send("That role is already a self role :no_entry:")
                return
        except: 
            pass
        await self._create_role(server, role)
        dataIO.save_json(self.file_path, self.data)
        await ctx.send("Added **{}** to the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command() 
    @checks.admin_or_permissions(manage_roles=True)
    async def remove(self, ctx, *, role: discord.Role): 
        """Remove a role to be self assignable"""
        server = ctx.message.guild
        if str(role.id) not in self.data[str(server.id)]["role"]:
            await ctx.send("That role isn't a self role :no_entry:")
            return
        del self.data[str(server.id)]["role"][str(role.id)]
        dataIO.save_json(self.file_path, self.data)
        await ctx.send("Removed **{}** from the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command() 
    @checks.admin_or_permissions(manage_roles=True)
    async def reset(self, ctx):
        """Reset all the selfroles"""
        server = ctx.message.guild
        self.data[str(server.id)] = {}
        dataIO.save_json(self.file_path, self.data)
        await ctx.send("All self roles have been deleted <:done:403285928233402378>")
		
    @selfrole.command() 
    async def list(self, ctx): 
        """List all the selfroles"""
        server = ctx.message.guild
        i = 0
        for roleid in self.data[str(server.id)]["role"]:
            role = discord.utils.get(server.roles, id=int(roleid))
            if role:
                i += 1
        page = 1
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        s.add_field(name="Self Roles ({})".format(i), value=await self._list(server, page))
        s.set_footer(text="Page {}/{}".format(page, math.ceil(i / 20)))
        try:
            message = await ctx.send(embed=s)
            await message.add_reaction("◀")
            await message.add_reaction("▶")
            def reactioncheck(reaction, user):
                if user != self.bot.user:
                    if user == ctx.author:
                        if reaction.message.channel == ctx.channel:
                            if reaction.emoji == "▶" or reaction.emoji == "◀":
                                return True
            page2 = True
            while page2:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=reactioncheck)
                    if reaction.emoji == "▶":
                        if page != math.ceil(i / 20):
                            page += 1
                            s=discord.Embed(colour=0xfff90d)
                            s.set_author(name=server.name, icon_url=server.icon_url)
                            s.add_field(name="Self Roles ({})".format(i), value=await self._list(server, page))
                            s.set_footer(text="Page {}/{}".format(page, math.ceil(i / 20)))
                            await message.edit(embed=s)
                        else:
                            page = 1
                            s=discord.Embed(colour=0xfff90d)
                            s.set_author(name=server.name, icon_url=server.icon_url)
                            s.add_field(name="Self Roles ({})".format(i), value=await self._list(server, page))
                            s.set_footer(text="Page {}/{}".format(page, math.ceil(i / 20)))
                            await message.edit(embed=s)
                    if reaction.emoji == "◀":
                        if page != 1:
                            page -= 1
                            s=discord.Embed(colour=0xfff90d)
                            s.set_author(name=server.name, icon_url=server.icon_url)
                            s.add_field(name="Self Roles ({})".format(i), value=await self._list(server, page))
                            s.set_footer(text="Page {}/{}".format(page, math.ceil(i / 20)))
                            await message.edit(embed=s)
                        else:
                            page = math.ceil(botnum / 20)
                            s=discord.Embed(colour=0xfff90d)
                            s.set_author(name=server.name, icon_url=server.icon_url)
                            s.add_field(name="Self Roles ({})".format(i), value=await self._list(server, page))
                            s.set_footer(text="Page {}/{}".format(page, math.ceil(i / 20)))
                            await message.edit(embed=s)
                except asyncio.TimeoutError:
                    await message.remove_reaction("◀", ctx.me)
                    await message.remove_reaction("▶", ctx.me)
                    page2 = False
        except:
            await ctx.send("This server has no Self Roles :no_entry:")
        
			
    @commands.command()
    async def role(self, ctx, *, role: discord.Role):
        """Self assign a role in the selfrole list"""
        author = ctx.message.author
        server = ctx.message.guild
        if str(server.id) not in self.data:
            self.data[str(server.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "role" not in self.data[str(server.id)]:
            self.data[str(server.id)]["role"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(role.id) in self.data[str(server.id)]["role"]:
            if role in author.roles:
                await author.remove_roles(role)
                await ctx.send("{}, You no longer have **{}**".format(author.mention, role.name))
                return
            if not role in author.roles:
                await author.add_roles(role)
                await ctx.send("{}, You now have **{}**".format(author.mention, role.name))
                return
        else:
            await ctx.send("That role is not self assignable :no_entry:")
			
    async def _create_role(self, server, role):
        if str(server.id) not in self.data:
            self.data[str(server.id)] = {}
            dataIO.save_json(self.file_path, self.data)
        if "role" not in self.data[str(server.id)]:
            self.data[str(server.id)]["role"] = {}
            dataIO.save_json(self.file_path, self.data)
        if str(role.id) not in self.data[str(server.id)]["role"]:
            self.data[str(server.id)]["role"][str(role.id)] = {}
            dataIO.save_json(self.file_path, self.data)
			
    async def _list(self, server, page):   
        msg = []
        for roleid in list(self.data[str(server.id)]["role"])[page*20-20:page*20]:
            role = discord.utils.get(server.roles, id=int(roleid))
            if role:
                msg.append(role)
        msg = "\n".join(sorted([x.name for x in msg], key=[x.name for x in server.role_hierarchy].index))
        return msg
		 
    async def on_server_role_delete(self, role):
        server = role.guild
        if str(role.id) in self.data[str(server.id)]["role"]:
            del self.data[str(server.id)]["role"][str(role.id)]

			
def check_files():
    f = 'data/general/selfroles.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default selfroles.json...')
		
def setup(bot):
    check_files()
    bot.add_cog(selfroles(bot))