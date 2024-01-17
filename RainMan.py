import pygame
from pygame.sprite import Group, Sprite
import sys
import random
accumulation = 0
speed = 2


class Drop(Sprite):
    def __init__(self, screen):
        super(Drop, self).__init__()
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.image = pygame.image.load("raindrop.bmp")
        self.rect = self.image.get_rect()
        self.x = random.randint(self.screen_rect.left - 100, self.screen_rect.right + 100)
        self.y = self.screen_rect.top
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.speed = 5.5

    def update(self):
        self.y += self.speed
        self.speed += 0.02
        self.x += 0.1
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def blit_me(self):
        self.screen.blit(self.image, self.rect)


class VerticalDrop(Drop):
    def __init__(self, screen, x, y):
        super(VerticalDrop, self).__init__(screen)
        self.x = x
        self.y = y
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def update(self):
        self.speed += 0.02
        self.y += self.speed
        self.rect.centerx = self.x
        self.rect.centery = self.y


class Man:
    def __init__(self, screen, ground, right_ani, left_ani):
        self.right_ani = [pygame.image.load(image) for image in right_ani]
        self.left_ani = [pygame.image.load(image) for image in left_ani]
        self.screen = screen
        self.ground = ground
        self.image = pygame.image.load("guyr0.bmp")
        self.rect = self.image.get_rect()
        self.rect.bottom = self.ground.rect.top
        self.rect.left = self.ground.rect.left + 400
        self.step = 0
        self.state = {
            "left": False,
            "right": False,
        }

    def blit_me(self):
        if self.state["left"]:
            index = self.step // 10
            index = index % 6
            self.image = self.left_ani[index]

        elif self.state['right']:
            index = self.step // 10
            index = index % 6
            self.image = self.right_ani[index]

        self.screen.blit(self.image, self.rect)

    def move(self, direction):
        self.state[direction] = True

    def update(self):
        global speed
        if self.state['left']:
            self.rect.centerx -= speed
            self.step += 1
        elif self.state['right']:
            self.rect.centerx += speed
            self.step += 1

    def stop(self):
        if self.state['left']:
            self.image = self.left_ani[0]
            self.state['left'] = False

        elif self.state['right']:
            self.image = self.right_ani[0]
            self.state['right'] = False

        self.step = 0


class Edge(Sprite):
    def __init__(self, screen, start_coordinates, colors, end_coordinates, line):
        super(Edge, self).__init__()
        self.screen = screen
        self.colors = colors
        self.start_coordinates = start_coordinates
        self.end_coordinates = end_coordinates
        self.state = {
            "left": False,
            "right": False
        }
        self.margin_start = self.start_coordinates[0] - line.rect.left
        self.margin_end = self.end_coordinates[0] - line.rect.left

    def draw_me(self):
        pygame.draw.line(self.screen,
                         self.colors["green"],
                         (self.start_coordinates[0],
                          self.start_coordinates[1]),
                         (self.end_coordinates[0],
                          self.end_coordinates[1]),
                         2)

    def update(self, line):
        self.start_coordinates[0] = line.rect.left + self.margin_start
        self.end_coordinates[0] = line.rect.left + self.margin_end


class Ground:
    def __init__(self, screen, colors):
        self.screen = screen
        self.colors = colors
        self.screen_rect = self.screen.get_rect()
        self.rect = pygame.Rect(self.screen_rect.left-100, self.screen_rect.bottom - 60, self.screen_rect.width + 100, 3)

    def draw_me(self):
        pygame.draw.rect(self.screen, self.colors["green"], self.rect)


class Line:
    def __init__(self, screen, colors, guy):
        self.screen = screen
        self.guy = guy
        self.colors = colors
        self.screen_rect = self.screen.get_rect()
        self.rect = pygame.Rect(self.guy.rect.left + 20, self.guy.rect.top, self.guy.rect.width + 85, 2)
        self.state = {
            "left": False,
            "right": True
        }

    def draw_me(self):
        pygame.draw.rect(self.screen, self.colors["green"], self.rect)

    def update(self, guy):
        if guy.state['right']:
            self.state['right'] = True
            self.state['left'] = False
        elif guy.state['left']:
            self.state['left'] = True
            self.state['right'] = False

    def update_direction(self, guy):
        if self.state['left']:
            self.rect.centerx = guy.rect.left + 19

        else:
            self.rect.centerx = guy.rect.right - 19


def update_screen(screen, rain_drops, colors, ground, guy, line, edges, vertical_drops):
    screen.fill(colors["black"])
    guy.blit_me()
    for rain in rain_drops.sprites():
        rain.blit_me()
    for edge in edges.sprites():
        edge.draw_me()
    for drop in vertical_drops.sprites():
        drop.blit_me()
    ground.draw_me()
    line.draw_me()
    pygame.display.update()


def create_rain(rain_drops, screen):
    rain = Drop(screen)
    rain_drops.add(rain)


def update_rain(rain_drops, cor_list, vertical_drops):
    global accumulation
    for rain in rain_drops.copy():
        if rain.rect.bottom > rain.screen_rect.bottom - 60:
            rain_drops.remove(rain)

    for rain in rain_drops.copy():
        for coordinate in cor_list:
            if rain.rect.bottom > coordinate[1]:
                if rain.rect.top <= coordinate[1]:
                    if rain.rect.right > coordinate[0]:
                        if rain.rect.left <= coordinate[0]:
                            accumulation += 1
                            rain_drops.remove(rain)

    for rain in rain_drops.sprites():
        rain.update()

    for drop in vertical_drops.sprites():
        drop.update()

    for drop in vertical_drops.copy():
        if drop.rect.bottom >= drop.screen_rect.bottom - 60:
            vertical_drops.remove(drop)


def parabola(x):
    y = - 1 / 250 * (x ** 2)
    return y


def create_point_list(line):
    startx = -127.5
    y_list = []
    x_list = []
    while startx < 127.5:
        y = -1 * parabola(startx)
        x = line.rect.centerx + startx
        y += line.rect.top - 65.025
        y_list.append(y)
        x_list.append(x)
        startx += 2
    cor_list = []
    for i in range(len(x_list)):
        cor_list.append([x_list[i], y_list[i]])
    return cor_list


def create_egdes(edges, screen, colors, cor_list, line):
    i = 0
    while i < len(cor_list):
        if i < len(cor_list) - 1:
            edge = Edge(screen, cor_list[i], colors, cor_list[i+1], line)
            edges.add(edge)
        i += 1


def create_vertical_drop(vertical_drops, screen, line):
    if random.randint(1, 3) == 1:
        drop = VerticalDrop(screen, line.rect.left, line.rect.centery)
    else:
        drop = VerticalDrop(screen, line.rect.right, line.rect.centery)
    vertical_drops.add(drop)


def update_edges(edges, line):
    for edge in edges.sprites():
        edge.update(line)


def update_line(line, guy):
    line.update(guy)
    line.update_direction(guy)


def main():
    pygame.init()
    colors = {
        "green": (0, 210, 0),
        "black": (0, 0, 0)
    }
    right_ani = ["guyr" + str(x) for x in range(4)]
    left_ani = ["guyl" + str(x) for x in range(4)]
    for i in range(len(right_ani)):
        right_ani[i] += ".bmp"
    for i in range(len(left_ani)):
        left_ani[i] += ".bmp"
    right_reverse = right_ani.copy()
    right_reverse = right_reverse[::-1]
    right_reverse.pop(0)
    for item in right_reverse:
        right_ani.append(item)

    left_reverse = left_ani.copy()
    left_reverse = left_reverse[::-1]
    left_reverse.pop(0)
    for item in left_reverse:
        left_ani.append(item)

    right_ani.pop(6)
    left_ani.pop(6)
    clock = pygame.time.Clock()
    frame_rate = 120
    screen = pygame.display.set_mode((1200, 700))
    pygame.display.set_caption("Rain_Man")
    ground = Ground(screen, colors)
    rain_drops = Group()
    vertical_drops = Group()
    edges = Group()
    guy = Man(screen, ground, right_ani, left_ani)
    line = Line(screen, colors, guy)
    cor_list = create_point_list(line)
    create_egdes(edges, screen, colors, cor_list, line)
    pygame.mixer.music.load("rain2.mp3")
    pygame.mixer.music.play(-1)
    current_frame = 0
    global accumulation
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("\nthank you")
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    print("\nthank you")
                    sys.exit(0)

                elif event.key == pygame.K_d:
                    guy.move('right')

                elif event.key == pygame.K_a:
                    guy.move('left')

            elif event.type == pygame.KEYUP:
                guy.stop()

        if current_frame / frame_rate > 3:
            for i in range(2):
                create_rain(rain_drops, screen)

            if current_frame / frame_rate == 6:
                pygame.image.save(screen, "screenshot.png")
        if accumulation >= 4:
            create_vertical_drop(vertical_drops, screen, line)
            accumulation = 0
        update_rain(rain_drops, cor_list, vertical_drops)
        guy.update()
        update_edges(edges, line)
        update_line(line, guy)
        update_screen(screen, rain_drops, colors, ground, guy, line, edges, vertical_drops)
        current_frame += 1
        clock.tick(frame_rate)

if __name__ == "__main__":
    main()
