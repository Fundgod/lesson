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
SIZE = (600, 490)


def format_coords(x, y):
    return f'{x},{y}'


class Button:
    def __init__(self, surface, color, x, y, length, height, width, text, text_color):
        self.surface = surface
        self.color = color
        self.x = x
        self.y = y
        self.length = length
        self.height = height
        self.width = width
        self.text = text
        self.text_color = text_color
        self.create_button()
        self.types_of_map = ['map', 'sat', 'skl']

    def create_button(self):
        self.draw_button()
        self.write_text(self.surface, self.text, self.text_color, self.length, self.height, self.x, self.y)
        self.rect = pygame.Rect(self.x, self.y, self.length, self.height)

    def write_text(self, surface, text, text_color, length, height, x, y):
        font_size = int(length//len(text))
        myFont = pygame.font.SysFont("Calibri", font_size)
        myText = myFont.render(text, True, text_color)
        surface.blit(myText, ((x+length/2) - myText.get_width()/2, (y+height/2) - myText.get_height()/2))

    def draw_button(self):
        for i in range(1, 10):
            s = pygame.Surface((self.length+(i*2), self.height+(i*2)))
            s.fill(self.color)
            alpha = (255/(i+2))
            if alpha <= 0:
                alpha = 1
            s.set_alpha(alpha)
            pygame.draw.rect(s, self.color, (self.x - i, self.y - i, self.length+i, self.height + i), self.width)
            self.surface.blit(s, (self.x - i, self.y - i))
        pygame.draw.rect(self.surface, self.color, (self.x, self.y, self.length, self.height), 0)
        pygame.draw.rect(self.surface, (190, 190, 190), (self.x, self.y, self.length, self.height), 1)
        self.write_text(self.surface, self.text, self.text_color, self.length, self.height, self.x, self.y)

    def pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        self.text = self.types_of_map[(self.types_of_map.index(self.text) + 1) % len(self.types_of_map)]
                        return True
        return False


class App:
    def __init__(self):
        self.spn = 0.005
        self.focus = (37.53, 55.7)
        self.view_mode = 'map'
        self.map = self._load_map()

    def _load_map(self):
        params = {
            "ll": format_coords(*self.focus),
            "spn": format_coords(self.spn, self.spn),
            "l": self.view_mode
        }
        response = requests.get(MAP_API_SERVER, params=params)
        with open('map.png', 'wb') as f:
            f.write(response.content)
        map = pygame.transform.scale(pygame.image.load('map.png'), SIZE)
        return map

    def change_view(self, text):
        self.view_mode = text

    def render(self, screen):
        screen.blit(self.map, (0, 100))


def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    app = App()
    button = Button(screen, 'black', 10, 10, 100, 40, 7, 'map', 'green')
    time = pygame.time.Clock()
    running = True
    while running:
        time.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pass
                # Тут будет какая-нибудь логика
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.pressed(pygame.mouse.get_pos()):
                    app.change_view(button.text)
                    app.map = app._load_map()
            elif event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)
        button.draw_button()
        app.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()