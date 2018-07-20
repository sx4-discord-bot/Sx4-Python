from discord.ext import commands
import discord
import discord.utils
import json

async def send(bot, ctx):
        msg = ""
        for x in ctx.command.params:
            if x != "ctx":
                if x != "self":
                    if "None" in str(ctx.command.params[x]):
                        msg += "[{}] ".format(x)
                    else:
                        msg += "<{}> ".format(x)
        if not ctx.command.aliases:
            aliases = "None"
        else:
            aliases = ", ".join([x for x in ctx.command.aliases])
        msg = "Usage: {}{} {}\nCommand aliases: {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, ctx.command.help)
        try:
            msg += "\n\nSub commands: {}".format(", ".join([x for x in ctx.command.all_commands if x not in ctx.command.all_commands[x].aliases]))
        except:
            pass
        s=discord.Embed(description=msg)
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        return await ctx.channel.send(embed=s)
