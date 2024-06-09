from sqlalchemy import Column, String, Integer


class CardIdentifier(Base):
    __tablename__ = "cardIdentifiers"

    id = Column(Integer, primary_key=True)
    cardKingdomEtchedId = Column(String)
    cardKingdomFoilId = Column(String)
    cardKingdomId = Column(String)
    cardsphereFoilId = Column(String)
    cardsphereId = Column(String)
    mcmId = Column(String)
    mcmMetaId = Column(String)
    mtgArenaId = Column(String)
    mtgjsonFoilVersionId = Column(String)
    mtgjsonNonFoilVersionId = Column(String)
    mtgjsonV4Id = Column(String)
    mtgoFoilId = Column(String)
    mtgoId = Column(String)
    multiverseId = Column(String)
    scryfallCardBackId = Column(String)
    scryfallId = Column(String)
    scryfallIllustrationId = Column(String)
    scryfallOracleId = Column(String)
    tcgplayerEtchedProductId = Column(String)
    tcgplayerProductId = Column(String)
    uuid = Column(String)
