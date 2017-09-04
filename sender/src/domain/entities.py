from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, BigInteger

Base = declarative_base()


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=True, unique=True)
    hash = Column(BigInteger, nullable=True)
    url = Column(String, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False)
    last_post_id = Column(Integer, nullable=True)
    last_sent_id = Column(Integer, nullable=True)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    redirect_url = Column(String, nullable=True)


class Subscription(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = (PrimaryKeyConstraint('channel_id', 'user_id'),)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    last_sent_id = Column(Integer, nullable=True)
    user = relationship(User)
    channel = relationship(Channel)


