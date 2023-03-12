import pygame
import sys
import space

pygame.init()

color_dict = {"white": (255, 255, 255),
              "black": (0, 0, 0),
              "red": (255, 40, 40),
              "blue": (0, 100, 255),
              "green": (0, 255, 150),
              "yellow": (255, 255, 0)}

size = width, height = 1280, 800
bg = 30, 30, 30
white = 255, 255, 255
pos = (990, 400)
radius = 10
circle_center = (640, 400)

screen = pygame.display.set_mode(size)

ball = None

world = space.Space(10, 1)

input_file = open("input.txt", "r")
lines = input_file.readlines()

pause = True

for line in lines:
    corpus_args = line.split()
    if corpus_args[0] != "#":
        corpus = space.Corpus([float(corpus_args[0]), float(corpus_args[1])],
                              [float(corpus_args[2]), float(corpus_args[3])],
                              float(corpus_args[4]), color_dict[corpus_args[5]])
        world.insert_corpus(corpus)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pause = not pause

    if not pause:
        world.run_frame(1)
        world.offset_origin(world.corpus_list[0])


    screen.fill(bg)
    for corpus in world.corpus_list:
        pos = x, y = world.translate_to_screen([corpus.x, corpus.y])
        pygame.draw.circle(screen, corpus.color, pos, corpus.radius)

    if pause:
        pause_rect1 = pygame.Rect(44, 20, 8, 26)
        pause_rect2 = pygame.Rect(28, 20, 8, 26)
        pygame.draw.rect(screen, white, pause_rect1)
        pygame.draw.rect(screen, white, pause_rect2)
    pygame.display.flip()
