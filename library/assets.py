import pygame


default_colors = {"white": (255, 255, 255),
                  "black": (0, 0, 0),
                  "red": (255, 40, 40),
                  "blue": (0, 100, 255),
                  "green": (0, 255, 150),
                  "yellow": (255, 255, 0)}


class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("library/pixelfont.ttf", 20)
        self.text = self.font.render(str(self.clock.get_fps()), True, default_colors["white"])

    def render(self, display, size):
        self.text = self.font.render(str(int(self.clock.get_fps())), True, default_colors["white"])
        display.blit(self.text, (size[0] - 40, 20))


def get_color(color):
    color = default_colors[color]
    if color is None:
        color = default_colors["white"]
    return color


def change_brightness(rgb, factor):
    rgb_list = list(rgb)
    for i, value in enumerate(rgb_list):
        new_value = int(value * factor)
        if new_value > 255:
            rgb_list[i] = 255
        else:
            rgb_list[i] = new_value
    return tuple(rgb_list)
