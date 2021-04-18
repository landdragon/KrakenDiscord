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
    embed = discord.Embed(title=f"KrakenDiscord", description="Bot pour faire des commande sur Kraken",
                          timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="HEROKU RELEASE VERSION",
                    value=HEROKU_RELEASE_VERSION)
    embed.add_field(name="HEROKU RELEASE CREATED AT",
                    value=HEROKU_RELEASE_CREATED_AT)
    embed.add_field(name="HEROKU SLUG DESCRIPTION",
                    value=HEROKU_SLUG_DESCRIPTION)
    embed.set_thumbnail(
        url="https://logo-marque.com/wp-content/uploads/2021/03/Kraken-Logo-650x366.png")

    await ctx.send(embed=embed)


@bot.listen()
async def on_ready():
    print(bot.user.name)
    print("[ON]")
    print('- - - - - - - -')

bot.run(TOKEN)
