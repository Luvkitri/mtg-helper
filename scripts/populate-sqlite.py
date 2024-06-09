import sqlite3
from pprint import pprint

connection = sqlite3.connect("data/AllPrintings.sqlite")
cursor = connection.cursor()

sql_query = """SELECT cards.name, identifier.scryfallId FROM cardIdentifiers as identifier INNER JOIN cards ON identifier.uuid = cards.uuid LIMIT 10;"""
query_card_identifiers_info = """PRAGMA table_info(cardIdentifiers);"""
query_cards_info = """PRAGMA table_info(cards);"""

# response = cursor.execute(query_card_identifiers_info)
# pprint(response.fetchall())

# response = cursor.execute(query_cards_info)
# pprint(response.fetchall())

response = cursor.execute(sql_query)
pprint(response.fetchall())

cursor.close()
connection.close()
