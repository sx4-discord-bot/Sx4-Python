import discord
from discord.ext import commands
from datetime import datetime
import os
import re
import logging
import asyncio
import random
import time
from utils import dateify


class serverlog:
    """Shows when the bot joins and leaves a server"""

    def __init__(self, bot, connection):
        self.bot = bot 
        self.db = connection

    async def on_guild_join(self, guild):
        try:
            server = guild
            s=discord.Embed(description="I am now in {:,} servers and connected to {:,} users".format(len(self.bot.guilds), len(self.bot.users)), colour=0x5fe468, timestamp=datetime.utcnow())
            s.set_author(name="Joined Server!", icon_url=self.bot.user.avatar_url)
            s.add_field(name="Server Name", value=server.name)
            s.add_field(name="Server ID", value=server.id)
            s.add_field(name="Server Owner", value="{}\n{}".format(server.owner, server.owner.id))
            s.add_field(name="Total members", value="{} members".format(len(server.members)))
            channels = server.text_channels
            try:
                if len(await server.invites()) > 0:
                    for x in await server.invites():
                        if x.max_age == 0:
                            invite = x.url
                            break
                else:
                    invite = None
            except:
                invite = None
            try:
                if invite:
                    s.add_field(name="Server Invite", value=invite)
            except:
                pass
            mutual = list(map(lambda x: x.name, sorted([x for x in self.bot.guilds if server.owner in x.members and x != server], key=lambda x: x.member_count, reverse=True)))
            if len(mutual) > 15:
                s.add_field(name="Mutual Servers (Owner)", value="\n".join(mutual[:15]) + "\n and {} more...".format(len(mutual)-15))
            else:
                s.add_field(name="Mutual Servers (Owner)", value="\n".join(mutual) if len(mutual) != 0 else "None")
            if server.icon_url:
                s.set_thumbnail(url=server.icon_url)
            else:
                s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
            await self.bot.get_channel(396013262514421761).send(embed=s)
            if server.system_channel:
                try:
                    await server.system_channel.send("Thanks for adding me (I'm now in {:,} servers, Thank you for contributing)!\nMy prefix is `s?`\nAll my info and commands can be found in `s?help`\nIf you need any help feel free to join the support server: https://discord.gg/PqJNcfB".format(len(self.bot.guilds)))
                    return
                except:
                    pass
            for channel in channels:
                try:
                    await channel.send("Thanks for adding me (I'm now in {:,} servers, Thank you for contributing)!\nMy prefix is `s?`\nAll my info and commands can be found in `s?help`\nIf you need any help feel free to join the support server: https://discord.gg/PqJNcfB".format(len(self.bot.guilds)))
                    break
                except:
                    pass
        except Exception as e:
            await self.bot.get_channel(396013262514421761).send(e)
		
    async def on_guild_remove(self, guild):
        try:
            server = guild
            s=discord.Embed(description="I am now in {:,} servers and connected to {:,} users".format(len(self.bot.guilds), len(self.bot.users)), colour=0xf84b50, timestamp=datetime.utcnow())
            s.set_author(name="Left Server!", icon_url=self.bot.user.avatar_url)
            s.add_field(name="Server Name", value=server.name)
            s.add_field(name="Server ID", value=server.id)
            s.add_field(name="Server Owner", value="{}\n{}".format(server.owner, server.owner.id))
            s.add_field(name="Total members", value="{} members".format(len(server.members)))
            try:
                s.add_field(name="Stayed For", value=dateify.get((datetime.utcnow() - server.me.joined_at).total_seconds()), inline=False)
            except Exception as e:
                pass
            if server.icon_url:
                s.set_thumbnail(url=server.icon_url)
            else:
                s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
            await self.bot.get_channel(396013262514421761).send(embed=s)
        except Exception as e:
            await self.bot.get_channel(396013262514421761).send(e)


def setup(bot, connection): 
    bot.add_cog(serverlog(bot, connection))