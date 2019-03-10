from discord.ext import commands
import discord
import discord.utils
import json
import inspect

async def send(bot, ctx):
        msg = ""
        try:
            perms = ctx.command.checks[0]
        except:
            perms = None
        if not ctx.command.usage:
            for x in ctx.command.params:
                if x != "ctx":
                    if x != "self":
                        if "=" in str(ctx.command.params[x]):
                            msg += "[{}] ".format(x)
                        else:
                            msg += "<{}> ".format(x)
        else:
            msg += ctx.command.usage
        if not ctx.command.aliases:
            aliases = "None"
        else:
            aliases = ", ".join([x for x in ctx.command.aliases])
        if not perms:
            msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: None\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, ctx.command.help)
        else:
            msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, 
            ", ".join(inspect.getclosurevars(perms).nonlocals["perms"]) if perms.__name__ != "is_owner_check" and str(perms).split(" ")[1].split(".")[0] != "is_main_owner" else "Bot Owner", ctx.command.help)
        try:
            msg += "\n\nSub commands: {}".format(", ".join([x for x in ctx.command.all_commands if x not in ctx.command.all_commands[x].aliases]))
        except:
            pass
        s=discord.Embed(description=msg)
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        return await ctx.channel.send(embed=s)
