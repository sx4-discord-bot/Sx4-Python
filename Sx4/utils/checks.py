from discord.ext import commands
import discord
import discord.utils
import json

def is_owner_check(ctx):
    if ctx.author.id in [153286414212005888, 51766611097944064, 402557516728369153, 190551803669118976]:
        return True
    else:
        return False

def is_owner():
    return commands.check(is_owner_check)

def is_owner_c(author):
    if author.id in [153286414212005888, 51766611097944064, 402557516728369153, 190551803669118976]:
        return True

def has_permissions(*perms):
    def predicate(ctx):
        setattr(ctx.command, "permissions",", ".join(perms))
        if is_owner_check(ctx):
            return True
        else:
            return all(getattr(ctx.author.guild_permissions, perm, None) for perm in perms)
    return commands.check(predicate)
