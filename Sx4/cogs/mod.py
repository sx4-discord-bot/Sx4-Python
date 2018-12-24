import discord
from discord.ext import commands
import rethinkdb as r
from utils import checks
import datetime
from collections import deque, defaultdict
import os
import re
import psutil
import requests
import logging
from utils import arghelp, ctime, arg
import asyncio
from urllib.request import Request, urlopen
import json
from threading import Timer
import random
import time
from . import owner as dev
import discord
from . import general as g
from discord.ext import commands
import math
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound

permsjson = {'change_nickname': 67108864, 'use_vad': 33554432, 'manage_channels': 16, 'manage_guild': 32, 'connect': 1048576, 'read_message_history': 65536, 'view_channel': 1024, 'move_members': 16777216, 'mention_everyone': 131072, 'manage_nicknames': 134217728, 'view_audit_log': 128, 'use_external_emojis': 262144, 'add_reactions': 64, 'manage_roles': 268435456, 'speak': 2097152, 'ban_members': 4, 'manage_webhooks': 536870912, 'send_messages': 2048, 'manage_messages': 8192, 'create_instant_invite': 1, 'embed_links': 16384, 'priority_speaker': 256, 'read_messages': 1024, 'manage_emojis': 1073741824, 'attach_files': 32768, 'mute_members': 4194304, 'administrator': 8, 'deafen_members': 8388608, 'send_tts_messages': 4096, 'kick_members': 2}


class mod:
    def __init__(self, bot):
        self.bot = bot
        self._task = bot.loop.create_task(self.check_mute())

    def __unload(self):
        self._task.cancel()

    @commands.group()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("blacklist").insert({"id": str(ctx.guild.id), "commands": [], "disabled": []}).run(durability="soft")

    @blacklist.command(name="add")
    @checks.has_permissions("manage_guild")
    async def _add(self, ctx, user_role_channel: str, *, command_or_module: str):
        """Add a user/role/channel to the blacklist for a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        commands = serverdata["commands"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        channel = arg.get_text_channel(ctx, user_role_channel)
        user = arg.get_server_member(ctx, user_role_channel)
        role = arg.get_role(ctx, user_role_channel)
        if not cog and not command:
            return await ctx.send("Invalid command/module :no_entry:")
        if channel:
            if command_or_module not in map(lambda x: x["id"], commands):
                commands.append({"id": command_or_module, "blacklisted": [{"id": str(channel.id), "type": "channel"}], "whitelisted": []})
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                try:
                    whitelisted = current_commands["whitelisted"]
                except KeyError:
                    whitelisted = []
                if str(channel.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "channel", blacklisted)):
                    return await ctx.send("This channel is already blacklisted from using this {} :no_entry:".format("command" if command else "module"))
                blacklisted.append({"id": str(channel.id), "type": "channel"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "The {} `{}` can no longer be used in {}".format("command" if command else "module", command_or_module, channel.mention)
        elif role:
            if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("You cannot blacklist a role higher or equal to your own :no_entry:")
            if role in ctx.author.roles and not checks.has_permissions("administrator").__closure__[0].cell_contents(ctx):
                return await ctx.send("You cannot blacklist a role you are in :no_entry:")
            if command_or_module not in map(lambda x: x["id"], commands):
                commands.append({"id": command_or_module, "blacklisted": [{"id": str(role.id), "type": "role"}], "whitelisted": []})
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                try:
                    whitelisted = current_commands["whitelisted"]
                except KeyError:
                    whitelisted = []
                if str(role.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "role", blacklisted)):
                    return await ctx.send("This role is already blacklisted from using this {} :no_entry:".format("command" if command else "module"))
                blacklisted.append({"id": str(role.id), "type": "role"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "Anyone in the role **{}** can no longer use the {} `{}`".format(role.name, "command" if command else "module", command_or_module)
        elif user:
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("You cannot blacklist a user higher or equal to you :no_entry:")
            if user == ctx.author:
                return await ctx.send("You cannot blacklist yourself from commands/modules :no_entry:")
            if command_or_module not in map(lambda x: x["id"], commands):
                commands.append({"id": command_or_module, "blacklisted": [{"id": str(user.id), "type": "user"}], "whitelisted": []})
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                try:
                    whitelisted = current_commands["whitelisted"]
                except KeyError:
                    whitelisted = []
                if str(user.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "user", blacklisted)):
                    return await ctx.send("This user is already blacklisted from using this {} :no_entry:".format("command" if command else "module"))
                blacklisted.append({"id": str(user.id), "type": "user"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "**{}** can no longer use the {} `{}`".format(user, "command" if command else "module", command_or_module)
        else:
            return await ctx.send("Invalid role/user/channel :no_entry:")
        await ctx.send(msg)
        serverdata.update({"commands": commands}).run(durability="soft", noreply=True)

    @blacklist.command(name="remove")
    @checks.has_permissions("manage_guild")
    async def __remove(self, ctx, user_role_channel: str, *, command_or_module: str):
        """Remove a user/role/channel from the blacklist for a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        commands = serverdata["commands"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        channel = arg.get_text_channel(ctx, user_role_channel)
        user = arg.get_server_member(ctx, user_role_channel)
        role = arg.get_role(ctx, user_role_channel)
        if not cog and not command:
            return await ctx.send("Invalid command/module :no_entry:")
        if channel:
            if command_or_module not in map(lambda x: x["id"], commands):
                return await ctx.send("This channel is not blacklisted from using this {} :no_entry:".format("command" if command else "module"))
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                try:
                    whitelisted = current_commands["whitelisted"]
                except KeyError:
                    whitelisted = []
                if str(channel.id) not in map(lambda x: x["id"], filter(lambda x: x["type"] == "channel", blacklisted)):
                    return await ctx.send("This channel is not blacklisted from using this {} :no_entry:".format("command" if command else "module"))
                blacklisted.remove({"id": str(channel.id), "type": "channel"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "The {} `{}` can now be used in {}".format("command" if command else "module", command_or_module, channel.mention)
        elif role:
            if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("You cannot undo a blacklist on a role higher or equal to your own :no_entry:")
            if command_or_module not in map(lambda x: x["id"], commands):
                return await ctx.send("This role is not blacklisted from using this {} :no_entry:".format("command" if command else "module"))
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                try:
                    whitelisted = current_commands["whitelisted"]
                except KeyError:
                    whitelisted = []
                if str(role.id) not in map(lambda x: x["id"], filter(lambda x: x["type"] == "role", blacklisted)):
                    return await ctx.send("This role is not blacklisted from using this {} :no_entry:".format("command" if command else "module"))
                blacklisted.remove({"id": str(role.id), "type": "role"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "Anyone in the role **{}** can now use the {} `{}`".format(role.name, "command" if command else "module", command_or_module)
        elif user:
            if user == ctx.author:
                return await ctx.send("You cannot undo a blacklist on yourself :no_entry:")
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("You cannot undo a blacklist on a user higher or equal to you :no_entry:")
            if command_or_module not in map(lambda x: x["id"], commands):
                return await ctx.send("This user is not blacklisted from using this {} :no_entry:".format("command" if command else "module"))
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                try:
                    whitelisted = current_commands["whitelisted"]
                except KeyError:
                    whitelisted = []
                if str(user.id) not in map(lambda x: x["id"], filter(lambda x: x["type"] == "user", blacklisted)):
                    return await ctx.send("This user is not blacklisted from using this {} :no_entry:".format("command" if command else "module"))
                blacklisted.remove({"id": str(user.id), "type": "user"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "**{}** can now use the {} `{}`".format(user, "command" if command else "module", command_or_module)
        else:
            return await ctx.send("Invalid role/user/channel :no_entry:")
        await ctx.send(msg)
        serverdata.update({"commands": commands}).run(durability="soft", noreply=True) 

    @blacklist.command(name="delete")
    @checks.has_permissions("manage_guild")
    async def __delete(self, ctx, *, command_or_module: str):
        """Delete all the blacklist data on a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        commands = serverdata["commands"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        if not command and not cog:
            return await ctx.send("Invalid command/module :no_entry:")
        if command_or_module not in map(lambda x: x["id"], commands):
            return await ctx.send("This command is not blacklisted for any role/user/channel :no_entry:")
        cmddata = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
        commands.remove(cmddata)
        cmddata["blacklisted"] = []
        commands.append(cmddata)
        await ctx.send("All blacklist data for `{}` has been deleted".format(command_or_module))
        serverdata.update({"commands": commands}).run(durability="soft", noreply=True) 

    @blacklist.command(name="reset")
    @checks.has_permissions("manage_guild")
    async def __reset(self, ctx):
        """Delete all blacklist data that you've set"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        message = await ctx.send("This will reset all your blacklist data that you've set are you sure you want to do this?\nYes or No")
        def check(m):
            return ctx.author == m.author and m.channel == ctx.channel
        try:
            response = await self.bot.wait_for("message", check=check, timeout=30)
            if response.content.lower() in ["yes", "y"]:
                try:
                   await response.delete()
                except:
                    pass
                try:
                   await message.delete()
                except: 
                    pass
                await ctx.send("All blacklist data has been deleted")
                commands = []
                for x in serverdata["commands"].run():
                    x["blacklisted"] = []
                    commands.append(x)
                serverdata.update({"commands": commands}).run(durability="soft", noreply=True) 
            else:
                try:
                   await response.delete()
                except:
                    pass
                try:
                   await message.delete()
                except: 
                    pass
        except asyncio.TimeoutError:
            try:
                await response.delete()
            except:
                pass
            try:
                await message.delete()
            except: 
                pass
            return await ctx.send("Response timed out :stopwatch:")

    @blacklist.command(name="toggle", aliases=["enable", "disable"])
    @checks.has_permissions("manage_guild")
    async def _toggle(self, ctx, command_or_module: str):
        """Toggle commands/modules on or off from the whole server"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        disabled_commands = serverdata["disabled"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        if not command and not cog:
            return await ctx.send("Invalid command/module :no_entry:")
        if command_or_module in disabled_commands:
            disabled_commands.remove(command_or_module)
            msg = "The {} `{}` is now enabled.".format("command" if command else "module", command_or_module)
        else:
            disabled_commands.append(command_or_module)
            msg = "The {} `{}` is now disabled.".format("command" if command else "module", command_or_module)
        await ctx.send(msg)
        serverdata.update({"disabled": disabled_commands}).run(durability="soft", noreply=True)

    @blacklist.command()
    async def disabled(self, ctx):
        """Shows you a list of all the current disabled commands and modules"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        disabled_commands = serverdata["disabled"].run()
        if not disabled_commands:
            return await ctx.send("This server has no disabled commands :no_entry:")
        modules, commands = [], []
        for x in disabled_commands:
            if self.bot.get_cog(x):
                modules.append(x)
            else:
                commands.append(x)
        s=discord.Embed(colour=ctx.author.colour)
        s.set_author(name="Disabled Commands/Modules")
        s.add_field(name="Modules", value="\n".join(modules) if modules else "None")
        s.add_field(name="Commands", value="\n".join(commands) if commands else "None")
        await ctx.send(embed=s)

    @blacklist.command(name="info", aliases=["stats"])
    async def _info(self, ctx, *, command_or_module: str):
        """Gives you informations about what is blacklisted on a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id)).run()
        try:
            cmddata = list(filter(lambda x: x["id"] == command_or_module, serverdata["commands"]))[0]["blacklisted"]
        except:
            return await ctx.send("Nothing is blacklisted from using this command :no_entry:")
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        if not command and not cog:
            return await ctx.send("Invalid command/module :no_entry:")
        s=discord.Embed(colour=ctx.author.colour)
        s.set_author(name="Blacklist Info for {}".format(command_or_module), icon_url=ctx.guild.icon_url)
        roles, users, channels = "", "", ""
        for x in filter(lambda x: x["type"] == "role", cmddata):
            role = discord.utils.get(ctx.guild.roles, id=int(x["id"]))
            if role:
                roles += "{}\n".format(role.mention)
        for x in filter(lambda x: x["type"] == "user", cmddata):
            user = discord.utils.get(ctx.guild.members, id=int(x["id"]))
            if user:
                users += "{}\n".format(user.mention)
        for x in filter(lambda x: x["type"] == "channel", cmddata):
            channel = discord.utils.get(ctx.guild.channels, id=int(x["id"]))
            if channel:
                channels += "{}\n".format(channel.mention)
        s.add_field(name="Roles", value=roles if roles else "None")
        s.add_field(name="Users", value=users if users else "None")
        s.add_field(name="Channels", value=channels if channels else "None")
        s.set_footer(text="Type: " + ("Command" if command else "Module"))
        await ctx.send(embed=s)

    @commands.group()
    async def whitelist(self, ctx):
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("blacklist").insert({"id": str(ctx.guild.id), "commands": [], "disabled": []}).run(durability="soft")

    @whitelist.command(name="add")
    @checks.has_permissions("manage_guild")
    async def _add__(self, ctx, user_role_channel: str, *, command_or_module: str):
        """Add a user/role/channel to the whitelist for a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        commands = serverdata["commands"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        channel = arg.get_text_channel(ctx, user_role_channel)
        user = arg.get_server_member(ctx, user_role_channel)
        role = arg.get_role(ctx, user_role_channel)
        if not cog and not command:
            return await ctx.send("Invalid command/module :no_entry:")
        if channel:
            if command_or_module not in map(lambda x: x["id"], commands):
                commands.append({"id": command_or_module, "whitelisted": [{"id": str(channel.id), "type": "channel"}], "blacklisted": []})
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                whitelisted = current_commands["whitelisted"]
                if str(channel.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "channel", whitelisted)):
                    return await ctx.send("This channel is already whitelisted from using this {} :no_entry:".format("command" if command else "module"))
                whitelisted.append({"id": str(channel.id), "type": "channel"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "The {} `{}` can now be used in {} overriding blacklists".format("command" if command else "module", command_or_module, channel.mention)
        elif role:
            if command_or_module not in map(lambda x: x["id"], commands):
                commands.append({"id": command_or_module, "whitelisted": [{"id": str(role.id), "type": "role"}], "blacklisted": []})
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                whitelisted = current_commands["whitelisted"]
                if str(role.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "role", whitelisted)):
                    return await ctx.send("This role is already whitelisted from using this {} :no_entry:".format("command" if command else "module"))
                whitelisted.append({"id": str(role.id), "type": "role"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "Anyone in the role **{}** can now use the {} `{}` overriding blacklists".format(role.name, "command" if command else "module", command_or_module)
        elif user:
            if command_or_module not in map(lambda x: x["id"], commands):
                commands.append({"id": command_or_module, "whitelisted": [{"id": str(user.id), "type": "user"}], "blacklisted": []})
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                whitelisted = current_commands["whitelisted"]
                if str(user.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "user", whitelisted)):
                    return await ctx.send("This user is already whitelisted from using this {} :no_entry:".format("command" if command else "module"))
                whitelisted.append({"id": str(user.id), "type": "user"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "**{}** can now use the {} `{}` overriding blacklists".format(user, "command" if command else "module", command_or_module)
        else:
            return await ctx.send("Invalid role/user/channel :no_entry:")
        await ctx.send(msg)
        serverdata.update({"commands": commands}).run(durability="soft", noreply=True)

    @whitelist.command(name="remove")
    @checks.has_permissions("manage_guild")
    async def __remove_(self, ctx, user_role_channel: str, *, command_or_module: str):
        """Remove a user/role/channel from the whitelist for a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        commands = serverdata["commands"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        channel = arg.get_text_channel(ctx, user_role_channel)
        user = arg.get_server_member(ctx, user_role_channel)
        role = arg.get_role(ctx, user_role_channel)
        if not cog and not command:
            return await ctx.send("Invalid command/module :no_entry:")
        if channel:
            if command_or_module not in map(lambda x: x["id"], commands):
                return await ctx.send("This channel is not whitelisted from using this {} :no_entry:".format("command" if command else "module"))
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                whitelisted = current_commands["whitelisted"]
                if str(channel.id) not in map(lambda x: x["id"], filter(lambda x: x["type"] == "channel", whitelisted)):
                    return await ctx.send("This channel is not whitelisted from using this {} :no_entry:".format("command" if command else "module"))
                whitelisted.remove({"id": str(channel.id), "type": "channel"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "The whitelist for the {} `{}` has been removed in {}".format("command" if command else "module", command_or_module, channel.mention)
        elif role:
            if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("You cannot undo a whitelist on a role higher or equal to your own :no_entry:")
            if command_or_module not in map(lambda x: x["id"], commands):
                return await ctx.send("This role is not whitelisted from using this {} :no_entry:".format("command" if command else "module"))
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                whitelisted = current_commands["whitelisted"]
                if str(role.id) not in map(lambda x: x["id"], filter(lambda x: x["type"] == "role", whitelisted)):
                    return await ctx.send("This role is not whitelisted from using this {} :no_entry:".format("command" if command else "module"))
                whitelisted.remove({"id": str(role.id), "type": "role"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "The whitelist for anyone in the role **{}** has been removed for the {} `{}`".format(role.name, "command" if command else "module", command_or_module)
        elif user:
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                return await ctx.send("You cannot undo a whitelist on a user higher or equal to you :no_entry:")
            if command_or_module not in map(lambda x: x["id"], commands):
                return await ctx.send("This user is not whitelisted from using this {} :no_entry:".format("command" if command else "module"))
            else:
                current_commands = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
                blacklisted = current_commands["blacklisted"]
                whitelisted = current_commands["whitelisted"]
                if str(user.id) not in map(lambda x: x["id"], filter(lambda x: x["type"] == "user", whitelisted)):
                    return await ctx.send("This user is not whitelisted from using this {} :no_entry:".format("command" if command else "module"))
                whitelisted.remove({"id": str(user.id), "type": "user"})
                commands.remove(current_commands)
                commands.append({"id": command_or_module, "blacklisted": blacklisted, "whitelisted": whitelisted})
            msg = "The whitelist for **{}** has been removed for the {} `{}`".format(user, "command" if command else "module", command_or_module)
        else:
            return await ctx.send("Invalid role/user/channel :no_entry:")
        await ctx.send(msg)
        serverdata.update({"commands": commands}).run(durability="soft", noreply=True) 

    @whitelist.command(name="delete")
    @checks.has_permissions("manage_guild")
    async def __delete_(self, ctx, *, command_or_module: str):
        """Delete all the whitelist data on a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        commands = serverdata["commands"].run()
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        if not command and not cog:
            return await ctx.send("Invalid command/module :no_entry:")
        if command_or_module not in map(lambda x: x["id"], commands):
            return await ctx.send("This command is not whitelisted for any role/user/channel :no_entry:")
        cmddata = list(filter(lambda x: x["id"] == command_or_module, commands))[0]
        commands.remove(cmddata)
        cmddata["whitelisted"] = []
        commands.append(cmddata)
        await ctx.send("All whitelist data for `{}` has been deleted".format(command_or_module))
        serverdata.update({"commands": commands}).run(durability="soft", noreply=True) 

    @whitelist.command(name="reset")
    @checks.has_permissions("manage_guild")
    async def __reset_(self, ctx):
        """Delete all whitelist data that you've set"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id))
        message = await ctx.send("This will reset all your whitelist data that you've set are you sure you want to do this?\nYes or No")
        def check(m):
            return ctx.author == m.author and m.channel == ctx.channel
        try:
            response = await self.bot.wait_for("message", check=check, timeout=30)
            if response.content.lower() in ["yes", "y"]:
                try:
                   await response.delete()
                except:
                    pass
                try:
                   await message.delete()
                except: 
                    pass
                await ctx.send("All whitelist data has been deleted")
                commands = []
                for x in serverdata["commands"].run():
                    x["whitelisted"] = []
                    commands.append(x)
                serverdata.update({"commands": commands}).run(durability="soft", noreply=True) 
            else:
                try:
                   await response.delete()
                except:
                    pass
                try:
                   await message.delete()
                except: 
                    pass
        except asyncio.TimeoutError:
            try:
                await response.delete()
            except:
                pass
            try:
                await message.delete()
            except: 
                pass
            return await ctx.send("Response timed out :stopwatch:")

    @whitelist.command(name="info", aliases=["stats"])
    async def _info_(self, ctx, *, command_or_module: str):
        """Gives you informations about what is whitelisted on a specific command/module"""
        serverdata = r.table("blacklist").get(str(ctx.guild.id)).run()
        try:
            cmddata = list(filter(lambda x: x["id"] == command_or_module, serverdata["commands"]))[0]["whitelisted"]
        except:
            return await ctx.send("Nothing is whitelisted from using this command :no_entry:")
        command = self.bot.get_command(command_or_module)
        cog = self.bot.get_cog(command_or_module)
        if not command and not cog:
            return await ctx.send("Invalid command/module :no_entry:")
        s=discord.Embed(colour=ctx.author.colour)
        s.set_author(name="Whitelist Info for {}".format(command_or_module), icon_url=ctx.guild.icon_url)
        roles, users, channels = "", "", ""
        for x in filter(lambda x: x["type"] == "role", cmddata):
            role = discord.utils.get(ctx.guild.roles, id=int(x["id"]))
            if role:
                roles += "{}\n".format(role.mention)
        for x in filter(lambda x: x["type"] == "user", cmddata):
            user = discord.utils.get(ctx.guild.members, id=int(x["id"]))
            if user:
                users += "{}\n".format(user.mention)
        for x in filter(lambda x: x["type"] == "channel", cmddata):
            channel = discord.utils.get(ctx.guild.channels, id=int(x["id"]))
            if channel:
                channels += "{}\n".format(channel.mention)
        s.add_field(name="Roles", value=roles if roles else "None")
        s.add_field(name="Users", value=users if users else "None")
        s.add_field(name="Channels", value=channels if channels else "None")
        s.set_footer(text="Type: " + ("Command" if command else "Module"))
        await ctx.send(embed=s)


    @commands.group(aliases=["imgperms", "imgpermissions", "imaginaryperms", "imaginarypermissions", "fakeperms"])
    async def fakepermissions(self, ctx):
        """Allow users or roles to have permissions on the bot but not anywhere else"""
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("fakeperms").insert({"id": str(ctx.guild.id), "users": [], "roles": []}).run(durability="soft")

    @fakepermissions.command()
    @checks.has_permissions("administrator")
    async def add(self, ctx, user_or_role: str, *permissions):
        """Add permissions to a user or role"""
        data = r.table("fakeperms").get(str(ctx.guild.id))
        value, successfulperms = 0, []
        user = arg.get_server_member(ctx, user_or_role)
        role = arg.get_role(ctx, user_or_role)
        if user:
            if permissions:
                for x in permissions:
                    if data["users"].filter(lambda x: x["id"] == str(user.id)).run(durability="soft"):
                        if x in map(lambda x: x[0], filter(lambda x: x[1] == True, discord.Permissions(data["users"].filter(lambda x: x["id"] == str(user.id))[0]["perms"].run(durability="soft")))):
                            pass
                        else:
                            try:
                                value += permsjson[x]
                                successfulperms.append(x)
                            except: 
                                pass
                    else:
                        try:
                            value += permsjson[x]
                            successfulperms.append(x)
                        except: 
                            pass
                if value == 0:
                    return await ctx.send("None of the permissions you gave in the argument were valid/the user or role didn't have them, make sure they are formatted like so `manage_messages`, `manage_guild` :no_entry:")
            if str(user.id) not in data["users"].map(lambda x: x["id"]).run(durability="soft"):
                perms = {"id": str(user.id), "perms": value}
                data.update({"users": r.row["users"].append(perms)}).run(durability="soft")
            else:
                data.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"perms": x["perms"] + value}), x))}).run(durability="soft")
            await ctx.send("**{}** now can use commands with the required permissions of {}".format(user, ", ".join(successfulperms)))
        elif role:
            if permissions:
                for x in permissions:
                    if data["roles"].filter(lambda x: x["id"] == str(role.id)).run(durability="soft"):
                        try:
                            if x in map(lambda x: x[0], filter(lambda x: x[1] == True, discord.Permissions(data["roles"].filter(lambda x: x["id"] == str(role.id))[0]["perms"].run(durability="soft")))):
                                pass
                        except:
                            pass
                        else:
                            try:
                                value += permsjson[x]
                                successfulperms.append(x)
                            except: 
                                pass
                    else:
                        try:
                            value += permsjson[x]
                            successfulperms.append(x)
                        except: 
                            pass
                if value == 0:
                    return await ctx.send("None of the permissions you gave in the argument were valid/the user or role didn't have them, make sure they are formatted like so `manage_messages`, `manage_guild` :no_entry:")
            if str(role.id) not in data["roles"].map(lambda x: x["id"]).run(durability="soft"):
                perms = {"id": str(role.id), "perms": value}
                data.update({"roles": r.row["roles"].append(perms)}).run(durability="soft")
            else:
                data.update({"roles": r.row["roles"].map(lambda x: r.branch(x["id"] == str(role.id), x.merge({"perms": x["perms"] + value}), x))}).run(durability="soft")
            await ctx.send("**{}** now can use commands with the required permissions of {}".format(role, ", ".join(successfulperms)))
        else:
            return await ctx.send("Invalid role/user :no_entry:")

    @fakepermissions.command()
    @checks.has_permissions("administrator")
    async def remove(self, ctx, user_or_role: str, *permissions):
        """Remove permissions from a user or role"""
        data = r.table("fakeperms").get(str(ctx.guild.id))
        value, successfulperms = 0, []
        user = arg.get_server_member(ctx, user_or_role)
        role = arg.get_role(ctx, user_or_role)
        if user:
            if not data["users"].filter(lambda x: x["id"] == str(user.id)).run(durability="soft"):
                return await ctx.send("This user does not have any set permissions to remove :no_entry:")
            if permissions:
                for x in permissions:
                    if x not in map(lambda x: x[0], filter(lambda x: x[1] == True, discord.Permissions(data["users"].filter(lambda x: x["id"] == str(user.id))[0]["perms"].run(durability="soft")))):
                        pass
                    else:
                        try:
                            value += permsjson[x]
                            successfulperms.append(x)
                        except: 
                            pass
                if value == 0:
                    return await ctx.send("None of the permissions you gave in the argument were valid/the user or role didn't have them, make sure they are formatted like so `manage_messages`, `manage_guild` :no_entry:")
            else:
                return await ctx.send("Permissions are a required argument :no_entry:")
            if str(user.id) not in data["users"].map(lambda x: x["id"]).run(durability="soft"):
                perms = {"id": str(user.id), "perms": value}
                data.update({"users": r.row["users"].append(perms)}).run(durability="soft")
            else:
                data.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"perms": x["perms"] - value}), x))}).run(durability="soft")
            await ctx.send("**{}** now can't use commands with the required permissions of {}".format(user, ", ".join(successfulperms)))
        elif role:
            if not data["roles"].filter(lambda x: x["id"] == str(role.id)).run(durability="soft"):
                return await ctx.send("This user does not have any set permissions to remove :no_entry:")
            if permissions:
                for x in permissions:
                    if x not in map(lambda x: x[0], filter(lambda x: x[1] == True, discord.Permissions(data["roles"].filter(lambda x: x["id"] == str(role.id))[0]["perms"].run(durability="soft")))):
                        pass
                    else:
                        try:
                            value += permsjson[x]
                            successfulperms.append(x)
                        except: 
                            pass
                if value == 0:
                    return await ctx.send("None of the permissions you gave in the argument were valid/the user or role didn't have them, make sure they are formatted like so `manage_messages`, `manage_guild` :no_entry:")
            else:
                return await ctx.send("Permissions are a required argument :no_entry:")
            if str(role.id) not in data["roles"].map(lambda x: x["id"]).run(durability="soft"):
                perms = {"id": str(role.id), "perms": value}
                data.update({"roles": r.row["roles"].append(perms)}).run(durability="soft")
            else:
                data.update({"roles": r.row["roles"].map(lambda x: r.branch(x["id"] == str(role.id), x.merge({"perms": x["perms"] - value}), x))}).run(durability="soft")
            await ctx.send("**{}** now can't use commands with the required permissions of {}".format(role, ", ".join(successfulperms)))
        else:
            return await ctx.send("Invalid role/user :no_entry:")

    @fakepermissions.command()
    async def info(self, ctx, user_or_role: str):
        """Get the fake permissions of a user or role"""
        data = r.table("fakeperms").get(str(ctx.guild.id))
        user = arg.get_server_member(ctx, user_or_role)
        role = arg.get_role(ctx, user_or_role)
        if user:
            if data["users"].filter(lambda x: x["id"] == str(user.id)).run(durability="soft"):
                perms = "\n".join(map(lambda x: x[0].replace("_", " ").title(), filter(lambda x: x[1] == True, discord.Permissions(data["users"].filter(lambda x: x["id"] == str(user.id))[0]["perms"].run(durability="soft") | user.guild_permissions.value))))
            else:
                perms = None
            s=discord.Embed(colour=user.colour)
            s.set_author(name=user.name, icon_url=user.avatar_url)
            s.add_field(name="Permissions", value=perms if perms else "None")
        elif role:
            if data["roles"].filter(lambda x: x["id"] == str(role.id)).run(durability="soft"):
                perms = "\n".join(map(lambda x: x[0].replace("_", " ").title(), filter(lambda x: x[1] == True, discord.Permissions(data["roles"].filter(lambda x: x["id"] == str(role.id))[0]["perms"].run(durability="soft") | role.permissions.value))))
            else:
                perms = None
            s=discord.Embed(colour=role.colour)
            s.set_author(name=role.name, icon_url=ctx.guild.icon_url)
            s.add_field(name="Permissions", value=perms if perms else "None")
        else:
            return await ctx.send("Invalid role/user :no_entry:")
        await ctx.send(embed=s)

    @fakepermissions.command(name="list")
    async def __list(self, ctx):
        """Lists all supported permissions you can use"""
        s=discord.Embed(description="\n".join(list(map(lambda x: x[0], discord.Permissions()))))
        s.set_author(name="Supported Permissions", icon_url=self.bot.user.avatar_url)
        s.set_footer(text="manage_guild is equivilant to manage_server")
        await ctx.send(embed=s)

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
        await channel.edit(slowmode_delay=time_interval)
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
                s.add_field(name="Server Prefixes", value="{}".format(", ".join(serverdata["prefixes"].run(durability="soft")) if serverdata["prefixes"].run(durability="soft") else "None"), inline=False)
            except:
                s.add_field(name="Server Prefixes", value="None", inline=False)
            try:
                s.add_field(name="{}'s Prefixes".format(ctx.author.name), value="{}".format(", ".join(authordata["prefixes"].run(durability="soft") if authordata["prefixes"].run(durability="soft") else "None")), inline=False)
            except:
                s.add_field(name="{}'s Prefixes".format(ctx.author.name), value="None", inline=False)
            await ctx.send(embed=s, content="For help on setting the prefix use `{}help prefix`".format(ctx.prefix))
        else:
            r.table("prefix").insert({"id": str(ctx.author.id), "prefixes": []}).run(durability="soft")
            r.table("prefix").insert({"id": str(ctx.guild.id), "prefixes": []}).run(durability="soft")

    @prefix.command()
    async def self(self, ctx, *prefixes):
        "Set a prefix or multiple for yourself on the bot"
        prefixes = [x for x in prefixes if x != "" and x != " "]
        authordata = r.table("prefix").get(str(ctx.author.id))
        if len(prefixes) == 0:
            authordata.update({"prefixes": []}).run(durability="soft")
            await ctx.send("Your prefixes have been reset <:done:403285928233402378>")
        else:
            authordata.update({"prefixes": list(set(prefixes))}).run(durability="soft")
            if len(prefixes) > 1:
                await ctx.send("Your prefixes have been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))
            else:
                await ctx.send("Your prefix has been set to `{}` <:done:403285928233402378>".format(", ".join(prefixes)))

    @prefix.command()
    @checks.has_permissions("manage_guild")
    async def server(self, ctx, *prefixes):
        """Set a prefix for the server you're in"""
        prefixes = [x for x in prefixes if x != "" and x != " "]
        serverdata = r.table("prefix").get(str(ctx.guild.id))
        if len(prefixes) == 0:
            serverdata.update({"prefixes": []}).run(durability="soft")
            await ctx.send("The server prefixes have been reset <:done:403285928233402378>")
        else:
            serverdata.update({"prefixes": list(set(prefixes))}).run(durability="soft")
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
    async def massmove(self, ctx, from_channel: str, to_channel: str):
        """Mass move users from one channel to another"""
        author = ctx.author
        server = ctx.guild
        from_channel = arg.get_voice_channel(ctx, from_channel)
        to_channel = arg.get_voice_channel(ctx, to_channel)
        if not from_channel or not to_channel:
            return await ctx.send("One or both of your voice channel arguments are incorrect :no_entry:")
        i = 0
        if len(from_channel.members) == 0:
            await ctx.send("There is no one in that voice channel :no_entry:")
            return
        for user in [x for x in from_channel.members if x not in to_channel.members]:
            await user.edit(voice_channel=to_channel, reason="Massmove") 
            i = i + 1
        await ctx.send("Moved **{}** member{} from `{}` to `{}`".format(i, "s" if i != 1 else "", from_channel.name, to_channel.name))
        
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
        author = ctx.author
        if not nickname:
            nickname = user.name
        if author.top_role.position <= user.top_role.position and author != ctx.guild.owner:
            return await ctx.send("You cannot rename someone higher or equal than your top role :no_entry:")
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
            await ctx.send("I do not have the `manage_messages` permission")
            return
        if amount is None:
            amount = 100
        elif amount > 100:
            amount = 100
        try:
            deleted = await channel.purge(limit=amount, before=ctx.message, check=lambda m: m.author == user)
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        except:
            pass
        
    @commands.command(aliases=["bc"])
    @checks.has_permissions("manage_messages")
    async def botclean(self, ctx, limit: int=None):
        """Clears all bot messages"""
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `manage_messages` permission")
            return
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message, check=lambda e: e.author.bot)
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        except:
            pass

    @commands.command()
    @checks.has_permissions("manage_messages")
    async def contains(self, ctx, word: str, limit: int=None):
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `manage_messages` permission")
            return
        if limit is None:
            limit = 100
        elif limit > 100:
            limit = 100
        def check(m):
            return word.lower() in m.content.lower()
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message, check=check)
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        except:
            pass
        
    @commands.command(aliases=["prune"])
    @checks.has_permissions("manage_messages")
    async def purge(self, ctx, limit: int=None):
        """Purges a certain amount of messages"""
        channel = ctx.channel
        server = ctx.guild
        has_permissions = channel.permissions_for(ctx.me).manage_messages
        if not has_permissions:
            await ctx.send("I do not have the `manage_messages` permission")
            return
        if limit is None:
            limit = 10
        elif limit > 100:
            limit = 100
        try:
            deleted = await channel.purge(limit=limit, before=ctx.message)
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.send("I cannot delete messages 14 days or older :no_entry:")
            return
        except:
            pass
            
    @commands.group()
    async def modlog(self, ctx):
        """Have logs for all mod actions"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("modlogs").insert({"id": str(server.id), "channel": None, "toggle": False, "case#": 0, "case": []}).run(durability="soft")
        
            
    @modlog.command()
    @checks.has_permissions("manage_roles")
    async def toggle(self, ctx):
        """Toggle modlogs on or off"""
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        if serverdata["toggle"].run(durability="soft") == True:
            serverdata.update({"toggle": False}).run(durability="soft")
            await ctx.send("Modlogs are now disabled.")
            return
        if serverdata["toggle"].run(durability="soft") == False:
            serverdata.update({"toggle": True}).run(durability="soft")
            await ctx.send("Modlogs are now enabled.")
            return
            
    @modlog.command() 
    @checks.has_permissions("manage_roles")
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where you want modlogs to be posted"""
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id))
        serverdata.update({"channel": str(channel.id)}).run(durability="soft") 
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
            case.run(durability="soft")
        except:
            await ctx.send("Invalid case number :no_entry:")
            return
        if case["mod"].run(durability="soft") is not None and case["mod"].run(durability="soft") != str(author.id):
            await ctx.send("You do not have ownership of that log :no_entry:")
            return
        try:
            channel = self.bot.get_channel(int(serverdata["channel"].run(durability="soft")))
        except:
            await ctx.send("The modlog channel no longer exists :no_entry:")
            return
        try:
            message = await channel.get_message(int(case["message"].run(durability="soft")))
        except:
            await ctx.send("I am unable to find that case :no_entry:")
            return
        try:
            s=discord.Embed(title="Case {} | {}".format(case_number, case["action"].run(durability="soft")), timestamp=datetime.datetime.fromtimestamp(case["time"].run(durability="soft")))
        except:
            s=discord.Embed(title="Case {} | {}".format(case_number, case["action"].run(durability="soft")))
        s.add_field(name="User", value=await self.bot.get_user_info(int(case["user"].run(durability="soft"))))
        s.add_field(name="Moderator", value=author, inline=False)
        serverdata.update({"case": r.row["case"].map(lambda x: r.branch(x["id"] == case_number, x.merge({"mod": str(author.id)}), x))}).run(durability="soft")
        s.add_field(name="Reason", value=reason)
        serverdata.update({"case": r.row["case"].map(lambda x: r.branch(x["id"] == case_number, x.merge({"reason": reason}), x))}).run(durability="soft")
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
            if case["reason"].run(durability="soft") is None:
                reason = "None (Update using `s?modlog case {} <reason>`)".format(case_number)
            else:
                reason = case["reason"].run(durability="soft")
            if case["mod"].run(durability="soft") is None:
                author = "Unknown"
            else:
                author = await self.bot.get_user_info(case["mod"].run(durability="soft"))
            s=discord.Embed(title="Case {} | {}".format(case_number, case["action"].run(durability="soft")), timestamp=datetime.datetime.fromtimestamp(case["time"].run(durability="soft")))
            s.add_field(name="User", value=await self.bot.get_user_info(int(case["user"].run(durability="soft"))))
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
        serverdata.update({"case#": 0, "case": []}).run(durability="soft")
        await ctx.send("All cases have been reset <:done:403285928233402378>")

    @modlog.command()
    async def stats(self, ctx):
        server = ctx.guild
        serverdata = r.table("modlogs").get(str(server.id)).run(durability="soft")
        s=discord.Embed(colour=0xffff00)
        s.set_author(name="Mod-Log Settings", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Status", value="Enabled" if serverdata["toggle"] else "Disabled")
        s.add_field(name="Channel", value=self.bot.get_channel(int(serverdata["channel"])).mention if serverdata["channel"] else "Not set")
        s.add_field(name="Number of Cases", value=serverdata["case#"])
        await ctx.send(embed=s)
        
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
    async def addrole(self, ctx, user: discord.Member, *, role: str):
        """Add a role to a user"""
        author = ctx.message.author
        server = ctx.message.guild
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        if role.position > author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not add a role to a user which is higher than your own role :no_entry:")
                return
        if user is None:
            user = author
        if role in user.roles:
            await ctx.send("The user already has the role `{}` :no_entry:".format(role.name))
            return
        try:
            await user.add_roles(role)
            await ctx.send("**{}** has been added to **{}** <:done:403285928233402378>:ok_hand:".format(role, user))
        except discord.errors.Forbidden:
            await ctx.send("I'm not able to add the role to the user :no_entry:")
        
    @commands.command(aliases=["rr"]) 
    @checks.has_permissions("manage_roles")
    async def removerole(self, ctx, user: discord.Member, *, role: str):
        """Remove a role from a user"""
        author = ctx.message.author
        server = ctx.guild
        role = arg.get_role(ctx, role)
        if not role:
            return await ctx.send("I could not find that role :no_entry:")
        if role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            if author == server.owner:
                pass
            else:
                await ctx.send("You can not remove a role from a user higher than your own role :no_entry:")
                return
        if user is None:
            user = author
        if not role in user.roles:
            await ctx.send("The user doesn't have the role `{}` :no_entry:".format(role.name))
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
                await _log(self.bot, author, server, action, reason, user)
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
    @commands.cooldown(1, 3, commands.BucketType.user)
    @checks.has_permissions("ban_members")
    async def ban(self, ctx, user, *, reason: str = None):
        """Bans a user."""
        notinserver = False
        user = await arg.get_member(ctx, user)
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
                await _log(self.bot, author, server, action, reason, user)
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
    @commands.cooldown(1, 3, commands.BucketType.user)
    @checks.has_permissions("ban_members")
    async def unban(self, ctx, user, *, reason: str=None):
        """unbans a user by ID and will notify them about the unbanning in pm"""
        author = ctx.message.author 
        server = ctx.message.guild
        channel = ctx.message.channel
        action = "Unban"
        user = await arg.get_member(ctx, user)
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
            await _log(self.bot, author, server, action, reason, user)
        except:
            pass
        try:
            await user.send(embed=s)
        except:
            pass

    @dev.log   
    async def on_member_ban(self, guild, user):
        author = None
        for x in await guild.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.ban:
                author = x.user
                if x.reason != "":
                    reason = x.reason
                else:
                    reason = None
        action = "Ban"
        server = guild
        try:
            await _log(self.bot, author, server, action, reason, user)
        except:
            pass

    @dev.log           
    async def on_member_unban(self, guild, user):
        author = None
        for x in await guild.audit_logs(limit=1).flatten():
            if x.action == discord.AuditLogAction.unban:
                author = x.user
                if x.reason != "":
                    reason = x.reason
                else:
                    reason = None
        action = "Unban"
        server = guild
        try:
            await _log(self.bot, author, server, action, reason, user)
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
            await _log(self.bot, author, server, action, reason, user)
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
            await _log(self.bot, author, server, action, reason, user)
        except:
            pass

    @dev.log
    async def on_member_join(self, member):
        server = member.guild
        serverdata = r.table("mute").get(str(server.id))
        user = serverdata["users"].filter(lambda x: x["id"] == str(member.id))[0].run()
        try:
            if user["toggle"] == True:
                role = discord.utils.get(server.roles, name="Muted - Sx4")
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
        r.table("mute").insert({"id": str(server.id), "users": []}).run(durability="soft")
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
            await _log(self.bot, author, server, action, reason, user)
        except:
            pass
        if str(user.id) not in serverdata["users"].map(lambda x: x["id"]).run(durability="soft"):
            userobj = {}
            userobj["id"] = str(user.id)
            userobj["toggle"] = True
            userobj["amount"] = time2
            userobj["time"] = ctx.message.created_at.timestamp()
            serverdata.update({"users": r.row["users"].append(userobj)}).run(durability="soft")
        else:
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": ctx.message.created_at.timestamp(), "amount": time2, "toggle": True}), x))}).run(durability="soft")
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
            await _log(self.bot, author, server, action, reason, user)
        except:
            pass
        serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": None, "amount": None, "toggle": False}), x))}).run(durability="soft")
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
            for data in serverdata["users"].run(durability="soft"):
                if data["toggle"] == True:
                    i += 1
        except: 
            await ctx.send("No one is muted in this server :no_entry:")
            return
        if i == 0:   
            await ctx.send("No one is muted in this server :no_entry:")
            return
        for data in serverdata["users"].run(durability="soft"):
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
            if str(user.id) not in serverdata["users"].map(lambda x: x["id"]).run(durability="soft"):
                pass
            else:
                serverdata.update({"users": r.row["users"].filter(lambda x: x["id"] != str(user.id))}).run(durability="soft", noreply=True)
            for x in await server.audit_logs(limit=1).flatten():
                if x.action == discord.AuditLogAction.member_role_update:
                    author = x.user
                    if x.reason != "":
                        reason = x.reason
            if author == self.bot.user:
                return
            action = "Unmute"
            try:
                await _log(self.bot, author, server, action, reason, user)
            except:
                pass
        if role in after.roles and role not in before.roles:
            for x in await server.audit_logs(limit=1).flatten():
                if x.action == discord.AuditLogAction.member_role_update:
                    author = x.user
                    if x.reason != "":
                        reason = x.reason
            if author == self.bot.user:
                return
            action = "Mute (Infinite)"
            try:
                await _log(self.bot, author, server, action, reason, user)
            except:
                pass

    @dev.log      
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

    @commands.group()
    async def warnconfig(self, ctx):
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("warn").insert({"id": str(ctx.guild.id), "users": [], "punishments": True, "config": []}).run(durability="soft")

    @warnconfig.command()
    @checks.has_permissions("manage_guild")
    async def punishments(self, ctx):
        """Toggles whether you want punishments for warnings or not (Defaults at True)"""
        serverdata = r.table("warn").get(str(ctx.guild.id))
        if serverdata["punishments"].run() == True:
            await ctx.send("Punishments for warnings are now disabled.")
            return serverdata.update({"punishments": False}).run(durability="soft")
        elif serverdata["punishments"].run() == False:
            await ctx.send("Punishments for warnings are now enabled.")
            return serverdata.update({"punishments": True}).run(durability="soft")

    @warnconfig.command(name="set", aliases=["add"])
    @checks.has_permissions("manage_guild")
    async def _set(self, ctx, warning_number: int, *, action: str):
        """Sets an action for a specific warning a user is on, if it's a mute and you want to add a customized time add a time ('30m', '1h 30m' etc) after 'mute'"""
        serverdata = r.table("warn").get(str(ctx.guild.id))
        if warning_number <= 0 or warning_number > 50:
            return await ctx.send("Warnings have to be more than 0 but less than 50 :no_entry:")
        if action.lower() in ["mute", "kick", "ban"] or "mute" in action.lower():
            time = 0
            final = serverdata["config"].run()
            if "mute" == action.lower():
                action = "mute"
                time = 1800
                configdb = {"warning": warning_number, "action": action, "time": time}
            elif "mute" in action.lower():
                try:
                    time = ctime.convert(action.split(" ", 1)[1])
                except ValueError:
                    return await ctx.send("Make sure the mute time is formatted something like this `4d 3h 2m 1s` :no_entry:")
                action = "mute"
                if time <= 0:
                    return await ctx.send("Time has to be more than 0 seconds :no_entry:")
                configdb = {"warning": warning_number, "action": action, "time": time}
            elif "kick" == action.lower():
                action = "kick"
                configdb = {"warning": warning_number, "action": action}
            elif "ban" == action.lower(): 
                action = "ban"   
                configdb = {"warning": warning_number, "action": action}
            if warning_number in serverdata["config"].map(lambda x: x["warning"]).run():
                current = serverdata["config"].filter(lambda x: x["warning"] == warning_number)[0].run()
                final.remove(current)
            final.append(configdb)
            await ctx.send("Warning #{} will now {} the user {}".format(warning_number, action, "for {}".format(self.format_mute(time)) if action == "mute" else ""))
            serverdata.update({"config": final}).run(durability="soft")
        else:
            return await ctx.send("Invalid Action, make sure it is mute, kick or ban :no_entry:")

    @warnconfig.command(name="remove")
    @checks.has_permissions("manage_guild")
    async def _remove(self, ctx, warning_number: int):
        """Removes a warning from your warn configuration"""
        serverdata = r.table("warn").get(str(ctx.guild.id))
        if not serverdata["config"].run():
            return await ctx.send("Warnings have not been set up in this server :no_entry:")
        try:
            warning = serverdata["config"].filter(lambda x: x["warning"] == warning_number)[0].run()
        except:
            return await ctx.send("That warning number is not set up to an action :no_entry:")
        await ctx.send("Warning #{} has been removed.".format(warning_number))
        serverdata.update({"config": r.row["config"].filter(lambda x: x["warning"] != warning_number)}).run(durability="soft")

    @warnconfig.command(name="reset")
    @checks.has_permissions("manage_guild")
    async def _reset(self, ctx):
        """Resets all your data for warns you have set up in the server"""
        serverdata = r.table("warn").get(str(ctx.guild.id))
        await ctx.send("All set warnings have been reset.")
        serverdata.update({"config": []}).run(durability="soft")

    @warnconfig.command(name="list")
    async def _list(self, ctx):
        """Shows you how your warn configuration is set up"""
        serverdata = r.table("warn").get(str(ctx.guild.id)).run()
        if not serverdata["config"]:
            return await ctx.send("Warnings have not been set up in this server :no_entry:")
        data = sorted(serverdata["config"], key=lambda x: x["warning"])
        msg = "\n".join(["Warning #{}: {} {}".format(x["warning"], x["action"].title(), "(" + self.format_mute(x["time"]) + ")" if x["action"] == "mute" else "") for x in data])
        s=discord.Embed(description=msg)
        s.set_author(name="Warn Configuration", icon_url=ctx.guild.icon_url)
        s.set_footer(text="If a warning number isn't shown it means that warning will give a text warning")
        await ctx.send(embed=s)
        
    @commands.command(no_pm=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @checks.has_permissions("manage_messages")
    async def warn(self, ctx, user: str, *, reason: str=None):
        """Warns a user in pm, a reason is also optional."""
        author = ctx.author
        server = ctx.guild
        channel = ctx.channel
        user = arg.get_server_member(ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        if user.bot:
            return await ctx.send("You cannot warn bots :no_entry:")
        if user == author:
            await ctx.send("You can not warn yourself :no_entry:")
            return
        if user.top_role.position >= author.top_role.position and ctx.author != ctx.guild.owner:
            return await ctx.send("You can not warn someone higher than your own role :no_entry:")
        self._create_warn(server, user)
        serverdata = r.table("warn").get(str(server.id))
        userdata = serverdata["users"].filter({"id": str(user.id)})[0]
        punishments = serverdata["punishments"].run()
        config = serverdata["config"].run()
        userwarns = userdata["warnings"].run()
        if punishments:
            if not config:
                config = [{"warning": 1, "action": None}, {"warning": 2, "action": "mute", "time": 1800}, {"warning": 3, "action": "kick"}, {"warning": 4, "action": "ban"}]
            maxwarning = sorted(config, key=lambda x: x["warning"], reverse=True)[0]
            if userwarns + 1 > maxwarning["warning"]:
                currentwarning = {"warning": userwarns + 1, "action": maxwarning["action"]}
                nextwarning = {"warning": userwarns + 2, "action": None}
            else:
                try:
                    currentwarning = list(filter(lambda x: x["warning"] == userwarns + 1, config))[0]
                except IndexError:
                    currentwarning = {"warning": userwarns + 1, "action": None}
                try:
                    nextwarning = list(filter(lambda x: x["warning"] == userwarns + 2, config))[0]
                except IndexError:
                    nextwarning = {"warning": userwarns + 2, "action": None}
            if not currentwarning["action"]:
                await ctx.send("**{}** has been warned ({} warning) :warning:".format(user, self.suffix(currentwarning["warning"])))
                s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name="You have been warned in {}".format(server.name), icon_url=server.icon_url)
                s.add_field(name="Reason", value=reason if reason else "None Given", inline=False)
                s.add_field(name="Moderator", value=author)
                s.add_field(name="Next Action", value=nextwarning["action"].title() + (" (" + self.format_mute(nextwarning["time"]) + ")" if nextwarning["action"] == "mute" else "") if nextwarning["action"] else "None")
                action = "Warn ({} Warning)".format(self.suffix(currentwarning["warning"]))
            elif currentwarning["action"] == "mute":
                r.table("mute").insert({"id": str(server.id), "users": []}).run(durability="soft")
                mutedata = r.table("mute").get(str(server.id))
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
                time = currentwarning["time"]
                try:
                    await user.add_roles(role)
                    if str(user.id) not in mutedata["users"].map(lambda x: x["id"]).run(durability="soft"):
                        user2 = {}
                        user2["id"] = str(user.id)
                        user2["toggle"] = True
                        user2["amount"] = time
                        user2["time"] = ctx.message.created_at.timestamp()
                        mutedata.update({"users": r.row["users"].append(user2)}).run(durability="soft")
                    else:
                        mutedata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"time": ctx.message.created_at.timestamp(), "amount": time, "toggle": True}), x))}).run(durability="soft")
                except: 
                    return await ctx.send("I cannot add the mute role to the user :no_entry:")
                await ctx.send("**{}** has been muted for {} ({} warning) <:done:403285928233402378>".format(user, self.format_mute(time), self.suffix(currentwarning["warning"])))
                s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name="You have been muted in {}".format(server.name), icon_url=server.icon_url)
                s.add_field(name="Reason", value=reason if reason else "None Given", inline=False)
                s.add_field(name="Moderator", value=author)
                s.add_field(name="Next Action", value=nextwarning["action"].title() + (" (" + self.format_mute(nextwarning["time"]) + ")" if nextwarning["action"] == "mute" else "") if nextwarning["action"] else "None")
                action = "Mute {} ({} Warning)".format(self.format_mute(time), self.suffix(currentwarning["warning"]))
            elif currentwarning["action"] == "kick":
                if not checks.has_permissions("kick_members").__closure__[0].cell_contents(ctx):
                    return await ctx.send("You need the kick_members permission to warrn this user again :no_entry:")
                try:
                    await server.kick(user, reason="Kick made by {}".format(author))
                except:
                    return await ctx.send("I'm not able to kick that user :no_entry:")
                await ctx.send("**{}** has been kicked ({} warning) <:done:403285928233402378>".format(user, self.suffix(currentwarning["warning"])))
                s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name="You have been kicked from {}".format(server.name), icon_url=server.icon_url)
                s.add_field(name="Reason", value=reason if reason else "None Given", inline=False)
                s.add_field(name="Moderator", value=author)
                s.add_field(name="Next Action", value=nextwarning["action"].title() + (" (" + self.format_mute(nextwarning["time"]) + ")" if nextwarning["action"] == "mute" else "") if nextwarning["action"] else "None")
                action = "Kick ({} Warning)".format(self.suffix(currentwarning["warning"]))
            elif currentwarning["action"] == "ban":
                if not checks.has_permissions("ban_members").__closure__[0].cell_contents(ctx):
                    return await ctx.send("You need the ban_members permission to warrn this user again :no_entry:")
                try:
                    await server.ban(user, reason="Ban made by {}".format(author))
                except:
                    await ctx.send("I'm not able to ban that user :no_entry:")
                    return
                await ctx.send("**{}** has been banned ({} warning) <:done:403285928233402378>".format(user, self.suffix(currentwarning["warning"])))
                s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name="You have been banned from {}".format(server.name), icon_url=server.icon_url)
                s.add_field(name="Reason", value=reason if reason else "None Given", inline=False)
                s.add_field(name="Moderator", value=author)
                s.add_field(name="Next Action", value=nextwarning["action"].title() + (" (" + self.format_mute(nextwarning["time"]) + ")" if nextwarning["action"] == "mute" else "") if nextwarning["action"] else "None")
                action = "Ban ({} Warning)".format(self.suffix(currentwarning["warning"]))
            try:
                await _log(self.bot, author, server, action, reason, user)
            except:
                pass
            try:
                await user.send(embed=s)
            except:
                pass
            if maxwarning["warning"] <= currentwarning["warning"]:
                return serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": 0, "reasons": (x["reasons"] if not reason else x["reasons"].append(reason))}), x))}).run(durability="soft")
            else:
                return serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": x["warnings"] + 1, "reasons": (x["reasons"] if not reason else x["reasons"].append(reason))}), x))}).run(durability="soft")
        else:
            currentwarning = {"warning": userwarns + 1, "action": None}
            await ctx.send("**{}** has been warned ({} warning) :warning:".format(user, self.suffix(currentwarning["warning"])))
            s=discord.Embed(colour=0xfff90d, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name="You have been warned in {}".format(server.name), icon_url=server.icon_url)
            s.add_field(name="Reason", value=reason if reason else "None Given", inline=False)
            s.add_field(name="Moderator", value=author)
            s.add_field(name="Next Action", value="None")
            action = "Warn ({} Warning)".format(self.suffix(currentwarning["warning"]))
            try:
                await _log(self.bot, author, server, action, reason, user)
            except:
                pass
            try:
                await user.send(embed=s)
            except:
                pass
            return serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": x["warnings"] + 1, "reasons": x["reasons"].append(reason if reason else "No Reason")}), x))}).run(durability="soft")
            
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
            if page > math.ceil(len(list(filter(lambda x: int(x["id"]) in map(lambda x: x.id, server.members) and x["warnings"] != 0, r.table("warn").get(str(server.id))["users"].run(durability="soft"))))/20):
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
    async def warnings(self, ctx, *, user: discord.Member): 
        """Check how many warnings a specific user is on"""
        server = ctx.message.guild
        serverdata = r.table("warn").get(str(server.id))
        try:
            userdata = serverdata["users"].filter({"id": str(user.id)})[0].run(durability="soft")
        except IndexError:
            userdata = {"id": str(user.id), "warnings": 0, "reasons": []}
        try:
            try:
                nextwarn = serverdata["config"].filter(lambda x: x["warning"] == userdata["warnings"] + 1)[0].run()
            except IndexError:
                nextwarn = {"warning": userdata["warnings"] + 1, "action": None}
            if nextwarn["action"]:
                action = nextwarn["action"].title() + (" (" + self.format_mute(nextwarn["time"]) + ")" if nextwarn["action"] == "mute" else "")
            else:
                action = "None"
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
        self._create_warn(server, user)
        if not warnings:  
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": 0, "reasons": []}), x))}).run(durability="soft")
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if warnings == 0:
            serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": 0, "reasons": []}), x))}).run(durability="soft")
            await ctx.send("**{}'s** warnings have been reset".format(user.name))
            return
        if serverdata["config"].run():
            maxwarning = sorted(serverdata["config"].run(), key=lambda x: x["warning"], reverse=True)[0]["warning"]
        else:
            maxwarning = 4
        if warnings <= 0 or warnings >= maxwarning:
            return await ctx.send("You can set warnings to 1-{} only :no_entry:".format(maxwarning - 1))
        serverdata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"warnings": warnings}), x))}).run(durability="soft")

        await ctx.send("**{}'s** warnings have been set to **{}**".format(user.name, warnings))  

    @commands.command()
    async def offences(self, ctx, user: str=None, page: int=None):
        """Shows the offences a certain user has had in the server"""
        if not page:
            page = 1
        if not user:
            user = ctx.author
        else:
            user = arg.get_server_member(ctx, user)
            if not user:
                return await ctx.send("Invalid user :no_entry:")
        userdata = r.table("offence").get(str(user.id))
        if not userdata.run():
            return await ctx.send("This user has no offences :no_entry:")
        if not userdata["offences"].run():
            return await ctx.send("This user has no offences :no_entry:")
        if page <= 0 or page > math.ceil(len(userdata["offences"].filter(lambda x: x["server"] == str(ctx.guild.id)).run())/5):
            return await ctx.send("Invalid Page :no_entry:")
        s=discord.Embed()
        for i, x in enumerate(sorted(userdata["offences"].filter(lambda x: x["server"] == str(ctx.guild.id)).run(), key=lambda x: x["time"])[page*5-5:page*5], start=(page*5) - 4):
            s.add_field(name="Offence #{}".format(i), value="Action: {}\nReason: {}\nModerator: {}\nProof: {}\nTime: {}".format(x["action"], x["reason"], 
            arg.get_server_member(ctx, x["mod"]) if arg.get_server_member(ctx, x["mod"]) else x["mod"], x["proof"] if x["proof"] else "None Given", 
            datetime.datetime.fromtimestamp(x["time"]).strftime("%d/%m/%y %H:%M")), inline=False)
        s.set_author(name="{}'s Offences".format(user.name), icon_url=user.avatar_url)
        s.set_footer(text="Update proof using {}proof {} <offence_number> <proof> | Page {}/{}".format(ctx.prefix, str(user) if " " not in str(user) else '"' + str(user) + '"', page, math.ceil(len(userdata["offences"].filter(lambda x: x["server"] == str(ctx.guild.id)).run())/5)))
        await ctx.send(embed=s)
        
    @commands.command()
    @checks.has_permissions("manage_messages")
    async def proof(self, ctx, user: str, offence: int, *, proof: str):
        """Update proof for a user offence"""
        user = arg.get_server_member(ctx, user)
        if not user:
            return await ctx.send("Invalid user :no_entry:")
        userdata = r.table("offence").get(str(user.id))
        if not userdata.run():
            return await ctx.send("This user has no offences :no_entry:")
        if not userdata["offences"].run():
            return await ctx.send("This user has no offences :no_entry:")
        try:
            offence_db = sorted(userdata["offences"].filter(lambda x: x["server"] == str(ctx.guild.id)).run(), key=lambda x: x["time"])[offence - 1]
        except:
            return await ctx.send("Invalid offence number :no_entry:")
        mod = arg.get_server_member(ctx, offence_db["mod"])
        if not mod or mod != ctx.author:
            return await ctx.send("You do not have permission to edit this offence :no_entry:")
        offence_new = userdata["offences"].run()
        offence_new.remove(offence_db)
        offence_db["proof"] = proof
        offence_new.append(offence_db)
        await ctx.send("Proof has been updated for Offence #{}".format(offence))
        userdata.update({"offences": offence_new}).run(durability="soft")

    async def check_mute(self):
        @dev.log
        async def check():
            servers = {x.id: x for x in self.bot.guilds}

            data = r.table("mute")
            for d in data.filter(r.row["users"] != []).run(durability="soft"):
                try:
                    server = servers[int(d["id"])]
                except: 
                    continue
                            
                members = {x.id: x for x in server.members}
                        
                role = discord.utils.get(server.roles, name="Muted - Sx4")
                if role:
                    serverdata = data.get(d["id"])
                    users = serverdata["users"].filter((r.row["amount"]) & (r.row["time"]) & (r.row["toggle"] != False)).run()
                    for x in list(users):
                        try:
                            user = members[int(x["id"])]
                        except:
                            continue
                                    
                        time2 = x["time"] - datetime.datetime.utcnow().timestamp() + x["amount"]
                        if time2 <= 0:
                            users.remove(x)
                            if role in user.roles:
                                try:
                                    await user.remove_roles(role)
                                except:
                                    continue
                                action = "Unmute (Automatic)"
                                author = self.bot.user
                                reason = "Time limit served"
                                try:
                                    await _log(self.bot, author, server, action, reason, user)
                                except:
                                    pass
                            
                    serverdata.update({"users": users}).run(durability="soft", noreply=True)
        while not self.bot.is_closed():
            try:
                await check()
            except Exception as e:
                await self.bot.get_channel(344091594972069888).send(e)
                pass
            await asyncio.sleep(45)
      
                    
        
    def _create_warn(self, server, user):
        r.table("warn").insert({"id": str(server.id), "users": [], "punishments": True, "config": []}).run(durability="soft")
        if str(user.id) not in r.table("warn").get(str(server.id))["users"].map(lambda x: x["id"]).run(durability="soft"):
            warn = {}
            warn["id"] = str(user.id)
            warn["warnings"] = 0
            warn["reasons"] = []
            r.table("warn").update({"users": r.row["users"].append(warn)}).run(durability="soft")
            
    async def _list_warns(self, server, page):
        msg = ""
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name=server.name, icon_url=server.icon_url)
        sortedwarn = sorted(filter(lambda x: int(x["id"]) in map(lambda x: x.id, server.members) and x["warnings"] != 0, r.table("warn").get(str(server.id))["users"].run(durability="soft")), key=lambda x: x["warnings"], reverse=True)[page*20-20:page*20]
        for x in sortedwarn:
            users = discord.utils.get(server.members, id=int(x["id"]))
            msg += "\n`{}`: Warning **#{}**".format(users, x["warnings"])
        s.add_field(name="Users on Warnings", value=msg)
        s.set_footer(text="Page {}/{}".format(page, math.ceil(len(list(filter(lambda x: int(x["id"]) in map(lambda x: x.id, server.members) and x["warnings"] != 0, r.table("warn").get(str(server.id))["users"].run(durability="soft"))))/20)))
        return s

    def format_mute(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 1:
            days = "day"
        else: 
            days = "days"
        if h == 1:
            hours = "hour"
        else: 
            hours = "hours"
        if m == 1:
            minutes = "minute"
        else: 
            minutes = "minutes"
        if s == 1:
            seconds = "seconds"
        else: 
            seconds = "seconds"
        duration = ("%d %s " % (d, days) if d != 0 else "") + ("%d %s " % (h, hours) if h != 0 else "") + ("%d %s " % (m, minutes) if m != 0 else "") + ("%d %s " % (s, seconds) if s >= 1 else "")
        return duration[:-1]


    def suffix(self, number: int):
        suffix = ""
        num = number % 100
        if num >= 11 and num <= 13:
            suffix = "th"
        else:
            num = number % 10
            if num == 1:
                suffix = "st"
            elif num == 2:
                suffix = "nd"
            elif num == 3:
                suffix = "rd"
            else:
                suffix = "th"
        return "{:,}{}".format(number, suffix)

async def _log(bot, author, server, action, reason, user):
    if author == bot.user and "(Automatic)" not in action:
        return
    r.table("modlogs").insert({"id": str(server.id), "channel": None, "toggle": False, "case#": 0, "case": []}).run(durability="soft")
    serverdata = r.table("modlogs").get(str(server.id))
    try:
        channel = bot.get_channel(int(serverdata["channel"].run(durability="soft")))
    except: 
        channel = None
    if serverdata.run():
        if serverdata["toggle"].run(durability="soft") == True and channel is not None:
            number = serverdata["case#"].run(durability="soft") + 1
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
            serverdata.update({"case": r.row["case"].append(case2), "case#": r.row["case#"] + 1}).run(durability="soft")
    r.table("offence").insert({"id": str(user.id), "offences": []}).run(durability="soft")
    userdata = r.table("offence").get(str(user.id))
    proof = None
    if author == bot.user:
        proof = "Automod features enabled"
    offence = {}
    offence["mod"] = str(author.id)
    offence["time"] = datetime.datetime.utcnow().timestamp()
    offence["proof"] = proof
    offence["server"] = str(server.id)
    offence["action"] = action.replace("(Automatic)", "")
    offence["reason"] = "None Given" if not reason else reason
    userdata.update({"offences": r.row["offences"].append(offence)}).run(durability="soft")
        
def setup(bot): 
    bot.add_cog(mod(bot))