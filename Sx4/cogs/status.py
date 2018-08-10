import os
import discord
from discord.ext import commands
from discord.utils import find
from random import randint
import asyncio

class statuses:
    """Bot Status"""

    def __init__(self, bot):
        self.bot = bot

    async def display_status(self):
        i = 0
        while not self.bot.is_closed():
            try:
                statuses = [
                    '{:,} servers'.format(len(self.bot.guilds)),
                    '{:,} users'.format(len(set(self.bot.get_all_members())))
                ]
                new_status = statuses[i]
                await self.bot.change_presence(activity=discord.Game(name=new_status, type=discord.ActivityType.watching))
            except:
                pass
            await asyncio.sleep(30)
            if i == 0:
                i += 1
            else:
                i -= 1

def setup(bot):
    n = statuses(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.display_status())  
    bot.add_cog(n)