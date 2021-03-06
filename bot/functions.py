import psycopg2
import os
from datetime import datetime
import time
import krakenex

DATABASE_URL = os.getenv("DATABASE_URL")
ALL = "all"
CHANNEL_WORK = os.getenv("CHANNEL_WORK")
CHANNEL_SIMULATION = os.getenv("CHANNEL_SIMULATION")
KRAKEN_KEY = os.getenv("KRAKEN_KEY")
KRAKEN_SECRET = os.getenv("KRAKEN_SECRET")

conn = psycopg2.connect(DATABASE_URL)


def addCurrencyToDataBase(userName, quantity, currency):
    previous_quantity = GetQuantityForCurrencyFromDataBase(userName, currency)
    if previous_quantity is None:
        InsertCurrencyToDataBase(userName, quantity, currency)
    else:
        UpdateCurrencyToDataBase(
            userName, previous_quantity[0] + quantity, currency)


def InsertCurrencyToDataBase(authorName: str, quantity: float, currency: str):
    sql = """
                INSERT INTO "Wallets"
                ("UserName", "Currency", "Quantity", "createdAt", "updatedAt")
                VALUES (%(UserName)s, %(Currency)s, %(Quantity)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency,
                      'Quantity': quantity, 'createdAt': datetime.now(), 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def InsertOrderToDataBase(authorName: str, way: str, quantity: float, price: float, currency: str, From: str):
    sql = """
                INSERT INTO "Orders"
                ("UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt")
	            VALUES ( %(UserName)s, %(Way)s, %(Quantity)s, %(Price)s, %(Currency)s, %(From)s, %(State)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Way': way, 'Quantity': quantity, 'Price': price,
                      'Currency': currency, 'From': From, 'State': "In Progress", 'createdAt': datetime.now(),
                      'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def InsertVirtualRuleToDataBase(authorName: str, currency: str, allocatedBudget: float, buyPercent: float,
                                sellPercent: float, startPrice: float):
    sql = """
                INSERT INTO "VirtualRules"
                ("UserName", "Currency", "AllocatedBudget", "BuyPercent", "SellPercent", "StartPrice", "IsActif", "createdAt", "updatedAt")
	            VALUES (    %(UserName)s, %(Currency)s, %(AllocatedBudget)s, %(BuyPercent)s, %(SellPercent)s, %(StartPrice)s,
                            %(IsActif)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency, 'AllocatedBudget': allocatedBudget,
                      'BuyPercent': buyPercent,
                      'SellPercent': sellPercent, 'StartPrice': startPrice, 'IsActif': False,
                      'createdAt': datetime.now(), 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def ChangeIsActifVirtualRuleToDataBase(id: int, isActif: bool):
    sql = """
                UPDATE "VirtualRules"
	            SET "IsActif" = %(IsActif)s, "updatedAt" = %(updatedAt)s
	            WHERE id = %(id)s;
        """
    cur = conn.cursor()
    cur.execute(sql, {'IsActif': isActif,
                      'updatedAt': datetime.now(), 'id': id})
    conn.commit()
    cur.close()


def GetVirtualRuleForUserToDataBase(authorName: str):
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


def GetVirtualRuleActivedToDataBase():
    sql = """
                SELECT id, "UserName", "Currency", "AllocatedBudget", "BuyPercent", "SellPercent", "StartPrice", "IsActif", "createdAt", "updatedAt"
	            FROM "VirtualRules"
                WHERE "IsActif" = %(IsActif)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'IsActif': True})
    records = cur.fetchall()
    cur.close()
    return records


def UpdateOrderToDataBase(id: str, state: str):
    sql = """
                Update "Orders"
                set "State" = %(State)s,
                    "updatedAt" = %(updatedAt)s
                where id = %(id)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'id': id, 'State': state, 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def UpdateCurrencyToDataBase(authorName: str, quantity: float, currency: str):
    sql = """
                Update "Wallets"
                Set "Quantity" = %(Quantity)s,
                    "updatedAt" = %(updatedAt)s
                WHERE "UserName" = %(UserName)s 
                    And "Currency" = %(Currency)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency,
                      'Quantity': quantity, 'updatedAt': datetime.now()})
    conn.commit()
    cur.close()


def GetQuantityForCurrencyFromDataBase(authorName: str, currency: str):
    sql = """
                SELECT "Quantity"
                FROM "Wallets"
                WHERE "UserName" = %(UserName)s
                AND "Currency" = %(Currency)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Currency': currency})
    records = cur.fetchone()
    cur.close()
    return records


def GetWalletFromDataBase(authorName: str):
    sql = """
                SELECT id, "UserName", "Currency", "Quantity", "createdAt", "updatedAt"
                FROM "Wallets"
                WHERE "UserName" = %(UserName)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersInProgressFromDataBase(currency: str):
    sql = """
                Select id, "UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt"
                From  "Orders"
                WHERE "Currency" = %(Currency)s
                    And "State" = %(State)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'Currency': currency, 'State': "In Progress"})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersInProgressForUserFromDataBase(userName: str):
    sql = """
                Select id, "UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt"
                From  "Orders"
                WHERE "UserName" = %(UserName)s
                    And "State" = %(State)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': userName, 'State': "In Progress"})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersForFromOrderedByCreationDateFromDataBase(From: str):
    sql = """
                Select id, "UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt"
                From  "Orders"
                WHERE "From" = %(From)s
                order by "createdAt" desc;
            """
    cur = conn.cursor()
    cur.execute(sql, {'From': From})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersInProgressForFromFromDataBase(From: str):
    sql = """
                Select id, "UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt"
                From  "Orders"
                WHERE "State" = %(State)s
                and "From" = %(From)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'State': "In Progress", 'From': From})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrdersInProgressForUsersFromDataBase():
    sql = """
                Select id, "UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt"
                From  "Orders"
                WHERE "State" = %(State)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'State': "In Progress"})
    records = cur.fetchall()
    cur.close()
    return records


def GetOrderFromDataBase(id: int):
    sql = """
                Select id, "UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt"
                From  "Orders"
                WHERE "id" = %(id)s;
            """
    cur = conn.cursor()
    cur.execute(sql, {'id': id})
    record = cur.fetchone()
    cur.close()
    return record


def GetPairsName():
    kraken = krakenex.API()
    response = kraken.query_public('AssetPairs')
    kraken.close()
    assetPairs = list(response['result'])
    shouldContain = 'eur'
    eurAssetPairs = [
        s for s in assetPairs if shouldContain.lower() in s.lower()]
    return eurAssetPairs


def GetPriceOfPair(pair: str) -> float:
    kraken = krakenex.API()
    response = kraken.query_public('Ticker?pair=' + pair)
    kraken.close()
    # print(response)
    price = float(response['result'][pair]['c'][0])
    return price


def isChannelIsAuthorised(currentChannel: str, accessChannel: str):
    if accessChannel == CHANNEL_WORK:
        return currentChannel == CHANNEL_WORK
    if accessChannel == CHANNEL_SIMULATION:
        return currentChannel == CHANNEL_SIMULATION
    if accessChannel == ALL:
        return currentChannel == CHANNEL_WORK or currentChannel == CHANNEL_SIMULATION


def GetWalletFromKraken() -> dict:
    kraken = krakenex.API(KRAKEN_KEY, KRAKEN_SECRET)
    response: dict = kraken.query_private('Balance')
    kraken.close()
    # print(response)
    return response['result']


def GetClosedOrdersFromKraken() -> list:
    kraken = krakenex.API(KRAKEN_KEY, KRAKEN_SECRET)
    response: dict = kraken.query_private('TradesHistory', {
        "nonce": str(int(1000 * time.time())),
    })
    kraken.close()

    # print(response)
    orders = []
    for order_id, order in response['result']['trades'].items():
        orders.append({
            "id": order_id,
            "ordertxid": order['ordertxid'],
            "postxid": order['postxid'],
            "pair": order['pair'],
            "quantity": float(order['vol']),
            "type": order['type'],
            "price": float(order['price']),
            "fee": float(order['fee']),
            "time": datetime.fromtimestamp(order['time'])
        });
    # print(orders)

    return orders


def GetCurrentGainFromKraken() -> list:
    orders = GetClosedOrdersFromKraken()
    orders.reverse()
    wallet_histo = {}
    for order in orders:
        if order['pair'] not in wallet_histo:
            wallet_histo[order['pair']] = {
                "pair": order['pair'],
                "quantity": order['quantity'],
                "price": order['price'],
                "gain": 0.0,
            }
        else:
            if order['type'] == 'buy':
                wallet_histo[order['pair']]['price'] = (order['quantity'] * order['price'] +
                                                        wallet_histo[order['pair']][
                                                            'quantity'] * wallet_histo[order['pair']]['price']) / (
                                                               order['quantity'] + wallet_histo[order['pair']][
                                                           'quantity'])
                wallet_histo[order['pair']]['quantity'] += order['quantity']
            else:
                wallet_histo[order['pair']]['quantity'] -= order['quantity']
                wallet_histo[order['pair']]['gain'] += order['quantity'] * (
                        order['price'] - wallet_histo[order['pair']]['price'])

    # print(wallet_histo)
    for wallet_id, wallet_line in wallet_histo.items():
        current_price = GetPriceOfPair(wallet_id)
        wallet_histo[wallet_id]['CurrentPrice'] = current_price
        wallet_histo[wallet_id]['WaitGain'] = wallet_histo[wallet_id]['quantity'] * (
                    current_price - wallet_histo[wallet_id]['price'])
    list = []
    for value in wallet_histo.values():
        list.append(value)
    list.sort(key=lambda o: o['WaitGain'])
    return list


NameOfCurrencies = \
    {
        "XXDG": "Dogecoin",
        "SOL": "Solana",
        "XETH": "Ethereum",
        "TRX": "TRON",
        "XXLM": "Stellar/Lumen",
        "SOL.S": "Solana Stacked",
        "EWT": "Energy Web Token",
        "ZEUR": "Euro",
        "SC": "Siacoin",
        "XXRP": "Ripple",
        "DAI": "Dai",
        "UNI": "Uniswap",
    }


def GetNameOfCurrency(code: str) -> str:
    if code in NameOfCurrencies:
        return NameOfCurrencies[code]
    return code


NameOfPairs = \
    {
        "XXDG": "XDGEUR",
        "SOL": "SOLEUR",
        "XETH": "XETHZEUR",
        "TRX": "TRXEUR",
        "XXLM": "XXLMZEUR",
        "SOL.S": "SOLEUR",
        "EWT": "EWTEUR",
        "ZEUR": "NotApplicable",
        "SC": "SCEUR",
        "XXRP": "XXRPZEUR",
        "DAI": "DAIEUR",
        "UNI": "UNIEUR",
    }


def GetPriceOfCurrency(code: str) -> float:
    if code == "ZEUR":
        return 1.0
    if code in NameOfPairs:
        pair = NameOfPairs[code]
        return GetPriceOfPair(pair)
    else:
        return 0.0
