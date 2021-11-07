import discord
from discord.ext import commands, tasks
import signal
import locale
from functions import *

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION")
HEROKU_RELEASE_CREATED_AT = os.getenv("HEROKU_RELEASE_CREATED_AT")
HEROKU_SLUG_DESCRIPTION = os.getenv("HEROKU_SLUG_DESCRIPTION")
CONST_BUY = "Buy"
CONST_SELL = "Sell"
NOTIFICATION_VIRTUAL = "notification-virtual"

locale.setlocale(locale.LC_ALL, 'fr_FR')


bot = commands.Bot(command_prefix='#', description="This is a test Bot")


@bot.command(help="ping pong")
async def ping(ctx: commands.Context):
    print("ping")
    if not isChannelIsAuthorised(ctx.channel.name, ALL):
        return
    await ctx.send('pong')


@bot.command(help="where I should request this bot")
async def where(ctx: commands.Context):
    print("where")
    await ctx.send("The command will work at " + CHANNEL_WORK + " or at " + CHANNEL_SIMULATION + " and you are at " + ctx.channel.name + ". you are not at the good place ? " +
                   isChannelIsAuthorised(ctx.channel.name, ALL))


@bot.command(help="get info")
async def info(ctx: commands.Context):
    print("info")
    if not isChannelIsAuthorised(ctx.channel.name, ALL):
        return
    embed = discord.Embed(title=f"KrakenDiscord", description="Bot pour faire des commandes sur Kraken",
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
    if not isChannelIsAuthorised(ctx.channel.name, ALL):
        return
    eurAssetPairs = GetPairsName()
    await ctx.send(eurAssetPairs)



@bot.command(help="get last transaction Price of pair")
async def price(ctx: commands.Context, pair: str):
    if not isChannelIsAuthorised(ctx.channel.name, ALL):
        return
    price = GetPriceOfPair(pair)
    await ctx.send(price)



@bot.command(help="add cash to virtual wallet")
async def addCash(ctx: commands.Context, quantity: float):
    if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
        return
    addCurrencyToDataBase(ctx.author.name, quantity, "eur")
    await ctx.send("Done")


@bot.command(help="get cash to virtual wallet")
async def getCash(ctx: commands.Context):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
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
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
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

@bot.command(help="get Closed Orders")
async def GetClosedOrders(ctx: commands.Context):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_WORK):
            return
        orders = GetClosedOrdersFromKraken()
        for order in orders:
            embed = discord.Embed(title=order['id'], color=discord.Color.red())
            embed.add_field(name="pair",
                            value=order['pair'], inline=True)
            embed.add_field(name="quantity",
                            value=order['quantity'], inline=True)
            embed.add_field(name="type",
                            value=order['type'], inline=True)
            embed.add_field(name="price",
                            value=order['price'], inline=True)
            embed.add_field(name="fee",
                            value=order['fee'], inline=True)
            await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)

@bot.command(help="get wallet")
async def getWallet(ctx: commands.Context):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_WORK):
            return
        wallet = GetWalletFromKraken()
        datetime_now = datetime.now()
        total_Price = 0.0
        if len(wallet) == 0:
            await ctx.send("Empty")
        else:
            for code, quantity_string in wallet.items():
                quantity = float(quantity_string)
                current_price = GetPriceOfCurrency(code);
                name = GetNameOfCurrency(code)
                if quantity > 0:
                    embed = discord.Embed(title=name+'('+code+')',
                                          timestamp=datetime_now, color=discord.Color.red())
                    embed.add_field(name="Quantity",
                                    value=quantity, inline=True)
                    embed.add_field(name="CurrentPriceUnitary",
                                    value=locale.currency(current_price, grouping=True), inline=True)
                    embed.add_field(name="CurrentPrice",
                                    value=locale.currency(current_price * quantity, grouping=True), inline=True)
                    await ctx.send(embed=embed)
                    total_Price += current_price * quantity

        embed = discord.Embed(title="Total",
                              timestamp=datetime_now, color=discord.Color.red())
        embed.add_field(name="WalletPrice",
                        value=locale.currency(total_Price, grouping=True), inline=True)
        await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="add a vitual order to buy")
async def buyVirtual(ctx: commands.Context, currency: str, price: float, quantity: float):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
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
                              quantity, price, currency, "Manual")
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="add a vitual rules for bot")
async def addRuleVirtual(ctx: commands.Context, currency: str, allocatedBudget: float, buyPercent: float, sellPercent: float, startPrice: float):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
            return
        InsertVirtualRuleToDataBase(ctx.author.name, currency,
                                    allocatedBudget, buyPercent, sellPercent, startPrice)
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="start a vitual rules for bot")
async def startRuleVirtual(ctx: commands.Context, id: int):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
            return
        ChangeIsActifVirtualRuleToDataBase(id, True)
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="stop a vitual rules for bot")
async def stopRuleVirtual(ctx: commands.Context, id: int):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
            return
        ChangeIsActifVirtualRuleToDataBase(id, False)
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="show a vitual rules for bot")
async def showRuleVirtual(ctx: commands.Context):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
            return
        rules = GetVirtualRuleForUserToDataBase(ctx.author.name)
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
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
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
                              quantity, price, currency, "Manual")
        await ctx.send("Done")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="get all virtual orders In Progress for current user")
async def getInProgressOrdersVirtual(ctx: commands.Context):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
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
            embed.add_field(name="From",
                            value=record[6], inline=True)
            embed.add_field(name="createdAt",
                            value=record[8], inline=True)
            await ctx.send(embed=embed)
        await ctx.send("End")
    except ValueError:
        await ctx.send("Error")
        print("error : " + ValueError)


@bot.command(help="cancel a virtual orders")
async def cancelVirtualOrder(ctx: commands.Context, orderId: int):
    try:
        if not isChannelIsAuthorised(ctx.channel.name, CHANNEL_SIMULATION):
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
        if Channel.name == NOTIFICATION_VIRTUAL:
            ChannelNotif = Channel
    currentOrder = GetOrdersInProgressForUsersFromDataBase()
    if previousOrder != None:
        for order in previousOrder:
            result = any(newOrder[0] == order[0] for newOrder in currentOrder)
            if result != True:
                if ChannelNotif != None:
                    orderToDisplay = GetOrderFromDataBase(order[0])
                    await ChannelNotif.send(str(orderToDisplay[1]) + " your order (way : " + orderToDisplay[2] + ", price : " + str(orderToDisplay[4]) + ", Quantity : " + str(orderToDisplay[3]) + ") From " + orderToDisplay[6] + " is " + orderToDisplay[7])
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


@tasks.loop(seconds=3.0)
async def batch_VirtualRulesExecution():
    rules = GetVirtualRuleActivedToDataBase()
    for rule in rules:
        ruleName = "Rule-"+str(rule[0])
        orders = GetOrdersInProgressForFromFromDataBase(ruleName)
        if orders != None and any(orders):
            # order is in progress so we do nothing
            continue
        orders = GetOrdersForFromOrderedByCreationDateFromDataBase(ruleName)
        if orders == None or any(orders) != True or orders[0][2] == CONST_SELL:
            print("should create an order of buy")
            currentPrice = GetPriceOfPair(rule[2])
            price = currentPrice-currentPrice*(rule[4]/100)
            InsertOrderToDataBase(
                rule[1], CONST_BUY, rule[3]/price, price, rule[2], ruleName)
        elif orders[0][2] == CONST_BUY:
            print("should create an order of sell")
            currentPrice = orders[0][4]
            price = currentPrice+currentPrice*(rule[5]/100)
            InsertOrderToDataBase(
                rule[1], CONST_SELL, orders[0][3], price, rule[2], ruleName)


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
    batch_VirtualRulesExecution.start()


def exit_gracefully(signum, frame):
    print(bot.user.name)
    print("[OFF]")
    print('- - - - - - - -')

    batch_NotificationVirtual.stop()
    batch_VirtualExecution.stop()
    batch_VirtualRulesExecution.stop()


bot.run(TOKEN)
