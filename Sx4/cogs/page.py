import discord
import asyncio
from discord.ext import commands
from utils.PagedResult import PagedResult
from utils.PagedResult import PagedResultData
from random import choice as randchoice
import time
import datetime
import random
from utils import checks
import numbers
import os
from random import choice
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
from enum import Enum
import asyncio
from difflib import get_close_matches

class page:
	def __init__(self, bot, connection):
		self.bot = bot
		self.db = connection
	
	@commands.command(no_pm=True, aliases=["sroles", "roles"])
	async def serverroles(self, ctx):
		server = ctx.message.guild
		channel = ctx.message.channel
		author = ctx.message.author

		if server.id not in PagedResultData.paged_results:
			PagedResultData.paged_results[server.id] = dict()
			
		if channel.id not in PagedResultData.paged_results[server.id]:
			PagedResultData.paged_results[server.id][channel.id] = dict()
			
		paged_result = PagedResult(ctx.guild.roles[::-1], lambda role: role.mention)
		paged_result.list_indexes = True
		paged_result.selectable = False

		message = await channel.send(embed=paged_result.get_current_page_embed())

		paged_result.message_id = message.id

		PagedResultData.paged_results[server.id][channel.id][author.id] = paged_result
	
	@commands.command()
	async def members(self, ctx):
		server = ctx.message.guild
		channel = ctx.message.channel
		author = ctx.message.author
		
		if server.id not in PagedResultData.paged_results:
			PagedResultData.paged_results[server.id] = dict()
		
		if channel.id not in PagedResultData.paged_results[server.id]:
			PagedResultData.paged_results[server.id][channel.id] = dict()
		
		paged_result = PagedResult(list(server.members), lambda member: member.mention)
		paged_result.list_indexes = True
		paged_result.selectable = True
		
		async def selected(event):
			joined_server = event.entry.joined_at.strftime("%d %b %Y %H:%M")
			joined_discord = event.entry.created_at.strftime("%d %b %Y %H:%M")
			if event.entry.status == discord.Status.online:
				status="Online<:online:361440486998671381>"
			if event.entry.status == discord.Status.idle:
				status="Idle<:idle:361440487233814528>"
			if event.entry.status == discord.Status.do_not_disturb:
				status="DND<:dnd:361440487179157505>"
			if event.entry.status == discord.Status.offline:
				status="Offline<:offline:361445086275567626>"
			description=""
			if not event.entry.activity:
				pass
			elif event.entry.activity:
				description="{} {}".format(event.entry.activity.type.name.title(), event.entry.activity.name)
			elif event.entry.activity.url:
				description="Streaming [{}]({})".format(event.entry.activity.name, event.entry.activity.url)
			s=discord.Embed(description=description, colour=event.entry.colour, timestamp=__import__('datetime').datetime.utcnow())
			s.set_author(name=event.entry.name, icon_url=event.entry.avatar_url)
			s.set_thumbnail(url=event.entry.avatar_url)
			s.add_field(name="Joined Discord", value=joined_discord)
			s.add_field(name="Joined {}".format(server .name), value=joined_server)
			s.add_field(name="Name", value="{}".format(event.entry.name))
			s.add_field(name="Nickname", value="{}".format(event.entry.nick))
			s.add_field(name="Discriminator", value="#{}".format(event.entry.discriminator))
			s.add_field(name="Status", value="{}".format(status))
			s.add_field(name="User's Colour", value="{}".format(event.entry.colour))
			s.add_field(name="User's ID", value="{}".format(event.entry.id))
			s.set_footer(text="Requested by {}".format(author))
			s.add_field(name="Highest Role", value=event.entry.top_role)
			s.add_field(name="Roles", value=len(event.entry.roles)) 
			await channel.send(embed=s)
		
		paged_result.on_select = selected

		message = await channel.send(embed=paged_result.get_current_page_embed())

		paged_result.message_id = message.id

		PagedResultData.paged_results[server.id][channel.id][author.id] = paged_result
		
	async def on_message(self, message):
		# Not sure how you store the other stuff but I suppose you do something like this
		server = message.guild
		channel = message.channel
		author = message.author
		
		paged_results = PagedResultData.paged_results
		
		paged_result = None
		if server.id in paged_results:
			if channel.id in paged_results[server.id]:
				if author.id in paged_results[server.id][channel.id]:
					paged_result = paged_results[server.id][channel.id][author.id]
		
		if paged_result is None:
			return
		
		page_message = None
		
		try:
			# Get message from paged_result.message_id and set message to it
			page_message = await channel.get_message(paged_result.message_id)
		except TypeError:
			pass
		
		if message.content == "next page":
			if paged_result.next_page():
				await message.delete()
				if page_message == None:
					# Send paged_result.get_current_page_embed() and set paged_result.message_id to its id
					temp_message = await channel.send(embed=paged_result.get_current_page_embed())
					paged_result.message_id = temp_message.id
				else:
					# Edit the message by paged_result.message_id to paged_result.get_current_page_embed()
					await page_message.edit(embed=paged_result.get_current_page_embed())
		elif message.content == "previous page":
			if paged_result.previous_page():
				await message.delete()
				if page_message == None:
					# Send paged_result.get_current_page_embed() and set paged_result.message_id to its id
					temp_message = await channel.send(embed=paged_result.get_current_page_embed())
					paged_result.message_id = temp_message.id
				else:
					# Edit the message by paged_result.message_id to paged_result.get_current_page_embed()
					await page_message.edit(embed=paged_result.get_current_page_embed())
		elif message.content.startswith("go to page "):
			number = None
			try:
				number = int(message.content[len("go to page "):])
			except ValueError:
				await channel.send("Invalid page number")
			
				return
				
			if paged_result.set_page(number):
				await message.delete()
				if page_message == None:
					# Send paged_result.get_current_page_embed() and set paged_result.message_id to its id
					temp_message = await channel.send(embed=paged_result.get_current_page_embed())
					paged_result.message_id = temp_message.id
				else:
					# Edit the message by paged_result.message_id to paged_result.get_current_page_embed()
					await page_message.edit(embed=paged_result.get_current_page_embed())
			else:
				await channel.send("Invalid page number")
			return
		elif message.content == "cancel":
			if page_message != None:
				# Delete message by paged_result.message_id
				await message.delete()
				await page_message.delete()
			
			del paged_results[server.id][channel.id][author.id]
		
		if paged_result.selectable:
			number = None
			try:
				number = int(message.content)
			except ValueError:
				return
				
			if number > 0 and number <= paged_result.entries_per_page:
				del paged_results[server.id][channel.id][author.id]
				
				await message.delete()
				await page_message.delete()
				
				await paged_result.select(number)
	
def setup(bot, connection):
	bot.add_cog(page(bot, connection))