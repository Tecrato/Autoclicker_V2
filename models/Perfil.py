from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

import datetime


Base = declarative_base()

class Perfil(Base):
    __tablename__ = 'perfiles'
    id = Column(Integer(), primary_key=True)
    nombre = Column(String(50), unique=True)
    fecha_creacion = Column(DateTime(), default=datetime.datetime.now())

    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f'Perfil: {self.nombre}'
    

class Toque(Base):
    __tablename__ = 'click'
    id = Column(Integer(), primary_key=True)
    perfil_id = Column(Integer(), ForeignKey('perfiles.id'))
    x = Column(Integer())
    y = Column(Integer())
    tiempo = Column(Float())
    boton = Column(Integer())

    def __init__(self, x, y, tiempo, boton, perfil_id):
        self.x = x
        self.y = y
        self.tiempo = tiempo
        self.boton = boton
        self.perfil_id = perfil_id