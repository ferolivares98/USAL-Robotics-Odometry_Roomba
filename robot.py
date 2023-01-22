# -*- coding: utf-8 -*-

# Pedro Luis Alonso Díez
# Juan Carlos Cáceres Sánchez
# Fernando Olivares Naranjo
# Jorge Prieto de la Cruz
# Guillermo Vicente González

import pygame
import math
from constants import *


class Robot:
    def __init__(self, bot):
        self.bot = bot
        self.pos_x = 400
        self.pos_y = 400
        self.velocidad = 200  # Predeterminado a 200
        self.theta_giro = 0
        self.rueda_der = 0
        self.rueda_izq = 0
        self.diametro_der = DIAM_RUEDA_DER
        self.diametro_izq = DIAM_RUEDA_IZQ
        self.encoder = RESOLUCION_ENCODER
        self.flag_prueba_distancia = False
        # self.posicion_beta = self.calcular_posicion()
        self.posicion_beta = 0

        self.rotada = None
        self.rect_rotada = None
        self.color_de_linea = COLOR_LINEA
        self.trail_list = []

        self.fuente = pygame.font.SysFont("Arial", 24)
        self.fuenteInstrucciones = pygame.font.SysFont("Arial", 18)
        self.texto = self.fuente.render('default', True, COLOR_NEGRO, COLOR_BLANCO)
        self.textRect = self.texto.get_rect()
        self.textRect.center = (FULL_MAP_WIDTH / 10, FULL_MAP_HEIGHT / 10)
        self.texto_ruedas = self.fuente.render('default', True, COLOR_NEGRO, COLOR_BLANCO)
        self.textRect_ruedas = self.texto_ruedas.get_rect()
        self.textRect_ruedas.center = (FULL_MAP_WIDTH / 10, FULL_MAP_HEIGHT / 10 + self.texto_ruedas.get_height())
        self.instrucciones = self.fuenteInstrucciones.render('default', True, COLOR_BLANCO, COLOR_NEGRO)
        self.instruccionesRect = self.instrucciones.get_rect()

    '''
    Métodos de velocidad del robot.
    '''
    def movimiento_W(self):
        self.bot.drive_direct(self.velocidad, self.velocidad)
        return self.velocidad, self.velocidad

    def movimiento_S(self):
        self.bot.drive_direct(-self.velocidad, -self.velocidad)
        return -self.velocidad, -self.velocidad

    def movimiento_A(self):
        self.bot.drive_direct(self.velocidad, -self.velocidad)
        return self.velocidad, -self.velocidad

    def movimiento_D(self):
        self.bot.drive_direct(-self.velocidad, self.velocidad)
        return -self.velocidad, self.velocidad

    def movimiento_Q(self):
        self.bot.drive_direct(self.velocidad + 80, self.velocidad - 80)
        return self.velocidad + 80, self.velocidad - 80

    def movimiento_E(self):
        self.bot.drive_direct(self.velocidad - 80, self.velocidad + 80)
        return self.velocidad - 80, self.velocidad + 80

    def parada_segura(self):
        if self.flag_prueba_distancia:
            aux = self.calcular_posicion()
            self.posicion_beta = aux - self.posicion_beta
        self.bot.drive_stop()

    def velocidad_aumenta(self):
        if self.velocidad < 400:
            self.velocidad += 10

    def velocidad_disminuye(self):
        if self.velocidad > 100:
            self.velocidad -= 10

    '''
        Dibujos de fondo, robot, trazo, controles e información en tiempo real.
    '''
    def dibujar_robot(self, screen, imagen_robot):
        self.rotada = pygame.transform.rotozoom(imagen_robot, math.degrees(self.theta_giro), 1)
        self.rect_rotada = self.rotada.get_rect(center=(self.pos_x, self.pos_y))
        screen.blit(self.rotada, self.rect_rotada)

    def dibujar_fondo(self, screen):
        screen.fill(COLOR_BLANCO)
        pygame.draw.rect(screen, COLOR_NEGRO, (FULL_MAP_WIDTH, 0, EXTRA_WIDTH, EXTRA_HEIGHT))
        inst = ("Controles:\n- Avance -> W\n- Retroceso -> S\n"
                "- 90ºIzquierda -> A\n- 90ºDerecha -> D\n"
                "- LigeroGiroIzq -> Q\n- LigeroGiroDer -> E\n- Parar -> T\"\n\n"
                "- AumentarEncoder (+10) \n     I \n- DisminuirEncoder (-10)\n     O")
        inst_list = inst.splitlines()
        tam_height = self.instrucciones.get_size()
        pos_inst_height = FULL_MAP_HEIGHT / 60
        for i, l in enumerate(inst_list):
            self.instrucciones = self.fuenteInstrucciones.render(l, True, COLOR_BLANCO, COLOR_NEGRO)
            screen.blit(self.instrucciones,
                        ((FULL_MAP_WIDTH + EXTRA_WIDTH - (EXTRA_WIDTH / 1.05)), pos_inst_height))
            pos_inst_height += tam_height[1] + (tam_height[1] / 2)

    def dibujar_pos_info(self, screen):
        text = f"PosX = {int(self.pos_x)} | PosY = {int(self.pos_y)} | " \
               f"|| Velocidad = {int(self.velocidad)}"
        self.texto = self.fuente.render(text, True, COLOR_NEGRO, COLOR_BLANCO)
        screen.blit(self.texto, self.textRect)
        if self.flag_prueba_distancia:
            text2 = f"PruebaDeDistancia (BETA) = {float(self.posicion_beta)}"
            self.texto_ruedas = self.fuente.render(text2, True, COLOR_NEGRO, COLOR_BLANCO)
            screen.blit(self.texto_ruedas, self.textRect_ruedas)

    def dibujar_trail(self, screen):
        for i in range(0, len(self.trail_list) - 1):
            pygame.draw.line(screen, self.color_de_linea, (self.trail_list[i][0], self.trail_list[i][1]),
                             (self.trail_list[i + 1][0], self.trail_list[i + 1][1]), 3)
        self.trail_list.append((self.pos_x, self.pos_y))

    '''
        Cálculos principales de odometría del robot. Posición, velocidad, etc...
    '''
    def odo_calc(self, vel_encoder_der, vel_encoder_izq, ticks_vel):
        sensors = self.bot.get_sensors()
        conversion_der = (math.pi * (self.diametro_der / 2.0) / self.encoder) * sensors.encoder_counts_right * 0.0002646
        conversion_izq = (math.pi * (self.diametro_izq / 2.0) / self.encoder) * sensors.encoder_counts_right * 0.0002646
        self.rueda_der = conversion_der * vel_encoder_der
        self.rueda_izq = conversion_izq * vel_encoder_izq
        self.theta_giro += (self.rueda_der - self.rueda_izq) / SEPARACION_RUEDAS * ticks_vel / 2
        self.pos_x += ((self.rueda_der + self.rueda_izq) / 2) * math.cos(self.theta_giro) * ticks_vel / 2
        self.pos_y -= ((self.rueda_der + self.rueda_izq) / 2) * math.sin(self.theta_giro) * ticks_vel / 2

        if sensors.light_bumper_left > 500 or sensors.light_bumper_right > 500 \
                or sensors.light_bumper_center_left > 500 or sensors.light_bumper_center_right > 500 \
                or sensors.light_bumper_front_left > 500 or sensors.light_bumper_front_right > 500:
            return True
        return False

    def calcular_posicion(self):
        sensors = self.bot.get_sensors()
        pos = (2 * math.pi * (self.diametro_der / 2) / self.encoder) * sensors.encoder_counts_right / 1000
        return pos
