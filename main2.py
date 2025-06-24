import pygame as pag
import Utilidades as uti
import Utilidades_pygame as uti_pag
import time
import pynput
import os


from tkinter.simpledialog import askstring
from threading import Thread
from typing import override

from DB import DB
from Utilidades_pygame.base_app_class import Base_class

class AutoClicker(Base_class):
    @override
    def otras_variables(self):
        self.tiempo = 0

        self.capturando = False
        self.capturando_teclado = True
        self.imitando = False
        self.solo_moviendo = False
        self.limite = 1
        self.coldown = 0

        self.mouse_controller = pynput.mouse.Controller()
        self.listener_raton = pynput.mouse.Listener(on_click=self.mouse_handler)
        self.thread_listener_raton = Thread(target=self.listener_raton.start,daemon=True)
        self.listener_teclado = pynput.keyboard.Listener(on_press=self.keyboard_handler)
        self.thread_listener_teclado = Thread(target=self.listener_teclado.start,daemon=True)
        self.thread_imitacion = Thread(target=self.imitar,daemon=True)

        self.thread_listener_teclado.start()

        self.lista_clicks = []
        self.atajos = {
            'agregar pos': {'key': 'f4', 'funcion': lambda: self.agregar_click(teclado=True)},
            'reset': {'key': 'f11', 'funcion': self.reset},
            'imitar': {'key': pynput.keyboard.Key.f8.name, 'funcion': self.func_imitar},
            'solo mover': {'key': 'f7', 'funcion': self.func_solo_mover},
            'capturar': {'key': 'f6', 'funcion': self.func_capturar_mouse},
            'cancelar': {'key': pynput.keyboard.Key.shift_r.name, 'funcion': self.detener},
            'agregar perfil': {'key': pynput.keyboard.Key.f2.name, 'funcion': self.func_agregar_perfil}
        }
    
    def post_init(self):
        self.actualizar_lista_perfiles()
    
    def on_exit(self):
        self.detener()
        self.imitando = False
        self.solo_moviendo = False
        try:
            self.listener_raton.stop()
        except:
            pass
        try:
            self.listener_teclado.stop()
        except:
            pass
        if self.thread_imitacion.is_alive():
            self.thread_imitacion.join(.1)
    
    @override
    def load_resources(self):
        self.DB = DB(self.config.save_dir.joinpath('./perfiles.sqlite3'))


    @override
    def generate_objs(self):
        self.text_main_title = uti_pag.Text('Autoclicker', 26, self.config.fonts['mononoki'], (self.ventana_rect.centerx, 40))

        self.lista_main_perfiles = uti_pag.List(
            size=(self.ventana_rect.w*.85,self.ventana_rect.h/2 +20),
            pos = (self.ventana_rect.centerx - (self.ventana_rect.w*.85)/2, self.text_main_title.rect.bottom + 10),
            font=self.config.fonts['mononoki'],
            text_size=12,
            separation=5,
            header=True,
            text_header='Perfiles',
            # dire='topleft'
        )
        self.btn_main_agregar_perfil = uti_pag.Button(
            text='Agregar perfil',
            size=14,
            font=self.config.fonts['mononoki'],
            pos=(self.lista_main_perfiles.centerx+40,self.lista_main_perfiles.top),
            dire='bottom',
            border_radius=0,
            border_width=1,
            border_color=(0,0,0),
            min_height=35,
            func=self.func_agregar_perfil
        )

        self.input_main_repeticiones = uti_pag.Input(
            pos=self.lista_main_perfiles.bottomleft+(0,5),
            text_size=12,
            font=self.config.fonts['mononoki'],
            text_value='Repeticiones',
            border_radius=2,
            width=self.lista_main_perfiles.width/2 -5,
        )
        self.input_main_coldown = uti_pag.Input(
            pos=self.lista_main_perfiles.bottomright+(1,5),
            text_size=12,
            font=self.config.fonts['mononoki'],
            text_value='Coldown entre clicks',
            border_radius=2,
            dire='topright',
            width=self.lista_main_perfiles.width/2 -5,
        )

        self.btn_main_agregar_posicion = uti_pag.Button(
            text=f'Agregar pos({self.atajos["agregar pos"]["key"]})',
            size=12,
            font=self.config.fonts['mononoki'],
            pos=(self.input_main_repeticiones.centerx, self.input_main_repeticiones.bottom+5),
            dire='top',
            border_radius=10,
            border_width=2,
            border_color=(0,0,0),
            min_height=25,
            min_width=self.lista_main_perfiles.width/2 -5,
        )       
        self.btn_main_capturar_mouse = uti_pag.Button(
            text=f'Capturar Mouse({self.atajos["capturar"]["key"]})',
            size=12,
            font=self.config.fonts['mononoki'],
            pos=(self.input_main_coldown.centerx, self.input_main_coldown.bottom+5),
            dire='top',
            border_radius=10,
            border_width=2,
            border_color=(0,0,0),
            min_height=25,
            min_width=self.lista_main_perfiles.width/2 -5,
            func=self.func_capturar_mouse
        )

        self.btn_main_imitar_sin_click = uti_pag.Button(
            text=f'Solo Mover({self.atajos["solo mover"]["key"]})',
            size=12,
            font=self.config.fonts['mononoki'],
            pos=(self.btn_main_agregar_posicion.centerx, self.btn_main_agregar_posicion.bottom+5),
            dire='top',
            border_radius=10,
            border_width=2,
            border_color=(0,0,0),
            min_height=25,
            min_width=self.lista_main_perfiles.width/2 -5,
            func=self.func_solo_mover
        )
        self.btn_main_imitar = uti_pag.Button(
            text=f'Imitar({self.atajos["imitar"]["key"]})',
            size=12,
            font=self.config.fonts['mononoki'],
            pos=(self.btn_main_capturar_mouse.centerx, self.btn_main_capturar_mouse.bottom+5),
            dire='top',
            border_radius=10,
            border_width=2,
            border_color=(0,0,0),
            min_height=25,
            min_width=self.lista_main_perfiles.width/2 -5,
            func=self.func_imitar
        )

        self.btn_main_reset = uti_pag.Button(
            text=f'Reset({self.atajos["reset"]["key"]})',
            size=12,
            font=self.config.fonts['mononoki'],
            pos=(self.lista_main_perfiles.centerx, self.btn_main_imitar_sin_click.bottom+5),
            dire='top',
            border_radius=10,
            border_width=2,
            border_color=(0,0,0),
            min_height=25,
            min_width=self.lista_main_perfiles.width/2 -5,
            func=self.reset
        )
        
        self.btn_main_detener = uti_pag.Button(
            text=f'Detener({self.atajos["cancelar"]["key"]})',
            size=16,
            font=self.config.fonts['mononoki'],
            pos=(self.ventana_rect.centerx, self.ventana_rect.height+100),
            dire='center',
            border_radius=10,
            border_width=2,
            border_color=(0,0,0),
            padding=20,
            func=lambda: (self.lista_clicks.pop() if (len(self.lista_clicks) > 0 and self.capturando) else None, self.detener())
        )
        self.btn_main_detener.smothmove(1,.8,.5)

        self.text_main_num_clicks_actuales = uti_pag.Text('0 clicks', 12, self.config.fonts['mononoki'], (self.ventana_rect.centerx, self.btn_main_reset.bottom+5), 'top')

        self.lists_screens['main']['draw'] = [
            self.text_main_title,
            self.lista_main_perfiles,
            self.btn_main_agregar_perfil,
            self.input_main_repeticiones,
            self.input_main_coldown,
            self.btn_main_agregar_posicion,
            self.btn_main_capturar_mouse,
            self.btn_main_imitar_sin_click,
            self.btn_main_imitar,
            self.btn_main_reset,
            self.text_main_num_clicks_actuales,
            self.btn_main_detener
        ]
        self.lists_screens['main']['update'] = self.lists_screens['main']['draw']

        self.lists_screens['main']['click'] = [
            self.lista_main_perfiles,
            self.btn_main_agregar_perfil,
            self.input_main_repeticiones,
            self.input_main_coldown,
            self.btn_main_agregar_posicion,
            self.btn_main_capturar_mouse,
            self.btn_main_imitar_sin_click,
            self.btn_main_imitar,
            self.btn_main_reset,
            self.btn_main_detener
        ]
        self.lists_screens['main']['inputs'] = [
            self.input_main_repeticiones,
            self.input_main_coldown
        ]

    def update(self, actual_screen):
        # self.lista_perfiles.pos = pag.mouse.get_pos()
        ...
    
    def otro_evento(self, actual_screen, evento):
        if actual_screen == 'main':
            if evento.type == pag.MOUSEBUTTONDOWN and evento.button == 3:
                if self.lista_main_perfiles.click(pag.mouse.get_pos(),pag.key.get_pressed()[pag.K_LCTRL],button=3) and (result := self.lista_main_perfiles.get_selects()):
                    self.Mini_GUI_manager.add(
                        uti_pag.mini_GUI.select(
                            pag.Vector2(evento.pos)+(1,1),
                            ['Cargar','Eliminar'], # cambiar nombre, 
                            captured=result,
                        ),
                        func=self.func_select_perfiles
                    )
            if evento.type == pag.KEYDOWN:
                if evento.key == pag.K_ESCAPE:
                    if self.capturando or self.imitando:
                        self.detener()
                    else:
                        self.exit()


    # Funciones del programa
    def actualizar_lista_perfiles(self):
        self.lista_main_perfiles.clear()
        result = self.DB.buscar_perfiles()
        self.lista_main_perfiles.lista_palabras = [f'{x.nombre}' for x in result]
        if len(self.lista_main_perfiles.lista_palabras) == 0:
            self.lista_main_perfiles.append(None)

    def reset(self):
        self.capturando = False
        self.imitando = False
        self.tiempo = 0
        self.lista_clicks.clear()
        self.text_main_num_clicks_actuales.text = '0 clicks'
    
    def detener(self):
        self.capturando = False
        self.imitando = False
        self.solo_moviendo = False
        try:
            self.thread_imitacion.join(.1)
        except:
            pass
        try:
            self.listener_raton.stop()
        except:
            pass
        self.text_main_title.color = 'white'

        self.btn_main_imitar.change_color_rect_ad('lightgrey', 'grey')
        self.btn_main_imitar_sin_click.change_color_rect_ad('lightgrey', 'grey')
        self.btn_main_capturar_mouse.change_color_rect_ad('lightgrey', 'grey')

        self.btn_main_detener.pos = (self.ventana_rect.centerx, self.ventana_rect.height+100)

        self.redraw = True

    
    def keyboard_handler(self,key: pynput.keyboard.KeyCode|pynput.keyboard.Key):
        if isinstance(key, pynput.keyboard.KeyCode):
            tecla = key.char
        elif isinstance(key, pynput.keyboard.Key):
            tecla = key.name
        if not self.capturando_teclado:
            return
        for k,v in self.atajos.items():
            if v['key'] == tecla:
                tecla = k
                break
        if tecla not in self.atajos:
            return
        self.atajos[tecla]['funcion']()

    def mouse_handler(self,x:int ,y:int ,boton: pynput.mouse.Button ,is_pressed: bool):
        if not self.capturando:
            return
        if not is_pressed:
            return
        if boton == pynput.mouse.Button.left:
            btn = 1
        elif boton == pynput.mouse.Button.right:
            btn = 2
        self.agregar_click((x,y),btn,1)

    def agregar_click(self,pos=None,btn=1,teclado=False):
        # uti.debug_print(pos,btn,teclado)
        if not self.capturando_teclado and not teclado:
            return
        if pos is None:
            pos = self.mouse_controller.position
        self.lista_clicks.append((*pos,((time.time()-self.tiempo) if self.tiempo > 0 else 0),btn))
        self.tiempo = time.time()
        # uti.debug_print(self.lista_clicks)
        self.text_main_num_clicks_actuales.text = str(len(self.lista_clicks)) + ' clicks'

    def set_vars(self):
        try:
            self.limite = int(self.input_main_repeticiones.get_text())
        except:
            self.limite = 1
            self.input_main_repeticiones.set(1)
        try:
            self.coldown = float(self.input_main_coldown.get_text())
        except:
            self.coldown = 0
            self.input_main_coldown.set(0)

    def func_solo_mover(self):
        if self.imitando or self.capturando:
            return
        self.imitando = True
        self.solo_moviendo = True
        self.text_main_title.color = 'yellow'
        self.btn_main_imitar_sin_click.change_color_rect_ad('yellow', 'lightgrey')
        self.set_vars()
        if self.thread_imitacion.is_alive():
            self.thread_imitacion.join(.1)
        self.thread_imitacion = Thread(target=self.imitar,daemon=True)
        self.thread_imitacion.start()
        self.redraw = True
    
    def func_imitar(self):
        if self.imitando or self.capturando:
            return
        self.imitando = True
        self.solo_moviendo = False
        self.text_main_title.color = 'green'
        self.btn_main_imitar.change_color_rect_ad('green', 'lightgrey')
    
        self.set_vars()

        if self.thread_imitacion.is_alive():
            self.thread_imitacion.join(.1)
        self.thread_imitacion = Thread(target=self.imitar,daemon=True)
        self.thread_imitacion.start()
        self.redraw = True
    
    def imitar(self):
        for _ in range(self.limite):
            if not self.imitando:
                break
            for x,y,tiempo,boton in self.lista_clicks:
                if not self.imitando:
                    break
                time.sleep(tiempo)
                if not self.imitando:
                    break
                self.mouse_controller.position = (x,y)
                if not self.solo_moviendo:
                    self.mouse_controller.click(pynput.mouse.Button.left if boton == 1 else pynput.mouse.Button.right)
            time.sleep(self.coldown)
        self.detener()

    def func_agregar_perfil(self):
        perfil = askstring('Agregar perfil', 'Nombre del perfil')
        if perfil is None:
            return
        self.DB.nuevo_perfil(perfil, self.lista_clicks)
        self.actualizar_lista_perfiles()

    def func_select_perfiles(self, result):
        if result == 'exit' or not isinstance(result, dict):
            return
        uti.debug_print(result)
        if result['index'] == 0: # cargar perfil
            self.lista_clicks.clear()
            self.lista_clicks = self.DB.cargar_perfil(result['obj'][0][1])
            self.text_main_num_clicks_actuales.text = str(len(self.lista_clicks)) + ' clicks'
        # elif result['index'] == 1: # eliminar perfil
        #     self.DB.eliminar_perfil(result['obj'])
        #     self.actualizar_lista_perfiles()

    def func_capturar_mouse(self):
        self.btn_main_detener.pos = (self.ventana_rect.centerx, self.ventana_rect.height-100)
        self.capturando = True
        self.imitando = False
        self.solo_moviendo = False
        self.text_main_title.color = 'purple'
        self.btn_main_capturar_mouse.change_color_rect_ad('purple', 'lightgrey')
        try:
            self.listener_raton.stop()
        except:
            pass
        self.listener_raton = pynput.mouse.Listener(on_click=self.mouse_handler)
        self.listener_raton.start()
    

if __name__ == '__main__':
    # Iniciar el programa
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    config = uti_pag.Config(
        resolution=(360,520),
        window_resize=False,
        title='AutoClicker',
        my_company='Edouard Sandoval',
        author='Edouard Sandoval',
        version='2.1.0',
        fonts={'mononoki': './Data/fonts/mononoki Bold Nerd Font Complete Mono.ttf'}
    )
    AutoClicker(config=config)