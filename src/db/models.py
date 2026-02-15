from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

timestamp = lambda: datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    server_id = Column(ForeignKey("servers.id"), nullable=True)
    uuid = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=timestamp)
    updated_at = Column(DateTime(timezone=True), default=timestamp, onupdate=timestamp)

    server = relationship("Server", back_populates="users")

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
    
    created_at = Column(DateTime(timezone=True), default=timestamp)
    updated_at = Column(DateTime(timezone=True), default=timestamp, onupdate=timestamp)

    users = relationship("User", back_populates="server")