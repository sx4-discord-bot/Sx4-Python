import discord
from discord.ext import commands
from datetime import datetime
import os
import re
import logging
import asyncio
import random
import time


class serverlog:
    """Shows when the bot joins and leaves a server"""

    def __init__(self, bot):
        self.bot = bot 

    async def on_server_join(self, server):
        s=discord.Embed(description="I am now in {} servers and connected to {} users".format(len(self.bot.servers), str(len(set(self.bot.get_all_members())))), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Joined Server!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Server Name", value=server.name)
        s.add_field(name="Server ID", value=server.id)
        s.add_field(name="Server Owner", value=server.owner)
        s.add_field(name="Total members", value="{} members".format(len(server.members)))
        channels = [x for x in server.channels if x.type == discord.ChannelType.text]
        for channel in channels:
            try:
                invite = await self.bot.create_invite(channel)
            except:
                invite = None
            break
        if invite:
            s.add_field(name="Server Invite", value=str(invite))
        if server.icon_url:
            s.set_thumbnail(url=server.icon_url)
        else:
            s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
        await self.bot.send_message(self.bot.get_channel("396013262514421761"), embed=s)
		
    async def on_server_remove(self, server):
        s=discord.Embed(description="I am now in {} servers and connected to {} users".format(len(self.bot.servers), str(len(set(self.bot.get_all_members())))), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Left Server!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Server Name", value=server.name)
        s.add_field(name="Server ID", value=server.id)
        s.add_field(name="Server Owner", value=server.owner)
        s.add_field(name="Total members", value="{} members".format(len(server.members)))
        if server.icon_url:
            s.set_thumbnail(url=server.icon_url)
        else:
            s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
        await self.bot.send_message(self.bot.get_channel("396013262514421761"), embed=s)

def setup(bot): 
    bot.add_cog(serverlog(bot))