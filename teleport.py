import pygame

class Teleport:
    def __init__(self, x: int, y: int):
        self.door = pygame.image.load("door.png")
        self.width = self.door.get_width()
        self.height = self.door.get_height()
        self.x = x
        self.y = y
        self.outer_x = self.x + self.width
        self.outer_y = self.y + self.height
        self.entering_from = None

    ## Luo ovi ##
    def draw(self, window: pygame.Surface):
        window.blit(self.door, (self.x, self.y))

    ## Tarkista osuuko robotti oveen ##
    def collision(self, robot_x: int, robot_outer_x: int, robot_y: int, robot_outer_y: int):
        if (
            self.x <= robot_outer_x
            and self.outer_x >= robot_x
            and self.y <= robot_outer_y
            and self.outer_y >= robot_y
        ):
            ## LEFT
            if (
                robot_outer_x >= self.x
                and robot_outer_x <= self.x + 5
                and robot_outer_y >= self.y
                and robot_y <= self.outer_y
            ):
                self.entering_from = "left"

            ## RIGHT
            if (
                robot_x <= self.outer_x
                and robot_x >= self.outer_x - 5
                and robot_outer_y >= self.y
                and robot_y <= self.outer_y
            ):
                self.entering_from = "right"

            ## UP
            if (
                robot_outer_y >= self.y
                and robot_outer_y <= self.y + 5
                and robot_x <= self.outer_x
                and robot_x >= self.x
                or robot_outer_y >= self.y
                and robot_outer_y <= self.y + 5
                and robot_outer_x <= self.outer_x
                and robot_outer_x >= self.x
            ):
                self.entering_from = "up"

            ## DOWN
            if (
                robot_y <= self.outer_y
                and robot_y >= self.outer_y - 5
                and robot_x <= self.outer_x
                and robot_x >= self.x
                or robot_y <= self.outer_y
                and robot_y >= self.outer_y - 5
                and robot_outer_x <= self.outer_x
                and robot_outer_x >= self.x
            ):
                self.entering_from = "down"
            return self.entering_from
        return False