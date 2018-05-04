import collections
import discord
import math
from discord.ext import commands
import discord.utils

class PagedResultData:
    paged_results = dict()

class SelectedEvent:
	pass

class PagedResult:
	__page = 1
	entries_per_page = 10
	
	list_indexes = True
	selectable = True
	cancelable = True
	
	on_select = lambda s: s
	
	message_id = None
	
	def __init__(self, entries, display_function):
		if not isinstance(entries, collections.Iterable):
			raise ValueError("Incorrect type, entries is not an instance of list")
		
		if len(entries) <= 0:
			raise ValueError("List has no entries")
			
		self.entries = entries
		
		self.display_function = display_function
		
		self.__max_pages = self.determine_max_pages()
		
		self.embed = discord.Embed(colour=0xfff90d)
	
	def get_current_page(self):
		return self.__page
		
	def get_max_pages(self):
		return self.__max_pages
	
	def get_current_page_entries(self):
		start = (self.__page - 1) * self.entries_per_page
		
		if self.__page == self.__max_pages:
			end = len(self.entries) - start
		else:
			end = self.entries_per_page
			
		return self.entries[start:(start + end)]
	
	def get_current_page_embed(self):
		entries = self.get_current_page_entries()
		description = "Page **" + str(self.__page) + "**/**" + str(self.__max_pages) + "**\n"
		
		i = 1
		for e in entries:
			description = description + "\n" + (str(i) + " - " if self.list_indexes else "") + str(self.display_function(e))
			
			i = i + 1
			
		footer = ""
		if self.__page + 1 <= self.__max_pages:
			footer = footer + "next page | "
			
		if self.__page - 1 > 0:
			footer = footer + "previous page | "
		
		if self.__max_pages > 2:
			footer = footer + "go to page <page> | "
			
		if self.cancelable:
			footer = footer + "cancel"
		else:
			footer = footer[:-3]
			
		self.embed.description = description
		self.embed.set_footer(text=footer)
		
		return self.embed
	
	def determine_max_pages(self):
		return math.ceil(len(self.entries)/self.entries_per_page)
	
	async def select(self, index):
		event = SelectedEvent()
		event.page = self.__page
		event.index = index
		event.actual_index = (self.__page - 1) * self.entries_per_page + (index - 1)
		event.entry = self.entries[event.actual_index]
        
		await self.on_select(event)
			
	
	def set_page(self, page):
		if page > self.__max_pages:
			return False
		
		if page < 1:
			return False
		
		self.__page = page
		
		return True
	
	def next_page(self):
		if self.__page + 1 > self.__max_pages:
			return False
			
		self.__page = self.__page + 1
		
		return True
	
	def previous_page(self):
		if self.__page - 1 < 1:
			return False
			
		self.__page = self.__page - 1
		
		return True