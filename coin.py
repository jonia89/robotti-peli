import pygame 

class Coin:
    def __init__(self, x: int, y: int, coming_from: str = None):
        self.coin = pygame.image.load("coin.png")
        self.width = self.coin.get_width()
        self.height = self.coin.get_height()
        self.x = x
        self.y = y
        self.outer_x = self.x + self.width
        self.outer_y = self.y + self.height
        self.coming_from = coming_from

    ## Luo kolikko ##
    def draw(self, window: pygame.Surface):
        window.blit(self.coin, (self.x, self.y))

    ## kolikon liike ##
    def move(self, x: float, y: float):
        self.x += x
        self.outer_x += x
        self.y += y
        self.outer_y += y

    ## tarkista osuuko kolikko robottiin ##
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