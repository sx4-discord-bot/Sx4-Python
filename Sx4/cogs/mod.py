import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
import datetime
from collections import deque, defaultdict
import os
import re
import logging
import asyncio
from threading import Timer
import random
import time
import discord
from discord.ext import commands
import math
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound
from utils.dataIO import fileIO


class Mod:
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/mod/autobotclean.json"
        self.settings = dataIO.load_json(self.file_path)
        self.JSON = "data/mod/warn.json"
        self.data = dataIO.load_json(self.JSON)
        self.file = "data/mod/mute.json"
        self.d = dataIO.load_json(self.file)
        self._logs_file = "data/mod/logs.json"
        self._logs = dataIO.load_json(self._logs_file)
        
    
    @commands.command(pass_context=True, aliases=["mm"])
    @checks.mod_or_permissions(move_members=True)
    async def massmove(self, ctx, from_channel: discord.Channel, to_channel: discord.Channel):
        """Mass move users from one channel to another"""
        author = ctx.message.author
        server = ctx.message.server
        i = 0
        if from_channel in [x for x in server.channels if x.type == discord.ChannelType.text] or to_channel in [x for x in server.channels if x.type == discord.ChannelType.text]:
            await self.bot.say("You can only use voice channels as arguments :no_entry:")
            return
        if len(from_channel.voice_members) == 0:
            await self.bot.say("There is no one in that voice channel :no_entry:")
            return
        for user in [x for x in from_channel.voice_members if x not in to_channel.voice_members]:
            await self.bot.move_member(user, to_channel)
            i = i + 1
        await self.bot.say("Moved **{}** members from `{}` to `{}`".format(i, from_channel.name, to_channel.name))
        
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(move_members=True)
    async def move(self, ctx, user: discord.Member, to_channel: discord.Channel=None):
        """Move a user to your channel or a chosen channel"""
        author = ctx.message.author
        server = ctx.message.server
        channel = to_channel
        if not to_channel:
            channel = author.voice_channel
            if channel is None:
                await self.bot.say("You are not in a voice channel :no_entry:")
                return
        if channel in [x for x in server.channels if x.type == discord.ChannelType.text]:
            await self.bot.say("You can only use voice channels as arguments :no_entry:")
            return
        if channel == user.voice_channel:
            await self.bot.say("They are already in that voice channel :no_entry:")
            return
        await self.bot.move_member(user, channel)
        await self.bot.say("Moved **{}** to `{}`".format(user, channel.name))
        
        
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_nicknames=True)
    async def rename(self, ctx, user: discord.Member, *, nickname=None): 
        """Rename a user"""
        author = ctx.message.author
        if not nickname:
            nickname = user.name
        try:
            await self.bot.change_nickname(user, nickname)
        except discord.errors.Forbidden:
            await self.bot.say("I'm not able to change that users name :no_entry:")
            return
        await self.bot.say("I have changed **{}'s** name to **{}** <:done:403285928233402378>:ok_hand:".format(user.name, nickname))
        
    @commands.command(pass_context=True, aliases=["c"])
    @checks.mod_or_permissions(manage_messages=True) 
    async def clear(self, ctx, user: discord.Member, amount: int=None):
        """Clear a users messages"""
        channel = ctx.message.channel
        server = ctx.message.server
        has_permissions = channel.permissions_for(server.me).manage_messages
        if not has_permissions:
            await self.bot.say("I do not have the `MANAGE_MESSAGES` permission**")
            return
        if amount is None:
            amount = 100
        elif amount > 100:
            amount = 100
        await self.bot.delete_message(ctx.message)
        try:
            deleted = await self.bot.purge_from(ctx.message.channel, limit=amount, before=ctx.message, check=lambda m: m.author == user)
        except discord.HTTPException:
            await self.bot.say("I cannot delete messages 14 days or older :no_entry:")
            return
        if len(deleted) == 1:
            msg = await self.bot.say("Deleted **{}** message from **{}** <:done:403285928233402378>:ok_hand:".format(len(deleted), user))
        else:
            msg = await self.bot.say("Deleted **{}** messages from **{}** <:done:403285928233402378>:ok_hand:".format(len(deleted), user))
        await asyncio.sleep(3)
        try:
            await self.bot.delete_message(msg) 
        except discord.HTTPException:
            pass
        
    @commands.command(pass_context=True, aliases=["bc"])
    @checks.mod_or_permissions(manage_messages=True)
    async def botclean(self, ctx, limit: int=None):
        """Clears all bot messages"""
        channel = ctx.message.channel
        server = ctx.message.server
        has_permissions = channel.permissions_for(server.me).manage_messages
        if not has_permissions:
            await self.bot.say("I do not have the `MANAGE_MESSAGES` permission**")
            return
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        await self.bot.delete_message(ctx.message)
        try:
            deleted = await self.bot.purge_from(ctx.message.channel, limit=limit, before=ctx.message, check= lambda e: e.author.bot)
        except discord.HTTPException:
            await self.bot.say("I cannot delete messages 14 days or older :no_entry:")
            return
        if len(deleted) == 1:
            msg = await self.bot.say("*Deleted **{}** bot message <:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        else:
            msg = await self.bot.say("*Deleted **{}** bot messages* *<:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        await asyncio.sleep(3)
        try:
            await self.bot.delete_message(msg) 
        except discord.HTTPException:
            pass
        
    @commands.command(pass_context=True, aliases=["prune"])
    @checks.mod_or_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int=None):
        """Purges a certain amount of messages"""
        channel = ctx.message.channel
        server = ctx.message.server
        has_permissions = channel.permissions_for(server.me).manage_messages
        if not has_permissions:
            await self.bot.say("I do not have the `MANAGE_MESSAGES` permission**")
            return
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        await self.bot.delete_message(ctx.message)
        try:
            deleted = await self.bot.purge_from(ctx.message.channel, limit=limit, before=ctx.message)
        except discord.HTTPException:
            await self.bot.say("I cannot delete messages 14 days or older :no_entry:")
            return
        if len(deleted) == 1:
            msg = await self.bot.say("*Deleted **{}** message <:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        else:
            msg = await self.bot.say("*Deleted **{}** messages* *<:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        await asyncio.sleep(3)
        try:
            await self.bot.delete_message(msg) 
        except discord.HTTPException:
            pass
            
    @commands.group(pass_context=True)
    async def modlog(self, ctx):
        """Have logs for all mod actions"""
        server = ctx.message.server
        if server.id not in self._logs:
            self._logs[server.id] = {}
            dataIO.save_json(self._logs_file, self._logs)
        if "channel" not in self._logs[server.id]:
            self._logs[server.id]["channel"] = None
            dataIO.save_json(self._logs_file, self._logs)
        if "toggle" not in self._logs[server.id]:
            self._logs[server.id]["toggle"] = False
            dataIO.save_json(self._logs_file, self._logs)
        if "case#" not in self._logs[server.id]:
            self._logs[server.id]["case#"] = 0
            dataIO.save_json(self._logs_file, self._logs)
        if "case" not in self._logs[server.id]:
            self._logs[server.id]["case"] = {}
            dataIO.save_json(self._logs_file, self._logs)
        
            
    @modlog.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """Toggle modlogs on or off"""
        server = ctx.message.server
        if self._logs[server.id]["toggle"] == True:
            self._logs[server.id]["toggle"] = False
            dataIO.save_json(self._logs_file, self._logs)
            await self.bot.say("Modlogs are now disabled.")
            return
        if self._logs[server.id]["toggle"] == False:
            self._logs[server.id]["toggle"] = True
            dataIO.save_json(self._logs_file, self._logs)
            await self.bot.say("Modlogs are now enabled.")
            return
            
    @modlog.command(pass_context=True) 
    @checks.admin_or_permissions(manage_roles=True)
    async def channel(self, ctx, channel: discord.Channel):
        """Set the channel where you want modlogs to be posted"""
        server = ctx.message.server
        self._logs[server.id]["channel"] = channel.id
        dataIO.save_json(self._logs_file, self._logs)    
        await self.bot.say("<#{}> has been set as the modlog channel".format(channel.id))
        
    @modlog.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def case(self, ctx, case_number, *, reason):
        """Edit a modlog case"""
        author = ctx.message.author
        server = ctx.message.server 
        if self._logs[server.id]["case"][case_number]["mod"] is not None and self._logs[server.id]["case"][case_number]["mod"] != author.id:
            await self.bot.say("You do not have ownership of that log :no_entry:")
            return
        try:
            channel = self.bot.get_channel(self._logs[server.id]["channel"])
        except:
            await self.bot.say("The modlog channel no longer exists :no_entry:")
            return
        try:
            message = await self.bot.get_message(channel, self._logs[server.id]["case"][case_number]["message"])
        except:
            await self.bot.say("I am unable to find that case :no_entry:")
            return
        s=discord.Embed(title="Case {} | {}".format(case_number, self._logs[server.id]["case"][case_number]["action"]))
        s.add_field(name="User", value=await self.bot.get_user_info(self._logs[server.id]["case"][case_number]["user"]))
        s.add_field(name="Moderator", value=author, inline=False)
        self._logs[server.id]["case"][case_number]["mod"] = author.id
        s.add_field(name="Reason", value=reason)
        self._logs[server.id]["case"][case_number]["reason"] = reason
        dataIO.save_json(self._logs_file, self._logs)      
        try:
            await self.bot.edit_message(message, embed=s)
            await self.bot.say("Case #{} has been updated <:done:403285928233402378>".format(case_number))
        except: 
            await self.bot.say("I am unable to edit that case or it doesn't exist :no_entry:")
            
    @modlog.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def viewcase(self, ctx, case_number):
        """Someone delete their modlog case in your modlog channel, i store all of them so use this command to see the deleted case"""
        server = ctx.message.server
        if self._logs[server.id]["case"][case_number]["reason"] is None:
            reason = "None (Update using `s?modlog case {} <reason>`)".format(case_number)
        else:
            reason = self._logs[server.id]["case"][case_number]["reason"]
        if self._logs[server.id]["case"][case_number]["mod"] is None:
            author = "Unknown"
        else:
            author = await self.bot.get_user_info(self._logs[server.id]["case"][case_number]["mod"])
        s=discord.Embed(title="Case {} | {}".format(case_number, self._logs[server.id]["case"][case_number]["action"]))
        s.add_field(name="User", value=await self.bot.get_user_info(self._logs[server.id]["case"][case_number]["user"]))     
        s.add_field(name="Moderator", value=author, inline=False)
        s.add_field(name="Reason", value=reason)
        await self.bot.say(embed=s)
            
    @modlog.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def resetcases(self, ctx):
        """Reset all the cases in the modlog"""
        server = ctx.message.server
        self._logs[server.id]["case#"] = 0
        del self._logs[server.id]["case"]
        dataIO.save_json(self._logs_file, self._logs)    
        await self.bot.say("All cases have been reset <:done:403285928233402378>")
        
    async def _log(self, author, server, action, reason, user):
        if "case" not in self._logs[server.id]:
            self._logs[server.id]["case"] = {}
            dataIO.save_json(self._logs_file, self._logs)
        channel = self.bot.get_channel(self._logs[server.id]["channel"])
        if self._logs[server.id]["toggle"] == True and channel is not None:
            self._logs[server.id]["case#"] += 1 
            number = str(self._logs[server.id]["case#"])
            if number not in self._logs[server.id]["case"]:
                self._logs[server.id]["case"][number] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if "action" not in self._logs[server.id]["case"][number]:
                self._logs[server.id]["case"][number]["action"] = action
                dataIO.save_json(self._logs_file, self._logs)
            if "user" not in self._logs[server.id]["case"][number]:
                self._logs[server.id]["case"][number]["user"] = user.id
                dataIO.save_json(self._logs_file, self._logs)   
            if "mod" not in self._logs[server.id]["case"][number]:
                self._logs[server.id]["case"][number]["mod"] = author.id
                dataIO.save_json(self._logs_file, self._logs)   
            if "reason" not in self._logs[server.id]["case"][number]:
                self._logs[server.id]["case"][number]["reason"] = {}
                dataIO.save_json(self._logs_file, self._logs)                     
            if not reason: 
                reason = "None (Update using `s?modlog case {} <reason>`)".format(number)
                self._logs[server.id]["case"][number]["reason"] = None
            else:
                self._logs[server.id]["case"][number]["reason"] = reason
            s=discord.Embed(title="Case {} | {}".format(number, action))
            s.add_field(name="User", value=user)
            s.add_field(name="Moderator", value=author, inline=False)
            s.add_field(name="Reason", value=reason)
            message = await self.bot.send_message(self.bot.get_channel(self._logs[server.id]["channel"]), embed=s)
            if "message" not in self._logs[server.id]["case"][number]:
                self._logs[server.id]["case"][number]["message"] = message.id
                dataIO.save_json(self._logs_file, self._logs)    
        
    @commands.command(pass_context=True, aliases=["cr"])
    @checks.admin_or_permissions(manage_roles=True)
    async def createrole(self, ctx, rolename, colour_hex: discord.Colour=None):
        """Create a role in the server"""
        if not ctx.message.channel.permissions_for(ctx.message.server.me).manage_roles:
            await self.bot.say("I need the `MANGE_ROLES` Permission :no_entry:")
            return
        try:
            await self.bot.create_role(ctx.message.server, name=rolename, colour=colour_hex)
            await self.bot.say("I have created the role **{}** <:done:403285928233402378>:ok_hand:".format(rolename)) 
        except:
            await self.bot.say("I was not able to create the role :no_entry:")
            
    @commands.command(pass_context=True, aliases=["dr"])
    @checks.admin_or_permissions(manage_roles=True)
    async def deleterole(self, ctx, *, role: discord.Role):
        """Delete a role in the server"""
        if not ctx.message.channel.permissions_for(ctx.message.server.me).manage_roles:
            await self.bot.say("I need the `MANGE_ROLES` Permission :no_entry:")
            return
        try:
            await self.bot.delete_role(ctx.message.server, role)
            await self.bot.say("I have deleted the role **{}** <:done:403285928233402378>:ok_hand:".format(role.name)) 
        except:
            await self.bot.say("I was not able to delete the role or the role doesn't exist :no_entry:")
        
    @commands.command(pass_context=True, aliases=["ar"]) 
    @checks.admin_or_permissions(manage_roles=True)
    async def addrole(self, ctx, role: discord.Role, user: discord.Member=None):
        """Add a role to a user"""
        author = ctx.message.author
        server = ctx.message.server
        if role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not add a role to a user higher than your own role :no_entry:")
                return
        if user is None:
            user = author
        if role in user.roles:
            await self.bot.say("The user already has that role :no_entry:")
            return
        try:
            await self.bot.add_roles(user, role)
            await self.bot.say("**{}** has been added to **{}** <:done:403285928233402378>:ok_hand:".format(role, user))
        except discord.errors.Forbidden:
            await self.bot.say("I'm not able to add the role to the user :no_entry:")
        
    @commands.command(pass_context=True, aliases=["rr"]) 
    @checks.admin_or_permissions(manage_roles=True)
    async def removerole(self, ctx, role: discord.Role, user: discord.Member=None):
        """Remove a role from a user"""
        author = ctx.message.author
        if role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not remove a role from a user higher than your own role :no_entry:")
                return
        if user is None:
            user = author
        if not role in user.roles:
            await self.bot.say("The user doesn't have that role :no_entry:")
            return
        try:
            await self.bot.remove_roles(user, role)
            await self.bot.say("**{}** has been removed from **{}** <:done:403285928233402378>:ok_hand:".format(role, user))
        except discord.errors.Forbidden:
            await self.bot.say("I'm not able to remove the role from the user :no_entry:")
            
    @commands.command(pass_context=True) 
    @checks.admin_or_permissions(ban_members=True)
    async def Ban(self, ctx, user: discord.Member):
        """This is a fake bean don't exp0se"""
        await self.bot.say("**{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
            
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):
        """Kicks a user."""
        author = ctx.message.author
        server = author.server
        channel = ctx.message.channel
        destination = user
        action = "Kick"
        can_ban = channel.permissions_for(server.me).kick_members
        if not can_ban:
            await self.bot.say("I need the `KICK_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await self.bot.say("I'm not going to kick myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await self.bot.say("Why would you want to kick yourself, just leave.")
            return
        if user.top_role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not kick someone higher than your own role :no_entry:")
                return
        try: 
            await self.bot.kick(user)
            await self.bot.say("**{}** has been kicked <:done:403285928233402378>:ok_hand:".format(user))
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await self.bot.say("I'm not able to kick that user :no_entry:")
            return
        try: 
            u=discord.Embed(title="You have been kicked from {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            u.add_field(name="Moderator", value="{} ({})".format(author, author.id), inline=False)
            u.set_thumbnail(url=server.icon_url)
            if not reason:
                u.add_field(name="Reason", value="No reason specified")
            else:
                u.add_field(name="Reason", value=reason)
            try:
                await self.bot.send_message(user, embed=u)
            except discord.errors.HTTPException:
                pass
        except Exception as e:
            print(e)
            
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = None):
        """Bans a user."""
        author = ctx.message.author
        server = author.server
        channel = ctx.message.channel
        action = "Ban"
        destination = user
        can_ban = channel.permissions_for(server.me).ban_members
        if not can_ban:
            await self.bot.say("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await self.bot.say("I'm not going to ban myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await self.bot.say("Why would you want to ban yourself, just leave.")
            return
        if user.top_role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not ban someone higher than your own role :no_entry:")
                return
        try: 
            await self.bot.ban(user)
            await self.bot.say("**{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await self.bot.say("I'm not able to ban that user :no_entry:")
            return
        try: 
            u=discord.Embed(title="You have been banned from {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            u.add_field(name="Moderator", value="{} ({})".format(author, author.id), inline=False)
            u.set_thumbnail(url=server.icon_url)
            if not reason:
                u.add_field(name="Reason", value="No reason specified")
            else:
                u.add_field(name="Reason", value=reason)
            try:
                await self.bot.send_message(user, embed=u)
            except discord.errors.HTTPException:
                pass
        except Exception as e:
            print(e)
            
    @commands.command(pass_context=True, no_pm=True) 
    @checks.admin_or_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str=None):
        """unbans a user by ID and will notify them about the unbanning in pm"""
        author = ctx.message.author 
        server = ctx.message.server
        channel = ctx.message.channel
        action = "Unban"
        user_id = str(user_id)
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await self.bot.say("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await self.bot.say("The ID specified does not exist :no_entry:")
            return
        can_ban = channel.permissions_for(server.me).ban_members
        if not can_ban:
            await self.bot.say("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        ban_list = await self.bot.get_bans(server)
        is_banned = discord.utils.get(ban_list, id=user_id)
        invite = await self.bot.create_invite(channel)
        s=discord.Embed(title="You have been unbanned from {}".format(server.name), description="Feel free to join back whenever.", colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
        s.set_thumbnail(url=server.icon_url)
        s.add_field(name="Moderator", value="{} ({})".format(author, author.id), inline=False)
        s.add_field(name="Invite", value=invite)
        if user == author:
            await self.bot.say("You can't unban yourself :no_entry:")
            return
        if user == self.bot.user:
            await self.bot.say("I'm not even banned ¯\_(ツ)_/¯")
            return
        if not is_banned:
            await self.bot.say("This user is not banned :no_entry:")
            return
        try:
            await self.bot.unban(server, user)
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await self.bot.say("I need the **Ban Members** permission to unban :no_entry:")
            return
        await self.bot.say("**{}** has been unbanned <:done:403285928233402378>:ok_hand:".format(user))
        try:
            await self.bot.send_message(user, embed=s)
        except:
            pass
            
    #async def on_member_ban(self, member):
        #action = "Ban"
        #author = None
        #user = member
        #server = member.server
        #reason = None
        #if not self.temp_cache.check(user, server, action):   
            #try:
                #await self._log(author, server, action, reason, user)
            #except:
                #pass
                
    #async def on_member_unban(self, server, member):
        #action = "Unban"
        #author = None
        #user = member
        #reason = None
        #if not self.temp_cache.check(user, server, action):   
            #try:
                #await self._log(author, server, action, reason, user)
            #except:
                #pass
            
    @commands.command(pass_context=True, no_pm=True, aliases=["hb"]) 
    @checks.mod_or_permissions(ban_members=True)
    async def hackban(self, ctx, user_id: int, *, reason: str=None):
        """Ban a user before they even join the server, make sure you provide a user id"""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        action = "Ban"
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await self.bot.say("The user was not found, check if the ID specified is correct :no_entry:")
            return
        except discord.errors.HTTPException:
            await self.bot.say("The ID specified does not exist :no_entry:")
            return
        ban_list = await self.bot.get_bans(server)
        is_banned = discord.utils.get(ban_list, id=user_id)
        can_ban = channel.permissions_for(server.me).ban_members
        if user in server.members:
            await self.bot.say("Use the ban command to ban people in the server :no_entry:")
            return
        if not can_ban:
            await self.bot.say("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await self.bot.say("I'm not going to ban myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await self.bot.say("Why would you want to ban yourself, just leave.")
            return
        if is_banned:
            await self.bot.say("That user is already banned :no_entry:")
        try:
            await self.bot.http.ban(user_id, server.id, 0)
        except:
            await self.bot.say("I'm not able to ban that user :no_entry:")
            return
        await self.bot.say("**{}** has been banned by ID <:done:403285928233402378>:ok_hand:".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def cmute(self, ctx, user: discord.Member, *, reason=None):
        """Mute someone in the channel"""
        server = ctx.message.server
        author = ctx.message.author
        channel = ctx.message.channel
        action = "Mute"
        if channel.permissions_for(user).administrator:
            await self.bot.say("That user has administrator perms, why would i even try :no_entry:")
            return
        if not channel.permissions_for(user).send_messages:
            await self.bot.say("{} is already muted :no_entry:".format(user))
            return
        if user.top_role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not mute someone higher than your own role :no_entry:")
                return
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        try:
            await self.bot.edit_channel_permissions(channel, user, overwrite)
            if server.id not in self.d:
                self.d[server.id] = {}
                dataIO.save_json(self.file, self.d)
            if "channel" not in self.d[server.id]:
                self.d[server.id]["channel"] = {}
                dataIO.save_json(self.file, self.d)
            if channel.id not in self.d[server.id]["channel"]:
                self.d[server.id]["channel"][channel.id] = {}
                dataIO.save_json(self.file, self.d)
            if "user" not in self.d[server.id]["channel"][channel.id]:
                self.d[server.id]["channel"][channel.id]["user"] = {}
                dataIO.save_json(self.file, self.d)
            if user.id not in self.d[server.id]["channel"][channel.id]["user"]:
                self.d[server.id]["channel"][channel.id]["user"][user.id] = {}
                dataIO.save_json(self.file, self.d)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have permissions to edit the current channel :no_entry:")
            return
        await self.bot.say("**{}** has been muted <:done:403285928233402378>".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        try:
            s=discord.Embed(title="You have been muted in {} :speak_no_evil:".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, author.id), inline=False)
            if reason:
                s.add_field(name="Reason", value=reason) 
            else:
                s.add_field(name="Reason", value="None")
            await self.bot.send_message(user, embed=s)
        except:
            pass
        
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def cunmute(self, ctx, user: discord.Member, *, reason: str=None):
        """Unmute a muted user in the current channel"""
        server = ctx.message.server
        author = ctx.message.author
        action = "Unmute"
        channel = ctx.message.channel
        if channel.permissions_for(user).send_messages:
            await self.bot.say("{} is not muted :no_entry:".format(user))
            return
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        try:
            await self.bot.edit_channel_permissions(channel, user, overwrite)
            del self.d[server.id]["channel"][channel.id]
            dataIO.save_json(self.file, self.d)
        except discord.errors.Forbidden:
            await self.bot.say("I do not have permissions to edit the current channel :no_entry:")
            return
        try:
            s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, author.id))
            await self.bot.send_message(user, embed=s)
        except:
            pass
        await self.bot.say("**{}** has been unmuted <:done:403285928233402378>".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass

    async def on_member_join(self, member):
        server = member.server
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        if self.d[server.id][member.id]["toggle"] == True:
            await self.bot.add_roles(member, role)
        for channelid in self.d[server.id]["channel"]:
            channel = discord.utils.get(server.channels, id=channelid)
            if member.id in self.d[server.id]["channel"][channelid]["user"]:
                await self.bot.edit_channel_permissions(channel, member, overwrite)
        
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, time_and_unit=None, *, reason: str=None):
        """Mute a user for a certain amount of time
        Example: s?mute @Shea#4444 20m (this will mute the user for 20 minutes)"""
        server = ctx.message.server
        channel = ctx.message.channel
        author = ctx.message.author
        action = "Mute"
        if author == user:
            await self.bot.say("You can't mute yourself :no_entry:")
            return
        if channel.permissions_for(user).administrator:
            await self.bot.say("That user has administrator perms, why would i even try :no_entry:")
            return
        if user.top_role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not mute someone higher than your own role :no_entry:")
                return
        if not time_and_unit: 
            time2 = 600
            time = "10"
            unit = "minutes"
        else:
            try:
                unit = time_and_unit[len(time_and_unit)-1:len(time_and_unit)]
            except:
                await self.bot.say("Invalid time unit :no_entry:")
                return
            try:
                time = time_and_unit[0:len(time_and_unit)-1]
            except ValueError:
                await self.bot.say("Invalid time unit :no_entry:")
                return
            if unit == "s":
                time2 = int(time)
                if time == 1:
                    unit = "second"
                else:
                    unit = "seconds"
            elif unit == "m":
                time2 = int(time) * 60
                if time == 1:
                    unit = "minute"
                else:
                    unit = "minutes"
            elif unit == "h":
                time2 = int(time) * 3600
                if time == 1:
                    unit = "hour"
                else:
                    unit = "hours"
            elif unit == "d":
                time2 = int(time) * 86400
                if time == 1:
                    unit = "day"
                else:
                    unit = "days"
            else:
                await self.bot.say("Invalid time unit :no_entry:")
                return
        if server.id not in self.d:
            self.d[server.id] = {}
            dataIO.save_json(self.file, self.d)
        if user.id not in self.d[server.id]:
            self.d[server.id][user.id] = {}
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[server.id][user.id]:
            self.d[server.id][user.id]["toggle"] = False
            dataIO.save_json(self.file, self.d)
        if "time" not in self.d[server.id][user.id]:
            self.d[server.id][user.id]["time"] = None
            dataIO.save_json(self.file, self.d)
        if "amount" not in self.d[server.id][user.id]:
            self.d[server.id][user.id]["amount"] = None
            dataIO.save_json(self.file, self.d)
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            role = await self.bot.create_role(server, name="Muted - Sx4")
            for channels in [x for x in server.channels if x.type == discord.ChannelType.text]:
                await self.bot.edit_channel_permissions(channels, role, overwrite)
            for channels in [x for x in server.channels if x.type == discord.ChannelType.voice]:
                await self.bot.edit_channel_permissions(channels, role, perms)
        if role in user.roles:
            await self.bot.say("**{}** is already muted :no_entry:".format(user))
            return
        try:
            await self.bot.add_roles(user, role)
        except: 
            await self.bot.say("I cannot add the mute role to the user :no_entry:")
            return
        await self.bot.say("**{}** has been muted for {} {} <:done:403285928233402378>".format(user, time, unit))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        self.d[server.id][user.id]["toggle"] = True
        self.d[server.id][user.id]["amount"] = time2
        self.d[server.id][user.id]["time"] = ctx.message.timestamp.timestamp()
        dataIO.save_json(self.file, self.d)
        try:
            s=discord.Embed(title="You have been muted in {} :speak_no_evil:".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, author.id), inline=False)
            s.add_field(name="Time", value="{} {}".format(time, unit), inline=False)
            await self.bot.send_message(user, embed=s)
        except:
            pass
        await asyncio.sleep(time2)
        if role in user.roles:
            try:
                await self.bot.remove_roles(user, role)
            except:
                pass
            try:
                action = "Unmute"
                author = self.bot.user
                reason = "Time limit served"
                await self._log(author, server, action, reason, user)
            except:
                pass
            self.d[server.id][user.id]["time"] = None
            self.d[server.id][user.id]["toggle"] = False
            dataIO.save_json(self.file, self.d)
            s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(self.bot.user, self.bot.user.id), inline=False)
            s.add_field(name="Reason", value="Time Served", inline=False)
            try:
                await self.bot.send_message(user, embed=s)
            except:
                pass
            
            
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unmute(self, ctx, user: discord.Member, *, reason: str=None):
        """Unmute a user who is muted"""
        server = ctx.message.server
        channel = ctx.message.channel
        author = ctx.message.author
        action = "Unmute"
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        if not role:
            await self.bot.say("No-one is muted in this server :no_entry:")
            return
        if role not in user.roles:
            await self.bot.say("**{}** is not muted :no_entry:".format(user))
            return
        try:
            await self.bot.remove_roles(user, role)
        except: 
            await self.bot.say("I cannot remove the mute role from the user :no_entry:")
            return
        await self.bot.say("**{}** has been unmuted <:done:403285928233402378>".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        self.d[server.id][user.id]["toggle"] = False
        self.d[server.id][user.id]["time"] = None
        dataIO.save_json(self.file, self.d)
        try:
            s=discord.Embed(title="You have been unmuted early in {}".format(server.name), colour=0xfff90d, timestamp=datetime.datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, author.id))
            await self.bot.send_message(user, embed=s)
        except:
            pass
            
            
    @commands.command(pass_context=True) 
    async def mutedlist(self, ctx):
        """Check who is muted in the server and for how long"""
        server = ctx.message.server
        msg = ""
        i = 0;
        for userid in self.d[server.id]:
            if self.d[server.id][userid]["toggle"] == True:
                i = i + 1
        if i == 0:   
            await self.bot.say("No one is muted in this server :no_entry:")
            return
        for userid in self.d[server.id]:
            if self.d[server.id][userid]["time"] == None or self.d[server.id][userid]["time"] - ctx.message.timestamp.timestamp() + self.d[server.id][userid]["amount"] <= 0:
                time = "Infinite" 
            else:
                m, s = divmod(self.d[server.id][userid]["time"] - ctx.message.timestamp.timestamp() + self.d[server.id][userid]["amount"], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                if d == 0:
                    time = "%d hours %d minutes %d seconds" % (h, m, s)
                if h == 0 and d == 0:
                    time = "%d minutes %d seconds" % (m, s)
                elif h == 0 and m == 0:
                    time = "%d seconds" % (s)
                else:
                    time = "%d days %d hours %d minutes %d seconds" % (d, h, m, s)
            if self.d[server.id][userid]["toggle"] == True:
                user = discord.utils.get(server.members, id=userid)
                if user:
                    msg += "{} - {} (Till mute ends)\n".format(user, time)
        if not msg:
            await self.bot.say("No one is muted in this server :no_entry:")
            return
        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=datetime.datetime.utcnow())
        s.set_author(name="Mute List for {}".format(server), icon_url=server.icon_url)
        await self.bot.say(embed=s)
            
    async def on_member_update(self, before, after):
        server = before.server
        user = after
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        if role in before.roles:
            if role not in after.roles:
                self.d[server.id][before.id]["toggle"] = False
                self.d[server.id][user.id]["time"] = None
                self.d[server.id][user.id]["amount"] = None
                dataIO.save_json(self.file, self.d)
                return
        if role in after.roles:
            if role not in before.roles:
                self.d[server.id][before.id]["toggle"] = True
                self.d[server.id][user.id]["time"] = None
                self.d[server.id][user.id]["amount"] = None
                dataIO.save_json(self.file, self.d)
                return
            
    async def on_channel_create(self, channel):
        server = channel.server
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            return
        if channel.type == discord.ChannelType.text:
            await self.bot.edit_channel_permissions(channel, role, overwrite)
        if channel.type == discord.ChannelType.voice:
            await self.bot.edit_channel_permissions(channel, role, perms)
        
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str=None):
        """Warns a user in pm, a reason is also optional."""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        if user == author:
            await self.bot.say("You can not warn yourself :no_entry:")
            return
        if user.top_role.position > author.top_role.position:
            if author == server.owner:
                pass
            else:
                await self.bot.say("You can not warn someone higher than your own role :no_entry:")
                return
        if server.id not in self.d:
            self.d[server.id] = {}
            dataIO.save_json(self.file, self.d)
        if user.id not in self.d[server.id]:
            self.d[server.id][user.id] = {}
            dataIO.save_json(self.file, self.d)
        if "muted" not in self.d[server.id][user.id]:
            self.d[server.id][user.id]["toggle"] = False
            dataIO.save_json(self.file, self.d)
        if "time" not in self.d[server.id][user.id]:
            self.d[server.id][user.id]["time"] = None
            dataIO.save_json(self.file, self.d)
        if "amount" not in self.d[server.id][user.id]:
            self.d[server.id][user.id]["amount"] = None
            dataIO.save_json(self.file, self.d)
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            role = await self.bot.create_role(server, name="Muted - Sx4")
            for channels in [x for x in server.channels if x.type == discord.ChannelType.text]:
                await self.bot.edit_channel_permissions(channels, role, overwrite)
            for channels in [x for x in server.channels if x.type == discord.ChannelType.voice]:
                await self.bot.edit_channel_permissions(channels, role, perms)
        await self._create_warn(server, user)
        if reason:
            if reason not in self.data[server.id]["user"][user.id]["reasons"]:
                self.data[server.id]["user"][user.id]["reasons"][reason] = {}
        self.data[server.id]["user"][user.id]["warnings"] = self.data[server.id]["user"][user.id]["warnings"] + 1
        dataIO.save_json(self.JSON, self.data)
        if self.data[server.id]["user"][user.id]["warnings"] == 1:
            await self.bot.say("**{}** has been warned :warning:".format(user))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been warned in {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Mute")
            action = "Warn"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if self.data[server.id]["user"][user.id]["warnings"] == 2:
            try:
                await self.bot.add_roles(user, role)
                self.d[server.id][user.id]["toggle"] = True
                self.d[server.id][user.id]["amount"] = 600
                self.d[server.id][user.id]["time"] = ctx.message.timestamp.timestamp()
                dataIO.save_json(self.file, self.d)
            except: 
                await self.bot.say("I cannot add the mute role to the user :no_entry:")
                return
            await self.bot.say("**{}** has been muted due to their second warning <:done:403285928233402378>".format(user))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been muted in {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Kick")
            action = "Mute"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
            await asyncio.sleep(600)
            if role in user.roles:
                try:
                    await self.bot.remove_roles(user, role)
                except:
                    pass
                self.d[server.id][user.id]["toggle"] = False
                dataIO.save_json(self.file, self.d)
                action = "Unmute"
                try:
                    await self._log(author, server, action, reason, user)
                except:
                    pass
        if self.data[server.id]["user"][user.id]["warnings"] == 3:
            try:
                await self.bot.kick(user)
            except:
                await self.bot.say("I'm not able to kick that user :no_entry:")
                return
            await self.bot.say("**{}** has been kicked due to their third warning <:done:403285928233402378>".format(user))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been kicked from {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Ban")
            action = "Kick"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if self.data[server.id]["user"][user.id]["warnings"] >= 4:
            try:
                await self.bot.ban(user)
            except:
                await self.bot.say("I'm not able to ban that user :no_entry:")
                del self.data[server.id]["user"][user.id]
                dataIO.save_json(self.JSON, self.data)
                return
            await self.bot.say("**{}** has been banned due to their forth warning <:done:403285928233402378>".format(user))
            await self.bot.ban(user)
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been banned from {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="None")
            del self.data[server.id]["user"][user.id]
            dataIO.save_json(self.JSON, self.data)
            action = "Ban"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        try:
            await self.bot.send_message(user, embed=s)
        except:
            pass
            
    @commands.command(pass_context=True)
    async def warnlist(self, ctx, page: int=None):
        """View everyone who has been warned and how many warning they're on"""
        server = ctx.message.server 
        if not page:
            page = 1
        if page < 0:
            await self.bot.say("Invalid page :no_entry:")
            return
        if page > math.ceil(len(self.data[server.id]["user"])/20):
            await self.bot.say("Invalid page :no_entry:")
            return
        s = await self._list_warns(server, page)
        try:
            await self.bot.say(embed=s)
        except:
            await self.bot.say("There are no users with warnings in this server :no_entry:")
        
    @commands.command(pass_context=True)
    async def warnings(self, ctx, user: discord.Member): 
        """Check how many warnings a specific user is on"""
        server = ctx.message.server
        try:
            if self.data[server.id]["user"][user.id]["warnings"] == 1:
                action = "Mute"
            if self.data[server.id]["user"][user.id]["warnings"] == 2:
                action = "Kick"
            if self.data[server.id]["user"][user.id]["warnings"] >= 3:
                action = "Ban"
            if not self.data[server.id]["user"][user.id]["reasons"]:
                reasons = "None"
            else:
                reasons = ", ".join([x for x in self.data[server.id]["user"][user.id]["reasons"]])
            if self.data[server.id]["user"][user.id]["warnings"] == 1:
                await self.bot.say("**{}** is on **1** warning\nNext Action: **Mute**\nReasons: **{}**".format(user, reasons))
            else:
                try:
                    await self.bot.say("**{}** is on **{}** warnings\nNext Action: **{}**\nReasons: **{}**".format(user, self.data[server.id]["user"][user.id]["warnings"], action, reasons))
                except:
                    await self.bot.say("That user has no warnings")
        except:
            await self.bot.say("That user has no warnings")
                
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def setwarns(self, ctx, user: discord.Member, warnings: int=None):
        """Set the warn amount for a specific user"""
        server = ctx.message.server
        await self._create_warn(server, user)
        dataIO.save_json(self.JSON, self.data)
        if not warnings:  
            del self.data[server.id]["user"][user.id]
            dataIO.save_json(self.JSON, self.data)
            await self.bot.say("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings == 0:
            del self.data[server.id]["user"][user.id]
            dataIO.save_json(self.JSON, self.data)
            await self.bot.say("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings <= 0:
            await self.bot.say("You can set warnings to 1-4 only :no_entry:")
            return
        if warnings >= 5:
            await self.bot.say("You can set warnings to 1-4 only :no_entry:") 
            return
        self.data[server.id]["user"][user.id]["warnings"] = warnings    
        dataIO.save_json(self.JSON, self.data)
        await self.bot.say("**{}'s** warnings have been set to **{}**".format(user.name, warnings))  

    async def on_ready(self):
        for serverid in list(self.d)[:len(self.d)]:
            server = self.bot.get_server(serverid)
            if server != None:
                role = discord.utils.get(server.roles, name="Muted - Sx4")
                if self.d[server.id] != None:
                    for userid in self.d[serverid]:
                        user = discord.utils.get(server.members, id=userid)
                        if user != None:
                            if self.d[server.id][user.id]["toggle"] != False and self.d[server.id][user.id]["time"] != None and self.d[server.id][user.id]["amount"] != None:
                                time2 = self.d[server.id][user.id]["time"] - datetime.datetime.now().timestamp() + self.d[server.id][user.id]["amount"]
                                if time2 <= 0:
                                    await self.bot.remove_roles(user, role)
                                    self.d[server.id][user.id]["time"] = None
                                    self.d[server.id][user.id]["toggle"] = False
                                    dataIO.save_json(self.file, self.d)
                                    s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=datetime.datetime.now())
                                    s.add_field(name="Moderator", value="{} ({})".format(self.bot.user, self.bot.user.id), inline=False)
                                    s.add_field(name="Reason", value="Time Served", inline=False)
                                    try:
                                        await self.bot.send_message(user, embed=s)
                                    except:
                                        pass
                                    action = "Unmute"
                                    author = self.bot.user
                                    reason = "Time limit served"
                                    try:
                                        await self._log(author, server, action, reason, user)
                                    except:
                                        pass
                                else:
                                    await asyncio.sleep(round(time2))
                                    await self.bot.remove_roles(user, role)
                                    self.d[server.id][user.id]["time"] = None
                                    self.d[server.id][user.id]["toggle"] = False
                                    dataIO.save_json(self.file, self.d)
                                    s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=datetime.datetime.now())
                                    s.add_field(name="Moderator", value="{} ({})".format(self.bot.user, self.bot.user.id), inline=False)
                                    s.add_field(name="Reason", value="Time Served", inline=False)
                                    try:
                                        await self.bot.send_message(user, embed=s)
                                    except:
                                        pass
                                    action = "Unmute"
                                    author = self.bot.user
                                    reason = "Time limit served"
                                    try:
                                        await self._log(author, server, action, reason, user)
                                    except:
                                        pass
      
                    
        
    async def _create_warn(self, server, user):
        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.JSON, self.data)
        if "user" not in self.data[server.id]:
            self.data[server.id]["user"] = {}
            dataIO.save_json(self.JSON, self.data)
        if user.id not in self.data[server.id]["user"]:
            self.data[server.id]["user"][user.id] = {}
            dataIO.save_json(self.JSON, self.data)
        if "warnings" not in self.data[server.id]["user"][user.id]:
            self.data[server.id]["user"][user.id]["warnings"] = 0
            dataIO.save_json(self.JSON, self.data)
        if "reasons" not in self.data[server.id]["user"][user.id]:
            self.data[server.id]["user"][user.id]["reasons"] = {}
            dataIO.save_json(self.JSON, self.data)
            
    async def _list_warns(self, server, page):
        msg = ""
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        sortedwarn = sorted(self.data[server.id]["user"].items(), key=lambda x: x[1]["warnings"], reverse=True)[page*20-20:page*20]
        for x in sortedwarn:
            users = discord.utils.get(server.members, id=x[0])
            if users and self.data[server.id]["user"][x[0]]["warnings"] != 0:
                msg += "\n`{}`: Warning **#{}**".format(users, self.data[server.id]["user"][x[0]]["warnings"])
        s.add_field(name="Users on Warnings", value=msg)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(self.data[server.id]["user"])/20)))
        return s
    
def check_folders():
    if not os.path.exists("data/mod"):
        print("Creating data/mod folder...")
        os.makedirs("data/mod")


def check_files():
    s = "data/mod/autorole.json"
    if not dataIO.is_valid_json(s):
        print("Creating default mod's autorole.json...")
        dataIO.save_json(s, {})
    f = "data/mod/warn.json"
    if not dataIO.is_valid_json(f):
        print("Creating default mod's warn.json...")
        dataIO.save_json(f, {}) 
    f = "data/mod/mute.json"
    if not dataIO.is_valid_json(f):
        print("Creating default mod's mute.json...")
        dataIO.save_json(f, {})
    f = "data/mod/logs.json"
    if not dataIO.is_valid_json(f):
        print("Creating default mod's logs.json...")
        dataIO.save_json(f, {})
        
def setup(bot): 
    check_folders()
    check_files()
    bot.add_cog(Mod(bot))