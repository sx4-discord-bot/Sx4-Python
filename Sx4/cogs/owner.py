import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import requests
import datetime
import rethinkdb as r
from discord.ext.commands.view import StringView
import json
from utils import arg
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps
from utils import checks
import os

class owner:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_owner()
    async def collage(self, ctx):
        pixels = 64
        width = math.ceil(math.sqrt(ctx.guild.member_count)*pixels)
        height = math.ceil(math.sqrt(ctx.guild.member_count)*pixels)
        background = Image.new("RGBA", (width+pixels, height+pixels), (0, 0, 0, 0))
        x, y, i = 0, 0, 0
        await ctx.send("Creating collage...")
        t1 = time.perf_counter()
        for member in ctx.guild.members:
            i += 1
            print(str(member) + " ({}/{})".format(i, ctx.guild.member_count))
            try:
                with open("avatar.png", "wb") as f:
                    f.write(requests.get(member.avatar_url).content)
                image = Image.open("avatar.png").convert("RGBA")
                image = image.resize((pixels, pixels))
                background.paste(image, (x, y))
                x += pixels
                if x >= width:
                    y += pixels
                    x = 0
                print("Successful") 
            except Exception as e:
                print(e)
        background.save("collage.png")
        t2 = time.perf_counter()
        try:
            await ctx.send(content="Executed in **{}ms**".format(round((t2-t1)*1000)), file=discord.File("collage.png", "collage.png"))
        except:
            await ctx.send("Executed in **{}ms**\n\nImage saved in hosters files".format(round((t2-t1)*1000)))
            return os.remove("avatar.png")
        try:
            os.remove("collage.png")
            os.remove("avatar.png")
        except: 
            pass

    @commands.command(hidden=True, name="as")
    @checks.is_owner()
    async def _as(self, ctx, user: str, command_name: str, *, args: str=""):
        user = await arg.get_member(self.bot, ctx, user)
        if not user:
            return await ctx.send("You're retarded that's not a user :no_entry:")
        else:
            ctx.author = user
            ctx.message.author = user
        if " " in command_name:
            command = command_name.split(" ", 1)
            try:
                command = self.bot.all_commands[command[0]].all_commands[command[1]]
            except KeyError:
                return await ctx.send("Invalid command :no_entry:")
        else:
            try:
                command = self.bot.all_commands[command_name]
            except KeyError:
                return await ctx.send("Invalid command :no_entry:")
        ctx.message.content = ctx.prefix + command_name + " " + args
        ctx.view = StringView(args)
        await command.invoke(ctx)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def commandlog(self, ctx, *, code: str=None):
        if not code:
            with open("commandlog.json", "wb") as f:
                f.write(json.dumps(r.table("botstats").get("stats")["commandlog"].run(durability="soft")).encode())
        else:
            with open("commandlog.json", "wb") as f:
                f.write(json.dumps(list(eval(code.replace("data", 'r.table("botstats").get("stats")["commandlog"].run(durability="soft")')))).encode())
        await ctx.send(file=discord.File("commandlog.json"))
        os.remove("commandlog.json")

    @commands.command(hidden=True)
    @checks.is_owner()
    async def disable(self, ctx, command: str, boolean: bool=False):
        try:
            self.bot.all_commands[command].enabled = boolean
            if boolean == False:
                await ctx.send("`{}` has been disabled.".format(command))
            else:
                await ctx.send("`{}` has been enabled.".format(command))
        except KeyError:
            return await ctx.send("Invalid command :no_entry:")

    @commands.command(hidden=True)
    @checks.is_owner()
    async def blacklist(self, ctx, user_id: str, boolean: bool):
        r.table("blacklist").insert({"id": "owner", "users": []}).run(durability="soft")
        data = r.table("blacklist").get("owner")
        if boolean == True:
            if user_id not in data["users"].run(durability="soft"):
                data.update({"users": r.row["users"].append(user_id)}).run(durability="soft")
                await ctx.send("User has been blacklisted.")
            else:
                await ctx.send("That user is already blacklisted.")
        if boolean == False:
            if user_id not in data["users"].run(durability="soft"):
                await ctx.send("That user is not blacklisted.")
            else:
                data.update({"users": r.row["users"].difference([user_id])}).run(durability="soft")
                await ctx.send("That user is no longer blacklisted")
		
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

    async def on_guild_join(self, guild):
        guilds = len(self.bot.guilds)
        if guilds % 100 == 0:
            channel = self.bot.get_channel(493439822682259497)
            await channel.send("{:,} servers :tada:".format(guilds))

    async def on_guild_remove(self, guild):
        guilds = len(self.bot.guilds)
        if guilds % 100 != 0:
            channel = self.bot.get_channel(493439822682259497)
            for x in await channel.history(limit=1).flatten():
                if int(x.content.split(" ")[0].replace(",", "")) > guilds:
                    await x.delete()  
		
def setup(bot):
    bot.add_cog(owner(bot))