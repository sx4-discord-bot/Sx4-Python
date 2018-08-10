import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
import datetime
from collections import deque, defaultdict
import os
import re
import requests
import logging
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
from utils.dataIO import fileIO

class Prefix:
    _prefixes_file = "data/mod/prefixes.json"
    _prefixes = dataIO.load_json(_prefixes_file)


class mod:
    def __init__(self, bot):
        loop = asyncio.get_event_loop()
        self.bot = bot
        self._task = loop.create_task(self.check_mute())
        self.file_path = "data/mod/autobotclean.json"
        self.settings = dataIO.load_json(self.file_path)
        self.JSON = "data/mod/warn.json"
        self.data = dataIO.load_json(self.JSON)
        self.file = "data/mod/mute.json"
        self.d = dataIO.load_json(self.file)
        self._logs_file = "data/mod/logs.json"
        self._logs = dataIO.load_json(self._logs_file)

    def __unload(self):
        self._task.cancel()

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
            s=discord.Embed(colour=ctx.author.colour)
            s.set_author(name="Prefix Settings", icon_url=ctx.author.avatar_url)
            s.add_field(name="Default Prefixes", value="{}".format(", ".join(['sx4 ', 's?', 'S?', '<@440996323156819968> '])), inline=False)
            try:
                s.add_field(name="Server Prefixes", value="{}".format(", ".join(Prefix._prefixes["serverprefix"][str(ctx.guild.id)])), inline=False)
            except:
                s.add_field(name="Server Prefixes", value="None", inline=False)
            try:
                s.add_field(name="{}'s Prefixes".format(ctx.author.name), value="{}".format(", ".join(Prefix._prefixes["userprefix"][str(ctx.author.id)])), inline=False)
            except:
                s.add_field(name="{}'s Prefixes".format(ctx.author.name), value="None", inline=False)
            await ctx.send(embed=s, content="For help on setting the prefix use `{}help prefix`".format(ctx.prefix))
        else:
            if "userprefix" not in Prefix._prefixes:
                Prefix._prefixes["userprefix"] = {}
            if "serverprefix" not in Prefix._prefixes:
                Prefix._prefixes["serverprefix"] = {}
            dataIO.save_json(Prefix._prefixes_file, Prefix._prefixes)

    @prefix.command()
    async def self(self, ctx, *prefixes):
        "Set a prefix or multiple for yourself on the bot"
        prefixes = [x for x in prefixes if x != ""]
        if str(ctx.author.id) not in Prefix._prefixes["userprefix"]:
            Prefix._prefixes["userprefix"][str(ctx.author.id)] = {}
        if len(prefixes) == 0:
            del Prefix._prefixes["userprefix"][str(ctx.author.id)] 
            await ctx.send("Your prefixes have been reset <:done:403285928233402378>")
        else:
            Prefix._prefixes["userprefix"][str(ctx.author.id)] = prefixes
            if len(prefixes) > 1:
                await ctx.send("Your prefixes have been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
            else:
                await ctx.send("Your prefix has been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
        dataIO.save_json(Prefix._prefixes_file, Prefix._prefixes)

    @prefix.command()
    @checks.has_permissions("manage_guild")
    async def server(self, ctx, *prefixes):
        """Set a prefix for the server you're in"""
        prefixes = [x for x in prefixes if x != ""]
        if str(ctx.guild.id) not in Prefix._prefixes["serverprefix"]:
            Prefix._prefixes["serverprefix"][str(ctx.guild.id)] = {}
        if len(prefixes) == 0:
            del Prefix._prefixes["serverprefix"][str(ctx.guild.id)] 
            await ctx.send("The server prefixes have been reset <:done:403285928233402378>")
        else:
            Prefix._prefixes["serverprefix"][str(ctx.guild.id)] = prefixes
            if len(prefixes) > 1:
                await ctx.send("The server prefixes have been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
            else:
                await ctx.send("The server prefix has been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
        dataIO.save_json(Prefix._prefixes_file, Prefix._prefixes)


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
        if len(deleted) == 1:
            msg = await ctx.send("Deleted **{}** message from **{}** <:done:403285928233402378>:ok_hand:".format(len(deleted), user))
        else:
            msg = await ctx.send("Deleted **{}** messages from **{}** <:done:403285928233402378>:ok_hand:".format(len(deleted), user))
        await asyncio.sleep(3)
        try:
            await msg.delete() 
        except discord.HTTPException:
            pass
        
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
        if len(deleted) == 1:
            msg = await ctx.send("*Deleted **{}** bot message <:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        else:
            msg = await ctx.send("*Deleted **{}** bot messages* *<:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        await asyncio.sleep(3)
        try:
            await msg.delete()
        except discord.HTTPException:
            pass

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
        try:
            def check(m):
                return word.lower() in m.content.lower()
            deleted = await channel.purge(limit=limit, before=ctx.message, check=check)
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        if len(deleted) == 1:
            msg = await ctx.send("Deleted **{}** message <:done:403285928233402378>:ok_hand:".format(len(deleted)), delete_after=3)
        else:
            msg = await ctx.send("Deleted **{}** messages <:done:403285928233402378>:ok_hand:".format(len(deleted)), delete_after=3)
        
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
            limit = 100
        elif limit > 100:
            limit = 100
        await ctx.message.delete()
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message)
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        if len(deleted) == 1:
            msg = await ctx.send("*Deleted **{}** message <:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        else:
            msg = await ctx.send("*Deleted **{}** messages* *<:done:403285928233402378>:ok_hand:*".format(len(deleted)))
        await asyncio.sleep(3)
        try:
            await msg.delete()
        except discord.HTTPException:
            pass
            
    @commands.group()
    async def modlog(self, ctx):
        """Have logs for all mod actions"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            if str(server.id) not in self._logs:
                self._logs[str(server.id)] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if "channel" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["channel"] = None
                dataIO.save_json(self._logs_file, self._logs)
            if "toggle" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["toggle"] = False
                dataIO.save_json(self._logs_file, self._logs)
            if "case#" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["case#"] = 0
                dataIO.save_json(self._logs_file, self._logs)
            if "case" not in self._logs[str(server.id)]:
                self._logs[str(server.id)]["case"] = {}
                dataIO.save_json(self._logs_file, self._logs)
        
            
    @modlog.command()
    @checks.has_permissions("manage_roles")
    async def toggle(self, ctx):
        """Toggle modlogs on or off"""
        server = ctx.guild
        if self._logs[str(server.id)]["toggle"] == True:
            self._logs[str(server.id)]["toggle"] = False
            dataIO.save_json(self._logs_file, self._logs)
            await ctx.send("Modlogs are now disabled.")
            return
        if self._logs[str(server.id)]["toggle"] == False:
            self._logs[str(server.id)]["toggle"] = True
            dataIO.save_json(self._logs_file, self._logs)
            await ctx.send("Modlogs are now enabled.")
            return
            
    @modlog.command() 
    @checks.has_permissions("manage_roles")
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where you want modlogs to be posted"""
        server = ctx.guild
        self._logs[str(server.id)]["channel"] = str(channel.id)
        dataIO.save_json(self._logs_file, self._logs)    
        await ctx.send("<#{}> has been set as the modlog channel".format(str(channel.id)))
        
    @modlog.command()
    @checks.has_permissions("manage_messages")
    async def case(self, ctx, case_number, *, reason):
        """Edit a modlog case"""
        author = ctx.author
        server = ctx.guild
        try:
            self._logs[str(server.id)]["case"][case_number]
        except:
            await ctx.send("Invalid case number :no_entry:")
            return
        if self._logs[str(server.id)]["case"][case_number]["mod"] is not None and self._logs[str(server.id)]["case"][case_number]["mod"] != str(author.id):
            await ctx.send("You do not have ownership of that log :no_entry:")
            return
        try:
            channel = self.bot.get_channel(int(self._logs[str(server.id)]["channel"]))
        except:
            await ctx.send("The modlog channel no longer exists :no_entry:")
            return
        try:
            message = await channel.get_message(int(self._logs[str(server.id)]["case"][case_number]["message"]))
        except:
            await ctx.send("I am unable to find that case :no_entry:")
            return
        try:
            s=discord.Embed(title="Case {} | {}".format(case_number, self._logs[str(server.id)]["case"][case_number]["action"]), timestamp=datetime.datetime.fromtimestamp(self._logs[str(server.id)]["case"][case_number]["time"]))
        except:
            s=discord.Embed(title="Case {} | {}".format(case_number, self._logs[str(server.id)]["case"][case_number]["action"]))
        s.add_field(name="User", value=await self.bot.get_user_info(int(self._logs[str(server.id)]["case"][case_number]["user"])))
        s.add_field(name="Moderator", value=author, inline=False)
        self._logs[str(server.id)]["case"][case_number]["mod"] = str(author.id)
        s.add_field(name="Reason", value=reason)
        self._logs[str(server.id)]["case"][case_number]["reason"] = reason
        dataIO.save_json(self._logs_file, self._logs)      
        try:
            await message.edit(embed=s)
            await ctx.send("Case #{} has been updated <:done:403285928233402378>".format(case_number))
        except: 
            await ctx.send("I am unable to edit that case or it doesn't exist :no_entry:")
            
    @modlog.command()
    @checks.has_permissions("manage_messages")
    async def viewcase(self, ctx, case_number):
        """Someone delete their modlog case in your modlog channel, i store all of them so use this command to see the deleted case"""
        server = ctx.guild
        try:
            if self._logs[str(server.id)]["case"][case_number]["reason"] is None:
                reason = "None (Update using `s?modlog case {} <reason>`)".format(case_number)
            else:
                reason = self._logs[str(server.id)]["case"][case_number]["reason"]
            if self._logs[str(server.id)]["case"][case_number]["mod"] is None:
                author = "Unknown"
            else:
                author = await self.bot.get_user_info(self._logs[str(server.id)]["case"][case_number]["mod"])
            s=discord.Embed(title="Case {} | {}".format(case_number, self._logs[str(server.id)]["case"][case_number]["action"]))
            s.add_field(name="User", value=await self.bot.get_user_info(int(self._logs[str(server.id)]["case"][case_number]["user"])))
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
        self._logs[str(server.id)]["case#"] = 0
        del self._logs[str(server.id)]["case"]
        dataIO.save_json(self._logs_file, self._logs)    
        await ctx.send("All cases have been reset <:done:403285928233402378>")
        
    async def _log(self, author, server, action, reason, user):
        if author == self.bot.user and action != "Unmute (Automatic)":
            return
        if "case" not in self._logs[str(server.id)]:
            self._logs[str(server.id)]["case"] = {}
            dataIO.save_json(self._logs_file, self._logs)
        channel = self.bot.get_channel(int(self._logs[str(server.id)]["channel"]))
        if self._logs[str(server.id)]["toggle"] == True and channel is not None:
            self._logs[str(server.id)]["case#"] += 1 
            number = str(self._logs[str(server.id)]["case#"])
            if number not in self._logs[str(server.id)]["case"]:
                self._logs[str(server.id)]["case"][number] = {}
                dataIO.save_json(self._logs_file, self._logs)
            if "action" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["action"] = action
                dataIO.save_json(self._logs_file, self._logs)
            if "user" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["user"] = str(user.id)
                dataIO.save_json(self._logs_file, self._logs)   
            if "mod" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["mod"] = {}
                dataIO.save_json(self._logs_file, self._logs)   
            if "reason" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["reason"] = {}
                dataIO.save_json(self._logs_file, self._logs)     
            if "time" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["time"] = datetime.datetime.utcnow().timestamp()
                dataIO.save_json(self._logs_file, self._logs)     
            if not author:
                author = "Unknown (Update using `s?modlog case {} <reason>`)".format(number)
                self._logs[str(server.id)]["case"][number]["mod"] = None
            else:
                self._logs[str(server.id)]["case"][number]["mod"] = str(author.id)
            if not reason: 
                reason = "None (Update using `s?modlog case {} <reason>`)".format(number)
                self._logs[str(server.id)]["case"][number]["reason"] = None
            else:
                self._logs[str(server.id)]["case"][number]["reason"] = reason
            s=discord.Embed(title="Case {} | {}".format(number, action), timestamp=datetime.datetime.fromtimestamp(self._logs[str(server.id)]["case"][number]["time"]))
            s.add_field(name="User", value=user)
            s.add_field(name="Moderator", value=author, inline=False)
            s.add_field(name="Reason", value=reason)
            message = await channel.send(embed=s)
            if "message" not in self._logs[str(server.id)]["case"][number]:
                self._logs[str(server.id)]["case"][number]["message"] = str(message.id)
                dataIO.save_json(self._logs_file, self._logs)    
        
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
        if role.position > author.top_role.position:
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
        if role.position >= author.top_role.position:
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
            
    @commands.command() 
    @checks.has_permissions("ban_members")
    async def Ban(self, ctx, user: discord.Member):
        """This is a fake bean don't exp0se"""
        await ctx.send("**{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
            
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
        if user.top_role.position >= author.top_role.position:
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
            
    @commands.command(no_pm=True, )
    @checks.has_permissions("ban_members")
    async def ban(self, ctx, user, *, reason: str = None):
        """Bans a user."""
        notinserver = False
        if "<" in user and "@" in user and ">" in user:
            user = user.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
            user2 = discord.utils.get(ctx.guild.members, id=int(user))
            if not user2:
                user2 = discord.utils.get(self.bot.get_all_members(), id=int(user))
                notinserver = True
                if not user2:
                    user2 = await self.bot.get_user_info(int(user))
                    if not user2:
                        try:
                            if int(user) in [x.user.id for x in await ctx.guild.bans()]:
                                return await ctx.send("That user is already banned :no_entry:")
                            await ctx.guild.ban(discord.Object(int(user)), reason="Ban made by {}".format(ctx.author))
                            return await ctx.send("User with the ID **{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
                        except:
                            return await ctx.send("Invalid user :no_entry:")
                else:
                    user = user2
            else: 
                user = user2
        elif "#" in user:
            number = len([x for x in user if "#" not in x])
            usernum = number - 4
            user2 = discord.utils.get(ctx.guild.members, name=user[:usernum], discriminator=user[usernum + 1:len(user)])
            if not user2:
                user = discord.utils.get(self.bot.get_all_members(), name=user[:usernum], discriminator=user[usernum + 1:len(user)])
                notinserver = True
            else:
                user = user2
        else:
            try:
                user2 = discord.utils.get(ctx.guild.members, id=int(user))
                if not user2:
                    user2 = discord.utils.get(self.bot.get_all_members(), id=int(user))
                    notinserver = True
                    if not user2:
                        user2 = await self.bot.get_user_info(int(user))
                        if not user2:
                            try:
                                if int(user) in [x.user.id for x in await ctx.guild.bans()]:
                                    return await ctx.send("That user is already banned :no_entry:")
                                await ctx.guild.ban(discord.Object(int(user)), reason="Ban made by {}".format(ctx.author))
                                return await ctx.send("User with the ID **{}** has been banned <:done:403285928233402378>:ok_hand:".format(user))
                            except:
                                return await ctx.send("Invalid user :no_entry:")
                    else:
                        user = user2
                else:
                    user = user2
            except:
                user2 = discord.utils.get(ctx.guild.members, name=user)
                if not user2:
                    user = discord.utils.get(self.bot.get_all_members(), name=user)
                    notinserver = True
                else:
                    user = user2
        if not user:
            await ctx.send("I could not find that user :no_entry:")
            return
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
            if user.top_role.position >= author.top_role.position:
                if author == server.owner:
                    pass
                else:
                    await ctx.send("You can not ban someone higher than your own role :no_entry:")
                    return
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
    async def unban(self, ctx, user_id: int, *, reason: str=None):
        """unbans a user by ID and will notify them about the unbanning in pm"""
        author = ctx.message.author 
        server = ctx.message.guild
        channel = ctx.message.channel
        action = "Unban"
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.errors.NotFound:
            await ctx.send("The user was not found :no_entry:")
            return
        except discord.errors.HTTPException:
            await ctx.send("The ID specified does not exist :no_entry:")
            return
        can_ban = channel.permissions_for(ctx.me).ban_members
        if not can_ban:
            await ctx.send("I need the `BAN_MEMBERS` permission :no_entry:")
            return
        ban_list = await server.bans()
        invite = await channel.create_invite(max_age=86400, max_uses=1)
        s=discord.Embed(title="You have been unbanned from {}".format(server.name), description="Feel free to join back whenever.", colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
        s.set_thumbnail(url=server.icon_url)
        s.add_field(name="Moderator", value="{} ({})".format(author, str(author.id)), inline=False)
        s.add_field(name="Invite", value="{} (This will expire in 1 day)".format(str(invite)))
        if user == author:
            await ctx.send("You can't unban yourself :no_entry:")
            return
        if user == self.bot.user:
            await ctx.send("I'm not even banned ¯\_(ツ)_/¯")
            return
        i = 0
        n = 0
        if user in [x.user for x in ban_list]:
            pass
        else:
            await ctx.send("That user is not banned :no_entry:") 
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
        if user.top_role.position >= author.top_role.position:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not mute someone higher than your own role :no_entry:")
                return
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        try:
            await channel.set_permissions(user, overwrite=overwrite)
            if str(server.id) not in self.d:
                self.d[str(server.id)] = {}
                dataIO.save_json(self.file, self.d)
            if "channel" not in self.d[str(server.id)]:
                self.d[str(server.id)]["channel"] = {}
                dataIO.save_json(self.file, self.d)
            if str(channel.id) not in self.d[str(server.id)]["channel"]:
                self.d[str(server.id)]["channel"][str(str(channel.id))] = {}
                dataIO.save_json(self.file, self.d)
            if "user" not in self.d[str(server.id)]["channel"][str(channel.id)]:
                self.d[str(server.id)]["channel"][str(channel.id)]["user"] = {}
                dataIO.save_json(self.file, self.d)
            if str(user.id) not in self.d[str(server.id)]["channel"][str(channel.id)]["user"]:
                self.d[str(server.id)]["channel"][str(channel.id)]["user"][str(user.id)] = {}
                dataIO.save_json(self.file, self.d)
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
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        try:
            await channel.set_permissions(user, overwrite=overwrite)
            del self.d[str(server.id)]["channel"][str(channel.id)]
            dataIO.save_json(self.file, self.d)
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
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        try:
            if self.d[str(server.id)][str(member.id)]["toggle"] == True:
                await member.add_roles(role, reason="Mute evasion")
        except:
            pass
        for channelid in self.d[str(server.id)]["channel"]:
            channel = discord.utils.get(server.channels, id=int(channelid))
            if str(member.id) in self.d[str(server.id)]["channel"][channelid]["user"]:
                await channel.set_permissions(member, overwrite=overwrite)
        
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def mute(self, ctx, user: discord.Member, time_and_unit=None, *, reason: str=None):
        """Mute a user for a certain amount of time
        Example: s?mute @Shea#4444 20m (this will mute the user for 20 minutes)"""
        server = ctx.message.guild
        channel = ctx.message.channel
        author = ctx.message.author
        if author == user:
            await ctx.send("You can't mute yourself :no_entry:")
            return
        if author == ctx.me:
            return await ctx.send("No i like speaking thanks :no_entry:")
        if channel.permissions_for(user).administrator:
            await ctx.send("That user has administrator perms, why would i even try :no_entry:")
            return
        if user.top_role.position >= author.top_role.position:
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
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if str(user.id) not in self.d[str(server.id)]:
            self.d[str(server.id)][str(user.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "toggle" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["toggle"] = False
            dataIO.save_json(self.file, self.d)
        if "time" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["time"] = None
            dataIO.save_json(self.file, self.d)
        if "amount" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["amount"] = None
            dataIO.save_json(self.file, self.d)
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
        self.d[str(server.id)][str(user.id)]["toggle"] = True
        self.d[str(server.id)][str(user.id)]["amount"] = time2
        self.d[str(server.id)][str(user.id)]["time"] = ctx.message.created_at.timestamp()
        dataIO.save_json(self.file, self.d)
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
        self.d[str(server.id)][str(user.id)]["toggle"] = False
        self.d[str(server.id)][str(user.id)]["time"] = None
        self.d[str(server.id)][str(user.id)]["amount"] = None
        dataIO.save_json(self.file, self.d)
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
        try:
            for userid in self.d[str(server.id)]:
                if self.d[str(server.id)][userid]["toggle"] == True:
                    i = i + 1
        except: 
            await ctx.send("No one is muted in this server :no_entry:")
            return
        if i == 0:   
            await ctx.send("No one is muted in this server :no_entry:")
            return
        for userid in self.d[str(server.id)]:
            if self.d[str(server.id)][userid]["time"] == None or self.d[str(server.id)][userid]["time"] - ctx.message.created_at.timestamp() + self.d[str(server.id)][userid]["amount"] <= 0:
                time = "Infinite" 
            else:
                m, s = divmod(self.d[str(server.id)][userid]["time"] - ctx.message.created_at.timestamp() + self.d[str(server.id)][userid]["amount"], 60)
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
            if self.d[str(server.id)][userid]["toggle"] == True:
                user = discord.utils.get(server.members, id=int(userid))
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
        user = after
        author = None
        reason = None
        role = discord.utils.get(server.roles, name="Muted - Sx4")
        if role in before.roles and role not in after.roles:
            if str(server.id) not in self.d:
                self.d[str(server.id)] = {}
            if str(user.id) not in self.d[str(server.id)]:
                self.d[str(server.id)][str(user.id)] = {}
            if "muted" not in self.d[str(server.id)][str(user.id)]:
                self.d[str(server.id)][str(user.id)]["toggle"] = False
            if "time" not in self.d[str(server.id)][str(user.id)]:
                self.d[str(server.id)][str(user.id)]["time"] = None
            if "amount" not in self.d[str(server.id)][str(user.id)]:
                self.d[str(server.id)][str(user.id)]["amount"] = None
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
            self.d[str(server.id)][str(user.id)]["toggle"] = False
            self.d[str(server.id)][str(user.id)]["time"] = None
            self.d[str(server.id)][str(user.id)]["amount"] = None
            dataIO.save_json(self.file, self.d)
        if role in after.roles and role not in before.roles:
            if str(server.id) not in self.d:
                self.d[str(server.id)] = {}
            if str(user.id) not in self.d[str(server.id)]:
                self.d[str(server.id)][str(user.id)] = {}
            if "muted" not in self.d[str(server.id)][str(user.id)]:
                self.d[str(server.id)][str(user.id)]["toggle"] = False
            if "time" not in self.d[str(server.id)][str(user.id)]:
                self.d[str(server.id)][str(user.id)]["time"] = None
            if "amount" not in self.d[str(server.id)][str(user.id)]:
                self.d[str(server.id)][str(user.id)]["amount"] = None
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
            self.d[str(server.id)][str(user.id)]["toggle"] = True
            self.d[str(server.id)][str(user.id)]["time"] = None
            self.d[str(server.id)][str(user.id)]["amount"] = None
            dataIO.save_json(self.file, self.d)
            
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
        if user == author:
            await ctx.send("You can not warn yourself :no_entry:")
            return
        if user.top_role.position >= author.top_role.position:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not warn someone higher than your own role :no_entry:")
                return
        if str(server.id) not in self.d:
            self.d[str(server.id)] = {}
            dataIO.save_json(self.file, self.d)
        if str(user.id) not in self.d[str(server.id)]:
            self.d[str(server.id)][str(user.id)] = {}
            dataIO.save_json(self.file, self.d)
        if "muted" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["toggle"] = False
            dataIO.save_json(self.file, self.d)
        if "time" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["time"] = None
            dataIO.save_json(self.file, self.d)
        if "amount" not in self.d[str(server.id)][str(user.id)]:
            self.d[str(server.id)][str(user.id)]["amount"] = None
            dataIO.save_json(self.file, self.d)
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
        if reason:
            if reason not in self.data[str(server.id)]["user"][str(user.id)]["reasons"]:
                self.data[str(server.id)]["user"][str(user.id)]["reasons"][reason] = {}
        self.data[str(server.id)]["user"][str(user.id)]["warnings"] = self.data[str(server.id)]["user"][str(user.id)]["warnings"] + 1
        dataIO.save_json(self.JSON, self.data)
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 1:
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
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 2:
            try:
                await user.add_roles(role)
                self.d[str(server.id)][str(user.id)]["toggle"] = True
                self.d[str(server.id)][str(user.id)]["amount"] = 600
                self.d[str(server.id)][str(user.id)]["time"] = ctx.message.created_at.timestamp()
                dataIO.save_json(self.file, self.d)
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
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 3:
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
        if self.data[str(server.id)]["user"][str(user.id)]["warnings"] >= 4:
            try:
                await server.ban(user, reason="Ban made by {}".format(author))
            except:
                await ctx.send("I'm not able to ban that user :no_entry:")
                del self.data[str(server.id)]["user"][str(user.id)]
                dataIO.save_json(self.JSON, self.data)
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
            del self.data[str(server.id)]["user"][str(user.id)]
            dataIO.save_json(self.JSON, self.data)
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
        if not page:
            page = 1
        if page < 0:
            await ctx.send("Invalid page :no_entry:")
            return
        try:
            if page > math.ceil(len(self.data[str(server.id)]["user"])/20):
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
        try:
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 1:
                action = "Mute"
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 2:
                action = "Kick"
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] >= 3:
                action = "Ban"
            if not self.data[str(server.id)]["user"][str(user.id)]["reasons"]:
                reasons = "None"
            else:
                reasons = ", ".join([x for x in self.data[str(server.id)]["user"][str(user.id)]["reasons"]])
            if self.data[str(server.id)]["user"][str(user.id)]["warnings"] == 1:
                s=discord.Embed(description="{} is on 1 warning".format(user), colour=user.colour)
                s.set_author(name=str(user), icon_url=user.avatar_url)
                s.add_field(name="Next Action", value=action, inline=False)
                s.add_field(name="Reasons", value=reasons, inline=False)
                await ctx.send(embed=s)
            else:
                try:
                    s=discord.Embed(description="{} is on {} warnings".format(user, self.data[str(server.id)]["user"][str(user.id)]["warnings"]), colour=user.colour)
                    s.set_author(name=str(user), icon_url=user.avatar_url)
                    s.add_field(name="Next Action", value=action, inline=False)
                    s.add_field(name="Reasons", value=reasons, inline=False)
                    await ctx.send(embed=s)
                except:
                    await ctx.send("That user has no warnings :no_entry:")
        except:
            await ctx.send("That user has no warnings :no_entry:")
                
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def setwarns(self, ctx, user: discord.Member, warnings: int=None):
        """Set the warn amount for a specific user"""
        if user.top_role.position >= ctx.author.top_role.position:
            if ctx.author == ctx.guild.owner:
                pass
            else:
                return await ctx.send("You have to be above the user in the role hierarchy to set their warns :no_entry:")
        server = ctx.message.guild
        await self._create_warn(server, user)
        dataIO.save_json(self.JSON, self.data)
        if not warnings:  
            del self.data[str(server.id)]["user"][str(user.id)]
            dataIO.save_json(self.JSON, self.data)
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings == 0:
            del self.data[str(server.id)]["user"][str(user.id)]
            dataIO.save_json(self.JSON, self.data)
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings <= 0:
            await ctx.send("You can set warnings to 1-4 only :no_entry:")
            return
        if warnings >= 5:
            await ctx.send("You can set warnings to 1-4 only :no_entry:") 
            return
        self.data[str(server.id)]["user"][str(user.id)]["warnings"] = warnings    
        dataIO.save_json(self.JSON, self.data)
        await ctx.send("**{}'s** warnings have been set to **{}**".format(user.name, warnings))  

    async def check_mute(self):
        while not self.bot.is_closed():
            for serverid in list(self.d)[:len(self.d)]:
                server = self.bot.get_guild(int(serverid))
                if server != None:
                    role = discord.utils.get(server.roles, name="Muted - Sx4")
                    if role != None:
                        if self.d[str(server.id)] != None:
                            for userid in [x for x in self.d[serverid] if x != "channel"][:len([x for x in self.d[serverid] if x != "channel"])]:
                                user = discord.utils.get(server.members, id=int(userid))
                                if user != None:
                                    if self.d[str(server.id)][str(user.id)]["toggle"] != False and self.d[str(server.id)][str(user.id)]["time"] != None and self.d[str(server.id)][str(user.id)]["amount"] != None:
                                        time2 = self.d[str(server.id)][str(user.id)]["time"] - datetime.datetime.utcnow().timestamp() + self.d[str(server.id)][str(user.id)]["amount"]
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
                                            try:
                                                self.d[str(server.id)][str(user.id)]["time"] = None
                                                self.d[str(server.id)][str(user.id)]["toggle"] = False
                                                self.d[str(server.id)][str(user.id)]["amount"] = None               
                                            except:
                                                pass                             
                                            dataIO.save_json(self.file, self.d)
            await asyncio.sleep(10)
      
                    
        
    async def _create_warn(self, server, user):
        if str(server.id) not in self.data:
            self.data[str(server.id)] = {}
            dataIO.save_json(self.JSON, self.data)
        if "user" not in self.data[str(server.id)]:
            self.data[str(server.id)]["user"] = {}
            dataIO.save_json(self.JSON, self.data)
        if str(user.id) not in self.data[str(server.id)]["user"]:
            self.data[str(server.id)]["user"][str(user.id)] = {}
            dataIO.save_json(self.JSON, self.data)
        if "warnings" not in self.data[str(server.id)]["user"][str(user.id)]:
            self.data[str(server.id)]["user"][str(user.id)]["warnings"] = 0
            dataIO.save_json(self.JSON, self.data)
        if "reasons" not in self.data[str(server.id)]["user"][str(user.id)]:
            self.data[str(server.id)]["user"][str(user.id)]["reasons"] = {}
            dataIO.save_json(self.JSON, self.data)
            
    async def _list_warns(self, server, page):
        msg = ""
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        sortedwarn = sorted(self.data[str(server.id)]["user"].items(), key=lambda x: x[1]["warnings"], reverse=True)[page*20-20:page*20]
        for x in sortedwarn:
            users = discord.utils.get(server.members, id=int(x[0]))
            if users and self.data[str(server.id)]["user"][x[0]]["warnings"] != 0:
                msg += "\n`{}`: Warning **#{}**".format(users, self.data[str(server.id)]["user"][x[0]]["warnings"])
        s.add_field(name="Users on Warnings", value=msg)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(self.data[str(server.id)]["user"])/20)))
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
    f = "data/mod/prefixes.json"
    if not dataIO.is_valid_json(f):
        print("Creating default mod's prefixes.json...")
        dataIO.save_json(f, {})
        
def setup(bot): 
    check_folders()
    check_files()
    bot.add_cog(mod(bot))