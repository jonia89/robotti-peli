import pygame

class Monster:
    def __init__(self, x: int, y: int, coming_from: str = None):
        self.monster = pygame.image.load("monster.png")
        self.width = self.monster.get_width()
        self.height = self.monster.get_height()
        self.x = x
        self.y = y
        self.outer_x = self.x + self.width
        self.outer_y = self.y + self.height
        self.coming_from = coming_from

    ## Luo hirviö ##
    def draw(self, window: pygame.Surface):
        window.blit(self.monster, (self.x, self.y))

    ## Hirviön liike ##
    def move(self, x: float, y: float):
        self.x += x
        self.outer_x += x
        self.y += y
        self.outer_y += y

    ## Tarkista osuuko hirviö robottiin ##
    def collision(
        self, robot_x: int, robot_outer_x: int, robot_y: int, robot_outer_y: int
    ):
        if (
            self.x <= robot_outer_x
            and self.outer_x >= robot_x
            and self.y <= robot_outer_y
            and self.outer_y >= robot_y
        ):
            return True
        return False