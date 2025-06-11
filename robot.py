import pygame

class Robot:
    def __init__(self, x: int, y: int):
        self.robot = pygame.image.load("robot.png")
        self.width = self.robot.get_width()
        self.height = self.robot.get_height()
        self.x = x
        self.y = y
        self.outer_x = self.x + self.width
        self.outer_y = self.y + self.height

    ## Luo robotti ##
    def draw(self, window: pygame.Surface):
        window.blit(self.robot, (self.x, self.y))

    ## Liikuta robottia ##
    def move(self, x: int, y: int):
        self.x += x
        self.outer_x += x
        self.y += y
        self.outer_y += y