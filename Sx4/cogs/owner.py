import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
from utils import checks
import os

class owner:
    def __init__(self, bot):
        self.bot = bot
		
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def updateavatar(self, ctx, *, logoname):
        with open('sx4-{}.png'.format(logoname), 'r') as r:
            avatar_url = r.read()
        await self.bot.user.edit_profile(password=None, avatar=avatar_url)
        await ctx.send("I have changed my profile picture")
		
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def httpunban(self, ctx, server_id: str, user_id: str): 
        user = await self.bot.get_user_info(user_id)
        server = self.bot.get_guild(server_id)
        await self.bot.http.unban(user_id, server_id)
        await ctx.send("I have unbanned **{}** from **{}**".format(user, server))
		
    @commands.command(pass_context=True, hidden=True) 
    @checks.is_owner()
    async def msg(self, ctx, channel_id, *, text):
        await ctx.message.delete()
        await self.bot.http.send_message(channel_id, text)
		
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.logout()

		
def setup(bot):
    bot.add_cog(owner(bot))