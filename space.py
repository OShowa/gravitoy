import math

density = 10000  # a unit circle's mass
CENTER_SCREEN = [640, 400]

class Corpus:
    def __init__(self, pos, speed, mass, color=(255, 255, 255)):
        self.x = pos[0]
        self.y = pos[1]
        self.old_x = None
        self.old_y = None
        self.speed = speed
        self.accum_speed = [0, 0]
        self.mass = mass
        self.color = color
        if mass <= density:
            self.radius = 1
        else:
            self.radius = int(round(math.sqrt(mass / density)))
        self.collidedWith = None

    def move(self, time=1):
        self.old_x = self.x
        self.old_y = self.y
        self.x = self.x + time * self.speed[0]
        self.y = self.y + time * self.speed[1]

    def collide(self, corpus):
        old_mass = self.mass
        self.mass = self.mass + corpus.mass
        ratio = math.sqrt(self.mass / old_mass)
        self.radius = int(round(self.radius * ratio))
        if self.collidedWith == corpus:
            self.collidedWith = None


class Space:
    def __init__(self, scale=1, g=0.1):
        self.corpus_list = []
        self.origin_x = 0  # space coordinates correspondent to center screen (640, 400)
        self.origin_y = 0
        self.scale = scale  # how many units of space for each pixel on screen
        self.g = g

    def insert_corpus(self, new_corpus):
        if isinstance(new_corpus, Corpus):
            self.corpus_list.append(new_corpus)
        else:
            print("Attempt to insert non-corpus into space!")

    def translate_to_screen(self, pos):
        x = pos[0]
        y = pos[1]
        screen_x = int(round(CENTER_SCREEN[0] + (x - self.origin_x) / self.scale))
        screen_y = int(round(CENTER_SCREEN[1] + (y - self.origin_y) / self.scale))
        return screen_x, screen_y

    def offset_origin(self, corpus):
        self.origin_x = corpus.x
        self.origin_y = corpus.y

    def print_space(self):
        for i, corpus in enumerate(self.corpus_list):
            print("Corpus " + str(i) + ": " + str(corpus.x) + " " + str(corpus.y))

    def run_frame(self, interval=1):
        for i, corpus_a in enumerate(self.corpus_list):
            for corpus_b in self.corpus_list[i+1:]:
                self.calc_gravity_speed(corpus_a, corpus_b, interval)
        for corpus in self.corpus_list:
            if corpus.collidedWith is not None:
                corpus.collidedWith.collide(corpus)
                self.corpus_list.remove(corpus)
            corpus.speed = vector_sum(corpus.accum_speed, corpus.speed)
            corpus.accum_speed = [0, 0]
            corpus.move(interval)

    def calc_gravity_force(self, corpus_a: Corpus, corpus_b: Corpus, scalar_dist):
        return (self.g * corpus_a.mass * corpus_b.mass) / (scalar_dist ** 2)

    def calc_gravity_speed(self, corpus_a: Corpus, corpus_b: Corpus, interval=1):
        dist_a = [corpus_b.x - corpus_a.x, corpus_b.y - corpus_a.y]
        dist_b = [-dist_a[0], -dist_a[1]]
        scalar_dist = norm(dist_a)
        if scalar_dist <= corpus_a.radius * self.scale:
            corpus_b.collidedWith = corpus_a
        if scalar_dist <= corpus_b.radius * self.scale:
            corpus_a.collidedWith = corpus_b
        ctpd_v_a = normalize(dist_a)
        ctpd_v_b = normalize(dist_b)
        scalar_grav_force = self.calc_gravity_force(corpus_a, corpus_b, scalar_dist)
        vel_a = [(scalar_grav_force / corpus_a.mass) * coord * interval for coord in ctpd_v_a]
        vel_b = [(scalar_grav_force / corpus_b.mass) * coord * interval for coord in ctpd_v_b]
        corpus_a.accum_speed = vector_sum(corpus_a.accum_speed, vel_a)
        corpus_b.accum_speed = vector_sum(corpus_b.accum_speed, vel_b)


def calc_distance_vector(corpus1, corpus2):
    return [corpus1.x - corpus2.x, corpus1.y - corpus2.y]


def norm(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


def normalize(vector):
    v_norm = norm(vector)
    return [vector[0] / v_norm, vector[1] / v_norm]


def vector_sum(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]


def turn90(vector):
    return [vector[1], -vector[0]]
