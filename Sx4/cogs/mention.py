import discord
from discord.ext import commands
from random import randint


class mention:
    def __init__(self, bot):
        self.bot = bot
    

    async def on_message(self, message):
        bot = "<@!{}>".format(self.bot.user.id)
        if message.guild == 264445053596991498:
            return
        if message.content.lower() == self.bot.user.mention:
            if not isinstance(message.channel, discord.abc.PrivateChannel):
                await message.channel.send("My prefix is `s?`")

				
def setup(bot):
    n = mention(bot)
    bot.add_cog(n)
