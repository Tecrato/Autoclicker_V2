import pygame as pag, sys, Utilidades, os, sqlite3, pyautogui as pg, pynput, json, time
from platformdirs import user_config_path
from pygame import Vector2
from threading import Thread

from Utilidades import Create_text, Create_boton, List_Box, GUI, mini_GUI

from funcs import Other_funcs


class AutoClicker(Other_funcs):
    def __init__(self) -> None:
        self.ventana = pag.display.set_mode((360,520))
        self.ventana_rect = self.ventana.get_rect()
        pag.display.set_caption('AutoClicker')

        self.display = pag.Surface((360,520))
        self.display_rect = self.display.get_rect()

        self.imitando = False
        self.solo_moviendo = False
        self.capturando = False
        self.limite = 1
        self.coldown = 0
        self.drawing = True
        self.framerate = 60
        self.lista_toques = []
        self.cached_db_list = []
        self.tiempo = 0
        self.relog = pag.time.Clock()
        self.version = '1.0.0'
        self.atajos = {}

        self.listener_raton = pynput.mouse.Listener(on_click=self.listener_raton_on_click_func)
        self.listener_teclado = pynput.keyboard.Listener(on_press=self.listener_teclado_func)
        self.listener_teclado.start()
        self.hilo_imitacion = Thread(target=self.hilo_imitacion_func)

        self.font_mononoki: str = 'C:/Users/Edouard/Documents/fuentes/mononoki Bold Nerd Font Complete Mono.ttf'
        self.font_simbolos = 'C:/Users/Edouard/Documents/fuentes/Symbols.ttf'
        # self.font_mononoki = './Assets/fuentes/mononoki Bold Nerd Font Complete Mono.ttf'
        # self.font_simbolos = './Assets/fuentes/Symbols.ttf'
        
        self.load_datas()
        self.generate_objs()
        self.reload_list()

        
        self.screen_main_bool = True
        self.screen_extras_bool = False
        self.screen_configs_bool = False

        self.ciclo_general = [self.main_cycle, self.screen_extras,self.screen_configs]
        self.cicle_try = 0
        
        while self.cicle_try < 5:
            self.cicle_try += 1
            for x in self.ciclo_general:
                x()
        self.DB.close()
        pag.quit()
        sys.exit()

    def load_datas(self):
        self.carpeta_config = user_config_path('AutoClicker', 'Edouard Sandoval')
        self.carpeta_config.mkdir(parents=True, exist_ok=True)

        self.DB = sqlite3.connect(self.carpeta_config.joinpath('./perfiles.sqlite3'))
        self.DB_cursor = self.DB.cursor()

        try:
            self.DB_cursor.execute('SELECT * FROM perfiles')
        except sqlite3.OperationalError:
            self.DB_cursor.executescript(open('./db.sql').read())

        try:
            self.configs: dict = json.load(open(self.carpeta_config.joinpath('./configs.json')))
        except Exception:
            self.configs = {}

        self.atajos_para_guardar = self.configs.get('atajos',{
            'agregar pos': f'{pynput.keyboard.Key.f4}',
            'reset': f'{pynput.keyboard.Key.f10}',
            'imitar': f'{pynput.keyboard.Key.f6}',
            'solo mover': f'{pynput.keyboard.Key.f17}',
            'capturar': f'{pynput.keyboard.Key.f11}'
        })

        self.atajos.clear()
        
        for x,c in zip(self.atajos_para_guardar.values(),self.atajos_para_guardar.keys()):
            self.atajos[x] = c

        self.save_json()

    def save_json(self):
        self.atajos_para_guardar.clear()
        for x,c in zip(self.atajos.values(),self.atajos.keys()):
            self.atajos_para_guardar[x] = c

        self.configs['atajos'] = self.atajos_para_guardar

        json.dump(self.configs, open(self.carpeta_config.joinpath('./configs.json'), 'w'))
                
    def generate_objs(self) -> None:
        # Cosas varias
        Utilidades.GUI.configs['fuente_simbolos'] = self.font_simbolos
        self.GUI_manager = GUI.GUI_admin()
        self.Mini_GUI_manager = mini_GUI.mini_GUI_admin(self.display_rect)
        self.Func_pool = Utilidades.Funcs_pool()

        self.titulo_principal = Create_text('Autoclicker', 26, self.font_mononoki, (self.display_rect.centerx, 40))
        self.btn_extras = Create_boton('', 26, self.font_simbolos, (self.display_rect.w, 0), 20, 'topright', 'white',
                                       (20, 20, 20), (50, 50, 50), 0, -1, border_width=-1,
                                       func=self.func_main_to_extras)
        self.btn_configs = Create_boton('', 26, self.font_simbolos, (0, 0), 20, 'topleft', 'white', (20, 20, 20),
                                        (50, 50, 50), 0, -1, border_width=-1, func=self.func_main_to_config)

        self.lista_perfiles = List_Box((self.display_rect.w*.8,self.display_rect.h/2), (self.display_rect.centerx - (self.display_rect.w*.8)/2, self.titulo_principal.rect.bottom + 10),
                                       None, 14, 3, header=True, text_header='Perfiles', selected_color=(90,90,90),
                                       background_color=(0,0,0), smothscroll=False, font=self.font_mononoki, padding_top=5, padding_left=5)
        self.btn_nuevo_perfil = Create_boton('Agregar Nuevo', 14, self.font_mononoki, 
                                             (self.lista_perfiles.rect.centerx+59,self.lista_perfiles.rect.top),
                                              10,'bottom', 'black', 'darkgrey', 'lightgrey', 0, 0, border_width=-1, height=29,
                                              func=self.guardar_perfil)
        self.btn_reload_list = Create_boton('', 13, self.font_simbolos, (self.ventana_rect.w - 35, 75), 16,
                                            'topright', 'black', 'darkgrey', 'lightgrey', 0, border_width=1,
                                            border_radius=0, border_top_right_radius=20,
                                            func=self.reload_list)
        
        # Inputs
        self.input_repeticiones = Utilidades.Input_text(Vector2(self.lista_perfiles.rect.bottomleft)+(0,20), (12,self.display_rect.w*.4), 
                                                        self.font_mononoki, 'Repeticiones', padding=20,border_radius=2)
        self.input_coldown = Utilidades.Input_text(Vector2(self.lista_perfiles.rect.centerx,self.lista_perfiles.rect.bottom)+(1,20), 
                                                   (12,self.display_rect.w*.4), self.font_mononoki, 'Seg/Repeticiones', padding=20,
                                                   border_radius=2)
        
        # Botones
        self.btn_agregar_posicion = Create_boton('Agregar pos', 14, self.font_mononoki,
                                                 Vector2(self.input_repeticiones.rect2.bottomleft)+(0,5), dire='topleft', 
                                                 width=self.display_rect.w*.4, func=lambda:self.appli_func('agregar pos'))
        self.btn_capturar_mouse = Create_boton('Capturar Mouse', 14, self.font_mononoki,
                                                 Vector2(self.input_coldown.rect2.bottomleft)+(0,5), dire='topleft', 
                                                 width=self.display_rect.w*.4, func=lambda: self.appli_func('capturar',1 if self.capturando else 0))
        self.btn_imitar_sin_click = Create_boton('Solo Mover', 14, self.font_mononoki,
                                                 Vector2(self.btn_agregar_posicion.rect.bottomleft)+(0,5), dire='topleft', 
                                                 width=self.display_rect.w*.4, func=lambda:self.appli_func('solo mover'))
        self.btn_imitar = Create_boton('Imitar', 14, self.font_mononoki,
                                                 Vector2(self.btn_capturar_mouse.rect.bottomleft)+(0,5), dire='topleft', 
                                                 width=self.display_rect.w*.4, func=lambda:self.appli_func('imitar'))
        
        self.btn_reset = Create_boton('Reset', 14, self.font_mononoki,
                                                 Vector2(self.btn_imitar_sin_click.rect.bottomright)+(2,25), dire='center', 
                                                 width=self.display_rect.w*.4, func=lambda:self.appli_func('reset'))
        

        # Pantalla de configuraciones
        self.text_config_title = Create_text('Configuraciones', 24, self.font_mononoki,
                                             (self.display_rect.centerx, 30), with_rect=True, color_rect=(20,20,20))
        self.btn_config_exit = Create_boton('', 26, self.font_simbolos, (self.ventana_rect.w, 0), 20, 'topright',
                                            'white', (20, 20, 20), (50, 50, 50), 0, -1, border_width=-1,
                                            func=self.func_configs_to_main)
        

        # Pantalla de extras
        self.text_extras_title = Create_text('Extras', 26, self.font_mononoki, (self.display_rect.centerx, 30))
        self.btn_extras_exit = Create_boton('', 26, self.font_simbolos, (self.display_rect.w, 0), 20, 'topright',
                                            'white', (20, 20, 20), (50, 50, 50), 0, -1, border_width=-1,
                                            func=self.func_extras_to_main)

        self.text_extras_version = Create_text('Version '+self.version, 26, self.font_mononoki, self.display_rect.bottomright,
                                               'bottomright')

        self.text_extras_mi_nombre = Create_text('Edouard Sandoval', 30, self.font_mononoki, (self.display_rect.centerx, 100),
                                                 'center')
        self.btn_extras_link_github = Create_boton('', 30, self.font_simbolos, (self.display_rect.centerx*.8, 200), 20, 'bottomright',
                                                   func=lambda: os.startfile('http://github.com/Tecrato'))
        self.btn_extras_link_youtube = Create_boton('輸', 30, self.font_simbolos, (self.display_rect.centerx*1.2, 200), 20, 'bottomleft',
                                                    func=lambda: os.startfile(
                                                        'http://youtube.com/channel/UCeMfUcvDXDw2TPh-b7UO1Rw'))


        self.list_to_draw = [self.titulo_principal,self.btn_extras, self.lista_perfiles,self.input_repeticiones,
                             self.input_coldown,self.btn_agregar_posicion,self.btn_reload_list,
                             self.btn_capturar_mouse,self.btn_imitar_sin_click,self.btn_imitar,
                             self.btn_reset,self.btn_nuevo_perfil,self.btn_configs]
        self.list_to_click = [self.btn_extras, self.btn_capturar_mouse,self.btn_agregar_posicion,self.btn_imitar_sin_click,
                              self.btn_imitar,self.btn_reset, self.btn_nuevo_perfil,self.btn_reload_list,self.btn_configs]
        self.list_inputs = [self.input_repeticiones,self.input_coldown]

        # Pantalla de Extras
        self.list_to_draw_extras = [self.text_extras_title, self.btn_extras_exit, self.text_extras_mi_nombre,
                                    self.btn_extras_link_github, self.btn_extras_link_youtube, self.text_extras_version]
        self.list_to_click_extras = [self.btn_extras_exit, self.btn_extras_link_github, self.btn_extras_link_youtube]
        
        # Pantalla de Extras
        self.list_to_draw_configs = [self.text_config_title,self.btn_config_exit]
        self.list_to_click_configs = [self.btn_config_exit]

    def hilo_imitacion_func(self):
        for _ in range(self.limite):
            if not self.imitando:
                break
            for x,y,tiempo,boton in self.lista_toques:
                if not self.imitando:
                    break
                pg.moveTo(x,y,.3)
                if not self.solo_moviendo and boton == 3:
                    pg.doubleClick()
                if not self.solo_moviendo:
                    pg.click(button=("primary" if boton == 1 else "secondary"))
                time.sleep(tiempo)
            time.sleep(self.coldown)
        self.imitando = False
        self.btn_imitar.change_color_rect_ad('darkgrey','lightgrey')
        self.btn_imitar_sin_click.change_color_rect_ad('darkgrey','lightgrey')


    def appli_func(self,function, pop_toque=0):
        try:
            self.limite = int(self.input_repeticiones.get_text())
        except:
            self.input_repeticiones.set(1)
        try:
            self.coldown = float(self.input_coldown.get_text())
        except:
            self.input_coldown.set(0)
        if function == 'capturar':
            if pop_toque:
                self.listener_teclado_func(pynput.keyboard.Key.esc)
                self.lista_toques.pop()
                return
            if self.listener_raton.is_alive():
                self.listener_teclado_func(pynput.keyboard.Key.esc)
                return
            self.capturando = True
            self.btn_capturar_mouse.change_color_rect_ad('green','lightgreen')
            self.tiempo = 0
            self.listener_raton = pynput.mouse.Listener(on_click=self.listener_raton_on_click_func)
            self.listener_raton.start()
        elif function == 'imitar':
            if self.hilo_imitacion.is_alive() or self.capturando:
                return
            self.imitando = True
            self.solo_moviendo = False
            self.hilo_imitacion = Thread(target=self.hilo_imitacion_func)
            self.hilo_imitacion.daemon = True
            self.hilo_imitacion.start()
            self.btn_imitar.change_color_rect_ad('green','lightgreen')
        elif function == 'solo mover':
            if self.hilo_imitacion.is_alive() or self.capturando:
                return
            self.imitando = True
            self.solo_moviendo = True
            self.hilo_imitacion = Thread(target=self.hilo_imitacion_func)
            self.hilo_imitacion.daemon = True
            self.hilo_imitacion.start()
            self.btn_imitar_sin_click.change_color_rect_ad('green','lightgreen')
        elif function == 'agregar pos':
            self.listener_raton_on_click_func(pg.position()[0],pg.position()[1],1,True)
        elif function == 'reset':
            self.lista_toques.clear()
            self.imitando = False
            self.solo_moviendo = False
        elif function == 'guardar':
            self.guardar_perfil()

    def listener_teclado_func(self,tecla: pynput.keyboard.Key|pynput.keyboard.KeyCode):
        if isinstance(tecla, pynput.keyboard.Key):
            if f'{tecla}' in self.atajos:
                self.appli_func(self.atajos[f'{tecla}'])
            elif not f'{tecla}' == 'Key.esc':
                return
            elif self.imitando:
                self.imitando = False
            elif self.capturando:
                self.capturando = False
                self.listener_raton.stop()
                self.btn_capturar_mouse.change_color_rect_ad('darkgrey','lightgrey')
            elif self.screen_main_bool:
                self.screen_main_bool = False
            elif self.screen_extras_bool:
                self.screen_extras_bool = False
                self.screen_main_bool = True
            elif self.screen_configs_bool:
                self.screen_configs_bool = False
                self.screen_main_bool = True
        elif isinstance(tecla, pynput.keyboard.KeyCode):
            if tecla.char in self.atajos:
                self.appli_func(self.atajos[f'{tecla.char}'])
            elif tecla.char == 'k':
                print(self.lista_toques,pag.display.get_active())

    def activate_listener_raton(self,type):
        if type == 'imitar_sc':
            self.imitando = True
            self.btn_imitar_sin_click.change_color_rect_ad('green','lightgreen')
        elif type == 'imitar':
            self.imitando = True
            self.btn_imitar.change_color_rect_ad('green','lightgreen')
        elif type == 'capturar':
            ...

    def listener_raton_on_click_func(self,x,y,boton,direccion):
        if not direccion:
            return
        if boton == pynput.mouse.Button.left:
            boton = 1
        elif boton == pynput.mouse.Button.right:
            boton = 2
        if 0 < (time.time()-self.tiempo) < .220:
            boton = 3
        self.lista_toques.append((x,y,((time.time()-self.tiempo) if self.tiempo > 0 else 0), boton))
        self.tiempo = time.time()

    def func_select(self, result):
        print(self.cached_db_list[result['obj']['index']])
        if result['text'] == 'Cargar':
            self.cargar_perfil(self.cached_db_list[result['obj']['index']][0])
        elif result['text'] == 'Eliminar':
            self.eliminar_perfil(self.cached_db_list[result['obj']['index']][0])

    def eventos_en_comun(self,evento):
        if evento.type == pag.QUIT:
            pag.quit()
            sys.exit()
        elif evento.type == pag.WINDOWRESIZED:
            self.display = pag.Surface((evento.x,evento.y))
            self.display_rect = self.display.get_rect()
            self.move_objs()
            return True
        elif evento.type == pag.WINDOWMINIMIZED:
            self.drawing = False
            return True
        elif evento.type == pag.WINDOWFOCUSLOST:
            self.framerate = 30
            return True
        elif evento.type in [pag.WINDOWTAKEFOCUS, pag.WINDOWFOCUSGAINED, pag.WINDOWMAXIMIZED]:
            self.framerate = 60
            self.drawing = True
            return True

    def draw_screen_main(self,mouse_pos=None):
        if not mouse_pos:
            mouse_pos = (-500,-500)
        self.ventana.fill((20, 20, 20))
        for x in self.list_to_draw:
            if isinstance(x, Create_boton):
                x.draw(self.ventana, mouse_pos)
            else:
                x.draw(self.ventana)
        pag.display.flip()
    def main_cycle(self) -> None:
        if self.screen_main_bool:
            self.cicle_try = 0
            self.draw_screen_main()

        while self.screen_main_bool:
            self.relog.tick(self.framerate)

            mx, my = pag.mouse.get_pos()
            eventos = pag.event.get()
            self.GUI_manager.input_update(eventos)
            for x in self.list_inputs:
                x.eventos_teclado(eventos)

            for evento in eventos:
                if self.eventos_en_comun(evento):
                    break
                elif self.GUI_manager.active >= 0:
                    if evento.type == pag.KEYDOWN and evento.key == pag.K_ESCAPE:
                        self.GUI_manager.pop()
                    elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                        self.GUI_manager.click((mx, my))
                elif evento.type == pag.KEYDOWN:
                    ...
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.Mini_GUI_manager.click(evento.pos):
                        continue
                    elif self.lista_perfiles.rect.collidepoint((mx, my)):
                        self.lista_perfiles.click((mx, my))
                    for x in self.list_to_click:
                        if x.click(evento.pos):
                            break
                elif evento.type == pag.MOUSEBUTTONUP and evento.button == 1:
                    self.lista_perfiles.scroll = False
                elif evento.type == pag.MOUSEWHEEL and self.lista_perfiles.rect.collidepoint((mx, my)):
                    self.lista_perfiles.rodar(evento.y*20)
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 3:
                    for x in self.list_to_click:
                        if x.click((mx, my)):
                            break
                    if self.Mini_GUI_manager.click(evento.pos):
                        continue
                    elif self.lista_perfiles.rect.collidepoint((mx, my)):
                        self.lista_perfiles.click((mx, my))
                    if self.lista_perfiles.rect.collidepoint((mx, my)) and \
                            (result := self.lista_perfiles.click((mx, my))):
                        self.Mini_GUI_manager.add(
                            mini_GUI.select((mx, my),
                                ['Cargar', 'Eliminar'],
                                captured=result), self.func_select
                            )
                elif evento.type == pag.MOUSEMOTION:
                    for x in self.list_to_draw:
                        if isinstance(x, Utilidades.Create_boton):
                            x.draw(self.ventana, (mx,my))

                    self.GUI_manager.draw(self.ventana, (mx, my))
                    self.Mini_GUI_manager.draw(self.ventana, (mx, my))

            for x in self.list_to_draw:
                if isinstance(x, Utilidades.Input_text):
                    x.draw(self.ventana)
            pag.display.flip()
        
    def draw_screen_extras(self,mouse_pos=None):
        if not mouse_pos:
            mouse_pos = (-500,-500)
        self.display.fill((20, 20, 20))
        for x in self.list_to_draw_extras:
            if isinstance(x, Create_boton):
                x.draw(self.display, mouse_pos)
            else:
                x.draw(self.display)
        self.ventana.blit(self.display,(0,0))
        pag.display.flip()

    def screen_extras(self):
        if self.screen_extras_bool:
            self.cicle_try = 0
            self.draw_screen_extras()
        while self.screen_extras_bool:
            self.relog.tick(self.framerate)

            mx, my = pag.mouse.get_pos()
            eventos = pag.event.get()

            for evento in eventos:
                if self.eventos_en_comun(evento):
                    continue
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                    for x in self.list_to_click_extras:
                        if x.click((mx, my)):
                            break
                elif evento.type == pag.MOUSEMOTION:
                    self.draw_screen_extras((mx, my))

                    
    def draw_screen_configs(self,mouse_pos=None):
        if not mouse_pos:
            mouse_pos = (-500,-500)
        self.display.fill((20, 20, 20))
        for x in self.list_to_draw_configs:
            if isinstance(x, Create_boton):
                x.draw(self.display, mouse_pos)
            else:
                x.draw(self.display)
        self.ventana.blit(self.display,(0,0))
        pag.display.flip()
    def screen_configs(self):
        if self.screen_configs_bool:
            self.cicle_try = 0
            self.draw_screen_configs()

        while self.screen_configs_bool:
            self.relog.tick(self.framerate)

            mx, my = pag.mouse.get_pos()
            eventos = pag.event.get()
            
            for evento in eventos:
                if self.eventos_en_comun(evento):
                    continue
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                    for x in self.list_to_click_configs:
                        if x.click((mx, my)):
                            break
                elif evento.type == pag.MOUSEMOTION:
                    self.draw_screen_configs((mx,my))


if __name__ == '__main__':
    pag.init()
    clase = AutoClicker()