import discord
from discord.ext import commands
import rethinkdb as r
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
import logging
from cogs import mod
import asyncio
import random
from utils import arghelp, arg
import time

reinvite = re.compile("(?:[\s \S]|)*(?:https?://)?(?:www.)?(?:discord.gg|(?:canary.)?discordapp.com/invite)/((?:[a-zA-Z0-9]){2,32})(?:[\s \S]|)*", re.IGNORECASE)


class antiad:

    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
		
    @commands.group(usage="<sub command>")
    async def antiinvite(self, ctx):
        """Block out those discord invite advertisers"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("antiad").insert({"id": str(server.id), "toggle": False, "modtoggle": True, "admintoggle": False, "bottoggle": True, "baninvites": False, "channels": [], "action": None, "attempts": 3, "users": []}).run(self.db, durability="soft")
		
    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def toggle(self, ctx):
        """Toggle antiinvite on or off"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["toggle"].run(self.db, durability="soft") == True:
            data.update({"toggle": False}).run(self.db, durability="soft")
            await ctx.send("Anti-invite has been **Disabled**")
            return
        if data["toggle"].run(self.db, durability="soft") == False:
            data.update({"toggle": True}).run(self.db, durability="soft")
            await ctx.send("Anti-invite has been **Enabled**")
            return

    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def banusernames(self, ctx):
        """Ban users if they join with an advertising discord link username"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["baninvites"].run(self.db, durability="soft") == True:
            data.update({"baninvites": False}).run(self.db, durability="soft")
            await ctx.send("I will no longer ban users with a discord link as their name.")
            return
        if data["baninvites"].run(self.db, durability="soft") == False:
            data.update({"baninvites": True}).run(self.db, durability="soft")
            await ctx.send("I will now ban users with a discord link as their name.")
            return

    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def action(self, ctx, action: str):
        """Set an action (mute, kick, ban, none) to happen when a user reaches a certain amount of posted invites (defaults at 3 but can be changed using `s?antiinvite attempts <amount>`)"""
        data = r.table("antiad").get(str(ctx.guild.id))
        if action.lower() in ["none", "off"]:
            await ctx.send("Auto mod for antiinvite is now disabled.")
            data.update({"action": None}).run(self.db, durability="soft")
        elif action.lower() in ["mute", "kick", "ban"]:
            await ctx.send("Users who post **{}** {} will now receive a **{}**".format(data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites", action.lower()))
            data.update({"action": action.lower()}).run(self.db, durability="soft")
        else:
            await ctx.send("That is not a valid action :no_entry:")

    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def attempts(self, ctx, attempts: int):
        """Sets the amount of invites which can be sent by a user before an action happens"""
        data = r.table("antiad").get(str(ctx.guild.id))
        if attempts < 1:
            return await ctx.send("The amount of sent invites needs to be 1 or above :no_entry:")
        if attempts > 500:
            return await ctx.send("The max amount of attempts is 500 :no_entry:")
        if data["action"].run(self.db, durability="soft"):
            await ctx.send("Users who post **{}** {} will now receive a **{}**".format(attempts, "invite" if attempts == 1 else "invites", data["action"].run(self.db, durability="soft")))
        else:
            await ctx.send("Attempts set to **{}** to make the bot do an action after **{}** {}, use `{}antiinvite action <action>`".format(attempts, attempts, "attempt" if attempts == 1 else "attempts", ctx.prefix))
        data.update({"attempts": attempts}).run(self.db, durability="soft")

    @antiinvite.command(aliases=["reset"])
    async def resetattempts(self, ctx, user: str=None):
        """Resets the attempts of a user"""
        if not user:
            user = ctx.author
        else:
            user = arg.get_server_member(ctx, user)
            if not user:
                return await ctx.send("I could not find that user :no_entry:")
        data = r.table("antiad").get(str(ctx.guild.id))
        if str(user.id) not in data["users"].map(lambda x: x["id"]).run(self.db, durability="soft"):
            return await ctx.send("This user doesn't have any attempts :no_entry:")
        else:
            if data["users"].filter(lambda x: x["id"] == str(user.id))[0]["attempts"].run(self.db, durability="soft") == 0:
                return await ctx.send("This user doesn't have any attempts :no_entry:")
            else:
                await ctx.send("**{}** attempts have been reset.".format(user))
                data.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(user.id), x.merge({"attempts": 0}), x))}).run(self.db, durability="soft")
        
    @antiinvite.command() 
    @checks.has_permissions("manage_guild")
    async def modtoggle(self, ctx):
        """Choose whether you want your mods to be able to send invites or not (manage_message and above are classed as mods)"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["modtoggle"].run(self.db, durability="soft") == True:
            data.update({"modtoggle": False}).run(self.db, durability="soft")
            await ctx.send("Mods will now not be affected by anti-invite.")
            return
        if data["modtoggle"].run(self.db, durability="soft") == False:
            data.update({"modtoggle": True}).run(self.db, durability="soft")
            await ctx.send("Mods will now be affected by anti-invite.")
            return
			
    @antiinvite.command() 
    @checks.has_permissions("manage_guild")
    async def admintoggle(self, ctx):
        """Choose whether you want your admins to be able to send invites or not (administrator perms are classed as admins)"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["admintoggle"].run(self.db, durability="soft") == True:
            data.update({"admintoggle": False}).run(self.db, durability="soft")
            await ctx.send("Admins will now not be affected by anti-invite.")
            return
        if data["admintoggle"].run(self.db, durability="soft") == False:
            data.update({"admintoggle": True}).run(self.db, durability="soft")
            await ctx.send("Admins will now be affected by anti-invite.")
            return
			
    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def togglebot(self, ctx):
        """Choose whether bots can send invites or not"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if data["bottoggle"].run(self.db, durability="soft") == True:
            data.update({"bottoggle": False}).run(self.db, durability="soft")
            await ctx.send("Bots will now not be affected by anti-invite.")
            return
        if data["bottoggle"].run(self.db, durability="soft") == False:
            data.update({"bottoggle": True}).run(self.db, durability="soft")
            await ctx.send("Bots will now be affected by anti-invite.")
            return
			
    @antiinvite.command()
    @checks.has_permissions("manage_guild")
    async def togglechannel(self, ctx, channel: discord.TextChannel=None):
        """Choose what channels you want to count towards antiinvite"""
        server = ctx.guild
        data = r.table("antiad").get(str(server.id))
        if not channel:
           channel = ctx.channel 
        if str(channel.id) in data["channels"].run(self.db, durability="soft"):
            data.update({"channels": r.row["channels"].difference([str(channel.id)])}).run(self.db, durability="soft")
            await ctx.send("Anti-invite is now enabled in <#{}>".format(str(channel.id)))
        else: 
            data.update({"channels": r.row["channels"].append(str(channel.id))}).run(self.db, durability="soft")
            await ctx.send("Anti-invite is now disabled in <#{}>".format(str(channel.id)))
		 
    @antiinvite.command()
    async def stats(self, ctx):  
        """View the settings of the antiinvite in your server"""
        serverid=ctx.guild.id
        server=ctx.guild
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Anti-invite Settings", icon_url=self.bot.user.avatar_url)
        data = r.table("antiad").get(str(server.id))
        msg = ""
        if data["toggle"].run(self.db, durability="soft") == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        if data["modtoggle"].run(self.db, durability="soft") == False:
            mod = "Mods **Can** send links"
        else:
            mod = "Mods **Can't** send links"
        if data["bottoggle"].run(self.db, durability="soft") == False:
            bottoggle = "Bots **Can** send links"
        else:
            bottoggle = "Bots **Can't** send links"
        if data["admintoggle"].run(self.db, durability="soft") == False:
            admin = "Admins **Can** send links"
        else:
            admin = "Admins **Can't** send links"
        if data["action"].run(self.db, durability="soft"):
            action = "Sending {} {} will result in a {}".format(data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites", data["action"].run(self.db, durability="soft"))
        else:
            action = "Disabled"
        s.add_field(name="Status", value=toggle)
        s.add_field(name="Mod Perms", value=mod)
        s.add_field(name="Admin Perms", value=admin)
        s.add_field(name="Bots", value=bottoggle)
        s.add_field(name="Auto Mod", value=action)
        s.add_field(name="Ban Users with Invites in their names", value="Yes" if data["baninvites"].run(self.db) else "No")
        for channelid in data["channels"].run(self.db, durability="soft"):
            channel = discord.utils.get(server.channels, id=int(channelid))
            msg += channel.mention + "\n"
        s.add_field(name="Disabled Channels", value=msg if msg != "" else "None")
        await ctx.send(embed=s)

    async def on_member_join(self, member):
        server = member.guild
        if r.table("antiad").get(str(server.id))["baninvites"].run(self.db) == True:
            if reinvite.match(member.name):
                try:
                    invite = await self.bot.get_invite(reinvite.match(member.name).group(1))
                    if invite.guild == server:
                        return
                    else:
                        reason = "Invite in username"
                        action = "Ban (Automatic)"
                        author = member
                        await server.ban(member, reason=reason)
                        await mod._log(self.bot, self.bot.user, server, action, reason, author, self.db)
                except:
                    return
	
    async def on_message(self, message): 
        serverid = message.guild.id
        server = message.guild
        author = message.author
        channel = message.channel
        data = r.table("antiad").get(str(serverid))
        if not data.run(self.db):
            return
        if author == self.bot.user:
            return
        if data["modtoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).manage_messages:
                return
        if data["admintoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).administrator:
                return
        if data["bottoggle"].run(self.db, durability="soft") == False:
            if author.bot:
                return
        if str(channel.id) in data["channels"].run(self.db, durability="soft"):
            return
        if data["toggle"].run(self.db, durability="soft") == True:
            if reinvite.match(message.content):
                try:
                    invite = await self.get_invite(reinvite.match(message.content).group(1))
                    if "guild" in invite:
                        if invite["guild"]["id"] == str(server.id):
                            return
                    elif "channel" in invite:
                        pass
                    else:
                        return
                    await message.delete()
                    msg = "{}, You are not allowed to send invite links here :no_entry:".format(author.mention)
                    if data["action"].run(self.db, durability="soft"):
                        if str(author.id) not in data["users"].map(lambda x: x["id"]).run(self.db, durability="soft"):
                            amount = 1
                            userdata = {}
                            userdata["attempts"] = amount
                            userdata["id"] = str(author.id)
                            data.update({"users": r.row["users"].append(userdata)}).run(self.db, durability="soft", noreply=True)
                        else:
                            amount = data["users"].filter(lambda x: x["id"] == str(author.id))[0]["attempts"].run(self.db, durability="soft") + 1
                        msg = "{}, You are not allowed to send invite links here, If you continue you will receive a {}. **({}/{})** :no_entry:".format(author.mention, data["action"].run(self.db, durability="soft"), amount, data["attempts"].run(self.db, durability="soft"))
                        if amount >= data["attempts"].run(self.db, durability="soft"):
                            if data["action"].run(self.db, durability="soft") == "ban":
                                try:
                                    reason = "Auto ban (Sent {} invite link(s))".format(data["attempts"].run(self.db, durability="soft"))
                                    await server.ban(author, reason=reason)
                                    msg = "**{}** was banned for sending a total of **{}** {}".format(author, data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites")
                                    amount = 0
                                    action = "Ban (Automatic)"
                                except:
                                    msg = "I attempted to ban **{}** for posting too many invite links but it failed, check my role is above the users top role and i have sufficient permissions :no_entry:".format(author)
                            if data["action"].run(self.db, durability="soft") == "kick":
                                try:
                                    reason = "Auto kick (Sent {} invite link(s))".format(data["attempts"].run(self.db, durability="soft"))
                                    await server.kick(author, reason=reason)
                                    msg = "**{}** was kicked for sending a total of **{}** {}".format(author, data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites")
                                    amount = 0
                                    action = "Kick (Automatic)"
                                except:
                                    msg = "I attempted to kick **{}** for posting too many invite links but it failed, check my role is above the users top role and i have sufficient permissions :no_entry: {}".format(author)
                            if data["action"].run(self.db, durability="soft") == "mute":
                                if str(server.id) not in r.table("mute").map(lambda x: x["id"]).run(self.db, durability="soft"):
                                    r.table("mute").insert({"id": str(server.id), "users": []}).run(self.db, durability="soft", noreply=True)
                                mutedata = r.table("mute").get(str(serverid))
                                role = discord.utils.get(server.roles, name="Muted - Sx4")
                                if not role:
                                    try:
                                        role = await server.create_role(name="Muted - Sx4")
                                    except:
                                        msg = "I was unable to make the mute role therefore i was not able to mute {}, check if i have the manage_roles permission :no_entry:".format(author)
                                if role:
                                    try:
                                        await author.add_roles(role)
                                        msg = "**{}** was muted for 60 minutes for sending a total of **{}** {}".format(author, data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites")
                                        action = "Mute (Automatic)"
                                        reason = "Auto mute (Sent {} invite link(s))".format(data["attempts"].run(self.db, durability="soft"))
                                        amount = 0
                                        if str(author.id) not in mutedata["users"].map(lambda x: x["id"]).run(self.db, durability="soft"):
                                            userobj = {}
                                            userobj["id"] = str(author.id)
                                            userobj["toggle"] = True
                                            userobj["amount"] = 3600
                                            userobj["time"] = message.created_at.timestamp()
                                            mutedata.update({"users": r.row["users"].append(userobj)}).run(self.db, durability="soft", noreply=True)
                                        else:
                                            mutedata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(author.id), x.merge({"time": message.created_at.timestamp(), "amount": 3600, "toggle": True}), x))}).run(self.db, durability="soft", noreply=True)
                                    except:
                                        msg = "I attempted to mute **{}** for posting too many invite links but it failed, check that i have the manage_roles permission and that my role is above the mute role :no_entry:".format(author)
                        data.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(author.id), x.merge({"attempts": amount}), x))}).run(self.db, durability="soft", noreply=True)
                    await channel.send(msg)
                    await mod._log(self.bot, self.bot.user, server, action, reason, author, self.db)
                except:
                    return
				
    async def on_message_edit(self, before, after): 
        serverid = before.guild.id
        server = before.guild
        author = before.author
        channel = before.channel
        data = r.table("antiad").get(str(serverid))
        if not data.run(self.db):
            return
        if author == self.bot.user:
            return
        if data["modtoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).manage_messages:
                return
        if data["admintoggle"].run(self.db, durability="soft") == False:
            if channel.permissions_for(author).administrator:
                return
        if data["bottoggle"].run(self.db, durability="soft") == False:
            if author.bot:
                return
        if str(channel.id) in data["channels"].run(self.db, durability="soft"):
            return
        if data["toggle"].run(self.db, durability="soft") == True:
            if reinvite.match(after.content):
                try:
                    invite = await self.get_invite(reinvite.match(after.content).group(1))
                    if "guild" in invite:
                        if invite["guild"]["id"] == str(server.id):
                            return
                    elif "channel" in invite:
                        pass
                    else:
                        return
                    await after.delete()
                    msg = "{}, You are not allowed to send invite links here :no_entry:".format(author.mention)
                    if data["action"].run(self.db, durability="soft"):
                        if str(author.id) not in data["users"].map(lambda x: x["id"]).run(self.db, durability="soft"):
                            amount = 1
                            userdata = {}
                            userdata["attempts"] = amount
                            userdata["id"] = str(author.id)
                            data.update({"users": r.row["users"].append(userdata)}).run(self.db, durability="soft", noreply=True)
                        else:
                            amount = data["users"].filter(lambda x: x["id"] == str(author.id))[0]["attempts"].run(self.db, durability="soft", noreply=True) + 1
                        msg = "{}, You are not allowed to send invite links here, If you continue you will receive a {}. **({}/{})** :no_entry:".format(author.mention, data["action"].run(self.db, durability="soft"), amount, data["attempts"].run(self.db, durability="soft"))
                        if amount >= data["attempts"].run(self.db, durability="soft"):
                            if data["action"].run(self.db, durability="soft") == "ban":
                                try:
                                    reason = "Auto ban (Sent {} invite link(s))".format(data["attempts"].run(self.db, durability="soft"))
                                    await server.ban(author, reason=reason)
                                    msg = "**{}** was banned for sending a total of **{}** {}".format(author, data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites")
                                    amount = 0
                                    action = "Ban (Automatic)"
                                except:
                                    msg = "I attempted to ban **{}** for posting too many invite links but it failed, check my role is above the users top role and i have sufficient permissions :no_entry:".format(author)
                            if data["action"].run(self.db, durability="soft") == "kick":
                                try:
                                    reason = "Auto kick (Sent {} invite link(s))".format(data["attempts"].run(self.db, durability="soft"))
                                    await server.kick(author, reason=reason)
                                    msg = "**{}** was kicked for sending a total of **{}** {}".format(author, data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites")
                                    amount = 0
                                    action = "Kick (Automatic)"
                                except:
                                    msg = "I attempted to kick **{}** for posting too many invite links but it failed, check my role is above the users top role and i have sufficient permissions :no_entry:".format(author)
                            if data["action"].run(self.db, durability="soft") == "mute":
                                if str(server.id) not in r.table("mute").map(lambda x: x["id"]).run(self.db, durability="soft"):
                                    r.table("mute").insert({"id": str(server.id), "users": []}).run(self.db, durability="soft", noreply=True)
                                mutedata = r.table("mute").get(str(serverid))
                                role = discord.utils.get(server.roles, name="Muted - Sx4")
                                if not role:
                                    try:
                                        role = await server.create_role(name="Muted - Sx4")
                                    except:
                                        msg = "I was unable to make the mute role therefore i was not able to mute {}, check if i have the manage_roles permission :no_entry:".format(author)
                                if role:
                                    try:
                                        await author.add_roles(role)
                                        msg = "**{}** was muted for 60 minutes for sending a total of **{}** {}".format(author, data["attempts"].run(self.db, durability="soft"), "invite" if data["attempts"].run(self.db, durability="soft") == 1 else "invites")
                                        amount = 0
                                        action = "Mute (Automatic)"
                                        reason = "Auto mute (Sent {} invite link(s))".format(data["attempts"].run(self.db, durability="soft"))
                                        if str(author.id) not in mutedata["users"].map(lambda x: x["id"]).run(self.db, durability="soft"):
                                            userobj = {}
                                            userobj["id"] = str(author.id)
                                            userobj["toggle"] = True
                                            userobj["amount"] = 3600
                                            userobj["time"] = after.edited_at.timestamp()
                                            mutedata.update({"users": r.row["users"].append(userobj)}).run(self.db, durability="soft", noreply=True)
                                        else:
                                            mutedata.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(author.id), x.merge({"time": after.edited_at.timestamp(), "amount": 3600, "toggle": True}), x))}).run(self.db, durability="soft", noreply=True)
                                    except:
                                        msg = "I attempted to mute **{}** for posting too many invite links but it failed, check that i have the manage_roles permission and that my role is above the mute role :no_entry:".format(author)
                        data.update({"users": r.row["users"].map(lambda x: r.branch(x["id"] == str(author.id), x.merge({"attempts": amount}), x))}).run(self.db, durability="soft", noreply=True)
                    await channel.send(msg)
                    mod._log(self.bot, self.bot.user, server, action, reason, author, self.db)
                except:
                    return

    async def get_invite(self, invite):
        client = self.bot.http
        r = discord.http.Route('GET', '/invite/{invite}?with_counts=true', invite=invite)
        return await client.request(r)

def setup(bot, connection): 
    bot.add_cog(antiad(bot, connection))