from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    
    uuid = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    server = relationship("Server", back_populates="users")

    referrals_given = relationship(
        "Referral", 
        foreign_keys="[Referral.referrer_id]", 
        back_populates="referrer"
    )
    referral_received = relationship(
        "Referral", 
        foreign_keys="[Referral.invited_id]", 
        back_populates="invited", 
        uselist=False
    )

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    
    sni = Column(String, nullable=True)
    pbk = Column(String, nullable=True)
    sid = Column(String, nullable=True) 
    
    inbound_id = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    users = relationship("User", back_populates="server")

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, autoincrement=True)

    referrer_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    invited_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_given")
    invited = relationship("User", foreign_keys=[invited_id], back_populates="referral_received")

