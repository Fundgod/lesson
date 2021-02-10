import pygame
import requests
import sys
from io import BytesIO


GEOCODER_API_SERVER = "http://geocode-maps.yandex.ru/1.x/"
GEOCODER_PARAMS = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "format": "json"}
MAP_API_SERVER = "http://static-maps.yandex.ru/1.x/"
FPS = 60
BLACK = (0, 0, 0)
SIZE = (600, 450)
ARROW_BUTTONS = {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT}


def format_coords(x, y):
    return f'{x},{y}'


class App:
    def __init__(self):
        self.spn = 0.001
        self.focus = [37.53, 55.7]
        self.map = self._load_map()
        self.move_speed = 0.1
        self._SPN_VALUES = (0.0005, 0.0007, 0.001, 0.0015, 0.003, 0.006, 0.1, 1, 2)

    def _load_map(self):
        params = {
            "ll": format_coords(*self.focus),
            "spn": format_coords(self.spn, self.spn),
            "l": "map"
        }
        response = requests.get(MAP_API_SERVER, params=params)
        with open('map.png', 'wb') as f:
            f.write(response.content)
        map = pygame.transform.scale(pygame.image.load('map.png'), SIZE)
        return map

    def _change_spn(self, direction):
        try:
            self.spn = self._SPN_VALUES[self._SPN_VALUES.index(self.spn) + direction]
            self.update()
        except IndexError:  # уже установлено крайнее значение
            return

    def _change_focus(self, key):
        if key == pygame.K_UP:
            self.focus[1] += self.move_speed * self.spn
        elif key == pygame.K_DOWN:
            self.focus[1] -= self.move_speed * self.spn
        elif key == pygame.K_LEFT:
            self.focus[0] -= self.move_speed * self.spn
        elif key == pygame.K_RIGHT:
            self.focus[0] += self.move_speed * self.spn
        self.update()

    def update(self):
        self.map = self._load_map()

    def render(self, screen):
        screen.blit(self.map, (0, 0))

    def on_keypress(self, key):
        if key == pygame.K_PAGEDOWN:
            self._change_spn(1)
        elif key == pygame.K_PAGEUP:
            self._change_spn(-1)
        elif key in ARROW_BUTTONS:
            self._change_focus(key)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    app = App()
    time = pygame.time.Clock()
    running = True
    while running:
        time.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                app.on_keypress(event.key)
            elif event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)
        app.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()