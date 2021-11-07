import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

def addCurrencyToDataBase(userName, quantity, currency):
    previousQuantity = GetQuantityForCurrencyFromDataBase(userName, currency)
    if previousQuantity == None:
        InsertCurrencyToDataBase(userName, quantity, currency)
    else:
        UpdateCurrencyToDataBase(
            userName, previousQuantity[0] + quantity, currency)


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


def InsertOrderToDataBase(authorName: str, way: str,  quantity: float, price: float, currency: str, From: str):
    sql = """
                INSERT INTO "Orders"
                ("UserName", "Way", "Quantity", "Price", "Currency", "From", "State", "createdAt", "updatedAt")
	            VALUES ( %(UserName)s, %(Way)s, %(Quantity)s, %(Price)s, %(Currency)s, %(From)s, %(State)s, %(createdAt)s, %(updatedAt)s);
        """
    cur = conn.cursor()
    cur.execute(sql, {'UserName': authorName, 'Way': way, 'Quantity': quantity, 'Price': price,
                      'Currency': currency, 'From': From, 'State': "In Progress", 'createdAt': datetime.now(), 'updatedAt': datetime.now()})
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

