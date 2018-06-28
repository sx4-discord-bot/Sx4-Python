from discord.ext import commands
import discord
import discord.utils
import json

def is_owner_check(ctx):
    if ctx.author.id == 153286414212005888 or ctx.author.id == 151766611097944064 or ctx.author.id == 402557516728369153 or ctx.author.id == 190551803669118976:
        return True
    else:
        return False

def is_owner():
    return commands.check(is_owner_check)

def is_owner_c(author):
	if author.id in [153286414212005888, 51766611097944064, 402557516728369153, 190551803669118976]:
	    return True

def check_permissions(ctx, perms):
	if is_owner_check(ctx):
		return True
	ch = ctx.channel
	author = ctx.author
	resolved = ch.permissions_for(author)
	return all(getattr(resolved, name, None) == value for name, value in perms.items())

def role_or_permissions(ctx, check, **perms):
	if check_permissions(ctx, perms):
		return True

	ch = ctx.channel
	author = ctx.author
	if ch == discord.DMChannel:
		return False # can't have roles in PMs

	role = discord.utils.find(check, author.roles)
	return role is not None

def mod_or_permissions(**perms):
	def predicate(ctx):
		admin_role = "Sx4 Admin"
		mod_role = "Bot Commander"
		server = ctx.guild
		return role_or_permissions(ctx, lambda r: r.name.lower() in (mod_role,admin_role), **perms)

	return commands.check(predicate)

def admin_or_permissions(**perms):
	def predicate(ctx):
		admin_role = "Sx4 Admin"
		server = ctx.guild
		return role_or_permissions(ctx, lambda r: r.name.lower() == admin_role.lower(), **perms)

	return commands.check(predicate)

def serverowner_or_permissions(**perms):
	def predicate(ctx):
		if ctx.guild is None:
			return False
		server = ctx.guild
		owner = server.owner

		if ctx.author.id == owner.id:
			return True

	return commands.check(predicate)
