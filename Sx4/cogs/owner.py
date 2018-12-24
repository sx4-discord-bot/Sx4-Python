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
import inspect
from utils import arg
import math
import functools
import psutil
from PIL import Image, ImageDraw, ImageFont, ImageOps
from utils import checks
import os

execution_times = {}

def log(method):
    @functools.wraps(method)
    async def timed(*args, **kw):
        memory_start = psutil.Process(os.getpid()).memory_info().rss/1000000
        start_time = time.time()
        result = await method(*args, **kw)
        execution_time = int((time.time() - start_time) * 1000)
        memory_gained = (psutil.Process(os.getpid()).memory_info().rss/1000000) - memory_start
        
        method_name = method.__module__ + "." + method.__name__
        if method_name not in execution_times:
            execution_times[method_name] = {"average": 0, "data_points": 0, "memory_average": 0}
            
        entry = execution_times[method_name]
        
        new_average = ((entry["average"] * entry["data_points"]) + execution_time)/(entry["data_points"] + 1)
        new_average_memory = ((entry["memory_average"] * entry["data_points"]) + memory_gained)/(entry["data_points"] + 1)
        
        entry["average_memory"] = new_average_memory
        entry["average"] = new_average
        entry["data_points"] += 1
        
        if "min_execution_time" not in entry:
            entry["min_execution_time"] = execution_time
        
        entry["min_execution_time"] = min(entry["min_execution_time"], execution_time)
        
        if "max_execution_time" not in entry:
            entry["max_execution_time"] = execution_time
            
        entry["max_execution_time"] = max(entry["max_execution_time"], execution_time)
        
        if "min_memory_gained" not in entry:
            entry["min_memory_gained"] = memory_gained
        
        entry["min_memory_gained"] = min(entry["min_memory_gained"], memory_gained)
        
        if "max_memory_gained" not in entry:
            entry["max_memory_gained"] = memory_gained
            
        entry["max_memory_gained"] = max(entry["max_memory_gained"], memory_gained)
        return result
    return timed

class owner:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_owner()
    async def code(self, ctx, *, command: str=None):
        if not command:
            command = ctx.command
        else:
            command = self.bot.get_command(command)
            if not command:
                return await ctx.send("Invalid command :no_entry:")
        wrap = "```py\n{}```"
        code = inspect.getsource(command.callback)
        code = code.replace("```", "\```")
        if len(code) > 1990:
            pages = math.ceil(len(code)/1990)
            n = 0
            m = 1990
            for x in range(pages):
                if n != 0:
                    while code[n-1:n] != "\n":
                        n -= 1
                while code[m-1:m] != "\n":
                    m -= 1
                await ctx.send(wrap.format(code[n:m]))
                n += 1990
                m += 1990
        else:
            await ctx.send(wrap.format(code))

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
        user = await arg.get_member(ctx, user)
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
    async def disable(self, ctx, *, command: str):
        command = self.bot.get_command(command)
        if not command:
            return await ctx.send("Invalid command :no_entry:")
        command.enabled = not command.enabled
        if command.enabled == False:
            await ctx.send("`{}` has been disabled.".format(command))
        else:
            await ctx.send("`{}` has been enabled.".format(command))

    @commands.command(hidden=True)
    @checks.is_owner()
    async def blacklistuser(self, ctx, user: str, boolean: bool):
        user = await arg.get_member(ctx, user)
        r.table("blacklist").insert({"id": "owner", "users": []}).run(durability="soft")
        data = r.table("blacklist").get("owner")
        if boolean == True:
            if str(user.id) not in data["users"].run(durability="soft"):
                data.update({"users": r.row["users"].append(str(user.id))}).run(durability="soft")
                await ctx.send("{} has been blacklisted.".format(user))
            else:
                await ctx.send("{} is already blacklisted.".format(user))
        if boolean == False:
            if str(user.id) not in data["users"].run(durability="soft"):
                await ctx.send("{} is not blacklisted.".format(user))
            else:
                data.update({"users": r.row["users"].difference([str(user.id)])}).run(durability="soft")
                await ctx.send("{} is no longer blacklisted".format(user))
		
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
        avatar = requests.get(url).content
        try:
            await self.bot.user.edit(password=None, avatar=avatar)
        except:
            return await ctx.send("Clap you've changed my profile picture too many times")
        await ctx.send("I have changed my profile picture")
		
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
    
    @commands.command(hidden=True)
    async def executions(self, ctx):
        msg = "\n".join(["`{}` - {}ms, {}MB average memory, {}MB max memory, {}ms max execution (Executed {} times)".format(x[0], format(x[1]["average"], ".2f"), format(x[1]["average_memory"], ".2f"), format(x[1]["max_memory_gained"], ".2f"), format(x[1]["max_execution_time"], ".2f"), x[1]["data_points"]) for x in execution_times.items()])
        i, n = 0, 2000
        for x in range(math.ceil(len(msg)/2000)):
            if i != 0:
                while msg[i-1:i] != "\n":
                    i -= 1
            while msg[n-1:n] != "\n":
                n -= 1
            await ctx.send(msg[i:n])
            i += 2000
            n += 2000

    @log
    async def on_guild_join(self, guild):
        guilds = len(self.bot.guilds)
        if guilds % 100 == 0:
            channel = guild.get_channel(493439822682259497)
            await channel.send("{:,} servers :tada:".format(guilds))

    @log
    async def on_guild_remove(self, guild):
        guilds = len(self.bot.guilds)
        if guilds % 100 != 0:
            channel = guild.get_channel(493439822682259497)
            for x in await channel.history(limit=1).flatten():
                if int(x.content.split(" ")[0].replace(",", "")) > guilds:
                    await x.delete() 

    async def on_command(self, ctx):
        webhook = discord.utils.get(await self.bot.get_guild(330399610273136641).webhooks(), id=507684441020170251)
        if checks.is_owner_c(ctx.author):
            ctx.command.reset_cooldown(ctx)
        try:
            s=discord.Embed(colour=0xffff00, timestamp=ctx.message.edited_at if ctx.message.edited_at else ctx.message.created_at)
            s.add_field(name="Message", value="Content: {}\nID: {}".format(ctx.message.content, ctx.message.id), inline=False)
            s.add_field(name="Channel", value="Name: {}\nID: {}".format(ctx.channel.name, ctx.channel.id), inline=False)
            s.add_field(name="Guild", value="Name: {}\nID: {}\nShard: {}\nMember Count: {:,}".format(ctx.guild.name, ctx.guild.id, ctx.guild.shard_id + 1, ctx.guild.member_count), inline=False)
            s.add_field(name="Author", value="User: {}\nID: {}".format(ctx.author, ctx.author.id), inline=False)
            s.add_field(name="Command", value="Prefix: {}\nCommand: {}\nArguments: {}".format(ctx.prefix, ctx.command, ctx.kwargs), inline=False)
            s.add_field(name="Attachments", value="\n".join(map(lambda x: x.url, ctx.message.attachments)) if ctx.message.attachments else "None", inline=False)
            await webhook.send(embed=s)
        except Exception as e:
            await webhook.send(e)
		
def setup(bot):
    bot.add_cog(owner(bot))