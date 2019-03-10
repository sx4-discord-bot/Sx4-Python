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
from utils import arghelp, arg
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound


class autorole:
    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
		
    @commands.group(usage="<sub command>")
    async def autorole(self, ctx):
        """Allows a role to be added to a user when they join the server"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("autorole").insert({"id": str(server.id), "role": None, "toggle": False, "botrole": None}).run(self.db, durability="soft")

    @autorole.command() 
    @checks.has_permissions("manage_roles")
    async def role(self, ctx, *, role: str):
        """Set the role to be added to a user when they join"""
        server = ctx.guild
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        r.table("autorole").get(str(server.id)).update({"role": str(role.id)}).run(self.db, durability="soft")
        await ctx.send("The autorole role is now **{}** <:done:403285928233402378>".format(role.name))

    @autorole.command() 
    @checks.has_permissions("manage_roles")
    async def botrole(self, ctx, *, role: str):
        """Set the role to be added to a bot when it joins"""
        server = ctx.guild
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        r.table("autorole").get(str(server.id)).update({"botrole": str(role.id)}).run(self.db, durability="soft")
        await ctx.send("The autorole bot role is now **{}** <:done:403285928233402378>".format(role.name))
		
    @autorole.command()
    @commands.cooldown(1, 360, commands.BucketType.guild)
    @checks.has_permissions("manage_roles")
    async def fix(self, ctx):
        """Has the bot been offline and missed a few users? Use this to add the role to everyone who doesn't have it"""
        server = ctx.guild
        data = r.table("autorole").get(str(server.id)).run(self.db)
        if not data:
            return await ctx.send("You need to set the autorole before you can use this :no_entry:")
        if not data["role"]:
            return await ctx.send("You need to set the autorole before you can use this :no_entry:")
        role = ctx.guild.get_role(int(data["role"]))
        if not role:
            return await ctx.send("The auto role which is set was deleted or no longer exists :no_entry:")
        if data["botrole"]:
            botrole = ctx.guild.get_role(int(data["botrole"]))
        else:
            botrole = data["botrole"]
        members = [x for x in ctx.guild.members if not x.bot and role not in x.roles] if botrole else [x for x in ctx.guild.members if role not in x.roles]
        bots = [x for x in ctx.guild.members if x.bot and botrole not in x.roles]
        added_users, added_bots = 0, 0
        if botrole:
            for bot in bots:
                try:
                    await bot.add_roles(botrole, reason="Autorole fix")
                    added_bots += 1
                except:
                    pass
        for user in members:
            try:
                await user.add_roles(role, reason="Autorole fix")
                added_users += 1
            except:
                pass
        user_msg = ", I was unable to add the role to **{}** users".format(len(members) - added_users)
        bot_msg = ", I was unable to add the role to **{}** bots".format(len(bots) - added_bots)
        await ctx.send("Added **{}** to **{}** users{}\n{}".format(role.name, added_users, user_msg if len(members) != added_users else "", "Added **{}** to **{}** bots{}".format(botrole.name, added_bots, bot_msg if len(bots) != added_bots else "") if botrole else ""))      
        
    @autorole.command()
    @checks.has_permissions("manage_roles")
    async def toggle(self, ctx):
        """Toggle autorole on or off"""
        server = ctx.guild
        data = r.table("autorole").get(str(server.id))
        if data["toggle"].run(self.db, durability="soft") == True:
            data.update({"toggle": False}).run(self.db, durability="soft")
            await ctx.send("Auto-role has been **Disabled**")
            return
        if data["toggle"].run(self.db, durability="soft") == False:
            data.update({"toggle": True}).run(self.db, durability="soft")
            await ctx.send("Auto-role has been **Enabled**")
            return
		
    @autorole.command()
    async def stats(self, ctx):
        """View the settings of autorole on your server"""
        server = ctx.guild
        data = r.table("autorole").get(str(server.id)).run(self.db)
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Auto-role Settings", icon_url=self.bot.user.avatar_url)
        if data["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        s.add_field(name="Status", value=toggle)
        if not data["role"]:
            s.add_field(name="Auto-role role", value="Not set")
        else:
            s.add_field(name="Auto-role role", value=ctx.guild.get_role(int(data["role"])).mention if ctx.guild.get_role(int(data["role"])) else "Not set")
        if data["botrole"]:
            s.add_field(name="Auto-role bot role", value=ctx.guild.get_role(int(data["botrole"])).mention if ctx.guild.get_role(int(data["botrole"])) else "Not set")
        else:
            s.add_field(name="Auto-role bot role", value="Not set")
        await ctx.send(embed=s)
			
    async def on_member_join(self, member):
        server = member.guild
        data = r.table("autorole").get(str(server.id)).run(self.db)
        role = server.get_role(int(data["role"]))
        if data["toggle"] == True: 
            if member.bot:
                if data["botrole"]:
                    botrole = server.get_role(int(data["botrole"]))
                    if botrole:
                        await member.add_roles(botrole, reason="Autorole")
                    else:
                        await member.add_roles(role, reason="Autorole")
                else:
                    await member.add_roles(role, reason="Autorole")
            else:
                await member.add_roles(role, reason="Autorole")
		
def setup(bot, connection): 
    bot.add_cog(autorole(bot, connection))