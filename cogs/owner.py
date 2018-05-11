import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
from utils import checks
import os

class Owner:
    def __init__(self, bot):
        self.bot = bot
		
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def updateavatar(self, ctx):
        with open('blurple_sx4.png', 'rb') as r:
            avatar_url = r.read()
        await self.bot.edit_profile(password=None, avatar=avatar_url)
        await self.bot.say("I have changed my profile picture")

    @commands.command(pass_context=True, hidden=True) 
    @checks.is_owner()
    async def updates(self, ctx, version, *, text):
        channel = ctx.message.channel
        author = ctx.message.author
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Update!", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Bot version", value=version)
        s.add_field(name="Developer", value=author)
        s.add_field(name="Changes", value=text)
        s.set_thumbnail(url=self.bot.user.avatar_url)
        await self.bot.send_message(self.bot.get_channel("386667580456435712"), embed=s)
		
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def httpunban(self, ctx, server_id: str, user_id: str): 
        user = await self.bot.get_user_info(user_id)
        server = self.bot.get_server(server_id)
        await self.bot.http.unban(user_id, server_id)
        await self.bot.say("I have unbanned **{}** from **{}**".format(user, server))
		
    @commands.command(pass_context=True, hidden=True) 
    @checks.is_owner()
    async def msg(self, ctx, channel_id, *, text):
        await self.bot.delete_message(ctx.message)
        await self.bot.http.send_message(channel_id, text)
		
    @commands.command(pass_context=True, hidden=True) 
    @checks.is_owner()
    async def announce(self, ctx, *, text):
        i = 0;
        for server in self.bot.servers:
            try:
                await self.bot.send_message(server.default_channel, text)
                i = i + 1
            except:
                pass
        await self.bot.say("I have sent that message to {}/{} servers".format(i, len(self.bot.servers)))
        
		
    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def shutdown(self, ctx):
        await self.bot.say("Shutting down...")
        await self.bot.logout()

		
def setup(bot):
    bot.add_cog(Owner(bot))