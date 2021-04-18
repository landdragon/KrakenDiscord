import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION")
HEROKU_RELEASE_CREATED_AT = os.getenv("HEROKU_RELEASE_CREATED_AT")
HEROKU_SLUG_DESCRIPTION = os.getenv("HEROKU_SLUG_DESCRIPTION")


client = discord.Client()

bot = commands.Bot(command_prefix='>', description="This is a test Bot")


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    await ctx.send(numOne + numTwo)


@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", description="Lorem Ipsum asdasd",
                          timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(
        url="https://pluralsight.imgix.net/paths/python-7be70baaac.png")

    await ctx.send(embed=embed)


@client.event
async def on_ready():
    print(client.user.name)
    print("[ON]")
    print('- - - - - - - -')
    if IsInNotProd == "true":
        print('send message to say Hello')
        for Channel in client.get_all_channels():
            if Channel.type == discord.ChannelType.text:
                await Channel.send("salut je viens d'être livré avec pour version : " + HEROKU_RELEASE_VERSION)

client.run(TOKEN)
