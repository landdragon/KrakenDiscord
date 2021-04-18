import discord
from discord.ext import commands
import os
import datetime

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION")
HEROKU_RELEASE_CREATED_AT = os.getenv("HEROKU_RELEASE_CREATED_AT")
HEROKU_SLUG_DESCRIPTION = os.getenv("HEROKU_SLUG_DESCRIPTION")
CHANNEL_WORK = os.getenv("CHANNEL_WORK")

bot = commands.Bot(command_prefix='#', description="This is a test Bot")


@bot.command(help="ping pong")
async def ping(ctx: discord.ext.commands.Context):
    print("ping")
    if ctx.channel.name != CHANNEL_WORK:
        return
    await ctx.send('pong')


@bot.command(help="where I should request this bot")
async def where(ctx: discord.ext.commands.Context):
    print("where")
    print(ctx.channel.name != CHANNEL_WORK)
    await ctx.send("The commande will work at " + CHANNEL_WORK + "and you are at " + ctx.channel.name + ". you are not at the good place ? " +
                   ctx.channel.name != CHANNEL_WORK)


@bot.command(help="get info")
async def info(ctx: discord.ext.commands.Context):
    print("info")
    if ctx.channel.name != CHANNEL_WORK:
        return
    embed = discord.Embed(title=f"KrakenDiscord", description="Bot pour faire des commande sur Kraken",
                          timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="Version",
                    value=HEROKU_RELEASE_VERSION)
    embed.add_field(name="Date de deploiment",
                    value=HEROKU_RELEASE_CREATED_AT)
    embed.add_field(name="Github Version",
                    value=HEROKU_SLUG_DESCRIPTION)
    embed.set_thumbnail(
        url="https://pme-bourse.fr/wp-content/uploads/2019/08/kraken-avis-300x300.png")

    await ctx.send(embed=embed)


@bot.listen()
async def on_ready():
    print(bot.user.name)
    print("[ON]")
    print('- - - - - - - -')

bot.run(TOKEN)
