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

    async def on_guild_join(self, guild):
        server = guild
        s=discord.Embed(description="I am now in {} servers and connected to {} users".format(len(self.bot.guilds), str(len(set(self.bot.get_all_members())))), colour=0x5fe468, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Joined Server!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Server Name", value=server.name)
        s.add_field(name="Server ID", value=server.id)
        s.add_field(name="Server Owner", value=server.owner)
        s.add_field(name="Total members", value="{} members".format(len(server.members)))
        channels = server.text_channels
        for channel in channels:
            try:
                invite = await channel.create_invite()
            except:
                invite = None
            break
        if invite:
            s.add_field(name="Server Invite", value=str(invite))
        if server.icon_url:
            s.set_thumbnail(url=server.icon_url)
        else:
            s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
        await self.bot.get_channel(396013262514421761).send(embed=s)
        for channel in channels:
            try:
                await channel.send("Thanks for adding me (I'm now in {} servers, Thank you for contributing)!\nMy prefix is `s?`\nAll my info and commands can be found in `s?help`\nIf you need any help feel free to join the support server: https://discord.gg/WJHExmg".format(len(self.bot.guilds)))
            except:
                pass
            break
		
    async def on_guild_remove(self, guild):
        server = guild
        s=discord.Embed(description="I am now in {} servers and connected to {} users".format(len(self.bot.guilds), str(len(set(self.bot.get_all_members())))), colour=0xf84b50, timestamp=__import__('datetime').datetime.utcnow())
        s.set_author(name="Left Server!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Server Name", value=server.name)
        s.add_field(name="Server ID", value=server.id)
        s.add_field(name="Server Owner", value=server.owner)
        s.add_field(name="Total members", value="{} members".format(len(server.members)))
        if server.icon_url:
            s.set_thumbnail(url=server.icon_url)
        else:
            s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
        await self.bot.get_channel(396013262514421761).send(embed=s)

def setup(bot): 
    bot.add_cog(serverlog(bot))