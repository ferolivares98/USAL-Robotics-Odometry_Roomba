# -*- coding: utf-8 -*-

# Pedro Luis Alonso Díez
# Juan Carlos Cáceres Sánchez
# Fernando Olivares Naranjo
# Jorge Prieto de la Cruz
# Guillermo Vicente González

from pycreate2 import Create2
from robot import *
from constants import *
from time import sleep


def main():
    # Create a Create2.
    port = "/dev/ttyUSB0"  # where is your serial port?
    bot = Create2(port)
    # Start the Create 2
    bot.start()
    # Put the Create2 into 'safe' mode so we can drive it
    # This will still provide some protection
    bot.safe()
    # You are responsible for handling issues, no protection/safety in
    # this mode ... becareful
    # bot.full()
    bot.digit_led_ascii('NANO')

    pygame.init()
    screen = pygame.display.set_mode((FULL_MAP_WIDTH + EXTRA_WIDTH,
                                      FULL_MAP_HEIGHT))
    pygame.display.set_caption(' Rooomba  |  Odometría ')
    imagen_robot = cargar_robot()

    robot = Robot(bot)
    screen.fill(COLOR_BLANCO)
    robot.dibujar_robot(screen, imagen_robot)
    enc_der, enc_izq = 0, 0
    last_enc_der, last_enc_izq = 0, 0  # Necesario para recuperar valores ante paradas o teclas de config.
    necesidad_de_velocidad = False
    golpe = False  # Variable que controla un golpe del robot para detenerlo después de retroceder.

    run = True
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks()

    # Marcha atrás
    song = [90, 34]
    song_start = [76, 12, 76, 12, 20, 12, 76, 12, 20, 12, 72, 12, 76, 12, 20, 12, 79, 12, 20, 36, 67, 12, 20, 36]
    song_fail = [72, 12, 20, 24, 67, 12, 20, 24, 64, 24, 69, 16, 71, 16, 69, 16, 68, 24, 70, 24, 68,
                 24, 67, 12, 65, 12, 67, 48]
    song_num = 2
    bot.createSong(song_num, song_start)
    bot.playSong(song_num)
    song_num = 0
    bot.createSong(song_num, song)
    bot.playSong(song_num)
    song_flag = False

    while run:
        if song_flag:
            bot.playSong(song_num)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                enc_der, enc_izq = 0, 0  # Descomentar para movimiento continuado.
                necesidad_de_velocidad = False
                # Movimiento continuo hacia delante. Tecla W.
                if event.key == pygame.K_w:
                    enc_der, enc_izq = robot.movimiento_W()
                    song_flag = False
                # Movimiento continuo hacia atrás. Tecla S.
                elif event.key == pygame.K_s:
                    enc_der, enc_izq = robot.movimiento_S()
                    song_flag = True
                # Movimiento de giro sobre si mismo a la izquierda. Tecla A.
                elif event.key == pygame.K_a:
                    enc_der, enc_izq = robot.movimiento_A()
                    song_flag = False
                # Movimiento de giro sobre si mismo a la derecha. Tecla D.
                elif event.key == pygame.K_d:
                    enc_der, enc_izq = robot.movimiento_D()
                    song_flag = False
                # Parada segura del bot.
                elif event.key == pygame.K_t:
                    robot.parada_segura()
                    song_flag = False
                # Movimiento continuo con desviación izquierda. Tecla Q.
                elif event.key == pygame.K_q:
                    enc_der, enc_izq = robot.movimiento_Q()
                    song_flag = False
                # Movimiento continuo con desviación derecha. Tecla E.
                elif event.key == pygame.K_e:
                    enc_der, enc_izq = robot.movimiento_E()
                    song_flag = False
                # Aumentar velocidad.
                elif event.key == pygame.K_i:
                    robot.velocidad_aumenta()
                    necesidad_de_velocidad = True
                # Disminuir la velocidad.
                elif event.key == pygame.K_o:
                    robot.velocidad_disminuye()
                    necesidad_de_velocidad = True

        ticks_vel = (pygame.time.get_ticks() - last_time) / 1000
        last_time = pygame.time.get_ticks()
        pygame.display.flip()
        robot.dibujar_fondo(screen)
        robot.dibujar_robot(screen, imagen_robot)
        robot.dibujar_trail(screen)
        robot.dibujar_pos_info(screen)
        # pygame.display.flip()
        # Con esta variable se controla si la tecla pulsada causa comportamientos de cambios de
        # velocidad. Se evita perder la velocidad del robot.
        if necesidad_de_velocidad:
            enc_der, enc_izq = last_enc_der, last_enc_izq
        golpe = robot.odo_calc(enc_der, enc_izq, ticks_vel)  # Movimiento continuado
        if golpe:
            protocolo_golpe(bot, song_fail)
            song_num = 0
            bot.createSong(song_num, song)
            robot.color_de_linea = (255, 0, 0)
            enc_der, enc_izq = 0, 0
        golpe = False
        last_enc_der, last_enc_izq = enc_der, enc_izq
        clock.tick(FPS)

    bot.close()
    pygame.quit()


def cargar_robot():
    robot = pygame.transform.scale(pygame.image.load("assets/roombaUP.png"),
                                   (208, 232))
    return robot


def protocolo_golpe(bot, song_fail):
    bot.digit_led_ascii('OUCH')
    bot.drive_direct(-200, -200)
    song_num = 1
    bot.createSong(song_num, song_fail)
    bot.playSong(song_num)
    sleep(3)
    bot.drive_stop()
    bot.digit_led_ascii('FAIL')


if __name__ == '__main__':
    main()
