import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
import logging
import asyncio
import random
import time
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound
from utils.dataIO import fileIO

class Logs:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/logs/settings.json"
        self.data = dataIO.load_json(self.JSON)
		
    @commands.group(pass_context=True)
    async def logs(self, ctx):
        """Log actions in your server"""
        server = ctx.message.server
        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.JSON, self.data)
        if "channel" not in self.data[server.id]:
            self.data[server.id]["channel"] = {}
            dataIO.save_json(self.JSON, self.data)
        if "toggle" not in self.data[server.id]:
            self.data[server.id]["toggle"] = False
            dataIO.save_json(self.JSON, self.data)
		
    @logs.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True) 
    async def channel(self, ctx, channel: discord.Channel=None):
        """Set the channel where you want stuff to be logged"""
        server = ctx.message.server
        if not channel:
            channel = ctx.message.channel
        self.data[server.id]["channel"] = channel.id
        dataIO.save_json(self.JSON, self.data)
        await self.bot.say("Logs will be recorded in <#{}> if toggled on <:done:403285928233402378>".format(channel.id))
		
    @logs.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)  
    async def toggle(self, ctx):
        """Toggle logs on or off"""
        server = ctx.message.server
        if self.data[server.id]["toggle"] == False:
            self.data[server.id]["toggle"] = True
            dataIO.save_json(self.JSON, self.data)
            await self.bot.say("Logs have been toggled **on** <:done:403285928233402378>")
            return
        if self.data[server.id]["toggle"] == True:
            self.data[server.id]["toggle"] = False
            dataIO.save_json(self.JSON, self.data)
            await self.bot.say("Logs have been toggled **off** <:done:403285928233402378>")
            return
			
    async def on_message_delete(self, message):
        author = message.author
        server = message.server
        channel = message.channel
        s=discord.Embed(description="The message sent by **{}** was deleted in <#{}>".format(author.name, channel.id), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=author, icon_url=author.avatar_url)
        s.add_field(name="Message", value=message.content)
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_message_edit(self, before, after):
        author = before.author
        server = before.server
        channel = before.channel
        if before.content == after.content:
            return
        s=discord.Embed(description="{} edited their message in <#{}>".format(author.name, channel.id), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=author, icon_url=author.avatar_url)
        s.add_field(name="Before", value=before.content, inline=False)
        s.add_field(name="After", value=after.content)
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_channel_delete(self, channel):
        server = channel.server
        if channel.type == discord.ChannelType.text:
            s=discord.Embed(description="The text channel **{}** has just been deleted".format(channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
        elif channel.type == discord.ChannelType.voice:
            s=discord.Embed(description="The voice channel **{}** has just been deleted".format(channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
        else:
            s=discord.Embed(description="The category **{}** has just been deleted".format(channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_channel_create(self, channel):
        server = channel.server
        if channel.type == discord.ChannelType.text:
            s=discord.Embed(description="The text channel <#{}> has just been created".format(channel.id), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
        elif channel.type == discord.ChannelType.voice:
            s=discord.Embed(description="The voice channel **{}** has just been created".format(channel), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
        else:
            s=discord.Embed(description="The category **{}** has just been created".format(channel), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_channel_update(self, before, after):
        server = before.server
        if before.type == discord.ChannelType.text:
            s=discord.Embed(description="The text channel <#{}> has been renamed".format(after.id), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        elif before.type == discord.ChannelType.voice:
            s=discord.Embed(description="The voice channel **{}** has been renamed".format(after), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        else:
            s=discord.Embed(description="The category **{}** has been renamed".format(after.id), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        if self.data[server.id]["toggle"] == True:
            if before.name != after.name:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_member_join(self, member):
        server = member.server
        s=discord.Embed(description="**{}** just joined the server".format(member.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
        s.set_footer(text="User ID: {}".format(member.id))
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			 
    async def on_member_remove(self, member):
        server = member.server
        s=discord.Embed(description="**{}** just left the server".format(member.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
        s.set_footer(text="User ID: {}".format(member.id))
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_member_ban(self, member):
        server = member.server
        s=discord.Embed(description="**{}** has been banned".format(member.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
        s.set_footer(text="User ID: {}".format(member.id))
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_member_unban(self, server, user):
        s=discord.Embed(description="**{}** has been unbanned".format(user.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=user, icon_url=user.avatar_url)
        s.set_footer(text="User ID: {}".format(user.id))
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_server_role_create(self, role): 
        server = role.server
        s=discord.Embed(description="The role **{}** has been created".format(role.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			 
    async def on_server_role_delete(self, role):
        server = role.server
        s=discord.Embed(description="The role **{}** has been deleted".format(role.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_server_role_update(self, before, after):
        server = before.server
        s=discord.Embed(description="The role **{}** has been renamed".format(before.name), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        s.add_field(name="Before", value=before)
        s.add_field(name="After", value=after)
        if self.data[server.id]["toggle"] == True:
            if before.name != after.name:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
				
    async def on_voice_state_update(self, before, after):
        server = before.server
        if before.voice_channel != after.voice_channel:
            s=discord.Embed(description="**{}** just changed voice channels".format(before.name), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=before, icon_url=before.avatar_url)
            s.add_field(name="Before", value="`{}`".format(before.voice_channel), inline=False)
            s.add_field(name="After", value="`{}`".format(after.voice_channel))
        if after.voice_channel == None:
            s=discord.Embed(description="**{}** just left the voice channel `{}`".format(before.name, before.voice_channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=before, icon_url=before.avatar_url)
        if before.voice_channel == None:
            s=discord.Embed(description="**{}** just joined the voice channel `{}`".format(before.name, after.voice_channel), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=before, icon_url=before.avatar_url)
        if self.data[server.id]["toggle"] == True:
            await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
			
    async def on_member_update(self, before, after):
        server = before.server
        if before.roles != after.roles:
            for role in [x for x in before.roles if x not in after.roles]:
                s=discord.Embed(description="The role `{}` has been removed from **{}**".format(role, after.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
            for role in [x for x in after.roles if x not in before.roles]:
                s=discord.Embed(description="The role `{}` has been added to **{}**".format(role, after.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
        if before.nick != after.nick:
            if not before.nick:
                before.nick = after.name
            if not after.nick:
                after.nick = after.name
            s=discord.Embed(description="**{}** has has had their nickname changed".format(after.name), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=after, icon_url=after.avatar_url)
            s.add_field(name="Before", value=before.nick, inline=False)
            s.add_field(name="After", value=after.nick)
            if self.data[server.id]["toggle"] == True:
                await self.bot.send_message(self.bot.get_channel(self.data[server.id]["channel"]), embed=s)
		
		
def check_folders():
    if not os.path.exists("data/logs"):
        print("Creating data/logs folder...")
        os.makedirs("data/logs")


def check_files():
    s = "data/logs/settings.json"
    if not dataIO.is_valid_json(s):
        print("Creating empty settings.json...")
        dataIO.save_json(s, {})

def setup(bot): 
    check_folders()
    check_files() 
    bot.add_cog(Logs(bot))