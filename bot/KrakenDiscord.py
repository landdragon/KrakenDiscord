import discord
from discord.ext import commands, tasks
import os
import krakenex
import psycopg2
from datetime import datetime
import signal

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
    await ctx.send("The commande will work at " + CHANNEL_WORK + "and you are at " + ctx.channel.name + ". you are not at the good place ? " +
                   ctx.channel.name != CHANNEL_WORK)


@bot.command(help="get info")
async def info(ctx: commands.Context):
    print("info")
    if ctx.channel.name != CHANNEL_WORK:
        return
    embed = discord.Embed(title=f"KrakenDiscord", description="Bot pour faire des commande sur Kraken",
                          timestamp=datetime.utcnow(), color=discord.Color.blue())
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
    shouldContain = 'eur'
    eurAssetPairs = [
        s for s in assetPairs if shouldContain.lower() in s.lower()]
    await ctx.send(eurAssetPairs)


@bot.command(help="get last transaction Price of pair")
async def price(ctx: commands.Context, pair: str):
    if ctx.channel.name != CHANNEL_WORK:
        return
    kraken = krakenex.API()
    response = kraken.query_public('Ticker?pair=' + pair)
    price = response['result'][pair]['c'][0]
    await ctx.send(price)


@bot.command(help="add cash to virtual wallet")
async def addCash(ctx: commands.Context, quantity: int):
    if ctx.channel.name != CHANNEL_WORK:
        return
    previousQuantity = GetCashFromDataBase(ctx.author.name, "eur")
    if previousQuantity == None:
        InsertCurrencyToDataBase(ctx.author.name, quantity, "eur")
    else:
        UpdateCurrencyToDataBase(
            ctx.author.name, previousQuantity[0] + quantity, "eur")
    await ctx.send("Done")


def InsertCurrencyToDataBase(authorName: str, quantity: int, currency: str):
    sql = """
                INSERT INTO \"Wallets\"
                (\"UserName\", \"Currency\", \"Quantity\", \"createdAt\", \"updatedAt\")
                VALUES (%(UserName)s, %(Currency)s, %(Quantity)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency,
                      'Quantity': quantity, 'createdAt': datetime.now(), 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def InsertOrderToDataBase(authorName: str, way: str,  quantity: int, price: float, currency: str):
    sql = """
                INSERT INTO "Orders"
                (\"UserName\", \"Way\", \"Quantity\", \"Price\", \"Currency\", \"State\", \"createdAt\", \"updatedAt\")
	            VALUES ( %(UserName)s, %(Way)s, %(Quantity)s, %(Price)s, %(Currency)s, %(State)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Way': way, 'Quantity': quantity, 'Price': price,
                      'Currency': currency, 'State': "In Progress", 'createdAt': datetime.now(), 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def UpdateOrderToDataBase(id: str, state: str):
    sql = """
                Update "Orders"
                set \"State\" = %(State)s,
                    \"updatedAt\" = %(updatedAt)s
                where id = %(id)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'id': id, 'State': state, 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def UpdateCurrencyToDataBase(authorName: str, quantity: int, currency: str):
    sql = """
                Update \"Wallets\"
                Set \"Quantity\" = %(Quantity)s,
                    \"updatedAt\" = %(updatedAt)s
                WHERE \"UserName\" = %(UserName)s 
                    And \"Currency\" = %(Currency)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency,
                      'Quantity': quantity, 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


@bot.command(help="get cash to virtual wallet")
async def getCash(ctx: commands.Context):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        records = GetCashFromDataBase(ctx.author.name, "eur")
        if records == None:
            await ctx.send(0)
        else:
            await ctx.send(records[0])
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


def GetCashFromDataBase(authorName: str, currency: str):
    sql = "SELECT \"Quantity\" FROM \"Wallets\" WHERE \"UserName\" = '" + authorName + \
        "' and \"Currency\" = '"+currency+"'"
    cur = conn.cursor()
    cur.execute(sql)
    records = cur.fetchone()
    cur.close()
    return records


def GetOrdersInProgressFromDataBase(currency: str):
    sql = """
                Select id, \"UserName\", \"Way\", \"Quantity\", \"Price\", \"Currency\", \"State\", \"createdAt\", \"updatedAt\"
                From  \"Orders\"
                WHERE \"Currency\" = %(Currency)s
                    And \"State\" = %(State)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'Currency': currency, 'State': "In Progress"})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersInProgressForUserFromDataBase(userName: str):
    sql = """
                Select id, \"UserName\", \"Way\", \"Quantity\", \"Price\", \"Currency\", \"State\", \"createdAt\", \"updatedAt\"
                From  \"Orders\"
                WHERE \"UserName\" = %(UserName)s
                    And \"State\" = %(State)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': userName, 'State': "In Progress"})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersInProgressForUsersFromDataBase():
    sql = """
                Select id, \"UserName\", \"Way\", \"Quantity\", \"Price\", \"Currency\", \"State\", \"createdAt\", \"updatedAt\"
                From  \"Orders\"
                WHERE \"State\" = %(State)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'State': "In Progress"})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrderFromDataBase(id: int):
    sql = """
                Select id, \"UserName\", \"Way\", \"Quantity\", \"Price\", \"Currency\", \"State\", \"createdAt\", \"updatedAt\"
                From  \"Orders\"
                WHERE \"id\" = %(id)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'id': id})
    record = cur.fetchone()
    cur.close()
    return record


@bot.command(help="add a vitual order to buy")
async def buyVirtual(ctx: commands.Context, currency: str, price: float, quantity: int):
    # todo : a faire
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        InsertOrderToDataBase(ctx.author.name, "Buy",
                              quantity, price, currency)
        records = GetCashFromDataBase(ctx.author.name, "eur")
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="get all virtual orders In Progress for current user")
async def getInProgressOrdersVirtual(ctx: commands.Context):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        records = GetOrdersInProgressForUserFromDataBase(ctx.author.name)
        for record in records:
            embed = discord.Embed(title=f"Orders",
                                  timestamp=datetime.utcnow(), color=discord.Color.red())

            embed.add_field(name="id",
                            value=record[0], inline=True)
            embed.add_field(name="Way",
                            value=record[2], inline=True)
            embed.add_field(name="Quantity",
                            value=record[3], inline=True)
            embed.add_field(name="Price",
                            value=record[4], inline=True)
            embed.add_field(name="Currency",
                            value=record[5], inline=True)
            embed.add_field(name="createdAt",
                            value=record[7], inline=True)
            await ctx.send(embed=embed)
        await ctx.send("End")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="cancel a virtual orders")
async def cancelVirtualOrder(ctx: commands.Context, orderId: int):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        UpdateOrderToDataBase(orderId, "Cancel")
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@tasks.loop(seconds=5.0)
async def batch_Notification():
    global previousOrder
    currentOrder = GetOrdersInProgressForUsersFromDataBase()
    if previousOrder != None:
        for order in previousOrder:
            result = any(newOrder[0] == order[0] for newOrder in currentOrder)
            if result != True:
                print(GetOrderFromDataBase(order[0]))
    previousOrder = currentOrder
    print("loop")


@bot.listen()
async def on_ready():
    print(bot.user.name)
    print("[ON]")
    print('- - - - - - - -')

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    global previousOrder
    previousOrder = None
    batch_Notification.start()


def exit_gracefully(signum, frame):
    print(bot.user.name)
    print("[OFF]")
    print('- - - - - - - -')
    batch_Notification.stop()


bot.run(TOKEN)
