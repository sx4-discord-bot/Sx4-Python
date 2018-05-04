from discord.ext import commands
import discord.utils
import json

def is_owner_check(ctx):
    return ctx.message.author.id == "153286414212005888" or ctx.message.author.id == "151766611097944064" or ctx.message.author.id == "402557516728369153" or ctx.message.author.id == "190551803669118976"

def is_owner():
    return commands.check(is_owner_check)
	
def is_donor_check(ctx):
	donor_list = ['181355725790904320', '230533871119106049', '358115593343467521']
	if(ctx.message.author.id in donor_list):
		return True
	else:
		return False

def is_donor():
	return commands.check(is_donor_check)

def check_permissions(ctx, perms):
	if is_owner_check(ctx):
		return True
	ch = ctx.message.channel
	author = ctx.message.author
	resolved = ch.permissions_for(author)
	return all(getattr(resolved, name, None) == value for name, value in perms.items())

def role_or_permissions(ctx, check, **perms):
	if check_permissions(ctx, perms):
		return True

	ch = ctx.message.channel
	author = ctx.message.author
	if ch.is_private:
		return False # can't have roles in PMs

	role = discord.utils.find(check, author.roles)
	return role is not None

def mod_or_permissions(**perms):
	def predicate(ctx):
		admin_role = "Sx4 Admin"
		mod_role = "Bot Commander"
		server = ctx.message.server
		return role_or_permissions(ctx, lambda r: r.name.lower() in (mod_role,admin_role), **perms)

	return commands.check(predicate)

def admin_or_permissions(**perms):
	def predicate(ctx):
		admin_role = "Sx4 Admin"
		server = ctx.message.server
		return role_or_permissions(ctx, lambda r: r.name.lower() == admin_role.lower(), **perms)

	return commands.check(predicate)

def serverowner_or_permissions(**perms):
	def predicate(ctx):
		if ctx.message.server is None:
			return False
		server = ctx.message.server
		owner = server.owner

		if ctx.message.author.id == owner.id:
			return True

	return commands.check(predicate)
