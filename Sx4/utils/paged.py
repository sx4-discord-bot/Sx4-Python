import re
import asyncio
import math
import discord

previous_aliases = ["previous", "p", "previous page"]
next_aliases = ["next", "n", "next page"]
cancel_aliases = ["stop", "cancel", "c"]
page_locations = ["title", "footer"]
all_aliases =  previous_aliases + next_aliases + cancel_aliases
confirmed = ["y", "yes", "accept"]

async def page(ctx, array: list, selectable: bool=False, per_page: int=10, function: callable=None, timeout: int=60, auto_select: bool=False, indexed: bool=True, page_location: str="title", title: str="", colour: int=None, author: dict={"name": "", "icon_url": discord.Embed.Empty, "url": ""}):
    bot = ctx.bot
    page_location = page_location.lower()
    current_page = 1
    max_page = math.ceil(len(array)/per_page)
    last_page_entries = len(array) % per_page if len(array) % per_page != 0 else per_page
    if selectable and len(array) == 1 and auto_select:
        page = current_page
        index = 0
        index_on_page = 1
        object = array[index] 
        return {"object": object, "user_index": index_on_page, "index": index, "page": page}
    re_page = re.compile("go to ([0-9]+)")
    s=discord.Embed(title="Page {}/{}".format(current_page, max_page) + (" | " + title if title else "") if page_location == "title" else title, 
    description="\n".join([("{}. ".format(i) if indexed else "") +  "{}".format(function(x) if function else x) for i, x in enumerate(array[per_page*current_page-per_page:current_page*per_page], start=1)]),
    colour=discord.Colour(colour) if colour else discord.Embed.Empty)
    s.set_author(name=author["name"] if "name" in author else "", icon_url=author["icon_url"] if "icon_url" in author else discord.Embed.Empty, url=author["url"] if "url" in author else "")
    s.set_footer(text="next | previous | go to <page_number> | cancel{}".format(" | Page {}/{}".format(current_page, max_page) if page_location == "footer" else ""))
    message = await ctx.send(embed=s)
    def check(m):
        regex = re_page.match(m.content.lower())
        if ctx.channel == m.channel and ctx.author == m.author:
            if regex:
                return int(regex.group(1)) <= max_page and int(regex.group(1)) > 0
            if not selectable:
                return m.content.lower() in all_aliases
            else:
                if m.content.lower() in all_aliases:
                    return True
                elif m.content.isdigit():
                    return int(m.content) > 0 and int(m.content) <= (per_page if current_page != max_page else last_page_entries)
                else:
                    return False
    def update_page(current_page: int):
        embed = message.embeds[0]
        embed.description = "\n".join([("{}. ".format(i) if indexed else "") +  "{}".format(function(x) if function else x) for i, x in enumerate(array[per_page*current_page-per_page:current_page*per_page], start=1)])
        embed.title = "Page {}/{}".format(current_page, max_page) + (" | " + title if title else "") if page_location == "title" else title
        if page_location == "footer":
            embed.set_footer(text="next | previous | go to <page_number> | cancel | Page {}/{}".format(current_page, max_page))
        return embed
    while True:
        try:
            response = await bot.wait_for("message", check=check, timeout=timeout)
            regex_page = re_page.match(response.content.lower())
            if response.content.lower() in cancel_aliases:
                try:
                    await message.delete()
                except:
                    pass
                try:
                    await response.delete()
                except:
                    pass
                return None
            elif response.content.lower() in next_aliases:
                if current_page == max_page:
                    current_page = 1
                else:
                    current_page += 1
                try:
                    await response.delete()
                except:
                    pass
                await message.edit(embed=update_page(current_page))
            elif response.content.lower() in previous_aliases:
                if current_page == 1:
                    current_page = max_page
                else:
                    current_page -= 1
                try:
                    await response.delete()
                except:
                    pass
                await message.edit(embed=update_page(current_page))
            elif regex_page:
                current_page = int(regex_page.group(1))
                try:
                    await response.delete()
                except:
                    pass
                await message.edit(embed=update_page(current_page))
            elif response.content.isdigit():
                try:
                    await message.delete()
                except:
                    pass
                try:
                    await response.delete()
                except:
                    pass
                page = current_page
                index = ((current_page * per_page) - per_page) + (int(response.content) - 1)
                index_on_page = int(response.content)
                object = array[index] 
                return {"object": object, "user_index": index_on_page, "index": index, "page": page}
        except asyncio.TimeoutError:
            try:
                await message.delete()
            except:
                pass
            try:
                await response.delete()
            except:
                pass
            return None

async def confirm(ctx, timeout: int=60, message: discord.Message=None):
    bot = ctx.bot
    try:
        response = await bot.wait_for("message", check=lambda m: ctx.author == m.author and ctx.channel == m.channel, timeout=timeout)
        if response.content.lower() in confirmed:
            return True
        else:
            try:
                if message:
                    await message.delete()
            except:
                pass
            try:
                await response.delete()
            except:
                pass
            return False
    except asyncio.TimeoutError:
        try:
            if message:
                await message.delete()
        except:
            pass
        try:
            await response.delete()
        except:
            pass
