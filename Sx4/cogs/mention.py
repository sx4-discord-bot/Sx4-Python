import discord
from discord.ext import commands
from random import randint


class mention:
    def __init__(self, bot):
        self.bot = bot
    

    async def on_message(self, message):
        bot = "<@!{}>".format(self.bot.user.id)
        if message.server == "264445053596991498":
            return
        if message.content.lower() == self.bot.user.mention:
            if not message.channel.is_private:
                await self.bot.send_message(message.channel, "My prefix is `s?`")

				
def setup(bot):
    n = mention(bot)
    bot.add_cog(n)
