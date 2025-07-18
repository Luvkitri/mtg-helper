import time
import random
from typing import List
from app.models.card import CardField


async def get_unique_cards(db):
    query = """
        SELECT uuid, name, text FROM cards 
        WHERE (isFunny = 0 OR isFunny IS NULL) 
        AND (isOversized = 0 OR isOversized IS NULL) 
        AND (isOnlineOnly = 0 OR isOnlineOnly IS NULL) 
        AND (isFullArt = 0 OR isFullArt IS NULL) 
        AND (isAlternative = 0 or isAlternative IS NULL) 
        AND (setCode != "REX" AND setCode != "SLD" AND setCode != "40K") 
        GROUP BY name
    """

    cards_cursor = await db.execute(query)
    return await cards_cursor.fetchall()


async def get_card_by_uuid(db, uuid: str, fields: List[CardField] = [CardField.ALL]):
    fields_str = ", ".join(field.value for field in fields)
    card_by_id_query = f"""SELECT {fields_str} FROM cards WHERE uuid = ?"""
    card_cursor = await db.execute(card_by_id_query, (uuid,))
    card = await card_cursor.fetchone()

    if CardField.ALL in fields:
        return card

    return {field.value: value for field, value in zip(fields, card)}


async def get_similar_cards(
    db,
    filter_color: bool,
    filter_colors: bool,
    filter_type: bool,
    source_card,
    params,
    sim_scores,
):
    temp_table_name = f"temp_{int(time.time() + (random.random() * 100_000))}"

    db_cursor = await db.cursor()
    await db_cursor.execute(
        f"""CREATE TEMPORARY TABLE {temp_table_name} (uuid TEXT, sim_score REAL)""",
    )
    for uuid, sim_score in sim_scores.items():
        await db_cursor.execute(
            f"""INSERT INTO {temp_table_name} (uuid, sim_score) VALUES (?, ?)""",
            (
                uuid,
                sim_score,
            ),
        )

    condition = ""

    if filter_color and filter_type:
        condition = f"WHERE (card.colorIdentity = '{source_card.colorIdentity}' OR card.colors = '{source_card.colors}') AND card.types = '{source_card.types}'"
    elif filter_color:
        condition = f"WHERE card.colorIdentity = '{source_card.colorIdentity}' OR card.colors = '{source_card.colors}'"
    elif filter_colors:
        colors = source_card.colors.split(",")
        conditions = [f"card.colors='{color.strip()}'" for color in colors]
        condition = f"WHERE {" OR ".join(conditions)}"
        print(condition)
    elif filter_type:
        condition = f"WHERE card.types = '{source_card.types}'"

    similar_cards_query = f"""
        SELECT card.uuid, identifier.scryfallId, temp_card.sim_score
        FROM cards AS card
        INNER JOIN {temp_table_name} AS temp_card
        ON card.uuid = temp_card.uuid
        INNER JOIN cardIdentifiers AS identifier
        ON card.uuid = identifier.uuid
        {condition}
        ORDER BY temp_card.sim_score DESC
        LIMIT ?
        OFFSET ?
    """

    similar_cards_cursor = await db.execute(similar_cards_query, params)
    similar_cards = await similar_cards_cursor.fetchall()

    await db_cursor.execute(f"DROP TABLE {temp_table_name}")
    await db.commit()
    return similar_cards
