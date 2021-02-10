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


def format_coords(x, y):
    return f'{x},{y}'


class App:
    def __init__(self):
        self.spn = (0.005, 0.005)
        self.focus = (37.53, 55.7)
        self.map = self._load_map()

    def _load_map(self):
        params = {
            "ll": format_coords(*self.focus),
            "spn": format_coords(*self.spn),
            "l": "map"
        }
        response = requests.get(MAP_API_SERVER, params=params)
        with open('map.png', 'wb') as f:
            f.write(response.content)
        map = pygame.transform.scale(pygame.image.load('map.png'), SIZE)
        return map

    def render(self, screen):
        screen.blit(self.map, (0, 0))


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
                pass
                # Тут будет какая-нибудь логика
            elif event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)
        app.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()