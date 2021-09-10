from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AobaGuild(Base):
    __tablename__ = "guild"
    guild_id = Column(Integer, primary_key=True)
    command_prefix = Column(String)
    commands = relationship("AobaCommand", back_populates="guild")


class AobaCommand(Base):
    """
    Custom commands added by server admins
    """

    __tablename__ = "command"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String)
    guild_id = Column(Integer, ForeignKey("guild.guild_id"))
    guild = relationship("AobaGuild", back_populates="commands")
