from sqlalchemy import create_engine, Column,Integer,String,ForeignKey,\
    select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
engine = create_engine('sqlite:////tmp/tdlog.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class GameEntity(Base):

    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    players = relationship("PlayerEntity", back_populates="game",cascade="all, delete-orphan")


class PlayerEntity(Base):
 __tablename__ = 'player'
 id = Column(Integer, primary_key=True)
 name = Column(String, nullable=False)
 game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
 game = relationship("GameEntity", back_populates="players")
 battle_field = relationship("BattlefieldEntity", back_populates="player", uselist=False, cascade="all, delete-orphan")
 

class BattlefieldEntity(Base):
    __tablename__='battlefield'
    id= Column(Integer, primary_key=True)
    min_x=Column(Integer)
    min_y=Column(Integer)
    min_z=Column(Integer)
    max_x=Column(Integer)
    max_y=Column(Integer)
    max_z=Column(Integer)
    max_power=Column(Integer)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    vessel = relationship("VesselEntity", back_populates="Battle")
    player = relationship("PlayerEntity", back_populates="battle_field")



class VesseldEntity(Base):
    __tablename__='vessel'
    id= Column(Integer, primary_key=True)
    coord_x=Column(Integer)
    coord_y=Column(Integer)
    coord_z=Column(Integer)
    hits_to_be_destroyed=Column(Integer)
    type=Column(String)
    battle_field_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    Battle = relationship("BattlefieldEntity", back_populates="vessel")
    weapon = relationship("WeaponEntity", back_populates="vessel")


class WeapondEntity(Base):
    __tablename__='weapon'
    id= Column(Integer, primary_key=True)
    ammunitions=Column(Integer)
    range=Column(Integer)
    type=Column(String)
    battle_field_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    vessel= relationship("VesselEntity", back_populates="weapon")
    


class VesselTypes:

    CRUISER = "Cruiser"
    DESTROYER = "Destroyer"
    FRIGATE = "Frigate"
    SUBMARINE = "Submarine"
            
class  WeaponTypes:
    
    AIRMISSILELAUNCHER = "AirMissileLauncher"
    SURFACEMISSILELAUNCHER = "SurfaceMissileLauncher"
    TORPEDOLAUNCHER = "TorpedoLauncher"



def map_to_game(game_entity: GameEntity) -> GameEntity:
    if game_entity is None:
        return None
    game = GameEntity()
    game.id = game_entity.id
    for player_entity in game_entity.players:
        battle_field = BattlefieldEntity(player_entity.battle_field.min_x,
        player_entity.battle_field.max_x,
        player_entity.battle_field.min_y,
        player_entity.battle_field.max_y,
        player_entity.battle_field.min_z,
        player_entity.battle_field.max_z,
        player_entity.battle_field.max_power)
        battle_field.id = player_entity.battle_field.id
        battle_field.vessels = map_to_vessels(
            player_entity.battle_field.vessels)
        player = PlayerEntity(player_entity.name, battle_field)
        player.id = player_entity.id
        game.add_player(player)
    return game
        


class GameDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()


    def create_game(self, game: GameEntity) -> int:
        game_entity = map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id

    def find_game(self, game_id: int) -> GameEntity:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        return map_to_game(game_entity)

    
    def create_or_update_player(self, game_id: int, player: PlayerEntity) -> bool:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        for player_entity in game_entity.players:
            if player_entity.name == player.name:
                game_entity.players.remove(player_entity)
                break
            game_entity.players.append(map_to_player_entity(player))
        self.db_session.flush()
        select.db_session.commit()
        return True




    def map_to_game_entity(game: GameEntity) -> GameEntity:
        game_entity = GameEntity()
        if game.get_id() is not None:
            game_entity.id = game.get_id()
        for player in game.get_players():
            player_entity = PlayerEntity()
            player_entity.id = player.id
            player_entity.name = player.get_name()
            battlefield_entity = map_to_battlefield_entity(
            player.get_battlefield())
            vessel_entities = \
            map_to_vessel_entities(player.get_battlefield().id,player.get_battlefield().vessels)
            battlefield_entity.vessels = vessel_entities
            player_entity.battle_field = battlefield_entity
            game_entity.players.append(player_entity)
        return game_entity

    
    def map_to_vessel_entities(battlefield_id: int, vessels: list[Vessel]) \ -> list[VesselEntity]:
        vessel_entities: list[VesselEntity] = []
        for vessel in vessels:
            vessel_entity = map_to_vessel_entity(battlefield_id, vessel)
            vessel_entities.append(vessel_entity)

        return vessel_entities


    def map_to_vessel_entity(battlefield_id: int, vessel: Vessel) -> VesselEntity:
        vessel_entity = VesselEntity()
        weapon_entity = WeaponEntity()
        weapon_entity.id = vessel.weapon.id
        weapon_entity.ammunitions = vessel.weapon.ammunitions
        weapon_entity.range = vessel.weapon.range
        weapon_entity.type = type(vessel.weapon).__name__
        vessel_entity.id = vessel.id
        vessel_entity.weapon = weapon_entity
        vessel_entity.type = type(vessel).__name__
        vessel_entity.hits_to_be_destroyed = vessel.hits_to_be_destroyed
        vessel_entity.coord_x = vessel.coordinates[0]
        vessel_entity.coord_y = vessel.coordinates[1]
        vessel_entity.coord_z = vessel.coordinates[2]
        vessel_entity.battle_field_id = battlefield_id
        return vessel_entity


    def map_to_player_entity(player: Player) -> PlayerEntity:
        player_entity = PlayerEntity()
        player_entity.id = player.id
        player_entity.name = player.name
        player_entity.battle_field = map_to_battlefield_entity(player.get_battlefield())
        return player_entity


    def map_to_battlefield_entity(battlefield: Battlefield) -> BattlefieldEntity:
        battlefield_entity = BattlefieldEntity()
        battlefield_entity.id = battlefield.id
        battlefield_entity.max_x = battlefield.max_x
        battlefield_entity.max_y = battlefield.max_y
        battlefield_entity.max_z = battlefield.max_z
        battlefield_entity.min_x = battlefield.min_x
        battlefield_entity.min_y = battlefield.min_y
        battlefield_entity.min_z = battlefield.min_z
        battlefield_entity.max_power = battlefield.max_power
        return battlefield_entity

    
    
    
        
    

    
        
