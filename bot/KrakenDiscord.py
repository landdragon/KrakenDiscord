import discord
from discord.ext import commands
import os
import datetime
import krakenex
import psycopg2

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION")
HEROKU_RELEASE_CREATED_AT = os.getenv("HEROKU_RELEASE_CREATED_AT")
HEROKU_SLUG_DESCRIPTION = os.getenv("HEROKU_SLUG_DESCRIPTION")
CHANNEL_WORK = os.getenv("CHANNEL_WORK")

DATABASE_URL = os.getenv("DATABASE_URL")

bot = commands.Bot(command_prefix='#', description="This is a test Bot")
conn = psycopg2.connect(DATABASE_URL)


@bot.command(help="ping pong")
async def ping(ctx: commands.Context):
    print("ping")
    if ctx.channel.name != CHANNEL_WORK:
        return
    await ctx.send('pong')


@bot.command(help="where I should request this bot")
async def where(ctx: commands.Context):
    print("where")
    print(ctx.channel.name != CHANNEL_WORK)
    await ctx.send("The commande will work at " + CHANNEL_WORK + "and you are at " + ctx.channel.name + ". you are not at the good place ? " +
                   ctx.channel.name != CHANNEL_WORK)


@bot.command(help="get info")
async def info(ctx: commands.Context):
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


@bot.command(help="get list of pairs")
async def pairs(ctx: commands.Context):
    if ctx.channel.name != CHANNEL_WORK:
        return
    kraken = krakenex.API()
    response = kraken.query_public('AssetPairs')
    assetPairs = list(response['result'])
    print(assetPairs)
    shouldContain = 'eur'
    eurAssetPairs = [
        s for s in assetPairs if shouldContain.lower() in s.lower()]
    print(eurAssetPairs)
    await ctx.send(eurAssetPairs)


@bot.command(help="get last transaction Price of pair")
async def price(ctx: commands.Context, pair: str):
    if ctx.channel.name != CHANNEL_WORK:
        return
    kraken = krakenex.API()
    response = kraken.query_public('Ticker?pair=' + pair)
    print(response['result'])
    price = response['result'][pair]['c'][0]
    print(price)
    await ctx.send(price)


@bot.command(help="add cash to virtual wallet")
async def addCash(ctx: commands.Context, quantity: int):
    if ctx.channel.name != CHANNEL_WORK:
        return
    await ctx.send("Done")


@bot.command(help="get cash to virtual wallet")
async def getCash(ctx: commands.Context):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        sql = "SELECT \"Quantity\" FROM \"Wallets\" WHERE \"UserName\" = '" + ctx.author.name + \
            "' and \"Currency\" = 'eur'"
        cur = conn.cursor()
        cur.execute(sql)
        records = cur.fetchone()
        cur.close()
        print(records)
        await ctx.send(records)
    except ValueError:
        print("error : " + ValueError)


@bot.listen()
async def on_ready():
    print(bot.user.name)
    print("[ON]")
    print('- - - - - - - -')

bot.run(TOKEN)
