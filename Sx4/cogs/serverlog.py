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
        try:
            server = guild
            s=discord.Embed(description="I am now in {:,} servers and connected to {:,} users".format(len(self.bot.guilds), len(set(self.bot.get_all_members()))), colour=0x5fe468, timestamp=datetime.utcnow())
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
            if server.icon_url:
                s.set_thumbnail(url=server.icon_url)
            else:
                s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
            await self.bot.get_channel(396013262514421761).send(embed=s)
            if server.system_channel:
                return await server.system_channel.send("Thanks for adding me (I'm now in {:,} servers, Thank you for contributing)!\nMy prefix is `s?`\nAll my info and commands can be found in `s?help`\nIf you need any help feel free to join the support server: https://discord.gg/PqJNcfB".format(len(self.bot.guilds)))
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
            s=discord.Embed(description="I am now in {:,} servers and connected to {:,} users".format(len(self.bot.guilds), len(set(self.bot.get_all_members()))), colour=0xf84b50, timestamp=datetime.utcnow())
            s.set_author(name="Left Server!", icon_url=self.bot.user.avatar_url)
            s.add_field(name="Server Name", value=server.name)
            s.add_field(name="Server ID", value=server.id)
            s.add_field(name="Server Owner", value="{}\n{}".format(server.owner, server.owner.id))
            s.add_field(name="Total members", value="{} members".format(len(server.members)))
            try:
                s.add_field(name="Stayed For", value=self.format_time(guild.me), inline=False)
            except:
                pass
            if server.icon_url:
                s.set_thumbnail(url=server.icon_url)
            else:
                s.set_thumbnail(url="https://cdn.discordapp.com/attachments/344091594972069888/396285725605363712/no_server_icon.png")
            await self.bot.get_channel(396013262514421761).send(embed=s)
        except Exception as e:
            await self.bot.get_channel(396013262514421761).send(e)

    def format_time(self, sx4):
        seconds = (datetime.utcnow() - sx4.joined_at).total_seconds()
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if m == 0 and h == 0 and d ==0:
            return "%d %s" % (s, "second" if s == 1 else "seconds")
        elif h == 0 and d == 0:
            return "%d %s %d %s" % (m, "minute" if m == 1 else "minutes", s, "second" if s == 1 else "seconds")
        elif d == 0:
            return "%d %s %d %s %d %s" % (h, "hour" if h == 1 else "hours", m, "minute" if m == 1 else "minutes", s, "second" if s == 1 else "seconds")
        else:
            return "%d %s %d %s %d %s %d %s" % (d, "day" if d == 1 else "days", h, "hour" if h == 1 else "hours", m, "minute" if m == 1 else "minutes", s, "second" if s == 1 else "seconds")


def setup(bot): 
    bot.add_cog(serverlog(bot))