# Complete your game here
import pygame
import random
import sys
import os
import time
import json

from coin import Coin
from monster import Monster
from robot import Robot
from teleport import Teleport

## Monkey patch ##
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


original_load = pygame.image.load
pygame.image.load = lambda file: original_load(resource_path(file))


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        ## Resoluutio ja fps vaihtoedhot ##
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1920, 1080),
            (2560, 1080),
            (3840, 1080),
            (5120, 1440),
        ]
        self.framerates = [30, 60, 90, 120, 150, 180, 210, 240]
        ## Käyttää aluksi ensimmäistä. Tässä voisi olla jokin keino tallentaa käyttäjän valinnat esim. teksti tai csv tiedostoon ##
        self.width, self.height = self.resolutions[0]
        self.fps = self.framerates[0]
        ## Määritetään ikkunan koko ja kokoruutu ##
        self.window = pygame.display.set_mode((self.width, self.height))
        self.is_fullscreen = False
        ## Kolikoiden ja hirviöiden tulosuunnat ##
        self.coming_from = ["up", "down", "left", "right"]
        ## Luodut esineet ja nopeuden kerroin ##
        self.doors = []
        self.monsters = []
        self.coins = []
        self.speed_multiplier = 1
        ## Robotin liikken määritykset aluksi False ettei heti liiku ##
        self.to_left = False
        self.to_right = False
        self.to_up = False
        self.to_down = False
        ## Taso, pisteet ja elämät ##
        self.level = 1
        self.points = 0
        self.lives = 3
        ## Pisteiden tallenusta varten luodaan tiedosto samaan kansioon ja määritellään nimi vielä tyhjäksi ##
        self.score_file_path = os.path.join(
            os.path.expanduser("~"), "RobottiPeli", "high_score.json"
        )
        os.makedirs(os.path.dirname(self.score_file_path), exist_ok=True)
        self.name = ""
        ## Itse robotin sijainti ikkunassa ##
        self.__robot = Robot(self.width / 2, self.height / 2)
        ## Onko peli pelitilassa ja missä näytössä mennään ##
        self.running = False
        self.current_screen = "start"
        ## Pause-tekstin fontti jota käyttää myös Game Over-teksti ##
        self.pause_font = pygame.font.SysFont("Arial", int(self.width / 10))
        ## Itse Pause-teksti luodaan ja sen korkeus ja leveys katsotaan ##
        self.pause_text = self.pause_font.render("Paused", True, (255, 0, 0))
        self.pause_text_width = self.pause_text.get_width()
        self.pause_text_height = self.pause_text.get_height()
        ## Sama homma Game Over-tekstillä ##
        self.game_over_text = self.pause_font.render("Game Over", True, (255, 0, 0))
        self.game_over_text_width = self.game_over_text.get_width()
        self.game_over_text_height = self.game_over_text.get_height()
        ## Luodaan valikkojen painikkeita ##
        self.start_button = self.Button(
            self.width / 8,
            self.height / 8,
            self.width / 5,
            self.height / 10,
            "Start",
            self.new_game,
            True,
        )
        self.restart_button = self.Button(
            self.width / 8,
            self.height / 8,
            self.width / 5,
            self.height / 10,
            "Restart",
            self.new_game,
            True,
        )
        self.resolution_button = self.Button(
            self.width / 8,
            (self.height / 8) * 2,
            self.width / 5,
            self.height / 10,
            "Video options",
            self.to_options,
            True,
        )
        self.main_menu_button = self.Button(
            self.width / 8,
            (self.height / 8) * 2,
            self.width / 5,
            self.height / 10,
            "Main Menu",
            self.back_to_menu,
            True,
        )
        self.windowed_button = self.Button(
            (self.width / 8) * 5,
            (self.height / 8) * 0.5,
            self.width / 5,
            self.height / 10,
            "Windowed",
            self.fullscreen,
            True,
        )
        self.fullscreen_button = self.Button(
            (self.width / 8) * 5,
            (self.height / 8) * 0.5,
            self.width / 5,
            self.height / 10,
            "Fullscreen",
            self.fullscreen,
            True,
        )
        self.exit_button = self.Button(
            self.width / 8,
            (self.height / 8) * 3,
            self.width / 5,
            self.height / 10,
            "Exit",
            self.exit_game,
            True,
        )
        ## Pelin info-tekstit (eli teksti ylälaidassa, jossa näkyy elämät, taso ja pisteet) luodaan ##
        self.info_font = pygame.font.SysFont("Arial", int(self.width / 40))

        self.points_text = self.info_font.render(
            f"Points: {self.points}", True, (255, 0, 0)
        )

        self.level_text = self.info_font.render(
            f"Level: {self.level}", True, (255, 0, 0)
        )

        self.lives_text = self.info_font.render(
            f"Lives: {'<3'*self.lives}", True, (255, 0, 0)
        )

        self.main_loop()

    class Button:
        ## https://thepythoncode.com/article/make-a-button-using-pygame-in-python ##
        def __init__(
            self,
            x: int,
            y: int,
            width: float,
            height: float,
            text: str,
            on_click=None,
            one_press: bool = False,
        ):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.on_click = on_click
            self.one_press = one_press
            self.pressed = False
            self.was_pressed = False
            self.menu_font = pygame.font.SysFont("Arial", int(self.width / 8))
            self.fillColors = {
                "normal": "#ffffff",
                "hover": "#666666",
                "pressed": "#333333",
            }

            self.button_surface = pygame.Surface((self.width, self.height))
            self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.button_surf = self.menu_font.render(text, True, (20, 20, 20))

        def process(self):
            mouse_position = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]

            self.button_surface.fill(self.fillColors["normal"])

            if self.button_rect.collidepoint(mouse_position):
                if mouse_pressed:
                    self.button_surface.fill(self.fillColors["pressed"])
                    self.was_pressed = True
                else:
                    self.button_surface.fill(self.fillColors["hover"])
                    if self.was_pressed:
                        self.was_pressed = False
                        if self.on_click:
                            self.on_click()
            else:
                self.was_pressed = False
                if not mouse_pressed:
                    self.pressed = False

            self.button_surface.blit(
                self.button_surf,
                [
                    self.button_rect.width / 2 - self.button_surf.get_rect().width / 2,
                    self.button_rect.height / 2
                    - self.button_surf.get_rect().height / 2,
                ],
            )
            return self.button_surface, self.button_rect

        ## Resoluution muutoksen myötä sijainnin joutuu päivittämään ##
        def update_position(self, x: int, y: int):
            self.x = x
            self.y = y
            self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            return self

        ## Samoin koon ##
        def update_size(self, width: float, height: float, text: str):
            self.width = width
            self.height = height
            self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.button_surface = pygame.Surface((self.width, self.height))
            self.menu_font = pygame.font.SysFont("Arial", int(self.width / 8))
            self.button_surf = self.menu_font.render(text, True, (20, 20, 20))
            return self

    def new_game(self):
        ## Nollataan kaikki (uudelleenpeluuta varten) ja siirrytään "peli" tilaan ##
        self.level = 1
        self.points = 0
        self.lives = 3
        self.running = True
        self.current_screen = "game"
        self.doors = []
        self.monsters = []
        self.coins = []
        ## robotin sijainti takaisin keskelle ##
        self.__robot.x = self.width / 2
        self.__robot.y = self.height / 2
        self.__robot.outer_x = self.__robot.x + self.__robot.width
        self.__robot.outer_y = self.__robot.y + self.__robot.height

        self.make_coins()
        self.make_monsters()
        for i in range(2):
            self.make_door()
        return self.running, self.current_screen

    def back_to_menu(self):
        ## Vie vain takaisin alkuvalikkoon ##
        self.current_screen = "start"

    def pause(self):
        ## keskeyttää kaiken liikken pelissä ##
        if self.running and self.current_screen == "game":
            self.running = False

            self.pause_font = pygame.font.SysFont("Arial", int(self.width / 10))
            self.pause_text = self.pause_font.render("Paused", True, (255, 0, 0))
            self.pause_text_width = self.pause_text.get_width()
            self.pause_text_height = self.pause_text.get_height()

            return self.running
        if not self.running and self.current_screen == "game":
            self.running = True
            return self.running

    def game_over(self):
        ## Elämät loppuivat joten peli pättyi ##
        self.running = False
        self.doors.clear()
        self.monsters.clear()
        self.coins.clear()

        self.pause_font = pygame.font.SysFont("Arial", int(self.width / 10))
        self.game_over_text = self.pause_font.render("Game Over", True, (255, 0, 0))
        self.game_over_text_width = self.game_over_text.get_width()
        self.game_over_text_height = self.game_over_text.get_height()

        self.window.blit(
            self.game_over_text,
            (
                (self.width / 2) - (self.game_over_text_width / 2),
                (self.height / 4) - (self.game_over_text_height / 2),
            ),
        )
        pygame.display.flip()
        time.sleep(3)
        ## Pieni tauko ennenkuin pääsee kirjoittamaan vähintään 2 merkkiä sisältävän nimen ##
        pygame.display.flip()
        ## https://www.geeksforgeeks.org/how-to-create-a-text-input-box-with-pygame/ ##
        input_font = pygame.font.SysFont(None, int(self.height / 20))
        input_color = "grey"
        input_rect = pygame.Rect(
            (self.width - (self.width * 0.6)),
            (self.height * 0.55),
            (self.width / 18),
            (self.height / 20),
        )
        game_over_info = [
            "Write your name...",
            "...then press Enter to continue",
            "Name must be at least 2 characters long!",
            "Name can't be over 12 characters long!",
        ]
        game_over_info_font = pygame.font.SysFont("Arial", int(self.width / 40))
        info_header_surf = game_over_info_font.render(
            game_over_info[0], True, ("black")
        )

        input_status = game_over_info[1]

        def current_input_status(input_status):
            self.window.fill(
                "white",
                (
                    self.width - (self.width * 0.61),
                    (self.height * 0.65),
                    self.width / 2,
                    self.height / 20,
                ),
            )

            if input_status == game_over_info[1]:
                input_info_surf = game_over_info_font.render(
                    input_status, True, ("black")
                )
                self.window.blit(
                    input_info_surf,
                    (
                        self.width - (self.width * 0.61),
                        (self.height * 0.65),
                    ),
                )
            else:
                input_error_surf = game_over_info_font.render(
                    input_status, True, ("red")
                )
                self.window.blit(
                    input_error_surf,
                    (
                        self.width - (self.width * 0.61),
                        (self.height * 0.65),
                    ),
                )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit_game()
                    elif event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if len(self.name.strip()) >= 2:
                            self.save_score(self.points, self.level, self.name)
                            self.current_screen = "end"
                            return
                        else:
                            input_color = "red"
                            pygame.draw.rect(self.window, input_color, input_rect)
                            input_status = game_over_info[2]
                            current_input_status(input_status)
                            pygame.display.flip()
                            time.sleep(1)
                            input_color = "grey"
                            pygame.draw.rect(self.window, input_color, input_rect)
                            input_status = game_over_info[1]
                            current_input_status(input_status)
                            pygame.display.flip()
                    else:
                        ## nimen maksimi pituus nyt 12 merkkkiä ##
                        if len(self.name) < 12:
                            self.name += event.unicode
                        else:
                            input_status = game_over_info[3]
                            current_input_status(input_status)
                            pygame.display.flip()
                            time.sleep(1)
                            input_status = game_over_info[1]
                            current_input_status(input_status)
                            pygame.display.flip()
                current_input_status(input_status)
                pygame.display.flip()

            self.window.blit(
                info_header_surf,
                (
                    self.width - (self.width * 0.61),
                    (self.height * 0.45),
                ),
            )

            pygame.draw.rect(self.window, input_color, input_rect)
            input_text_surf = input_font.render(self.name, True, (255, 0, 0))
            self.window.blit(input_text_surf, (input_rect.x + 5, input_rect.y + 5))
            input_rect.w = max(
                input_text_surf.get_width(), input_text_surf.get_width() + 5
            )

            pygame.display.flip()

    def exit_game(self):
        pygame.event.clear()
        if self.is_fullscreen:
            self.window = pygame.display.set_mode((self.width, self.height))
            self.is_fullscreen = False
        pygame.display.quit()
        pygame.quit()
        time.sleep(0.2)
        sys.exit()

    def start_screen(self):
        self.window.fill("Black")
        ## Alkuvalikko. painikkeiden koot ja sijainnit päivitetään ##
        start_button_surface, start_button_rect = self.start_button.process()
        resolution_button_surface, resolution_button_rect = (
            self.resolution_button.process()
        )
        exit_button_surface, exit_button_rect = self.exit_button.process()

        self.resolution_button.update_size(
            self.width / 5, self.height / 10, "Video Options"
        )
        self.start_button.update_size(self.width / 5, self.height / 10, "Start")
        self.exit_button.update_size(self.width / 5, self.height / 10, "Exit")

        self.resolution_button.update_position(self.width / 8, (self.height / 8) * 2)
        self.start_button.update_position(self.width / 8, (self.height / 8))
        self.exit_button.update_position(self.width / 8, (self.height / 8) * 3)

        self.window.blit(start_button_surface, start_button_rect)
        self.window.blit(resolution_button_surface, resolution_button_rect)
        self.window.blit(exit_button_surface, exit_button_rect)

        self.info_font = pygame.font.SysFont("Arial", int(self.width / 50))
        start_info = [
            "Collect coins and beware monsters.",
            "Use the doors to teleport,",
            "but the door you went in changes its place.",
            "Control robot with arrow keys",
            "or with WASD keys.",
            "Space to pause the game and again to continue.",
            "Esc to quit the game.",
        ]

        for i, line in enumerate(start_info):
            start_info_text = self.info_font.render(
                line,
                True,
                (255, 0, 0),
            )
            self.window.blit(
                start_info_text,
                ((self.width / 8) * 3.5, (self.height / 14) * i + (self.height / 8)),
            )

        self.check_events()
        pygame.display.flip()

    def graphics_screen(self):
        ## Kuva-asetusten säätövalikko ##
        self.window.fill("Black")
        ## Resoluutiot listasta painikkeiksi ##
        resolution_buttons = []
        for i, res in enumerate(self.resolutions):
            button = self.Button(
                self.width / 8,
                (self.height / 8) * ((i / 1.4) + 3),
                self.width / 5,
                self.height / 13,
                f"{res[0]}x{res[1]}",
                lambda i=i: self.change_resolution(i),
                True,
            )
            resolution_buttons.append(button)

        for index, button in enumerate(resolution_buttons):
            button_surface, button_rect = button.process()
            self.window.blit(button_surface, button_rect)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]
            if button_rect.collidepoint(mouse_pos) and mouse_pressed:
                self.change_resolution(index)
        ## Sama virkistystaajuuksille ##
        fps_buttons = []
        for i, fps in enumerate(self.framerates):
            if i == 0 or i % 2 == 0:
                button = self.Button(
                    (self.width / 8) * 4.5,
                    (self.height / 8) * ((i / 2.8) + 3),
                    self.width / 7,
                    self.height / 13,
                    f"{fps}",
                    lambda i=i: self.change_framerate(i),
                    True,
                )
            else:
                button = self.Button(
                    (self.width / 8) * 6,
                    (self.height / 8) * (((i - 1) / 2.8) + 3),
                    self.width / 7,
                    self.height / 13,
                    f"{fps}",
                    lambda i=i: self.change_framerate(i),
                    True,
                )
            fps_buttons.append(button)
        for index, button in enumerate(fps_buttons):
            button_surface, button_rect = button.process()
            self.window.blit(button_surface, button_rect)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]
            if button_rect.collidepoint(mouse_pos) and mouse_pressed:
                self.change_framerate(index)
        ## Lisää painikkeiden päivitystä jos ja kun kuvasuhde muuttuu sekä onko kokoruudun kokoinen vai pelkkä ikkuna ##
        self.windowed_button.update_position(
            (self.width / 8) * 5, (self.height / 8) * 0.5
        )
        self.windowed_button.update_size(self.width / 5, self.height / 10, "Windowed")

        self.fullscreen_button.update_position(
            (self.width / 8) * 5, (self.height / 8) * 0.5
        )
        self.fullscreen_button.update_size(
            self.width / 5, self.height / 10, "Fullscreen"
        )

        if self.is_fullscreen:
            windowed_button_surface, windowed_button_rect = (
                self.windowed_button.process()
            )
            self.window.blit(windowed_button_surface, windowed_button_rect)

        if not self.is_fullscreen:
            fullscreen_button_surface, fullscreen_button_rect = (
                self.fullscreen_button.process()
            )
            self.window.blit(fullscreen_button_surface, fullscreen_button_rect)

        self.main_menu_button.update_position(self.width / 8, (self.height / 8) * 0.5)
        self.main_menu_button.update_size(self.width / 5, self.height / 10, "Main Menu")
        main_menu_button_surface, main_menu_button_rect = (
            self.main_menu_button.process()
        )
        self.window.blit(main_menu_button_surface, main_menu_button_rect)

        self.info_font = pygame.font.SysFont("Arial", int(self.width / 50))
        options_info = [
            "Resolution:",
            "FPS:",
            "Raising resolution makes game area wider.",
            "Raising FPS makes game speed faster.",
        ]
        resolution_info_text = self.info_font.render(
            options_info[0],
            True,
            (255, 0, 0),
        )
        fps_info_text = self.info_font.render(
            options_info[1],
            True,
            (255, 0, 0),
        )
        self.window.blit(
            resolution_info_text, ((self.width / 5.6), (self.height / 8) * 2.3)
        )
        self.window.blit(fps_info_text, ((self.width / 1.415), (self.height / 8) * 2.3))

        for i, line in enumerate(options_info[2:]):
            options_info_text = self.info_font.render(
                line,
                True,
                (255, 0, 0),
            )
            self.window.blit(
                options_info_text,
                ((self.width / 8) * 3.8, (self.height / 15) * i + (self.height / 1.3)),
            )

        self.check_events()
        pygame.display.flip()

    def end_screen(self):
        self.window.fill("Black")
        ## Loppuvalikko, jossa 10 parasta pelaajaa ##
        end_screen_info = ["Top 10 players:", "Name", "Points"]

        score_font = pygame.font.SysFont("Courier New", int(self.width / 50))

        high_scores = self.read_scores()

        top_ten_surface = score_font.render(
            f"{end_screen_info[0]:<15}", True, (255, 0, 0)
        )
        self.window.blit(
            top_ten_surface,
            (
                self.width - (self.width / 2),
                (self.height / 16) * 2,
            ),
        )
        score_headers_surface = score_font.render(
            f"{end_screen_info[1]:<15}{end_screen_info[2]:>20}", True, ("white")
        )
        self.window.blit(
            score_headers_surface,
            (
                self.width - (self.width / 2),
                (self.height / 16) * 3,
            ),
        )
        for i, score in enumerate(high_scores[:10]):
            score_text_surface = score_font.render(
                f"{score['name']:<15}{score['score']:>20}", True, (255, 0, 0)
            )
            odd_score_text_surface = score_font.render(
                f"{score['name']:<15}{score['score']:>20}", True, ("white")
            )
            if i % 2 == 0:
                self.window.blit(
                    score_text_surface,
                    (
                        self.width - (self.width / 2),
                        (self.height / 16) * (i + 4),
                    ),
                )
            else:
                self.window.blit(
                    odd_score_text_surface,
                    (
                        self.width - (self.width / 2),
                        (self.height / 16) * (i + 4),
                    ),
                )
        ## Taas joutuu vähän päivittää painikkeita ##
        self.restart_button.update_position(self.width / 8, self.height / 8)
        self.main_menu_button.update_position(self.width / 8, (self.height / 8) * 2)
        self.exit_button.update_position(self.width / 8, (self.height / 8) * 3)

        restart_button_surface, restart_button_rect = self.restart_button.process()
        main_menu_button_surface, main_menu_button_rect = (
            self.main_menu_button.process()
        )
        exit_button_surface, exit_button_rect = self.exit_button.process()

        self.main_menu_button.update_size(self.width / 5, self.height / 10, "Main Menu")
        self.restart_button.update_size(self.width / 5, self.height / 10, "Restart")
        self.exit_button.update_size(self.width / 5, self.height / 10, "Exit")

        self.window.blit(restart_button_surface, restart_button_rect)
        self.window.blit(main_menu_button_surface, main_menu_button_rect)
        self.window.blit(exit_button_surface, exit_button_rect)
        self.check_events()
        pygame.display.flip()

    def change_resolution(self, index: int):
        ## Vaihtaa resoluutiota ja tietysti päivittää robotin sijainnin keskelle myös ##
        self.width, self.height = self.resolutions[index]
        self.window = pygame.display.set_mode((self.width, self.height))
        if self.is_fullscreen:
            self.window = pygame.display.set_mode(
                (self.width, self.height), pygame.FULLSCREEN
            )
        self.__robot.x = self.width / 2
        self.__robot.y = self.height / 2
        self.__robot.outer_x = self.__robot.x + self.__robot.width
        self.__robot.outer_y = self.__robot.y + self.__robot.height

    def change_framerate(self, index: int):
        ## Vaihtaa virkistystaajuutta ##
        self.fps = self.framerates[index]

    def to_options(self):
        ## Vaihtaa vain näyttämään asetus-valikon ##
        self.current_screen = "options"

    def fullscreen(self):
        ## Kokoruudun ja ikkunan vaihto ##
        if self.is_fullscreen:
            self.window = pygame.display.set_mode((self.width, self.height))
            self.is_fullscreen = False

        else:
            self.window = pygame.display.set_mode(
                (self.width, self.height), pygame.FULLSCREEN
            )
            self.is_fullscreen = True

    def save_score(self, score: int, level: int, name: str):
        try:
            ## Pisteet, taso, nimi ja milloin on pelattu/ peli loppunut ##
            score_data = {
                "name": name,
                "score": score,
                "level": level,
                "date": time.strftime("%H:%M:%S %m.%d.%y", time.localtime()),
            }
            ## Jos ei ole json tiedostoa jo valmiiksi niin luodaan se ja tallennetaan pisteet ##
            if not os.path.exists(self.score_file_path):
                with open(self.score_file_path, "w") as file:
                    json.dump([score_data], file)
            ## jos on jo json niin luetaan pisteet, lisätään uusi ja tallennetaan. oli ehkä katevin tapa toteuttaa ##
            else:
                high_scores = self.read_scores()
                high_scores.append(score_data)
                with open(self.score_file_path, "w") as file:
                    json.dump(high_scores, file)
        except Exception as e:
            print(f"Error saving score: {e}")

    def read_scores(self, custom_path=None):
        try:
            file_path = custom_path if custom_path else self.score_file_path
            
            if not os.path.exists(file_path):
                return []
                
            with open(file_path, "r") as file:
                scores = json.load(file)

            high_scores = []
           
            for line in scores:
                high_scores.append(line)

            return sorted(
                [top_score for top_score in high_scores],
                key=lambda top_score: top_score["score"],
                reverse=True,
            )
        except Exception as e:
            print(f"Error reading scores: {e}")
            return []

    def get_item(self, width, height, coming_from=None):
        if coming_from != None:
            if coming_from == "up":
                x = random.randint(0, self.width - width)
                y = random.randint(-self.height, 0 - height)
            if coming_from == "down":
                x = random.randint(0, self.width - width)
                y = random.randint(self.height, self.height * 2)
            if coming_from == "left":
                x = random.randint(-self.width, 0 - width)
                y = random.randint(0, self.height - height)
            if coming_from == "right":
                x = random.randint(self.width, self.width * 2)
                y = random.randint(0, self.height - height)
            return x, y, coming_from
        else:
            x = random.randint(width * 2, self.width - width * 2)
            y = random.randint(height * 2, self.height - height * 2)
            return x, y

    def make_coins(self):
        ## Kolikon luonti peliin ##
        coin = Coin(0, 0)
        if self.running:
            for i in range(self.level + random.randint(0, 2)):
                coming_from = random.choice(self.coming_from)
                x, y, coming_from = self.get_item(coin.width, coin.height, coming_from)
                self.coins.append(Coin(x, y, coming_from))

    def make_monsters(self):
        ## Hirviön luonti peliin ##
        monster = Monster(0, 0)
        if self.running:
            for i in range(self.level + random.randint(0, 2)):
                coming_from = random.choice(self.coming_from)
                x, y, coming_from = self.get_item(
                    monster.width, monster.height, coming_from
                )
                self.monsters.append(Monster(x, y, coming_from))

    def make_door(self):
        ## Luodaan teleportit ja varmistetaan ettei tuu enempää kuin 2 (toivottavasti) ##
        door = Teleport(0, 0)
        if self.running:
            x, y = self.get_item(door.width, door.height)
            new_door = Teleport(x, y)
            for door in self.doors:
                if (
                    new_door.x <= door.outer_x + door.width
                    and new_door.y <= door.outer_y + door.height
                    and new_door.outer_x >= door.x - door.width
                    and new_door.outer_y >= door.y - door.height
                ):

                    self.make_door()
            if len(self.doors) < 2:
                self.doors.append(new_door)

    def check_events(self):
        ## Robotin liikkeet ja pelin lopetus ##
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_game()
                if event.key == pygame.K_SPACE:
                    self.pause()
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.to_left = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.to_right = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.to_up = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.to_down = True
                if event.key == pygame.K_END and self.running == True:
                    self.game_over()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.to_left = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.to_right = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.to_up = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.to_down = False

        if (
            self.running
            and self.to_right
            and self.__robot.x <= (self.width - self.__robot.width)
        ):
            self.__robot.move(5, 0)
        if self.running and self.to_left and self.__robot.x >= 0:
            self.__robot.move(-5, 0)
        if self.running and self.to_up and self.__robot.y >= 0:
            self.__robot.move(0, -5)
        if (
            self.running
            and self.to_down
            and self.__robot.y <= (self.height - self.__robot.height)
        ):
            self.__robot.move(0, 5)

    def draw_window(self):
        ## Itse pelinäkymä ##
        self.window.fill("White")
        self.__robot.draw(self.window)
        ## Taas päivitetään fonttien kokoja ja sijainteja ##
        self.info_font = pygame.font.SysFont("Arial", int(self.width / 50))

        self.points_text_width = self.points_text.get_width()
        self.points_text_height = self.points_text.get_height()
        self.level_text_width = self.level_text.get_width()
        self.level_text_height = self.level_text.get_height()
        self.lives_text_width = self.lives_text.get_width()
        self.lives_text_height = self.lives_text.get_height()

        self.points_text = self.info_font.render(
            f"Points: {self.points}", True, (255, 0, 0)
        )
        self.level_text = self.info_font.render(
            f"Level: {self.level}", True, (255, 0, 0)
        )
        self.lives_text = self.info_font.render(
            f"Lives: {'<3'*self.lives}", True, (255, 0, 0)
        )
        self.window.blit(
            self.points_text,
            (
                self.width - (self.width * 0.05 + self.points_text_width),
                self.points_text_height,
            ),
        )
        self.window.blit(
            self.level_text,
            ((self.width / 2) - (self.level_text_width / 2), self.level_text_height),
        )
        self.window.blit(
            self.lives_text,
            (self.width * 0.05, self.lives_text_height),
        )

        if self.running:
            ## (Jos peli käynnissä) Kolikon liike ja uusien kolikoiden luonti kun vanhat loppuu ##
            for c in self.coins:
                c.draw(self.window)
                if c.coming_from == "up":
                    c.move(0, 1 * self.speed_multiplier)
                    if c.y > self.height:
                        self.coins.remove(c)
                elif c.coming_from == "down":
                    c.move(0, -1 * self.speed_multiplier)
                    if c.y < -c.height:
                        self.coins.remove(c)
                elif c.coming_from == "left":
                    c.move(1 * self.speed_multiplier, 0)
                    if c.x > self.width:
                        self.coins.remove(c)
                elif c.coming_from == "right":
                    c.move(-1 * self.speed_multiplier, 0)
                    if c.x < -c.width:
                        self.coins.remove(c)
                if c.collision(
                    self.__robot.x,
                    self.__robot.outer_x,
                    self.__robot.y,
                    self.__robot.outer_y,
                ):
                    self.points += 1
                    self.coins.remove(c)

            if len(self.coins) == 0:
                self.level += 1
                self.speed_multiplier += 0.1
                self.make_coins()

            if len(self.monsters) == 0:
                self.make_monsters()
            ## sama homma hirviöille ##
            for m in self.monsters:
                m.draw(self.window)
                if m.coming_from == "up":
                    m.move(0, 1 * self.speed_multiplier)
                    if m.y > self.height:
                        self.monsters.remove(m)
                if m.coming_from == "down":
                    m.move(0, -1 * self.speed_multiplier)
                    if m.y < -m.height:
                        self.monsters.remove(m)
                if m.coming_from == "left":
                    m.move(1 * self.speed_multiplier, 0)
                    if m.x > self.width:
                        self.monsters.remove(m)
                if m.coming_from == "right":
                    m.move(-1 * self.speed_multiplier, 0)
                    if m.x < -m.width:
                        self.monsters.remove(m)
                if m.collision(
                    self.__robot.x,
                    self.__robot.outer_x,
                    self.__robot.y,
                    self.__robot.outer_y,
                ):
                    self.lives -= 1
                    self.monsters.remove(m)
                    if self.lives <= 0:
                        self.game_over()
            ## Ovien logiikka, jossa ovi, josta on menty sisään, vaithaa paikkaa ##
            used_door = None
            for d in self.doors:
                d.draw(self.window)
                if d.collision(
                    self.__robot.x,
                    self.__robot.outer_x,
                    self.__robot.y,
                    self.__robot.outer_y,
                ):
                    used_door = d
                    entering_from = d.entering_from
                    break
            ## Ovi myös tunnistaa suuunnan josta robotti on mennyt sisään jolloin se tulee loogisesti ulos vastakkaisesta suunnasta, ##
            ## jotta liike pysyisi hyvi jatkuvana eikä ulostulo oveen törmäisi heti uudestaan                                        ##
            if not used_door == None:
                other_door = [door for door in self.doors if door != used_door]
                if other_door:
                    door = other_door[0]
                    if entering_from == "up":
                        self.__robot.x = door.x
                        self.__robot.y = door.outer_y + 20
                        self.__robot.outer_x = self.__robot.x + self.__robot.width
                        self.__robot.outer_y = self.__robot.y + self.__robot.height
                    if entering_from == "down":
                        self.__robot.x = door.x
                        self.__robot.outer_y = door.y - 20
                        self.__robot.outer_x = self.__robot.x + self.__robot.width
                        self.__robot.y = self.__robot.outer_y - self.__robot.height
                    if entering_from == "left":
                        self.__robot.x = door.outer_x + 20
                        self.__robot.y = door.y
                        self.__robot.outer_x = self.__robot.x + self.__robot.width
                        self.__robot.outer_y = self.__robot.y + self.__robot.height
                    if entering_from == "right":
                        self.__robot.outer_x = door.x - 20
                        self.__robot.x = self.__robot.outer_x - self.__robot.width
                        self.__robot.y = door.y
                        self.__robot.outer_y = self.__robot.y + self.__robot.height
                    ## ...ja aina kun ovi on "käytetty" niin luodaan uusi ##
                    self.doors.remove(used_door)
                    self.make_door()
        ## Välilyönnillä peli menee 'Pauselle' ja liike pysähtyy sekä näytetään "Pause" teksti ##
        if not self.running:
            self.window.blit(
                self.pause_text,
                (
                    (self.width / 2) - (self.pause_text_width / 2),
                    (self.height / 2) - (self.pause_text_height / 2),
                ),
            )
        pygame.display.flip()

    def main_loop(self):
        ## Pelin jatkuvuuden mahsollistava 'looppi' joka ohjaa myös eri näkymät ##
        while True:
            self.clock.tick(self.fps)
            self.check_events()
            if self.current_screen == "start":
                self.start_screen()
            elif self.current_screen == "options":
                self.graphics_screen()
            elif self.current_screen == "game":
                self.draw_window()
            elif self.current_screen == "end":
                self.end_screen()


if __name__ == "__main__":
    ## Sitten vain käynnistetään peli tässä sillä 'main_loop' ajetaan itse pelin initialisaatiosa ##
    Game()
