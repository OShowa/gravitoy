import math
from library import assets

MAX_TRAIL = 240


class Corpus:
    def __init__(self, pos, speed, mass, color=(255, 255, 255), is_negligible=False):
        self.x = pos[0]
        self.y = pos[1]
        self.old_x = None
        self.old_y = None
        self.speed = speed
        self.accum_speed = [0, 0]
        self.mass = mass
        self.color = color
        if color == (0, 0, 0):
            self.trail_color = (255, 255, 255)
        else:
            self.trail_color = assets.change_brightness(color, 0.5)
        self.real_radius = 0
        self.pixel_radius = 0
        self.collidedWith = None
        self.is_negligible = is_negligible
        self.trail = []

    def move(self, time=1):
        self.old_x = self.x
        self.old_y = self.y
        self.x = self.x + time * self.speed[0]
        self.y = self.y + time * self.speed[1]

    def def_real_radius(self, density, scale):
        self.real_radius = math.sqrt(self.mass / density)
        self.pixel_radius = int(round(self.real_radius / scale))

    def def_pixel_radius(self, scale):
        self.pixel_radius = int(round(self.real_radius / scale))

    def sum_speeds(self):
        self.speed = vector_sum(self.speed, self.accum_speed)
        self.accum_speed = [0, 0]


class Space:
    def __init__(self, screen_size, scale=10, g=1):
        self.corpus_list = []
        self.origin_x = 0  # space coordinates correspondent to center screen (640, 400)
        self.origin_y = 0
        self.scale = scale  # how many units of space for each pixel on screen
        self.g = g
        self.density = scale * 10
        self.center_screen = [screen_size[0] // 2, screen_size[1] // 2]

    def insert_corpus(self, new_corpus):
        if isinstance(new_corpus, Corpus):
            self.corpus_list.append(new_corpus)
            new_corpus.def_real_radius(self.density, self.scale)
        else:
            print("Attempt to insert non-corpus into space!")

    def translate_to_screen(self, pos):
        x = pos[0]
        y = pos[1]
        screen_x = int(round(self.center_screen[0] + (x - self.origin_x) / self.scale))
        screen_y = int(round(self.center_screen[1] + (y - self.origin_y) / self.scale))
        return screen_x, screen_y

    def translate_to_space(self, pos):  # USE ONLY FOR USER INPUT
        x = pos[0]
        y = pos[1]
        space_x = (x - self.center_screen[0]) * self.scale + self.origin_x
        space_y = (y - self.center_screen[1]) * self.scale + self.origin_y
        return space_x, space_y

    def pos_is_inside(self, pos):
        for corpus in self.corpus_list:
            dist = [pos[0] - corpus.x, pos[1] - corpus.y]
            practical_radius = corpus.pixel_radius  # radius for clicking
            if corpus.pixel_radius <= 2:  # if radius is too small, increases it to help user
                practical_radius = 3
            if norm(dist) <= practical_radius * self.scale:
                return corpus
        return None

    def add_trails(self, corpus):
        pos = self.translate_to_screen((corpus.old_x, corpus.old_y))
        if len(corpus.trail) < MAX_TRAIL:
            corpus.trail.append(pos)
        elif len(corpus.trail) == MAX_TRAIL:
            corpus.trail.pop(0)
            corpus.trail.append(pos)

    def empty_trails(self):
        for corpus in self.corpus_list:
            corpus.trail = []

    def redef_scale(self, new_scale):
        self.scale = new_scale
        for corpus in self.corpus_list:
            corpus.def_pixel_radius(self.scale)

    def redef_screen_size(self, screen_size):
        current_area = self.center_screen[0] * self.center_screen[1] * 4
        new_area = screen_size[0] * screen_size[1]
        scale_factor = math.sqrt(current_area / new_area)
        self.redef_scale(self.scale * scale_factor)
        self.center_screen = [screen_size[0]//2, screen_size[1]//2]

    def offset_origin(self, pos):
        self.origin_x = pos[0]
        self.origin_y = pos[1]

    def print_space(self):
        for i, corpus in enumerate(self.corpus_list):
            print("Corpus " + str(i) + ": " + str(corpus.x) + " " + str(corpus.y))

    def run_frame(self, interval=1):
        for i, corpus_a in enumerate(self.corpus_list):
            for corpus_b in self.corpus_list[i + 1:]:
                self.calc_gravity_speed(corpus_a, corpus_b, interval)
        for corpus in self.corpus_list:
            corpus.sum_speeds()
            corpus.move(interval)
            self.add_trails(corpus)
            if corpus.collidedWith is not None:
                self.collide(corpus, corpus.collidedWith)

    def collide(self, main_corpus, sec_corpus):
        sec_corpus.collidedWith = main_corpus.collidedWith = None
        sec_corpus.sum_speeds()
        if main_corpus.mass < sec_corpus.mass:
            temp = main_corpus
            main_corpus = sec_corpus
            sec_corpus = temp
        q = momentum(main_corpus.mass, main_corpus.speed, sec_corpus.mass, sec_corpus.speed)
        self.corpus_list.remove(sec_corpus)
        main_corpus.mass = main_corpus.mass + sec_corpus.mass
        main_corpus.real_radius = math.sqrt(main_corpus.mass / self.density)
        print(q)
        main_corpus.speed = scalar_mult(1 / main_corpus.mass, q)

    def calc_gravity_force(self, corpus_a: Corpus, corpus_b: Corpus, scalar_dist):
        return (self.g * corpus_a.mass * corpus_b.mass) / (scalar_dist ** 2)

    def calc_gravity_speed(self, corpus_a: Corpus, corpus_b: Corpus, interval=1):
        dist_a = [corpus_b.x - corpus_a.x, corpus_b.y - corpus_a.y]
        dist_b = [-dist_a[0], -dist_a[1]]
        scalar_dist = norm(dist_a)
        if scalar_dist <= corpus_a.real_radius:
            corpus_b.collidedWith = corpus_a
        if scalar_dist <= corpus_b.real_radius:
            corpus_a.collidedWith = corpus_b
        ctpd_v_a = normalize(dist_a)
        ctpd_v_b = normalize(dist_b)
        scalar_grav_force = self.calc_gravity_force(corpus_a, corpus_b, scalar_dist)
        vel_a = [(scalar_grav_force / corpus_a.mass) * coord * interval for coord in ctpd_v_a]
        vel_b = [(scalar_grav_force / corpus_b.mass) * coord * interval for coord in ctpd_v_b]
        if norm(vel_a) <= 0.0001:
            vel_a = [0, 0]
        if norm(vel_b) <= 0.0001:
            vel_b = [0, 0]
        corpus_a.accum_speed = vector_sum(corpus_a.accum_speed, vel_a)
        corpus_b.accum_speed = vector_sum(corpus_b.accum_speed, vel_b)


def calc_distance_vector(corpus1, corpus2):
    return [corpus1.x - corpus2.x, corpus1.y - corpus2.y]


def norm(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


def normalize(vector):
    v_norm = norm(vector)
    return [vector[0] / v_norm, vector[1] / v_norm]


def scalar_mult(scalar, vector):
    new_vector = []
    for value in vector:
        new_vector.append(value * scalar)
    return new_vector


def vector_sum(v1, v2):
    for i, value in enumerate(v2):
        v1[i] = v1[i] + value
    return v1


def momentum(mass1, speed1, mass2, speed2):
    q_1 = scalar_mult(mass1, speed1)
    q_2 = scalar_mult(mass2, speed2)
    print(q_1, q_2)
    return vector_sum(q_1, q_2)
