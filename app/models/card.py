from typing import Optional, List

from pydantic import BaseModel, Field


class ForeignData(BaseModel):
    faceName: Optional[str]
    flavorText: Optional[str]
    language: str
    multiverseId: Optional[int] = None
    name: str
    text: Optional[str]
    type: Optional[str]


class Identifiers(BaseModel):
    cardKingdomEtchedId: Optional[str]
    cardKingdomFoilId: Optional[str]
    cardKingdomId: Optional[str]
    cardsphereId: Optional[str]
    cardsphereFoilId: Optional[str]
    mcmId: Optional[str]
    mcmMetaId: Optional[str]
    mtgArenaId: Optional[str]
    mtgjsonFoilVersionId: Optional[str]
    mtgjsonNonFoilVersionId: Optional[str]
    mtgjsonV4Id: Optional[str]
    mtgoFoilId: Optional[str]
    mtgoId: Optional[str]
    multiverseId: Optional[str]
    scryfallId: Optional[str]
    scryfallCardBackId: Optional[str]
    scryfallOracleId: Optional[str]
    scryfallIllustrationId: Optional[str]
    tcgplayerProductId: Optional[str]
    tcgplayerEtchedProductId: Optional[str]


class LeadershipSkills(BaseModel):
    brawl: bool
    commander: bool
    oathbreaker: bool


class Legalities(BaseModel):
    alchemy: Optional[str]
    brawl: Optional[str]
    commander: Optional[str]
    duel: Optional[str]
    explorer: Optional[str]
    future: Optional[str]
    gladiator: Optional[str]
    historic: Optional[str]
    historicbrawl: Optional[str]
    legacy: Optional[str]
    modern: Optional[str]
    oathbreaker: Optional[str]
    oldschool: Optional[str]
    pauper: Optional[str]
    paupercommander: Optional[str]
    penny: Optional[str]
    pioneer: Optional[str]
    predh: Optional[str]
    premodern: Optional[str]
    standard: Optional[str]
    standardbrawl: Optional[str]
    timeless: Optional[str]
    vintage: Optional[str]


class PurchaseUrls(BaseModel):
    cardKingdom: Optional[str]
    cardKingdomEtched: Optional[str]
    cardKingdomFoil: Optional[str]
    cardmarket: Optional[str]
    tcgplayer: Optional[str]
    tcgplayerEtched: Optional[str]


class RelatedCards(BaseModel):
    reverseRelated: Optional[List[str]] = None
    spellbook: Optional[List[str]] = None


class Rulings(BaseModel):
    date: str
    text: str


class CardAtomic(BaseModel):
    asciiName: Optional[str]
    attractionLights: List[int] = Field(default_factory=list)
    colorIdentity: List[str] = Field(default_factory=list)
    colorIndicator: Optional[List[str]] = None
    colors: List[str] = Field(default_factory=list)
    convertedManaCost: int
    defense: Optional[str]
    edhrecRank: Optional[int]
    edhrecSaltiness: Optional[int]
    faceConvertedManaCost: Optional[int]
    faceManaValue: Optional[int]
    faceName: Optional[str]
    firstPrinting: str
    foreignData: Optional[List[ForeignData]] = None
    hand: Optional[str]
    hasAlternativeDeckLimit: bool
    identifiers: Identifiers
    isFunny: bool
    isReserved: bool
    keywords: Optional[List[str]] = None
    layout: str
    leadershipSkills: Optional[LeadershipSkills] = None
    legalities: Legalities
    life: Optional[str]
    loyalty: Optional[str]
    manaCost: Optional[str]
    manaValue: int
    name: str
    power: Optional[str]
    printings: Optional[List[str]] = None
    purchaseUrls: PurchaseUrls
    relatedCards: RelatedCards
    rulings: Optional[List[Rulings]] = None
    side: Optional[str]
    subsets: List[str] = Field(default_factory=list)
    supertypes: List[str] = Field(default_factory=list)
    text: Optional[str]
    toughness: Optional[str]
    type: str
    types: List[str] = Field(default_factory=list)
