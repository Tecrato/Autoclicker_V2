import pygame as pag, sqlite3
from tkinter.simpledialog import askstring

from Utilidades import GUI


class Other_funcs:
    def reload_list(self):
        self.lista_perfiles.clear()
        self.DB_cursor.execute('SELECT * FROM perfiles')
        lista = self.DB_cursor.fetchall()
        self.cached_db_list = lista
        for x in lista:
            self.lista_perfiles.append(x[1])
            
    def guardar_perfil(self):
        if len(self.lista_toques) < 1:
            self.GUI_manager.add(
                GUI.Info(self.display_rect.center, 'Error', 'Debe agregar clicks \n\npara guardar el perfil.',(300,200))
            )
            return
        nombre = askstring('Nombre del perfil', 'Ingrese el nombre para el perfil.')
        if not nombre:
            return
        elif not nombre or len(nombre) < 2:
            self.GUI_manager.add(
                GUI.Info(self.display_rect.center, 'Error', 'Nombre del perfil\n\n demasiado corto.',(300,200))
            )
            return
        try:
            self.DB_cursor.execute("INSERT INTO perfiles VALUES(NULL,?)",[nombre])
            self.DB_cursor.execute('SELECT * FROM perfiles WHERE nombre=?',[nombre])
            lvl_id = self.DB_cursor.fetchone()[0]
            for x,y,t,boton in self.lista_toques:
                datos = [lvl_id,x,y,t,boton]
                self.DB_cursor.execute(f"INSERT INTO clicks VALUES(NULL,?,?,?,?,?)",datos)
            
            self.DB.commit()
            self.reload_list()
        except sqlite3.IntegrityError as err:
            self.GUI_manager.add(
                GUI.Info(self.display_rect.center, 'Error', 'Nombre del perfil ya existente en la base de datos')
            )
        except Exception as err:
            print(err)
            print(type(err))
            self.GUI_manager.add(
                GUI.Info(self.display_rect.center, 'Error', 'Nombre del perfil ya existente en la base de datos')
            )
    def cargar_perfil(self,id):
        self.DB_cursor.execute('SELECT * FROM clicks WHERE id_perfil=?',[id])
        lista = self.DB_cursor.fetchall()
        for id, id_perfil, x, y, tiempo, boton in lista:
            self.lista_toques.append([x,y,tiempo,boton])

    def eliminar_perfil(self,id):
        self.DB_cursor.execute("DELETE FROM perfiles WHERE id=?",[id])
        self.DB_cursor.execute("DELETE FROM clicks WHERE id_perfil=?",[id])
        self.DB.commit()
        self.reload_list()
    def func_extras_to_main(self) -> None:
        self.screen_main_bool = True
        self.screen_extras_bool = False

    def func_main_to_extras(self) -> None:
        self.screen_main_bool = False
        self.screen_extras_bool = True

    def func_main_to_config(self):
        self.screen_main_bool = False
        self.screen_configs_bool = True

    def func_configs_to_main(self) -> None:
        self.screen_main_bool = True
        self.screen_configs_bool = False