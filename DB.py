import Utilidades as uti
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.Perfil import Perfil, Toque, Base

class DB:
    def __init__(self, path):
        self.engine = create_engine('sqlite:///'+path.as_posix())
        Base.metadata.create_all(self.engine)
        uti.debug_print(self.engine.url.database)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def agregar_perfil(self, nombre,commit=True):
        perfil = Perfil(nombre)
        self.session.add(perfil)
        if commit:
            self.session.commit()
        return perfil

    def agregar_click(self, x, y, tiempo, boton, perfil_id,commit=True):
        click = Toque(x, y, tiempo, boton, perfil_id)
        self.session.add(click)
        if commit:
            self.session.commit()
        return click
    
    def nuevo_perfil(self, nombre, clicks):
        perfil = self.agregar_perfil(nombre)
        for x, y, tiempo, boton in clicks:
            click = Toque(x, y, tiempo, boton, perfil.id)
            self.session.add(click)
        self.session.commit()

    def buscar_perfiles(self, **kwargs):
        return self.session.query(Perfil).filter_by(**kwargs).all()

    def cargar_perfil(self, perfil_name):
        perfil = self.session.query(Perfil).filter_by(nombre=perfil_name).first()
        lista_clicks = self.session.query(Toque).filter_by(perfil_id=perfil.id).all()
        return [(x.x, x.y, x.tiempo, x.boton) for x in lista_clicks]

