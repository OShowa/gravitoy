import pygame
import sys
import space
import assets


pygame.init()

size = width, height = 1280, 800
bg = 10, 10, 10
white = 255, 255, 255
radius = 10

screen = pygame.display.set_mode(size)

ball = None

world = space.Space(10, 1)

input_file = open("input.txt", "r")
lines = input_file.readlines()
center_corpus = None
new_center = None
space_pos = None
draw_selection = False
pause_rect1 = pygame.Rect(44, 20, 8, 26)
pause_rect2 = pygame.Rect(28, 20, 8, 26)


pause = True
draw_trails = True

fps = assets.FPS()

for line in lines:
    corpus_args = line.split()
    if corpus_args[0] != "#":
        corpus = space.Corpus([float(corpus_args[0]), float(corpus_args[1])],
                              [float(corpus_args[2]), float(corpus_args[3])],
                              float(corpus_args[4]), assets.get_color(corpus_args[5]))
        world.insert_corpus(corpus)

while True:
    screen.fill(bg)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = not pause
            if event.key == pygame.K_t:
                draw_trails = not draw_trails
        if event.type == pygame.MOUSEBUTTONDOWN:
            space_pos = world.translate_to_space(event.pos)
            center_corpus = world.pos_is_inside(space_pos)
            if center_corpus is None:
                draw_selection = False
                new_center = space_pos
            else:
                draw_selection = True
            world.empty_trails()

    if center_corpus is not None:
        world.offset_origin([center_corpus.x, center_corpus.y])
    elif new_center is not None:
        world.offset_origin(space_pos)
        new_center = None
    if not pause:
        draw_selection = False
        world.run_frame(0.1)

    if draw_selection:
        center_pos = x, y = world.translate_to_screen([center_corpus.x, center_corpus.y])
        select_color = assets.change_brightness(assets.get_color("white"), 0.5)
        pygame.draw.circle(screen, center_corpus.color, center_pos, center_corpus.radius)
        pygame.draw.circle(screen, select_color, center_pos, center_corpus.radius + 2)
    for corpus in world.corpus_list:
        pos = x, y = world.translate_to_screen([corpus.x, corpus.y])
        if len(corpus.trail) > 0 and draw_trails:
            pygame.draw.lines(screen, corpus.trail_color, False, corpus.trail + [pos])
        pygame.draw.circle(screen, corpus.color, pos, corpus.radius)
    fps.render(screen)

    if pause:
        pygame.draw.rect(screen, white, pause_rect1)
        pygame.draw.rect(screen, white, pause_rect2)
    pygame.display.flip()
    fps.clock.tick(60)
