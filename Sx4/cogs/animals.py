import discord
from discord.ext import commands
from utils import checks
from urllib.request import Request, urlopen
import json
import urllib
import requests

class animals:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def catfact(self, ctx):
        """Learn cat stuff"""
        url = "https://catfact.ninja/fact"
        request = Request(url)
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=data["fact"], colour=ctx.message.author.colour)
        s.set_author(name="Did you know?")
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/134/cat-face_1f431.png")
        await ctx.send(embed=s)
        
    @commands.command()
    async def dogfact(self, ctx):
        """Learn dog stuff"""
        url = "https://fact.birb.pw/api/v1/dog"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=data["string"], colour=ctx.message.author.colour)
        s.set_author(name="Did you know?")
        s.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/134/dog-face_1f436.png")
        await ctx.send(embed=s)
        
    @commands.command(aliases=["bird"])
    async def birb(self, ctx):
        """Shows a random birb"""
        url = "http://random.birb.pw/tweet.json/"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=":bird:", colour=ctx.message.author.colour)
        s.set_image(url="http://random.birb.pw/img/" + data["file"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The birb didn't make it, sorry :no_entry:")
        
    @commands.command()
    async def dog(self, ctx):
        """Shows a random dog"""
        url = "https://dog.ceo/api/breeds/image/random"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=":dog:", colour=ctx.message.author.colour)
        s.set_image(url=data["message"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The dog didn't make it, sorry :no_entry:")
        
    @commands.command()
    async def cat(self, ctx):
        """Shows a random cat"""
        response = requests.get("http://thecatapi.com/api/images/get?format=src")
        image = response.url
        s=discord.Embed(description=":cat:", colour=ctx.message.author.colour)
        s.set_image(url=image)
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The cat didn't make it, sorry :no_entry:")
		
    @commands.command()
    async def duck(self, ctx):
        "Shows a random duck"
        url = "https://random-d.uk/api/v1/random"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=":duck:", colour=ctx.message.author.colour)
        s.set_image(url=data["url"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The duck didn't make it, sorry :no_entry:")

    @commands.command()
    async def fox(self, ctx):
        "Shows a random fox"
        url = "https://randomfox.ca/floof/"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        s=discord.Embed(description=":fox:", colour=ctx.message.author.colour)
        s.set_image(url=data["image"])
        try:
            await ctx.send(embed=s)
        except:
            await ctx.send("The Fox didn't make it, sorry :no_entry:")
        
def setup(bot):
    bot.add_cog(animals(bot))