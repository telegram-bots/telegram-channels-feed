from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, BigInteger

Base = declarative_base()


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    url = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    last_message_id = Column(BigInteger, nullable=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)


class Subscription(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = (PrimaryKeyConstraint('channel_id', 'user_id'), )

    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    last_message_id = Column(BigInteger, nullable=True)
    channel = relationship(Channel)
    user = relationship(User)


