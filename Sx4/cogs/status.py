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
        while self == self.bot.get_cog('statuses'):
            try:
                statuses = [
                    '{} servers'.format(len(self.bot.servers)),
                    '{} users'.format(str(len(set(self.bot.get_all_members()))))
                ]
                status = randint(0, len(statuses)-1)
                new_status = statuses[status]
                await self.bot.change_presence(game=discord.Game(name=new_status, type=3))
            except:
                pass
            await asyncio.sleep(30)

def setup(bot):
    n = statuses(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.display_status())  
    bot.add_cog(n)