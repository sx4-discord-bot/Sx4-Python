import re
import asyncio
import math

previous_aliases = ["previous", "p", "previous page"]
next_aliases = ["next", "n", "next page"]
cancel_aliases = ["stop", "cancel", "c"]
all_aliases =  previous_aliases + next_aliases + cancel_aliases

async def page(ctx, array: list, selectable: bool=False, per_page: int=10, function: callable=None, timeout: int=60, indexed: bool=True):
    bot = ctx.bot
    current_page = 1
    max_page = math.ceil(len(array)/per_page)
    last_page_entries = len(array) % per_page if len(array) % per_page != 0 else per_page
    re_page = re.compile("go to ([0-9]+)")
    s=discord.Embed(title="Page {}/{}".format(current_page, max_page), description="\n".join([("{}. ".format(i) if indexed else "") +  "{}".format(function(x) if function else x) for i, x in enumerate(array[per_page*current_page-per_page:current_page*per_page], start=1)]))
    s.set_footer(text="next | previous | go to <page_number> | cancel")
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
                embed = message.embeds[0]
                embed.description = "\n".join([("{}. ".format(i) if indexed else "") +  "{}".format(function(x) if function else x) for i, x in enumerate(array[per_page*current_page-per_page:current_page*per_page], start=1)])
                embed.title = "Page {}/{}".format(current_page, max_page)
                try:
                    await response.delete()
                except:
                    pass
                await message.edit(embed=embed)
            elif response.content.lower() in previous_aliases:
                if current_page == 1:
                    current_page = max_page
                else:
                    current_page -= 1
                embed = message.embeds[0]
                embed.description = "\n".join([("{}. ".format(i) if indexed else "") +  "{}".format(function(x) if function else x) for i, x in enumerate(array[per_page*current_page-per_page:current_page*per_page], start=1)])
                embed.title = "Page {}/{}".format(current_page, max_page)
                try:
                    await response.delete()
                except:
                    pass
                await message.edit(embed=embed)
            elif regex_page:
                current_page = int(regex_page.group(1))
                embed = message.embeds[0]
                embed.description = "\n".join([("{}. ".format(i) if indexed else "") +  "{}".format(function(x) if function else x) for i, x in enumerate(array[per_page*current_page-per_page:current_page*per_page], start=1)])
                embed.title = "Page {}/{}".format(current_page, max_page)
                try:
                    await response.delete()
                except:
                    pass
                await message.edit(embed=embed)
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
                object = array[((current_page * per_page) - per_page) + (int(response.content) - 1)] 
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