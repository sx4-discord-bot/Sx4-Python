import os
import discord
from discord.ext import commands
from discord.utils import find
from random import randint
import asyncio

class status:
    """Bot Status"""

    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
        self._task = bot.loop.create_task(self.display_status())

    def __unload(self):
        self._task.cancel()

    async def display_status(self):
        i = 0
        while not self.bot.is_closed():
            try:
                statuses = [
                    "{:,} servers".format(len(self.bot.guilds)),
                    "{:,} users".format(len(self.bot.users))
                ]
                new_status = statuses[i]
                await self.bot.change_presence(activity=discord.Activity(name=new_status, type=discord.ActivityType.watching))
            except Exception as e:
                await self.bot.get_channel(439745234285625355).send(e)
            if i == len(statuses) - 1:
                i = 0
            else:
                i += 1
            await asyncio.sleep(300)

def setup(bot, connection):
    n = status(bot, connection)
    bot.add_cog(n)