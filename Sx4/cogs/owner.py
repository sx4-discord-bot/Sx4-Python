import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import requests
import datetime
from utils import checks
import os

class owner:
    def __init__(self, bot):
        self.bot = bot
		
    @commands.command(hidden=True)
    async def modules(self, ctx):
        unloaded, loaded = [], []
        list = [x.replace(".py", "") for x in os.listdir("cogs") if ".py" in x]
        for x in list:
            if not self.bot.get_cog(x):
                unloaded.append(x)
            else:
                loaded.append(x)
        s=discord.Embed(title="Modules ({})".format(len(list)))
        s.add_field(name="Loaded ({})".format(len(loaded)), value=", ".join(loaded) if loaded != [] else "None", inline=False)
        s.add_field(name="Unloaded ({})".format(len(unloaded)), value=", ".join(unloaded) if unloaded != [] else "None", inline=False)
        await ctx.send(embed=s)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def updateavatar(self, ctx, *, url=None):
        if not url:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                await ctx.send("Provide a valid image :no_entry:")
                return
        with open("logo.png", 'wb') as f:
            f.write(requests.get(url).content)
        with open("logo.png", "rb") as f:
            avatar = f.read()
        try:
            await self.bot.user.edit(password=None, avatar=avatar)
        except:
            return await ctx.send("Clap you've changed my profile picture too many times")
        await ctx.send("I have changed my profile picture")
        os.remove("logo.png")
		
    @commands.command(hidden=True)
    @checks.is_owner()
    async def httpunban(self, ctx, server_id: str, user_id: str): 
        user = await self.bot.get_user_info(user_id)
        server = self.bot.get_guild(server_id)
        await self.bot.http.unban(user_id, server_id)
        await ctx.send("I have unbanned **{}** from **{}**".format(user, server))
		
    @commands.command(hidden=True) 
    @checks.is_owner()
    async def msg(self, ctx, channel_id, *, text):
        await ctx.message.delete()
        await self.bot.http.send_message(channel_id, text)
		
    @commands.command(hidden=True)
    @checks.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.logout()

		
def setup(bot):
    bot.add_cog(owner(bot))