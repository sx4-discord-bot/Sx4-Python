import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import random
from utils import checks
from utils import arghelp, arg
import os
import math
from random import choice
import rethinkdb as r
import re
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
from enum import Enum
import asyncio
from difflib import get_close_matches

re_emoji = re.compile("<(?:a|):.+:([0-9]+)>")

class selfroles:
    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection

    @commands.group(usage="<sub command>")
    async def reactionrole(self, ctx):
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("reactionrole").insert({"id": str(ctx.guild.id), "messages": [], "dm": True}).run(self.db, durability="soft")

    @reactionrole.command()
    @checks.has_permissions("manage_roles")
    async def create(self, ctx, channel: str, *, title: str=None):
        """Creates the base message for a reaction role in a certain channel with an optional title"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        channel = arg.get_text_channel(ctx, channel)
        if not channel:
            return await ctx.send("Invalid Channel :no_entry:")
        if title:
            if len(title) > 256:
                return await ctx.send("Titles can not be more than 256 characters :no_entry:")
        s=discord.Embed(title="Reaction Role" if not title else title, description="To add reactions use `{}reactionrole add` (This message will be removed upon adding a role)".format(ctx.prefix))
        s.set_footer(text="React to the corresponding emote to get the desired role")
        message = await channel.send(embed=s)
        new_message = {"id": str(message.id), "channel": str(channel.id), "roles": [], "bot_menu": True}
        await ctx.send("The base reaction role menu has been created In {}".format(channel.mention))
        serverdata.update({"messages": r.row["messages"].append(new_message)}).run(self.db, durability="soft")
        
    @reactionrole.command(name="add")
    @checks.has_permissions("manage_roles")
    async def _add(self, ctx, message_id: int, emote: str, *, role: str):
        """Adds an emote and role to the reaction role message"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("Invalid Role :no_entry:")
        if str(message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message_id))[0]
            try:
                message = await ctx.guild.get_channel(int(message_db["channel"].run(self.db))).get_message(message_id)
            except discord.errors.NotFound:
                return await ctx.send("That message has been deleted :no_entry:")
            if str(role.id) in message_db["roles"].map(lambda x: x["id"]).run(self.db):
                return await ctx.send("This role is already on this reaction role message :no_entry:")
            if len(message.reactions) >= 20:
                return await ctx.send("This message has hit the reaction cap of 20 :no_entry:")
            if re_emoji.match(emote):
                if str(re_emoji.match(emote).group(1)) in message_db["roles"].map(lambda x: x["emote"]).run(self.db):
                    return await ctx.send("This emote is already being used in this reaction role message :no_entry:")
                emote = self.bot.get_emoji(int(re_emoji.match(emote).group(1)))
                if not emote:
                    return await ctx.send("I'm not able to use that emoji or It's invalid :no_entry:")
                else:
                    emote_db = str(emote.id)
                    await message.add_reaction(emote)
            else:
                if emote in message_db["roles"].map(lambda x: x["emote"]).run(self.db):
                    return await ctx.send("This emote is already being used in this reaction role message :no_entry:")
                try:
                    await message.add_reaction(emote)
                    emote_db = str(emote)
                except:
                    return await ctx.send("Inavlid Emoji :no_entry:")
            if message.author == ctx.me and message.embeds:
                s = message.embeds[0]
                if not message_db["roles"].run(self.db):
                    s.description = "{}: {}".format(str(emote), role.mention)
                else:
                    s.description += "\n\n{}: {}".format(str(emote), role.mention)
                await message.edit(embed=s)
            role_db = {"id": str(role.id), "emote": emote_db}
            new_message = message_db.run(self.db)
            new_message["roles"].append(role_db)
            message_new = serverdata["messages"].run(self.db)
            message_new.remove(message_db.run(self.db))
            message_new.append(new_message)
            await ctx.send("The role `{}` will now be given when reacting with {}".format(role.name, emote))
            serverdata.update({"messages": message_new}).run(self.db, durability="soft")
        else:
            try:
                message = await ctx.channel.get_message(message_id)
            except discord.errors.NotFound:
                return await ctx.send("That message is not a reaction role message/I could not find that message within this channel :no_entry:")
            if len(message.reactions) >= 20:
                return await ctx.send("This message has hit the reaction cap of 20 :no_entry:")
            if re_emoji.match(emote):
                emote = self.bot.get_emoji(int(re_emoji.match(emote).group(1)))
                if not emote:
                    return await ctx.send("I'm not able to use that emoji or It's invalid :no_entry:")
                else:
                    emote_db = str(emote.id)
                    await message.add_reaction(emote)
            else:
                try:
                    await message.add_reaction(emote)
                    emote_db = str(emote)
                except:
                    return await ctx.send("Inavlid Emoji :no_entry:")
            new_message = {"id": str(message.id), "channel": str(ctx.channel.id), "roles": [{"id": str(role.id), "emote": emote_db}], "bot_menu": False}
            await ctx.send("The role `{}` will now be given when reacting with {}".format(role.name, emote))
            serverdata.update({"messages": r.row["messages"].append(new_message)}).run(self.db, durability="soft")

    @reactionrole.command(name="remove")
    @checks.has_permissions("manage_roles")
    async def _remove(self, ctx, message_id: int, *, role: str):
        """Removes an emote and role from the reaction role message"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("Invalid Role :no_entry:")
        if str(message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message_id))[0]
            new_message = message_db.run(self.db)
            message = await ctx.guild.get_channel(int(message_db["channel"].run(self.db))).get_message(message_id)
            if str(role.id) not in message_db["roles"].map(lambda x: x["id"]).run(self.db):
                return await ctx.send("This role is not on this reaction role message :no_entry:")
            else:
                role_db = message_db["roles"].filter(lambda x: x["id"] == str(role.id))[0]
                emote_db = role_db["emote"].run(self.db)
                if emote_db.isdigit():
                    emote = self.bot.get_emoji(int(emote_db))
                else:
                    emote = emote_db
            if self.is_bot_menu(new_message, message):
                s = message.embeds[0]
                content = "{}: {}\n\n".format(str(emote), "<@&{}>".format(role.id))
                try:
                    before = s.description
                    s.description = s.description.replace(content, "")
                    if before == s.description:
                        content = "\n\n{}: {}".format(str(emote), "<@&{}>".format(role.id))
                        s.description = s.description.replace(content, "")
                except:
                    pass
                await message.edit(embed=s)
            await message.remove_reaction(emote, ctx.me)
            role_db = {"id": str(role.id), "emote": emote_db}
            new_message["roles"].remove(role_db)
            message_new = serverdata["messages"].run(self.db)
            message_new.remove(message_db.run(self.db))
            message_new.append(new_message)
            await ctx.send("The role `{}` has been removed from the reaction role <:done:403285928233402378>".format(role.name))
            serverdata.update({"messages": message_new}).run(self.db, durability="soft")
        else:
            return await ctx.send("That message is not a reaction role message :no_entry:")

    @reactionrole.command()
    @checks.has_permissions("manage_roles")
    async def forceremove(self, ctx, message_id: int):
        """Removes all deleted roles from the reactionrole menu"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        if str(message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message_id))[0]
            new_message = message_db.run(self.db)
            try:
                message = await ctx.guild.get_channel(int(message_db["channel"].run(self.db))).get_message(message_id)
            except discord.errors.NotFound:
                return await ctx.send("That message has been deleted :no_entry:")
            if self.is_bot_menu(new_message, message):
                s = message.embeds[0]
            dataToRemove = {} 
            for x in message_db["roles"].map(lambda x: x["id"]).run(self.db):
                role = ctx.guild.get_role(int(x))
                if role not in ctx.guild.roles:
                    role_db = message_db["roles"].filter(lambda y: y["id"] == x)[0]
                    emote_db = role_db["emote"].run(self.db)
                    if emote_db.isdigit():
                        emote = self.bot.get_emoji(int(emote_db))
                    else:
                        emote = emote_db
                    await message.remove_reaction(emote, ctx.me)
                    dataToRemove.update({"id": x, "emote": emote_db})
                    if self.is_bot_menu(new_message, message):
                        content = "{}: {}\n\n".format(str(emote), "<@&{}>".format(x))
                        try:
                            before = s.description
                            s.description = s.description.replace(content, "")
                            if before == s.description:
                                content = "\n\n{}: {}".format(str(emote), "<@&{}>".format(x))
                                s.description = s.description.replace(content, "")
                        except:
                            pass
            if not dataToRemove:
                return await ctx.send("There were no deleted roles on this reaction role :no_entry:")
            if self.is_bot_menu(new_message, message):
                await message.edit(embed=s)
            new_message["roles"].remove(dataToRemove)
            message_new = serverdata["messages"].run(self.db)
            message_new.remove(message_db.run(self.db))
            message_new.append(new_message)
            await ctx.send("All roles which were deleted on the reaction role menu have been removed from it <:done:403285928233402378>")
            serverdata.update({"messages": message_new}).run(self.db, durability="soft")
        else:
            return await ctx.send("That message is not a reaction role message :no_entry:")

    @reactionrole.command()
    @checks.has_permissions("manage_roles")
    async def refresh(self, ctx, message_id: int):
        """Refreshes a reactionrole menu and updates the colours and names of roles in their mentions"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        if str(message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message_id))[0].run(self.db)
            message = await ctx.guild.get_channel(int(message_db["channel"])).get_message(message_id)
            if self.is_bot_menu(message_db, message):
                await ctx.send("Refreshed the reaction role menu <:done:403285928233402378>")
                await message.edit(embed=message.embeds[0])
            else:
                return await ctx.send("You can only refresh on reaction roles created by the bot :no_entry:")
        else:
            return await ctx.send("That message is not a reaction role message :no_entry:")


    @reactionrole.command()
    @checks.has_permissions("manage_roles")
    async def delete(self, ctx, message_id: int):
        """Deletes a reactionrole message and it's data"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        if str(message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message_id))[0]
            try:
                message = await ctx.guild.get_channel(int(message_db["channel"].run(self.db))).get_message(message_id)
                await message.delete()
            except:
                pass
            await ctx.send("That reaction role has been deleted")
            serverdata.update({"messages": r.row["messages"].filter(lambda x: x["id"] != str(message_id))}).run(self.db, durability="soft")
        else:
            return await ctx.send("I could not find that message, make sure it's a reaction role message :no_entry:")

    @reactionrole.command()
    @checks.has_permissions("manage_roles")
    async def dmtoggle(self, ctx):
        """Toggles whether the bot dms users when they get/remove a role"""
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        if serverdata["dm"].run(self.db) == True:
            await ctx.send("I will no longer dm users when they get a role through reaction roles.")
            serverdata.update({"dm": False}).run(self.db, durability="soft")
        elif serverdata["dm"].run(self.db) == False:
            await ctx.send("I will now dm users when they get a role through reaction roles.")
            serverdata.update({"dm": True}).run(self.db, durability="soft")

    @reactionrole.command()
    @checks.has_permissions("manage_roles")
    async def maxroles(self, ctx, message_id: int, max_roles: int=None):
        """Allows you to set the max amount of roles a user can have from a reaction role page"""
        if max_roles:
            if max_roles < 1:
                return await ctx.send("The maximum amount of roles a user can have can't be less than 1 :no_entry:")
        serverdata = r.table("reactionrole").get(str(ctx.guild.id))
        if str(message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message_id))[0].run(self.db)
            messages = serverdata["messages"].run(self.db)
            if max_roles:
                if max_roles > len(message_db["roles"]):
                    return await ctx.send("The maximum amount of roles a user can have can't be more than the amount of roles on the reaction role page :no_entry:")
            messages.remove(message_db)
            if "max_roles" not in message_db:
                message_db.update({"max_roles": max_roles})
            else:
                if max_roles == message_db["max_roles"]:
                    return await ctx.send("The maximum roles on this reaction role menu is already set to `{}` :no_entry:".format(max_roles if max_roles else "disabled"))
                message_db["max_roles"] = max_roles
            if max_roles:
                await ctx.send("The maximum roles a user can now have from that reaction role menu is now **{}** role{}".format(max_roles, "s" if max_roles != 1 else ""))
            else: 
                await ctx.send("That reaction role menu will no longer have a limit for the maximum roles a user can have")
            messages.append(message_db)
            serverdata.update({"messages": messages}).run(self.db, durability="soft")
        else:
            return await ctx.send("I could not find that message, make sure it's a reaction role message :no_entry:")
	
    @commands.group(usage="<sub command>")
    async def selfrole(self, ctx): 
        """Make it so users can self assign roles without perms"""
        server = ctx.message.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("selfroles").insert({"id": str(server.id), "roles": []}).run(self.db, durability="soft")
			
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
            if str(role.id) in data["roles"].run(self.db, durability="soft"):
                await ctx.send("That role is already a self role :no_entry:")
                return
        except: 
            pass
        self._create_role(server, role)
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
        if str(role.id) not in data["roles"].run(self.db, durability="soft"):
            await ctx.send("That role isn't a self role :no_entry:")
            return
        data.update({"roles": r.row["roles"].difference([str(role.id)])}).run(self.db, durability="soft")
        await ctx.send("Removed **{}** from the self roles list <:done:403285928233402378>".format(role.name))
		
    @selfrole.command() 
    @checks.has_permissions("manage_roles")
    async def reset(self, ctx):
        """Reset all the selfroles"""
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id))
        data.update({"roles": []}).run(self.db, durability="soft")
        await ctx.send("All self roles have been deleted <:done:403285928233402378>")
		
    @selfrole.command() 
    async def list(self, ctx): 
        """List all the selfroles"""
        server = ctx.message.guild
        data = r.table("selfroles").get(str(server.id)).run(self.db, durability="soft")
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
        s.add_field(name="Self Roles ({})".format(i), value=self._list(server, page))
        s.set_footer(text="Page {}/{} | Use s?role <selfrole> to assign a role".format(page, math.ceil(i / 20)))
        try:
            message = await ctx.send(embed=s)
            await message.add_reaction("◀")
            await message.add_reaction("▶")
            def reactioncheck(reaction, user):
                if user == ctx.author:
                    if reaction.message.id == message.id:
                        if reaction.emoji == "▶" or reaction.emoji == "◀":
                            return True
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=reactioncheck)
                    if reaction.emoji == "▶":
                        if page != math.ceil(i / 20):
                            page += 1
                        else:
                            page = 1
                        s=discord.Embed(colour=0xfff90d)
                        s.set_author(name=server.name, icon_url=server.icon_url)
                        s.add_field(name="Self Roles ({})".format(i), value=self._list(server, page))
                        s.set_footer(text="Page {}/{} | Use s?role <selfrole> to assign a role".format(page, math.ceil(i / 20)))
                        await message.edit(embed=s)
                    if reaction.emoji == "◀":
                        if page != 1:
                            page -= 1
                        else:
                            page = math.ceil(botnum / 20)
                        s=discord.Embed(colour=0xfff90d)
                        s.set_author(name=server.name, icon_url=server.icon_url)
                        s.add_field(name="Self Roles ({})".format(i), value=self._list(server, page))
                        s.set_footer(text="Page {}/{} | Use s?role <selfrole> to assign a role".format(page, math.ceil(i / 20)))
                        await message.edit(embed=s)
                except asyncio.TimeoutError:
                    try:
                        await message.remove_reaction("◀", ctx.me)
                    except:
                        pass
                    try:
                        await message.remove_reaction("▶", ctx.me)
                    except:
                        pass
                    break
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
        data = r.table("selfroles").get(str(server.id)).run(self.db, durability="soft")
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
			
    def _create_role(self, server, role):
        r.table("selfroles").get(str(server.id)).update({"roles": r.row["roles"].append(str(role.id))}).run(self.db, durability="soft")
			
    def _list(self, server, page):   
        msg = []
        data = r.table("selfroles").get(str(server.id)).run(self.db, durability="soft")
        for roleid in list(data["roles"])[page*20-20:page*20]:
            role = discord.utils.get(server.roles, id=int(roleid))
            if role:
                msg.append(role)
        msg = "\n".join(map(lambda x: x.name, (sorted(msg, key=server.roles.index))[::-1]))
        return msg
		 
    async def on_server_role_delete(self, role):
        server = role.guild
        data = r.table("selfroles").get(str(server.id))
        if str(role.id) in data["roles"].run(self.db, durability="soft"):
            data.update({"roles": r.row["roles"].difference([str(role.id)])}).run(self.db, durability="soft", noreply=True)

    async def on_raw_message_delete(self, payload):
        server = self.bot.get_guild(payload.guild_id)
        serverdata = r.table("reactionrole").get(str(server.id))
        if str(payload.message_id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            serverdata.update({"messages": r.row["messages"].filter(lambda x: x["id"] != str(payload.message_id))}).run(self.db, durability="soft", noreply=True)
            

    async def on_raw_reaction_add(self, payload):
        server = self.bot.get_guild(payload.guild_id)
        channel = server.get_channel(payload.channel_id)
        user = server.get_member(payload.user_id)
        if user.bot:
            return
        message = await channel.get_message(payload.message_id)
        serverdata = r.table("reactionrole").get(str(server.id))
        if str(message.id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message.id))[0]
            roles = message_db["roles"].map(lambda x: x["id"]).run(self.db)
            if payload.emoji.is_unicode_emoji():
                if str(payload.emoji) in message_db["roles"].map(lambda x: x["emote"]).run(self.db):
                    role = server.get_role(int(message_db["roles"].filter(lambda x: x["emote"] == str(payload.emoji))[0]["id"].run(self.db)))
                    if role in user.roles:
                        try:
                            await user.remove_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed taking the role away from you make sure I have the `manage_roles` and that my role is above the one I'm trying to take away from you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You no longer have the role **{}**".format(role.name))
                    else:
                        if "max_roles" in message_db.run(self.db):
                            max_roles = message_db["max_roles"].run(self.db)
                            if max_roles:
                                if len(list(filter(lambda x: x in list(map(lambda x: str(x.id), user.roles)), roles))) >= max_roles:
                                    return await user.send("You already have **{}** role{} from this reaction role menu, that is the maximum you can have from this specific reaction role menu :no_entry:".format(max_roles, "" if max_roles == 1 else "s"))
                        try:
                            await user.add_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed giving you the role make sure I have the `manage_roles` and that my role is above the one I'm trying to give you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You now have the role **{}**".format(role.name))
            else:
                if str(payload.emoji.id) in message_db["roles"].map(lambda x: x["emote"]).run(self.db):
                    role = server.get_role(int(message_db["roles"].filter(lambda x: x["emote"] == str(payload.emoji.id))[0]["id"].run(self.db)))
                    if role in user.roles:
                        try:
                            await user.remove_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed taking the role away from you make sure I have the `manage_roles` and that my role is above the one I'm trying to take away from you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You no longer have the role **{}**".format(role.name))
                    else:
                        if "max_roles" in message_db.run(self.db):
                            max_roles = message_db["max_roles"].run(self.db)
                            if max_roles:
                                if len(list(filter(lambda x: x in list(map(lambda x: str(x.id), user.roles)), roles))) >= max_roles:
                                    return await user.send("You already have **{}** role{} from this reaction role menu, that is the maximum you can have from this specific reaction role menu :no_entry:".format(max_roles, "" if max_roles == 1 else "s"))
                        try:
                            await user.add_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed giving you the role make sure I have the `manage_roles` and that my role is above the one I'm trying to give you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You now have the role **{}**".format(role.name))

    async def on_raw_reaction_remove(self, payload):
        server = self.bot.get_guild(payload.guild_id)
        channel = server.get_channel(payload.channel_id)
        user = server.get_member(payload.user_id)
        if user.bot:
            return
        message = await channel.get_message(payload.message_id)
        serverdata = r.table("reactionrole").get(str(server.id))
        if str(message.id) in serverdata["messages"].map(lambda x: x["id"]).run(self.db):
            message_db = serverdata["messages"].filter(lambda x: x["id"] == str(message.id))[0]
            roles = message_db["roles"].map(lambda x: x["id"]).run(self.db)
            if payload.emoji.is_unicode_emoji():
                if str(payload.emoji) in message_db["roles"].map(lambda x: x["emote"]).run(self.db):
                    role = server.get_role(int(message_db["roles"].filter(lambda x: x["emote"] == str(payload.emoji))[0]["id"].run(self.db)))
                    if role in user.roles:
                        try:
                            await user.remove_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed taking the role away from you make sure I have the `manage_roles` and that my role is above the one I'm trying to take away from you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You no longer have the role **{}**".format(role.name))
                    else:
                        if "max_roles" in message_db.run(self.db):
                            max_roles = message_db["max_roles"].run(self.db)
                            if max_roles:
                                if len(list(filter(lambda x: x in list(map(lambda x: str(x.id), user.roles)), roles))) >= max_roles:
                                    return await user.send("You already have **{}** role{} from this reaction role menu, that is the maximum you can have from this specific reaction role menu :no_entry:".format(max_roles, "" if max_roles == 1 else "s"))
                        try:
                            await user.add_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed giving you the role make sure I have the `manage_roles` and that my role is above the one I'm trying to give you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You now have the role **{}**".format(role.name))
            else:
                if str(payload.emoji.id) in message_db["roles"].map(lambda x: x["emote"]).run(self.db):
                    role = server.get_role(int(message_db["roles"].filter(lambda x: x["emote"] == str(payload.emoji.id))[0]["id"].run(self.db)))
                    if role in user.roles:
                        try:
                            await user.remove_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed taking the role away from you make sure I have the `manage_roles` and that my role is above the one I'm trying to take away from you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You no longer have the role **{}**".format(role.name))
                    else:
                        if "max_roles" in message_db.run(self.db):
                            max_roles = message_db["max_roles"].run(self.db)
                            if max_roles:
                                if len(list(filter(lambda x: x in list(map(lambda x: str(x.id), user.roles)), roles))) >= max_roles:
                                    return await user.send("You already have **{}** role{} from this reaction role menu, that is the maximum you can have from this specific reaction role menu :no_entry:".format(max_roles, "" if max_roles == 1 else "s"))
                        try:
                            await user.add_roles(role, reason="Reaction role")
                        except discord.errors.Forbidden:
                            return await user.send("I failed giving you the role make sure I have the `manage_roles` and that my role is above the one I'm trying to give you :no_entry:")
                        if serverdata["dm"].run(self.db):
                            await user.send("You now have the role **{}**".format(role.name))

    def is_bot_menu(self, data, message):
        if "bot_menu" in data:
            return data["bot_menu"]
        else:
            if message.author == self.bot.user and message.embeds:
                return True
            else:
                return False


		
def setup(bot, connection):
    bot.add_cog(selfroles(bot, connection))