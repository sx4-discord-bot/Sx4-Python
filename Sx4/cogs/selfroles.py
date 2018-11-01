import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import random
from utils import checks
from utils import arghelp
import os
import math
from random import choice
import rethinkdb as r
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
	
    @commands.group()
    async def selfrole(self, ctx): 
        """Make it so users can self assign roles without perms"""
        server = ctx.message.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("selfroles").insert({"id": str(server.id), "roles": []}).run(durability="soft")
			
    @selfrole.command() 
    @checks.has_permissions("manage_roles")
    async def add(self, ctx, *, role):
        """Add a role to be self assignable"""
        if "<" in role and "&" in role and ">" in role and "@" in role:
            role = role.replace("<", "").replace(">", "").replace("@", "").replace("&", "")
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(role))
            except:
                return await ctx.send("Invalid role :no_entry:")
        else:
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(role))
            except:
                try:
                    role = list(set(filter(lambda r: r.name.lower() == role.lower(), ctx.guild.roles)))[0]
                except:
                    return await ctx.send("I could not find that role :no_entry:")
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id))
        try:
            if str(role.id) in data["roles"].run(durability="soft"):
                await ctx.send("That role is already a self role :no_entry:")
                return
        except: 
            pass
        await self._create_role(server, role)
        await ctx.send("Added **{}** to the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command() 
    @checks.has_permissions("manage_roles")
    async def remove(self, ctx, *, role): 
        """Remove a role to be self assignable"""
        if "<" in role and "&" in role and ">" in role and "@" in role:
            role = role.replace("<", "").replace(">", "").replace("@", "").replace("&", "")
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(role))
            except:
                return await ctx.send("Invalid role :no_entry:")
        else:
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(role))
            except:
                try:
                    role = list(set(filter(lambda r: r.name.lower() == role.lower(), ctx.guild.roles)))[0]
                except:
                    return await ctx.send("I could not find that role :no_entry:")
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id))
        if str(role.id) not in data["roles"].run(durability="soft"):
            await ctx.send("That role isn't a self role :no_entry:")
            return
        data.update({"roles": r.row["roles"].difference([str(role.id)])}).run(durability="soft")
        await ctx.send("Removed **{}** from the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command() 
    @checks.has_permissions("manage_roles")
    async def reset(self, ctx):
        """Reset all the selfroles"""
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id))
        data.update({"roles": []}).run(durability="soft")
        await ctx.send("All self roles have been deleted <:done:403285928233402378>")
		
    @selfrole.command() 
    async def list(self, ctx): 
        """List all the selfroles"""
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id)).run(durability="soft")
        i = 0
        for roleid in data["roles"]:
            role = discord.utils.get(server.roles, id=int(roleid))
            if role:
                i += 1
        if i == 0:
            return await ctx.send("This server has no selfroles :no_entry:")
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
                if user == ctx.author:
                    if reaction.message.id == message.id:
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
            pass
        
			
    @commands.command()
    async def role(self, ctx, *, role):
        """Self assign a role in the selfrole list"""
        if "<" in role and "&" in role and ">" in role and "@" in role:
            role = role.replace("<", "").replace(">", "").replace("@", "").replace("&", "")
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(role))
            except:
                return await ctx.send("Invalid role :no_entry:")
        else:
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(role))
            except:
                try:
                    role = list(set(filter(lambda r: r.name.lower() == role.lower(), ctx.guild.roles)))[0]
                except:
                    return await ctx.send("I could not find that role :no_entry:")
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        author = ctx.message.author
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id)).run(durability="soft")
        if not data:
            return await ctx.send("That role is not self assignable :no_entry:")
        if str(role.id) in data["roles"]:
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
        r.table("selfroles").get(str(server.id)).update({"roles": r.row["roles"].append(str(role.id))}).run(durability="soft")
			
    async def _list(self, server, page):   
        msg = []
        data = r.table("selfroles").get(str(server.id)).run(durability="soft")
        for roleid in list(data["roles"])[page*20-20:page*20]:
            role = discord.utils.get(server.roles, id=int(roleid))
            if role:
                msg.append(role)
        msg = "\n".join(map(lambda x: x.name, (sorted(msg, key=server.roles.index))[::-1]))
        return msg
		 
    async def on_server_role_delete(self, role):
        server = role.guild
        data = r.table("selfroles").get(str(server.id))
        if str(role.id) in data["roles"].run(durability="soft"):
            data.update({"roles": r.row["roles"].difference([str(role.id)])}).run(durability="soft")
		
def setup(bot):
    bot.add_cog(selfroles(bot))