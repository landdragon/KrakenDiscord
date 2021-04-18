import discord
from discord.ext import commands
import os
import asyncio
import datetime

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION")
HEROKU_RELEASE_CREATED_AT = os.getenv("HEROKU_RELEASE_CREATED_AT")
HEROKU_SLUG_DESCRIPTION = os.getenv("HEROKU_SLUG_DESCRIPTION")


bot = commands.Bot(command_prefix='#', description="This is a test Bot")


@bot.command()
async def ping(ctx):
    print("ping")
    await ctx.send('pong')


@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    print("sum")
    await ctx.send(numOne + numTwo)


@bot.command()
async def info(ctx):
    print("info")
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


@bot.listen()
async def on_ready():
    print(bot.user.name)
    print("[ON]")
    print('- - - - - - - -')

bot.run(TOKEN)
