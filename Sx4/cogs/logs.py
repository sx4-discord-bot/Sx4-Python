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

class logs:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/logs/settings.json"
        self.data = dataIO.load_json(self.JSON)
		
    @commands.group(pass_context=True)
    async def logs(self, ctx):
        """Log actions in your server"""
        server = ctx.message.guild
        if str(server.id) not in self.data:
            self.data[str(server.id)] = {}
            dataIO.save_json(self.JSON, self.data)
        if "channel" not in self.data[str(server.id)]:
            self.data[str(server.id)]["channel"] = {}
            dataIO.save_json(self.JSON, self.data)
        if "toggle" not in self.data[str(server.id)]:
            self.data[str(server.id)]["toggle"] = False
            dataIO.save_json(self.JSON, self.data)
		
    @logs.command(pass_context=True)
    @checks.admin_or_permissions(manage_guild=True) 
    async def channel(self, ctx, channel: discord.TextChannel=None):
        """Set the channel where you want stuff to be logged"""
        server = ctx.message.guild
        if not channel:
            channel = ctx.message.channel
        self.data[str(server.id)]["channel"] = str(channel.id)
        dataIO.save_json(self.JSON, self.data)
        await ctx.send("Logs will be recorded in <#{}> if toggled on <:done:403285928233402378>".format(channel.id))
		
    @logs.command(pass_context=True)
    @checks.admin_or_permissions(manage_guild=True)  
    async def toggle(self, ctx):
        """Toggle logs on or off"""
        server = ctx.message.guild
        if self.data[str(server.id)]["toggle"] == False:
            self.data[str(server.id)]["toggle"] = True
            dataIO.save_json(self.JSON, self.data)
            await ctx.send("Logs have been toggled **on** <:done:403285928233402378>")
            return
        if self.data[str(server.id)]["toggle"] == True:
            self.data[str(server.id)]["toggle"] = False
            dataIO.save_json(self.JSON, self.data)
            await ctx.send("Logs have been toggled **off** <:done:403285928233402378>")
            return
			
    async def on_message_delete(self, message):
        author = message.author
        server = message.guild
        channel = message.channel
        s=discord.Embed(description="The message sent by **{}** was deleted in <#{}>".format(author.name, channel.id), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=author, icon_url=author.avatar_url)
        s.add_field(name="Message", value=message.content)
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_message_edit(self, before, after):
        author = before.author
        server = before.guild
        channel = before.channel
        if before.content == after.content:
            return
        s=discord.Embed(description="{} edited their message in <#{}>".format(author.name, channel.id), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=author, icon_url=author.avatar_url)
        s.add_field(name="Before", value=before.content, inline=False)
        s.add_field(name="After", value=after.content)
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_guild_channel_delete(self, channel):
        server = channel.guild
        if isinstance(channel, discord.TextChannel):
            s=discord.Embed(description="The text channel **{}** has just been deleted".format(channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        elif isinstance(channel, discord.VoiceChannel):
            s=discord.Embed(description="The voice channel **{}** has just been deleted".format(channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        else:
            s=discord.Embed(description="The category **{}** has just been deleted".format(channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_guild_channel_create(self, channel):
        server = channel.guild
        if isinstance(channel, discord.TextChannel):
            s=discord.Embed(description="The text channel <#{}> has just been created".format(channel.id), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        elif isinstance(channel, discord.VoiceChannel):
            s=discord.Embed(description="The voice channel **{}** has just been created".format(channel), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        else:
            s=discord.Embed(description="The category **{}** has just been created".format(channel), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_guild_channel_update(self, before, after):
        server = before.guild
        if isinstance(before, discord.TextChannel):
            s=discord.Embed(description="The text channel <#{}> has been renamed".format(after.id), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        elif isinstance(before, discord.VoiceChannel):
            s=discord.Embed(description="The voice channel **{}** has been renamed".format(after), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        else:
            s=discord.Embed(description="The category **{}** has been renamed".format(after), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        if self.data[str(server.id)]["toggle"] == True:
            if before.name != after.name:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_member_join(self, member):
        server = member.guild
        s=discord.Embed(description="**{}** just joined the server".format(member.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
        s.set_footer(text="User ID: {}".format(member.id))
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			 
    async def on_member_remove(self, member):
        server = member.guild
        s=discord.Embed(description="**{}** just left the server".format(member.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
        s.set_footer(text="User ID: {}".format(member.id))
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_member_ban(self, guild, user):
        server = guild
        s=discord.Embed(description="**{}** has been banned".format(user.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=user, icon_url=user.avatar_url)
        s.set_footer(text="User ID: {}".format(user.id))
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_member_unban(self, guild, user):
        server = guild
        s=discord.Embed(description="**{}** has been unbanned".format(user.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=user, icon_url=user.avatar_url)
        s.set_footer(text="User ID: {}".format(user.id))
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_guild_role_create(self, role): 
        server = role.guild
        s=discord.Embed(description="The role **{}** has been created".format(role.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			 
    async def on_guild_role_delete(self, role):
        server = role.guild
        s=discord.Embed(description="The role **{}** has been deleted".format(role.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_guild_role_update(self, before, after):
        server = before.guild
        s=discord.Embed(description="The role **{}** has been renamed".format(before.name), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        s.add_field(name="Before", value=before)
        s.add_field(name="After", value=after)
        if self.data[str(server.id)]["toggle"] == True:
            if before.name != after.name:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
				
    async def on_voice_state_update(self, member, before, after):
        server = member.guild
        if before.channel != after.channel:
            s=discord.Embed(description="**{}** just changed voice channels".format(member.name), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=member, icon_url=member.avatar_url)
            s.add_field(name="Before", value="`{}`".format(before.channel), inline=False)
            s.add_field(name="After", value="`{}`".format(after.channel))
        if after.channel == None:
            s=discord.Embed(description="**{}** just left the voice channel `{}`".format(member.name, before.channel), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=member, icon_url=member.avatar_url)
        if before.channel == None:
            s=discord.Embed(description="**{}** just joined the voice channel `{}`".format(member.name, after.channel), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=member, icon_url=member.avatar_url)
        if self.data[str(server.id)]["toggle"] == True:
            await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
			
    async def on_member_update(self, before, after):
        server = before.guild
        if before.roles != after.roles:
            for role in [x for x in before.roles if x not in after.roles]:
                s=discord.Embed(description="The role `{}` has been removed from **{}**".format(role, after.name), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
            for role in [x for x in after.roles if x not in before.roles]:
                s=discord.Embed(description="The role `{}` has been added to **{}**".format(role, after.name), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
        if before.nick != after.nick:
            if not before.nick:
                before.nick = after.name
            if not after.nick:
                after.nick = after.name
            s=discord.Embed(description="**{}** has has had their nickname changed".format(after.name), colour=0xe6842b, timestamp=__import__('datetime').datetime.utcnow())
            s.set_author(name=after, icon_url=after.avatar_url)
            s.add_field(name="Before", value=before.nick, inline=False)
            s.add_field(name="After", value=after.nick)
            if self.data[str(server.id)]["toggle"] == True:
                await self.bot.get_channel(int(self.data[str(server.id)]["channel"])).send(embed=s)
		
		
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
    bot.add_cog(logs(bot))