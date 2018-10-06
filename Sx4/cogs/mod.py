import discord
from discord.ext import commands
import rethinkdb as r
from utils import checks
import datetime
from collections import deque, defaultdict
import os
import re
import requests
import logging
from utils import arg
from utils import arghelp
import asyncio
from urllib.request import Request, urlopen
import json
from threading import Timer
import random
import time
import discord
from discord.ext import commands
import math
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound

class mod:
    def __init__(self, bot):
        self.bot = bot
        self._task = bot.loop.create_task(self.check_mute())

    def __unload(self):
        self._task.cancel()
		
    @commands.command()
    @checks.has_permissions("manage_channels")
    async def slowmode(self, ctx, time_interval):
        """Set the slowmode for the current channnel"""
        if time_interval.lower() in ["off", "none"]:
            time_interval = 0
        else:
            try:
                time_interval = int(time_interval)
            except:
                return await ctx.send("Invalid time interval :no_entry:")
        if int(time_interval) > 120:
            time_interval = 120
        channel = ctx.channel
        client = self.bot.http
        r = discord.http.Route('PATCH', '/channels/{channel_id}', channel_id=channel.id)
        request = client.request(r, json={"rate_limit_per_user": time_interval})
        await request
        if time_interval != 0:
            await ctx.send("Set the current channels slowmode to **{} {}** <:done:403285928233402378>".format(time_interval, "second" if time_interval == 1 else "seconds"))
        else:
            await ctx.send("Slowmode has been turned off in the current channel <:done:403285928233402378>")

    @commands.command()
    @checks.has_permissions("manage_guild")
    async def lockdown(self, ctx, *, channel: discord.TextChannel=None):
        """Locks down a channel so no one can speak in it at the current time using the command again will unlock it"""
        if not channel:
            channel = ctx.channel
        try:
            if channel.overwrites_for(ctx.guild.default_role).send_messages == True or channel.overwrites_for(ctx.guild.default_role).send_messages == None:
                overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                return await ctx.send("{} has been locked down <:done:403285928233402378>".format(channel.mention))
            else:
                overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                return await ctx.send("{} is no longer locked down <:done:403285928233402378>".format(channel.mention))
        except:
            await ctx.send("I'm unable to edit the channel permissions :no_entry:")

    @commands.command()
    @checks.has_permissions("manage_guild")
    async def region(self, ctx, *, region: str):
        """change the server region"""
        region = region.replace(" ", "_").lower()
        if hasattr(discord.VoiceRegion, region):
            try:
                if ctx.guild.region == region:
                    return await ctx.send("The voice region is already set to that :no_entry:")
                await ctx.guild.edit(region=getattr(discord.VoiceRegion, region, None))
                await ctx.send("Succesfully changed the voice region to **{}** <:done:403285928233402378>".format(region.replace("_", " ").title()))
            except:
                return await ctx.send("I was unable to change the voice region :no_entry:")
        else:
            await ctx.send("Not a valid voice region :no_entry:")

    @commands.command(aliases=["colorrole"])
    @checks.has_permissions("manage_roles")
    async def colourrole(self, ctx, role: discord.Role, colour: discord.Colour):
        try:
            await role.edit(colour=colour)
        except:
            return await ctx.send("I'm not able to edit that role :no_entry:")
        await ctx.send("**{}** now has the hex `{}` <:done:403285928233402378>".format(role.name, colour))

    @commands.group()
    async def prefix(self, ctx):
        "Set a prefix for your server or yourself, your personal prefix(es) will overwrite server ones"
        if ctx.invoked_subcommand is None:
            serverdata = r.table("prefix").get(str(ctx.guild.id))
            authordata = r.table("prefix").get(str(ctx.author.id))
            s=discord.Embed(colour=ctx.author.colour)
            s.set_author(name="Prefix Settings", icon_url=ctx.author.avatar_url)
            s.add_field(name="Default Prefixes", value="{}".format(", ".join(['sx4 ', 's?', 'S?', '<@440996323156819968> '])), inline=False)
            try:
                s.add_field(name="Server Prefixes", value="{}".format(", ".join(serverdata["prefixes"].run() if serverdata["prefixes"].run() else "None")), inline=False)
            except:
                s.add_field(name="Server Prefixes", value="None", inline=False)
            try:
                s.add_field(name="{}'s Prefixes".format(ctx.author.name), value="{}".format(", ".join(authordata["prefixes"].run() if authordata["prefixes"].run() else "None")), inline=False)
            except:
                s.add_field(name="{}'s Prefixes".format(ctx.author.name), value="None", inline=False)
            await ctx.send(embed=s, content="For help on setting the prefix use `{}help prefix`".format(ctx.prefix))
        else:
            r.table("prefix").insert({"id": str(ctx.author.id), "prefixes": []}).run()
            r.table("prefix").insert({"id": str(ctx.guild.id), "prefixes": []}).run()

    @prefix.command()
    async def self(self, ctx, *prefixes):
        "Set a prefix or multiple for yourself on the bot"
        prefixes = [x for x in prefixes if x != ""]
        authordata = r.table("prefix").get(str(ctx.author.id))
        if len(prefixes) == 0:
            authordata.update({"prefixes": []}).run()
            await ctx.send("Your prefixes have been reset <:done:403285928233402378>")
        else:
            authordata.update({"prefixes": prefixes}).run()
            if len(prefixes) > 1:
                await ctx.send("Your prefixes have been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
            else:
                await ctx.send("Your prefix has been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))

    @prefix.command()
    @checks.has_permissions("manage_guild")
    async def server(self, ctx, *prefixes):
        """Set a prefix for the server you're in"""
        prefixes = [x for x in prefixes if x != ""]
        serverdata = r.table("prefix").get(str(ctx.guild.id))
        if len(prefixes) == 0:
            serverdata.update({"prefixes": []}).run()
            await ctx.send("The server prefixes have been reset <:done:403285928233402378>")
        else:
            serverdata.update({"prefixes": prefixes}).run()
            if len(prefixes) > 1:
                await ctx.send("The server prefixes have been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
            else:
                await ctx.send("The server prefix has been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))


    @commands.command()
    async def checkbans(self, ctx, *, user_arg: str=None):
        author = ctx.message.author
        server = ctx.guild
        if not user_arg:
            user = author
        else:
            if "<" in user_arg and "@" in user_arg:
                user = user_arg.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
                user = discord.utils.get(self.bot.get_all_members(), id=int(user))
            elif "#" in user_arg:
                number = len([x for x in user_arg if "#" not in x])
                usernum = number - 4
                user = discord.utils.get(self.bot.get_all_members(), name=user_arg[:usernum], discriminator=user_arg[usernum + 1:len(user_arg)])
            else:
                try:
                    user = discord.utils.get(self.bot.get_all_members(), id=int(user_arg))
                    if not user:
                        user = await self.bot.get_user_info(int(user_arg))
                except:
                    user = discord.utils.get(self.bot.get_all_members(), name=user_arg)
            if not user:
                await ctx.send("I could not find that user :no_entry:")
                return
        #url = "https://bans.discordlist.net/api"
        urlds = "https://discord.services/api/ban/{}".format(user.id)
        headers = {"token" : "H5sqJpBmow", "userid" : str(user.id), 'User-Agent' : 'Mozilla/5.0'}
        #request = requests.post(url, data=headers)
        requestds = requests.get(urlds, headers={'User-Agent': 'Mozilla/5.0'}).json()
        description = ""
        #if request.text == True:
            #description += "**{}** is banned on [DiscordList](https://bans.discordlist.net/)\n\n".format(user)
        try:
            requestds["msg"]
        except:
            description += "**{}** is banned on [Discord Services](https://discord.services/bans) for [{}]({})".format(user, requestds["ban"]["reason"], requestds["ban"]["proof"])
        if description == "":
            description = "There were no bans found for **{}**".format(user)
        await ctx.send(embed=discord.Embed(description=description))

		
    @commands.command()
    @checks.has_permissions("manage_roles", "mention_everyone")
    async def announce(self, ctx, role: discord.Role, *, text: str):
        """Send an announcement in the channel you want by using the command in the channel you want choose a role you want to use and some text and the rest the bot will do"""
        if role.name == "@everyone" and ctx.channel.permissions_for(ctx.author).mention_everyone == False:
            await ctx.send("You do not have the permissions to mention everyone so you can not use announce to do it :no_entry:")
        try:
            await ctx.message.delete()
        except: 
            pass
        try:
            await role.edit(mentionable=True)
        except:
            await ctx.send("I'm not able to edit that role :no_entry:") 
            return
        await ctx.send(role.mention + ", " + text + " - " + str(ctx.message.author))
        await role.edit(mentionable=False)
    
    @commands.command(aliases=["mm"])
    @checks.has_permissions("move_members")
    async def massmove(self, ctx, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
        """Mass move users from one channel to another"""
        author = ctx.author
        server = ctx.guild
        i = 0
        if len(from_channel.members) == 0:
            await ctx.send("There is no one in that voice channel :no_entry:")
            return
        for user in [x for x in from_channel.members if x not in to_channel.members]:
            await user.edit(voice_channel=to_channel, reason="Massmove") 
            i = i + 1
        await ctx.send("Moved **{}** members from `{}` to `{}`".format(i, from_channel.name, to_channel.name))
        
    @commands.command()
    @checks.has_permissions("move_members")
    async def move(self, ctx, user: discord.Member, to_channel: discord.VoiceChannel=None):
        """Move a user to your channel or a chosen channel"""
        author = ctx.author
        server = ctx.guild
        channel = to_channel
        if not to_channel:
            channel = author.voice.channel
            if channel is None:
                await ctx.send("You are not in a voice channel :no_entry:")
                return
        if not user.voice.channel:
            await ctx.send("That user isn't in a voice channel :no_entry:")
            return
        if channel == user.voice.channel:
            await ctx.send("They are already in that voice channel :no_entry:")
            return
        await user.edit(voice_channel=channel)
        await ctx.send("Moved **{}** to `{}`".format(user, channel.name))
        
        
    @commands.command()
    @checks.has_permissions("manage_nicknames")
    async def rename(self, ctx, user: discord.Member, *, nickname=None): 
        """Rename a user"""
        author = ctx.message.author
        if not nickname:
            nickname = user.name
        try:
            await user.edit(nick=nickname)
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to change that users name :no_entry:")
            return
        await ctx.send("I have changed **{}'s** name to **{}** <:done:403285928233402378>:ok_hand:".format(user.name, nickname))
        
    @commands.command(aliases=["c"])
    @checks.has_permissions("manage_messages")
    async def clear(self, ctx, user: discord.Member, amount: int=None):
        """Clear a users messages"""
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `MANAGE_MESSAGES` permission")
            return
        if amount is None:
            amount = 100
        elif amount > 100:
            amount = 100
        await ctx.message.delete()
        try:
            deleted = await channel.purge(limit=amount, before=ctx.message, check=lambda m: m.author == user)
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        
    @commands.command(aliases=["bc"])
    @checks.has_permissions("manage_messages")
    async def botclean(self, ctx, limit: int=None):
        """Clears all bot messages"""
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `MANAGE_MESSAGES` permission")
            return
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        await ctx.message.delete()
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message, check=lambda e: e.author.bot)
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return

    @commands.command()
    @checks.has_permissions("manage_messages")
    async def contains(self, ctx, word: str, limit: int=None):
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `MANAGE_MESSAGES` permission")
            return
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        await ctx.message.delete()
        def check(m):
            return word.lower() in m.content.lower()
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message, check=check)
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        
    @commands.command(aliases=["prune"])
    @checks.has_permissions("manage_messages")
    async def purge(self, ctx, limit: int=None):
        """Purges a certain amount of messages"""
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `MANAGE_MESSAGES` permission")
            return
        if limit is None:
            limit = 10
        elif limit > 100:
            limit = 100
        await ctx.message.delete()
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message)
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
            
    @commands.group()
    async def modlog(self, ctx):
        """Have logs for all mod actions"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("modlogs").insert({"id": str(server.id), "channel": None, "toggle": False, "case#": 0, "case": []}).run()
        
            
    @modlog.command()
    @checks.has_permissions("manage_roles")
    async def toggle(self, ctx):
        """Toggle modlogs on or off"""
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        if serverdata["toggle"].run() == True:
            serverdata.update({"toggle": False}).run()
            await ctx.send("Modlogs are now disabled.")
            return
        if serverdata["toggle"].run() == False:
            serverdata.update({"toggle": True}).run()
            await ctx.send("Modlogs are now enabled.")
            return
            
    @modlog.command() 
    @checks.has_permissions("manage_roles")
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where you want modlogs to be posted"""
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        serverdata.update({"channel": str(channel.id)}).run() 
        await ctx.send("<#{}> has been set as the modlog channel".format(str(channel.id)))
        
    @modlog.command()
    @checks.has_permissions("manage_messages")
    async def case(self, ctx, case_number: int, *, reason):
        """Edit a modlog case"""
        author = ctx.author
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        case = serverdata["case"].filter({"id": case_number})[0]
        try:
            case.run()
        except:
            await ctx.send("Invalid case number :no_entry:")
            return
        if case["mod"].run() is not None and case["mod"].run() != str(author.id):
            await ctx.send("You do not have ownership of that log :no_entry:")
            return
        try:
            channel = self.bot.get_channel(int(serverdata["channel"].run()))
        except:
            await ctx.send("The modlog channel no longer exists :no_entry:")
            return
        try:
            message = await channel.get_message(int(case["message"].run()))
        except:
            await ctx.send("I am unable to find that case :no_entry:")
            return
        try:
            s=discord.Embed(title="Case {} | {}".format(case_number, case["action"].run()), timestamp=datetime.datetime.fromtimestamp(case["time"].run()))
        except:
            s=discord.Embed(title="Case {} | {}".format(case_number, case["action"].run()))
        s.add_field(name="User", value=await self.bot.get_user_info(int(case["user"].run())))
        s.add_field(name="Moderator", value=author, inline=False)
        serverdata.update({"case": r.row["case"].map(lambda x: r.branch(x["id"] == case_number, x.merge({"mod": str(author.id)}), x))}).run()
        s.add_field(name="Reason", value=reason)
        serverdata.update({"case": r.row["case"].map(lambda x: r.branch(x["id"] == case_number, x.merge({"reason": reason}), x))}).run()
        try:
            await message.edit(embed=s)
            await ctx.send("Case #{} has been updated <:done:403285928233402378>".format(case_number))
        except: 
            await ctx.send("I am unable to edit that case or it doesn't exist :no_entry:")
            
    @modlog.command()
    @checks.has_permissions("manage_messages")
    async def viewcase(self, ctx, case_number: int):
        """View any modlog case even if it's been deleted"""
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        case = serverdata["case"].filter({"id": case_number})[0]
        try:
            if case["reason"].run() is None:
                reason = "None (Update using `s?modlog case {} <reason>`)".format(case_number)
            else:
                reason = case["reason"].run()
            if case["mod"].run() is None:
                author = "Unknown"
            else:
                author = await self.bot.get_user_info(case["mod"].run())
            s=discord.Embed(title="Case {} | {}".format(case_number, case["action"].run()), timestamp=datetime.datetime.fromtimestamp(case["time"].run()))
            s.add_field(name="User", value=await self.bot.get_user_info(int(case["user"].run())))
            s.add_field(name="Moderator", value=author, inline=False)
            s.add_field(name="Reason", value=reason)
            await ctx.send(embed=s)
        except:
            await ctx.send("Invalid case number :no_entry:")
            
    @modlog.command()
    @checks.has_permissions("manage_roles")
    async def resetcases(self, ctx):
        """Reset all the cases in the modlog"""
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        serverdata.update({"case#": 0, "case": []}).run()
        await ctx.send("All cases have been reset <:done:403285928233402378>")

    @modlog.command()
    async def stats(self, ctx):
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id)).run()
        s=discord.Embed(colour=0xffff00)
        s.set_author(name="Mod-Log Settings", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Status", value="Enabled" if serverdata["toggle"] else "Disabled")
        s.add_field(name="Channel", value=self.bot.get_channel(int(serverdata["channel"])).mention if serverdata["channel"] else "Not set")
        s.add_field(name="Number of Cases", value=serverdata["case#"])
        await ctx.send(embed=s)

    async def _log(self, author, server, action, reason, user):
        if author == self.bot.user and action != "Unmute (Automatic)":
            return
        r.table("modlogs").insert({"id": str(server.id), "channel": None, "toggle": False, "case#": 0, "case": []}).run()
        serverdata = r.table("modlogs").get(str(server.id))
        channel = self.bot.get_channel(int(serverdata["channel"].run()))
        if serverdata["toggle"].run() == True and channel is not None:
            serverdata.update({"case#": r.row["case#"] + 1}).run() 
            number = serverdata["case#"].run()
            if not author:
                authortext = "Unknown (Update using `s?modlog case {} <reason>`)".format(number)
            else:
                authortext = str(author)
            if not reason: 
                reasontext = "None (Update using `s?modlog case {} <reason>`)".format(number)
            else:
                reasontext = reason
            s=discord.Embed(title="Case {} | {}".format(number, action), timestamp=datetime.datetime.utcnow())
            s.add_field(name="User", value=user)
            s.add_field(name="Moderator", value=authortext, inline=False)
            s.add_field(name="Reason", value=reasontext)
            message = await channel.send(embed=s)
            case2 = {}
            case2["id"] = number
            case2["action"] = action
            case2["user"] = str(user.id)
            case2["mod"] = str(author.id) if author else None
            case2["reason"] = reason if reason else None
            case2["time"] = datetime.datetime.utcnow().timestamp()
            case2["message"] = str(message.id)
            serverdata.update({"case": r.row["case"].append(case2)}).run()
        
    @commands.command(aliases=["cr"])
    @checks.has_permissions("manage_roles")
    async def createrole(self, ctx, rolename, colour_hex: discord.Colour=None):
        """Create a role in the server"""
        if not ctx.message.channel.permissions_for(ctx.me).manage_roles:
            await ctx.send("I need the `MANGE_ROLES` Permission :no_entry:")
            return
        try:
            if colour_hex:
                await ctx.guild.create_role(name=rolename, colour=colour_hex)
            else:
                await ctx.guild.create_role(name=rolename)
            await ctx.send("I have created the role **{}** <:done:403285928233402378>:ok_hand:".format(rolename)) 
        except:
            await ctx.send("I was not able to create the role :no_entry:")
            
    @commands.command(aliases=["dr"])
    @checks.has_permissions("manage_roles")
    async def deleterole(self, ctx, *, role: discord.Role):
        """Delete a role in the server"""
        if not ctx.message.channel.permissions_for(ctx.me).manage_roles:
            await ctx.send("I need the `MANGE_ROLES` Permission :no_entry:")
            return
        try:
            await role.delete()
            await ctx.send("I have deleted the role **{}** <:done:403285928233402378>:ok_hand:".format(role.name)) 
        except:
            await ctx.send("I was not able to delete the role or the role doesn't exist :no_entry:")
        
    @commands.command(aliases=["ar"]) 
    @checks.has_permissions("manage_roles")
    async def addrole(self, ctx, role: discord.Role, *, user: discord.Member=None):
        """Add a role to a user"""
        author = ctx.message.author
        server = ctx.message.guild
        if role.position > author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not add a role to a user which is higher than your own role :no_entry:")
                return
        if user is None:
            user = author
        if role in user.roles:
            await ctx.send("The user already has that role :no_entry:")
            return
        try:
            await user.add_roles(role)
            await ctx.send("**{}** has been added to **{}** <:done:403285928233402378>:ok_hand:".format(role, user))
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to add the role to the user :no_entry:")
        
    @commands.command(aliases=["rr"]) 
    @checks.has_permissions("manage_roles")
    async def removerole(self, ctx, role: discord.Role, *, user: discord.Member=None):
        """Remove a role from a user"""
        author = ctx.message.author
        server = ctx.guild
        if role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not remove a role from a user higher than your own role :no_entry:")
                return
        if user is None:
            user = author
        if not role in user.roles:
            await ctx.send("The user doesn't have that role :no_entry:")
            return
        try:
            await user.remove_roles(role)
            await ctx.send("**{}** has been removed from **{}** <:done:403285928233402378>:ok_hand:".format(role, user))
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to remove the role from the user :no_entry:")
            
    @commands.command(no_pm=True, )
    @checks.has_permissions("kick_members")
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):
        """Kicks a user."""
        author = ctx.message.author
        server = author.guild
        channel = ctx.message.channel
        destination = user
        action = "Kick"
        can_ban = channel.permissions_for(ctx.me).kick_members
        if not can_ban:
            await ctx.send("I need the `KICK_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not going to kick myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await ctx.send("Why would you want to kick yourself, just leave.")
            return
        if user.top_role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not kick someone higher than your own role :no_entry:")
                return
        try: 
            await server.kick(user, reason="Kick made by {}".format(author))
            await ctx.send("**{}** has been kicked <:done:403285928233402378>:ok_hand:".format(user))
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to kick that user :no_entry:")
            return
        try: 
            u=discord.Embed(title="You have been kicked from {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            u.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
            u.set_thumbnail(url=server.icon_url)
            if not reason:
                u.add_field(name="Reason", value="No reason specified")
            else:
                u.add_field(name="Reason", value=reason)
            try:
                await user.send(embed=u)
            except discord.errors.HTTPException:
                pass
        except Exception as e:
            print(e)

    @commands.command(no_pm=True)
    @checks.has_permissions("ban_members")
    async def Ban(self, ctx, user: discord.Member):
        """Fake bean don't exp0se"""
        await ctx.send("**{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
            
    @commands.command(no_pm=True)
    @checks.has_permissions("ban_members")
    async def ban(self, ctx, user, *, reason: str = None):
        """Bans a user."""
        notinserver = False
        user = await arg.get_member(self.bot, ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        if user not in ctx.guild.members:
            notinserver = True
        author = ctx.message.author
        server = author.guild
        channel = ctx.message.channel
        action = "Ban"
        destination = user
        can_ban = channel.permissions_for(ctx.me).ban_members
        if not can_ban:
            await ctx.send("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not going to ban myself ¯\_(ツ)_/¯")
            return
        if author == user:
            await ctx.send("Why would you want to ban yourself, just leave.")
            return
        if notinserver == False:
            if user.top_role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
                if author == server.owner:
                    pass
                else:
                    await ctx.send("You can not ban someone higher than your own role :no_entry:")
                    return
        if user in [x.user for x in await ctx.guild.bans()]:
            return await ctx.send("That user is already banned :no_entry:")
        try: 
            await server.ban(user, reason="Ban made by {}".format(author))
            await ctx.send("**{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to ban that user :no_entry:")
            return
        if notinserver == False:
            try: 
                u=discord.Embed(title="You have been banned from {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                u.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
                u.set_thumbnail(url=server.icon_url)
                if not reason:
                    u.add_field(name="Reason", value="No reason specified")
                else:
                    u.add_field(name="Reason", value=reason)
                try:
                    await user.send(embed=u)
                except discord.errors.HTTPException:
                    pass
            except Exception as e:
                print(e)

        
            
    @commands.command(no_pm=True) 
    @checks.has_permissions("ban_members")
    async def unban(self, ctx, user, *, reason: str=None):
        """unbans a user by ID and will notify them about the unbanning in pm"""
        author = ctx.message.author 
        server = ctx.message.guild
        channel = ctx.message.channel
        action = "Unban"
        user = await arg.get_member(self.bot, ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        can_ban = channel.permissions_for(ctx.me).ban_members
        if not can_ban:
            await ctx.send("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        ban_list = await server.bans()
        try:
            invite = await channel.create_invite(max_age=86400, max_uses=1)
        except:
            invite=None
        s=discord.Embed(title="You have been unbanned from {}".format(server.name), description="Feel free to join back whenever.", colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
        s.set_thumbnail(url=server.icon_url)
        s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
        if invite:
            s.add_field(name="Invite", value="{} (This will expire in 1 day)".format(str(invite)))
        if user == author:
            await ctx.send("You can't unban yourself :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not even banned ¯\_(ツ)_/¯")
            return
        i = 0
        n = 0
        if user not in [x.user for x in ban_list]:
            return await ctx.send("That user is not banned :no_entry:") 
            return
        try:
            await server.unban(user, reason="Unban made by {}".format(author))
        except discord.errors.Forbidden:
            await ctx.send("I need the **Ban Members** permission to unban :no_entry:")
            return
        await ctx.send("**{}** has been unbanned <:done:403285928233402378>:ok_hand:".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        try:
            await user.send(embed=s)
        except:
            pass
            
    async def on_member_ban(self, guild, user):
        author = None
        for x in await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten():
            author = x.user
            if x.reason != "":
                reason = x.reason
            else:
                reason = None
        action = "Ban"
        server = guild
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
                
    async def on_member_unban(self, guild, user):
        author = None
        for x in await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten():
            author = x.user
            if x.reason != "":
                reason = x.reason
            else:
                reason = None
        action = "Unban"
        server = guild
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def cmute(self, ctx, user: discord.Member, *, reason=None):
        """Mute someone in the channel"""
        server = ctx.message.guild
        author = ctx.message.author
        channel = ctx.message.channel
        action = "Mute"
        if channel.permissions_for(user).administrator:
            await ctx.send("That user has administrator perms, why would i even try :no_entry:")
            return
        if not channel.permissions_for(user).send_messages:
            await ctx.send("{} is already muted :no_entry:".format(user))
            return
        if user.top_role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not mute someone higher than your own role :no_entry:")
                return
        overwrite = ctx.channel.overwrites_for(user)
        overwrite.send_messages = False
        try:
            await channel.set_permissions(user, overwrite=overwrite)
        except discord.errors.Forbidden:
            await ctx.send("I do not have permissions to edit the current channel :no_entry:")
            return
        await ctx.send("**{}** has been muted <:done:403285928233402378>".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        try:
            s=discord.Embed(title="You have been muted in {} :speak_no_evil:".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
            if reason:
                s.add_field(name="Reason", value=reason) 
            else:
                s.add_field(name="Reason", value="None")
            await user.send(embed=s)
        except:
            pass
        
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def cunmute(self, ctx, user: discord.Member, *, reason: str=None):
        """Unmute a muted user in the current channel"""
        server = ctx.message.guild
        author = ctx.message.author
        action = "Unmute"
        channel = ctx.message.channel
        if channel.permissions_for(user).send_messages:
            await ctx.send("{} is not muted :no_entry:".format(user))
            return
        overwrite = ctx.channel.overwrites_for(user)
        overwrite.send_messages = True
        try:
            await channel.set_permissions(user, overwrite=overwrite)
        except discord.errors.Forbidden:
            await ctx.send("I do not have permissions to edit the current channel :no_entry:")
            return
        try:
            s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)))
            await user.send(embed=s)
        except:
            pass
        await ctx.send("**{}** has been unmuted <:done:403285928233402378>".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass

    async def on_member_join(self, member):
        server = member.guild
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        serverdata = r.table("mute").get(str(server.id)).run()
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        try:
            if serverdata["toggle"] == True:
                await member.add_roles(role, reason="Mute evasion")
        except:
            pass
        
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def mute(self, ctx, user: discord.Member, time_and_unit=None, *, reason: str=None):
        """Mute a user for a certain amount of time
        Example: s?mute @Shea#4444 20m (this will mute the user for 20 minutes)"""
        server = ctx.message.guild
        channel = ctx.message.channel
        author = ctx.message.author
        r.table("mute").insert({"id": str(server.id), "users": []}).run()
        serverdata = r.table("mute").get(str(server.id))
        if author == user:
            await ctx.send("You can't mute yourself :no_entry:")
            return
        if author == ctx.me:
            return await ctx.send("No i like speaking thanks :no_entry:")
        if channel.permissions_for(user).administrator:
            await ctx.send("That user has administrator perms, why would i even try :no_entry:")
            return
        if user.top_role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not mute someone higher than your own role :no_entry:")
                return
        if not time_and_unit: 
            time2 = 600
            time = "10"
            unit = "minutes"
        else:
            try:
                unit = time_and_unit[len(time_and_unit)-1:len(time_and_unit)]
            except ValueError:
                await ctx.send("Invalid time unit :no_entry:")
                return
            try:
                time = time_and_unit[0:len(time_and_unit)-1]
            except ValueError:
                await ctx.send("Invalid time unit :no_entry:")
                return
            if unit == "s":
                try:
                    time2 = int(time)
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "second"
                else:
                    unit = "seconds"
            elif unit == "m":
                try:
                    time2 = int(time) * 60
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "minute"
                else:
                    unit = "minutes"
            elif unit == "h":
                try:
                    time2 = int(time) * 3600
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "hour"
                else:
                    unit = "hours"
            elif unit == "d":
                try:
                    time2 = int(time) * 86400
                except ValueError:
                    await ctx.send("Invalid time unit :no_entry:")
                    return
                if time == "1":
                    unit = "day"
                else:
                    unit = "days"
            else:
                await ctx.send("Invalid time unit :no_entry:")
                return
        action = "Mute ({} {})".format(time, unit)
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            role = await server.create_role(name="Muted - Sx4")
            for channels in ctx.guild.text_channels:
                await channels.set_permissions(role, overwrite=overwrite)
            for channels in ctx.guild.voice_channels:
                await channels.set_permissions(role, overwrite=perms)
        if role in user.roles:
            await ctx.send("**{}** is already muted :no_entry:".format(user))
            return
        try:
            await user.add_roles(role)
        except: 
            await ctx.send("I cannot add the mute role to the user :no_entry:")
            return
        await ctx.send("**{}** has been muted for {} {} <:done:403285928233402378>".format(user, time, unit))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        if str(user.id) not in serverdata["users"].map(lambda x: x["id"]).run():
            userobj = {}
            userobj["id"] = str(user.id)
            userobj["toggle"] = True
            userobj["amount"] = time2
            userobj["time"] = ctx.message.created_at.timestamp()
            serverdata.update({"users": r.row["users"].append(userobj)}).run()
        else:
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": ctx.message.created_at.timestamp(), "amount": time2, "toggle": True}), x))}).run()
        try:
            s=discord.Embed(title="You have been muted in {} :speak_no_evil:".format(server.name), colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
            s.add_field(name="Time", value="{} {}".format(time, unit), inline=False)
            if reason:
                s.add_field(name="Reason", value=reason, inline=False)
            await user.send(embed=s)
        except:
            pass
            
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def unmute(self, ctx, user: discord.Member, *, reason: str=None):
        """Unmute a user who is muted"""
        server = ctx.message.guild
        channel = ctx.message.channel
        author = ctx.message.author
        serverdata = r.table("mute").get(str(server.id))
        action = "Unmute"
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        if not role:
            await ctx.send("No-one is muted in this server :no_entry:")
            return
        if role not in user.roles:
            await ctx.send("**{}** is not muted :no_entry:".format(user))
            return
        try:
            await user.remove_roles(role)
        except: 
            await ctx.send("I cannot remove the mute role from the user :no_entry:")
            return
        await ctx.send("**{}** has been unmuted <:done:403285928233402378>".format(user))
        try:
            await self._log(author, server, action, reason, user)
        except:
            pass
        serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": None, "amount": None, "toggle": False}), x))}).run()
        try:
            s=discord.Embed(title="You have been unmuted early in {}".format(server.name), colour=0xfff90d, timestamp=datetime.datetime.utcnow())
            s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)))
            await user.send(embed=s)
        except:
            pass
                   
    @commands.command() 
    async def mutedlist(self, ctx):
        """Check who is muted in the server and for how long"""
        server = ctx.message.guild
        msg = ""
        i = 0;
        serverdata = r.table("mute").get(str(server.id))
        try:
            for data in serverdata["users"].run():
                if data["toggle"] == True:
                    i += 1
        except: 
            await ctx.send("No one is muted in this server :no_entry:")
            return
        if i == 0:   
            await ctx.send("No one is muted in this server :no_entry:")
            return
        for data in serverdata["users"].run():
            if data["time"] == None or data["time"] - ctx.message.created_at.timestamp() + data["amount"] <= 0:
                time = "Infinite" 
            else:
                m, s = divmod(data["time"] - ctx.message.created_at.timestamp() + data["amount"], 60)
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
            if data["toggle"] == True:
                user = discord.utils.get(server.members, id=int(data["id"]))
                if user:
                    msg += "{} - {} (Till mute ends)\n".format(user, time)
        if not msg:
            await ctx.send("No one is muted in this server :no_entry:")
            return
        s=discord.Embed(description=msg, colour=0xfff90d, timestamp=datetime.datetime.utcnow())
        s.set_author(name="Mute List for {}".format(server), icon_url=server.icon_url)
        await ctx.send(embed=s)
            
    async def on_member_update(self, before, after):
        server = before.guild
        serverdata = r.table("mute").get(str(server.id))
        user = after
        author = None
        reason = None
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        if role in before.roles and role not in after.roles:
            if str(user.id) not in serverdata["users"].map(lambda x: x["id"]).run():
                user = {}
                user["id"] = str(user.id)
                user["toggle"] = False
                user["amount"] = None
                user["time"] = None
                serverdata.update({"users": r.row["users"].append(user)}).run()
            else:
                serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": None, "amount": None, "toggle": False}), x))}).run()
            for x in await server.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten():
                author = x.user
                if x.reason != "":
                    reason = x.reason
            if author == self.bot.user:
                return
            action = "Unmute"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if role in after.roles and role not in before.roles:
            if str(user.id) not in serverdata["users"].map(lambda x: x["id"]).run():
                user = {}
                user["id"] = str(user.id)
                user["toggle"] = True
                user["amount"] = None
                user["time"] = None
                serverdata.update({"users": r.row["users"].append(user)}).run()
            else:
                serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": None, "amount": None, "toggle": True}), x))}).run()
            for x in await server.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten():
                author = x.user
                if x.reason != "":
                    reason = x.reason
            if author == self.bot.user:
                return
            action = "Mute (Infinite)"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
            
    async def on_guild_channel_create(self, channel):
        server = channel.guild
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            return
        if isinstance(channel, discord.TextChannel):
            await channel.set_permissions(role, overwrite=overwrite)
        if isinstance(channel, discord.VoiceChannel):
            await channel.set_permissions(role, overwrite=perms)
        
    @commands.command(no_pm=True)
    @checks.has_permissions("manage_messages")
    async def warn(self, ctx, user: discord.Member, *, reason: str=None):
        """Warns a user in pm, a reason is also optional."""
        author = ctx.message.author
        server = ctx.message.guild
        channel = ctx.message.channel
        r.table("mute").insert({"id": str(server.id), "users": []}).run()
        mutedata = r.table("mute").get(str(server.id))
        if user.bot:
            return await ctx.send("You cannot warn bots :no_entry:")
        if user == author:
            await ctx.send("You can not warn yourself :no_entry:")
            return
        if user.top_role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not warn someone higher than your own role :no_entry:")
                return
        if str(user.id) not in mutedata["users"].map(lambda x: x["id"]).run():
            user = {}
            user["id"] = str(user.id)
            user["toggle"] = False
            user["amount"] = None
            user["time"] = None
            mutedata.update({"users": r.row["users"].append(user)}).run()
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        perms = discord.PermissionOverwrite()
        perms.speak = False
        if not role:
            role = await server.create_role(name="Muted - Sx4")
            for channels in server.text_channels:
                await channels.set_permissions(role, overwrite=overwrite)
            for channels in server.voice_channels:
                await channels.set_permissions(role, overwrite=perms)
        await self._create_warn(server, user)
        serverdata = r.table("warn").get(str(server.id))
        userdata = serverdata["users"].filter({"id": str(user.id)})[0]
        if reason:
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"reasons": x["reasons"].append(reason)}), x))}).run()
        if userdata["warnings"].run() == 2 and not ctx.channel.permissions_for(ctx.author).kick_members:
            return await ctx.send("You need the kick members permission to warn the user again :no_entry:")
        if userdata["warnings"].run() == 3 and not ctx.channel.permissions_for(ctx.author).ban_members:
            return await ctx.send("You need the ban members permission to warn the user again :no_entry:")
        serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": x["warnings"] + 1}), x))}).run()
        if userdata["warnings"].run() == 1:
            await ctx.send("**{}** has been warned :warning:".format(user))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been warned in {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Mute")
            action = "Warn (1st Warning)"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if userdata["warnings"].run() == 2:
            try:
                await user.add_roles(role)
                mutedata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": ctx.message.created_at.timestamp(), "amount": 600, "toggle": True}), x))}).run()
            except: 
                await ctx.send("I cannot add the mute role to the user :no_entry:")
                return
            await ctx.send("**{}** has been muted due to their second warning <:done:403285928233402378>".format(user))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been muted in {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Kick")
            action = "Mute (2nd Warning)"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if userdata["warnings"].run() == 3:
            try:
                await server.kick(user, reason="Kick made by {}".format(author))
            except:
                await ctx.send("I'm not able to kick that user :no_entry:")
                return
            await ctx.send("**{}** has been kicked due to their third warning <:done:403285928233402378>".format(user))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been kicked from {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="Ban")
            action = "Kick (3rd Warning)"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        if userdata["warnings"].run() >= 4:
            try:
                await server.ban(user, reason="Ban made by {}".format(author))
            except:
                await ctx.send("I'm not able to ban that user :no_entry:")
                return
            await ctx.send("**{}** has been banned due to their forth warning <:done:403285928233402378>".format(user))
            await server.ban(user, reason="Ban made by {}".format(author))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been banned from {}".format(server.name), icon_url=server.icon_url)
            try:
                s.add_field(name="Reason", value=reason, inline=False)
            except:
                s.add_field(name="Reason", value="None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="None")
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": 0, "reasons": []}), x))}).run()
            action = "Ban (4th Warning)"
            try:
                await self._log(author, server, action, reason, user)
            except:
                pass
        try:
            await user.send(embed=s)
        except:
            pass
            
    @commands.command()
    async def warnlist(self, ctx, page: int=None):
        """View everyone who has been warned and how many warning they're on"""
        server = ctx.message.guild 
        serverdata = r.table("warn").get(str(server.id))
        if not page:
            page = 1
        if page < 0:
            await ctx.send("Invalid page :no_entry:")
            return
        try:
            if page > math.ceil(len(serverdata["users"].run())/20):
                await ctx.send("Invalid page :no_entry:")
                return
        except:
            await ctx.send("No one has been warned in this server :no_entry:")
            return
        s = await self._list_warns(server, page)
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("There are no users with warnings in this server :no_entry:")
        
    @commands.command()
    async def warnings(self, ctx, user: discord.Member): 
        """Check how many warnings a specific user is on"""
        server = ctx.message.guild
        serverdata = r.table("warn").get(str(server.id))
        userdata = serverdata["users"].filter({"id": str(user.id)})[0].run()
        try:
            if userdata["warnings"] == 1:
                action = "Mute"
            if userdata["warnings"] == 2:
                action = "Kick"
            if userdata["warnings"] >= 3:
                action = "Ban"
            if not userdata["reasons"]:
                reasons = "None"
            else:
                reasons = ", ".join([x for x in userdata["reasons"]])
            if userdata["warnings"] == 1:
                s=discord.Embed(description="{} is on 1 warning".format(user), colour=user.colour)
                s.set_author(name=str(user), icon_url=user.avatar_url)
                s.add_field(name="Next Action", value=action, inline=False)
                s.add_field(name="Reasons", value=reasons, inline=False)
                await ctx.send(embed=s)
            else:
                try:
                    s=discord.Embed(description="{} is on {} warnings".format(user, userdata["warnings"]), colour=user.colour)
                    s.set_author(name=str(user), icon_url=user.avatar_url)
                    s.add_field(name="Next Action", value=action, inline=False)
                    s.add_field(name="Reasons", value=reasons, inline=False)
                    await ctx.send(embed=s)
                except:
                    await ctx.send("This user has no warnings :no_entry:")
        except:
            await ctx.send("This user has no warnings :no_entry:")
                
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def setwarns(self, ctx, user: discord.Member, warnings: int=None):
        """Set the warn amount for a specific user"""
        server = ctx.message.guild
        serverdata = r.table("warn").get(str(server.id))
        if user.top_role.position >= ctx.author.top_role.position:
            if ctx.author == ctx.guild.owner:
                pass
            else:
                return await ctx.send("You have to be above the user in the role hierarchy to set their warns :no_entry:")
        await self._create_warn(server, user)
        if not warnings:  
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": 0, "reasons": []}), x))}).run()
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings == 0:
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": 0, "reasons": []}), x))}).run()
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings <= 0:
            await ctx.send("You can set warnings to 1-4 only :no_entry:")
            return
        if warnings >= 5:
            await ctx.send("You can set warnings to 1-4 only :no_entry:") 
            return
        serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": warnings}), x))}).run()

        await ctx.send("**{}'s** warnings have been set to **{}**".format(user.name, warnings))  

    async def check_mute(self):
        while not self.bot.is_closed():
            data = r.table("mute")
            for d in data.run():
                server = self.bot.get_guild(int(d["id"]))
                serverdata = data.get(d["id"])
                if server != None:
                    role = discord.utils.get(server.roles, name="Muted - Sx4")
                    if role != None:
                        if serverdata["users"].run() != None:
                            for x in serverdata["users"].run():
                                user = discord.utils.get(server.members, id=int(x["id"]))
                                if user != None:
                                    if x["toggle"] != False and x["time"] != None and x["amount"] != None:
                                        time2 = x["time"] - datetime.datetime.utcnow().timestamp() + x["amount"]
                                        if time2 <= 0:
                                            if role in user.roles:
                                                await user.remove_roles(role)
                                                s=discord.Embed(title="You have been unmuted in {}".format(server.name), colour=0xfff90d, timestamp=datetime.datetime.now())
                                                s.add_field(name="Moderator", value="{} ({})".format(self.bot.user, self.bot.user.id), inline=False)
                                                s.add_field(name="Reason", value="Time Served", inline=False)
                                                try:
                                                    await user.send(embed=s)
                                                except:
                                                    pass
                                                action = "Unmute (Automatic)"
                                                author = self.bot.user
                                                reason = "Time limit served"
                                                try:
                                                    await self._log(author, server, action, reason, user)
                                                except:
                                                    pass
                                            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": None, "amount": None, "toggle": False}), x))}).run()          
            await asyncio.sleep(45)
      
                    
        
    async def _create_warn(self, server, user):
        r.table("warn").insert({"id": str(server.id), "users": []}).run()
        if str(user.id) not in r.table("warn").get(str(server.id))["users"].map(lambda x: x["id"]).run():
            warn = {}
            warn["id"] = str(user.id)
            warn["warnings"] = 0
            warn["reasons"] = []
            r.table("warn").update({"users": r.row["users"].append(warn)}).run()
            
    async def _list_warns(self, server, page):
        msg = ""
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        sortedwarn = sorted(r.table("warn").get(str(server.id))["users"].run(), key=lambda x: x["warnings"], reverse=True)[page*20-20:page*20]
        for x in sortedwarn:
            users = discord.utils.get(server.members, id=int(x["id"]))
            if users and x["warnings"] != 0:
                msg += "\n`{}`: Warning **#{}**".format(users, x["warnings"])
        s.add_field(name="Users on Warnings", value=msg)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(r.table("warn").get(str(server.id))["users"].run())/20)))
        return s
        
def setup(bot): 
    bot.add_cog(mod(bot))