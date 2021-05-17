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
CONST_BUY = "Buy"
CONST_SELL = "Sell"

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
    eurAssetPairs = GetPairsName()
    await ctx.send(eurAssetPairs)


def GetPairsName():
    kraken = krakenex.API()
    response = kraken.query_public('AssetPairs')
    assetPairs = list(response['result'])
    shouldContain = 'eur'
    eurAssetPairs = [
        s for s in assetPairs if shouldContain.lower() in s.lower()]
    return eurAssetPairs


@bot.command(help="get last transaction Price of pair")
async def price(ctx: commands.Context, pair: str):
    if ctx.channel.name != CHANNEL_WORK:
        return
    price = GetPriceOfPair(pair)
    await ctx.send(price)


def GetPriceOfPair(pair: str) -> float:
    kraken = krakenex.API()
    response = kraken.query_public('Ticker?pair=' + pair)
    price = float(response['result'][pair]['c'][0])
    return price


@bot.command(help="add cash to virtual wallet")
async def addCash(ctx: commands.Context, quantity: float):
    if ctx.channel.name != CHANNEL_WORK:
        return
    addCurrencyToDataBase(ctx.author.name, quantity, "eur")
    await ctx.send("Done")


def addCurrencyToDataBase(userName, quantity, currency):
    previousQuantity = GetQuantityForCurrencyFromDataBase(userName, currency)
    if previousQuantity == None:
        InsertCurrencyToDataBase(userName, quantity, currency)
    else:
        UpdateCurrencyToDataBase(
            userName, previousQuantity[0] + quantity, currency)


def InsertCurrencyToDataBase(authorName: str, quantity: float, currency: str):
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


def InsertOrderToDataBase(authorName: str, way: str,  quantity: float, price: float, currency: str):
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


def InsertVirtualRuleToDataBase(authorName: str, currency: str,  allocatedBudget: float, buyPercent: float, sellPercent: float, startPrice: float):
    sql = """
                INSERT INTO "VirtualRules"
                ("UserName", "Currency", "AllocatedBudget", "BuyPercent", "SellPercent", "StartPrice", "IsActif", "createdAt", "updatedAt")
	            VALUES (    %(UserName)s, %(Currency)s, %(AllocatedBudget)s, %(BuyPercent)s, %(SellPercent)s, %(StartPrice)s,
                            %(IsActif)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency, 'AllocatedBudget': allocatedBudget, 'BuyPercent': buyPercent,
                      'SellPercent': sellPercent, 'StartPrice': startPrice, 'IsActif': False,
                      'createdAt': datetime.now(), 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def GetVirtualRuleToDataBase(authorName: str):
    sql = """
                SELECT id, "UserName", "Currency", "AllocatedBudget", "BuyPercent", "SellPercent", "StartPrice", "IsActif", "createdAt", "updatedAt"
	            FROM "VirtualRules"
                WHERE "UserName" = %(UserName)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName})
    records = cur.fetchall()
    cur.close()
    return records


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


def UpdateCurrencyToDataBase(authorName: str, quantity: float, currency: str):
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
        walletLine = GetQuantityForCurrencyFromDataBase(ctx.author.name, "eur")

        if walletLine == None:
            await ctx.send(0)
        else:
            await ctx.send(walletLine[0])
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="get wallet to virtual wallet")
async def getWalletVirtual(ctx: commands.Context):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        walletLines = GetWalletFromDataBase(ctx.author.name)
        if any(walletLine[3] > 0 for walletLine in walletLines) == False:
            await ctx.send("Empty")
        else:
            for walletLine in walletLines:
                if walletLine[3] > 0:
                    embed = discord.Embed(title=walletLine[2],
                                          timestamp=walletLine[5], color=discord.Color.red())
                    embed.add_field(name="Quantity",
                                    value=walletLine[3], inline=True)
                    await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


def GetQuantityForCurrencyFromDataBase(authorName: str, currency: str):
    sql = """
                SELECT \"Quantity\"
                FROM \"Wallets\"
                WHERE \"UserName\" = %(UserName)s
                AND \"Currency\" = %(Currency)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'UserName': currency})
    records = cur.fetchone()
    cur.close()
    return records


def GetWalletFromDataBase(authorName: str):
    sql = """
                SELECT id, \"UserName\", \"Currency\", \"Quantity\", \"createdAt\", \"updatedAt\"
                FROM \"Wallets\"
                WHERE \"UserName\" = %(UserName)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName})
    records = cur.fetchall()
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
async def buyVirtual(ctx: commands.Context, currency: str, price: float, quantity: float):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        pairs = GetPairsName()
        result = any(pair == currency for pair in pairs)
        if result != True:
            await ctx.send("Error : Wrong Currency name")
            return
        result = GetQuantityForCurrencyFromDataBase(ctx.author.name, "eur")
        if result == None or result[0] < price*quantity:
            await ctx.send("Error : not enouth Eur")
            return

        InsertOrderToDataBase(ctx.author.name, CONST_BUY,
                              quantity, price, currency)
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="add a vitual rules for bot")
async def addRuleVirtual(ctx: commands.Context, currency: str, allocatedBudget: float, buyPercent: float, sellPercent: float, startPrice: float):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        InsertVirtualRuleToDataBase(ctx.author.name, currency,
                                    allocatedBudget, buyPercent, sellPercent, startPrice)
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="show a vitual rules for bot")
async def showRuleVirtual(ctx: commands.Context):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        rules = GetVirtualRuleToDataBase(ctx.author.name)
        if rules != None:
            for rule in rules:
                embed = discord.Embed(title=f"Rules",
                                      timestamp=rule[9], color=discord.Color.red())
                embed.add_field(name="id",
                                value=rule[0], inline=True)
                embed.add_field(name="AllocatedBudget",
                                value=rule[3], inline=True)
                embed.add_field(name="BuyPercent",
                                value=rule[4], inline=True)
                embed.add_field(name="SellPercent",
                                value=rule[5], inline=True)
                embed.add_field(name="StartPrice",
                                value=rule[6], inline=True)
                embed.add_field(name="IsActif",
                                value=rule[7], inline=True)
                await ctx.send(embed=embed)
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="sell a vitual order to buy")
async def sellVirtual(ctx: commands.Context, currency: str, price: float, quantity: float):
    try:
        if ctx.channel.name != CHANNEL_WORK:
            return
        pairs = GetPairsName()
        result = any(pair == currency for pair in pairs)
        if result != True:
            await ctx.send("Error : Wrong Currency name")
            return
        result = GetQuantityForCurrencyFromDataBase(ctx.author.name, currency)
        if result == None or result[0] < quantity:
            await ctx.send("Error : not enouth " + currency)
            return

        InsertOrderToDataBase(ctx.author.name, CONST_SELL,
                              quantity, price, currency)
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


@tasks.loop(seconds=1.0)
async def batch_NotificationVirtual():
    global previousOrder
    ChannelNotif = None
    for Channel in bot.get_all_channels():
        if Channel.name == "notification-virtual":
            ChannelNotif = Channel
    currentOrder = GetOrdersInProgressForUsersFromDataBase()
    if previousOrder != None:
        for order in previousOrder:
            result = any(newOrder[0] == order[0] for newOrder in currentOrder)
            if result != True:
                if ChannelNotif != None:
                    orderToDisplay = GetOrderFromDataBase(order[0])
                    await ChannelNotif.send(str(orderToDisplay[1]) + " your order (way : " + orderToDisplay[2] + ", price : " + str(orderToDisplay[4]) + ", Quantity : " + str(orderToDisplay[3]) + ") is " + orderToDisplay[6])
    previousOrder = currentOrder


@tasks.loop(seconds=5.0)
async def batch_VirtualExecution():
    orders = GetOrdersInProgressForUsersFromDataBase()
    currencies = (o[5] for o in orders)
    currencies = list(dict.fromkeys(currencies))
    dic = {}
    for x in currencies:
        dic[x] = []
    for x in orders:
        dic[x[5]].append(x)
    for pairName in dic:
        currentPrice = GetPriceOfPair(pairName)
        for order in dic[pairName]:
            if order[2] == CONST_BUY and currentPrice < float(order[4]):
                addCurrencyToDataBase(order[1], order[3], order[5])
                addCurrencyToDataBase(order[1], order[3]*order[4]*-1, "eur")
                UpdateOrderToDataBase(order[0], "Executed")
            elif order[2] == CONST_SELL and currentPrice > float(order[4]):
                addCurrencyToDataBase(order[1], order[3]*-1, order[5])
                addCurrencyToDataBase(order[1], order[3]*order[4], "eur")
                UpdateOrderToDataBase(order[0], "Executed")


@bot.listen()
async def on_ready():
    print(bot.user.name)
    print("[ON]")
    print('- - - - - - - -')

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    global previousOrder
    previousOrder = None
    batch_NotificationVirtual.start()
    batch_VirtualExecution.start()


def exit_gracefully(signum, frame):
    print(bot.user.name)
    print("[OFF]")
    print('- - - - - - - -')

    batch_NotificationVirtual.stop()
    batch_VirtualExecution.stop()


bot.run(TOKEN)
