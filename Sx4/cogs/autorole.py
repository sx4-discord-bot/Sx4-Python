import discord
from discord.ext import commands
from utils import checks
import datetime
from collections import deque, defaultdict
import os
import re
import logging
import rethinkdb as r
import asyncio
import random
import time
from utils import arghelp
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound


class autorole:
    def __init__(self, bot):
        self.bot = bot
		
    @commands.group()
    async def autorole(self, ctx):
        """Allows a role to be added to a user when they join the server"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("autorole").insert({"id": str(server.id), "role": None, "toggle": False}).run()

    @autorole.command() 
    @checks.has_permissions("manage_roles")
    async def role(self, ctx, *, role: discord.Role):
        """Set the role to be added to a user whne they join"""
        server = ctx.guild
        r.table("autorole").get(str(server.id)).update({"role": str(role.id)}).run()
        await ctx.send("The autorole role is now **{}** <:done:403285928233402378>".format(role.name))
		
    @autorole.command()
    @checks.has_permissions("manage_roles")
    async def fix(self, ctx, subarg=None):
        """Has the bot been offline and missed a few users? Use this to add the role to everyone who doesn't have it"""
        server = ctx.guild
        data = r.table("autorole").get(str(server.id))
        if not subarg:
            users = server.members
        elif subarg.lower() == "nobots":
            users = list(set(filter(lambda m: not m.bot, server.members)))
        elif subarg.lower() == "bots":
            users = list(set(filter(lambda m: m.bot, server.members)))
        role = discord.utils.get(server.roles, id=int(data["role"].run()))
        if not role:
            return await ctx.send("You need to set the autorole before you can use this :no_entry:")
        members = len([x for x in users if role not in x.roles])
        if not role:
            await ctx.send("Role is not set or does not exist :no_entry:")
        i = 0
        for user in [x for x in users if role not in x.roles]:
            try:
                await user.add_roles(role, reason="Autorole fix")
                i += 1
            except:
                pass
        msg = ", I was unable to add the role to **{}** users".format(members - i)
        await ctx.send("Added **{}** to **{}** users{} <:done:403285928233402378>".format(role.name, i, msg if members != i else ""))      
        
    @autorole.command()
    @checks.has_permissions("manage_roles")
    async def toggle(self, ctx):
        """Toggle autorole on or off"""
        server = ctx.guild
        data = r.table("autorole").get(str(server.id))
        if data["toggle"].run() == True:
            data.update({"toggle": False}).run()
            await ctx.send("Auto-role has been **Disabled**")
            return
        if data["toggle"].run() == False:
            data.update({"toggle": True}).run()
            await ctx.send("Auto-role has been **Enabled**")
            return
		
    @autorole.command()
    async def stats(self, ctx):
        """View the settings of autorole on your server"""
        server = ctx.guild
        data = r.table("autorole").get(str(server.id))
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Auto-role Settings", icon_url=self.bot.user.avatar_url)
        if data["toggle"].run() == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        s.add_field(name="Status", value=toggle)
        if not data["role"].run():
            s.add_field(name="Auto-role role", value="Role not set")
        else:
            try:
                s.add_field(name="Auto-role role", value=discord.utils.get(ctx.guild.roles, id=int(data["role"].run())).mention)
            except:
                s.add_field(name="Auto-role role", value="Role not set")
        await ctx.send(embed=s)
			
    async def on_member_join(self, member):
        server = member.guild
        data = r.table("autorole").get(str(server.id))
        role = discord.utils.get(server.roles, id=int(data["role"].run()))
        if data["toggle"].run() == True: 
            await member.add_roles(role, reason="Autorole")
		
def setup(bot): 
    bot.add_cog(autorole(bot))