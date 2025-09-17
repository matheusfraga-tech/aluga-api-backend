# app/models.py

from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Text, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

# Importa o 'Base' do nosso novo arquivo de conexão
from .database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    # Usamos Uuid como tipo para corresponder ao schema que gera um uuid string
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    userName = Column(String, unique=True, index=True, nullable=False)
    # Adicione os outros campos conforme necessário, por exemplo:
    emailAddress = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relacionamento: Um usuário pode ter várias avaliações
    avaliacoes = relationship("Avaliacao", back_populates="usuario")

class Hotel(Base):
    __tablename__ = "hoteis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    endereco = Column(String)
    
    # Relacionamento: Um hotel pode ter várias avaliações
    avaliacoes = relationship("Avaliacao", back_populates="hotel")


class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    nota = Column(Float, nullable=False)
    comentario = Column(Text, nullable=True)
    dataCriacao = Column(DateTime(timezone=True), server_default=func.now())

    # Chaves Estrangeiras
    hotel_id = Column(Integer, ForeignKey("hoteis.id"), nullable=False)
    usuario_id = Column(Uuid, ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    hotel = relationship("Hotel", back_populates="avaliacoes")
    usuario = relationship("Usuario", back_populates="avaliacoes")