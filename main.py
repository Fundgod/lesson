import pygame
import requests

GEOCODER_API_SERVER = "http://geocode-maps.yandex.ru/1.x/"
GEOCODER_PARAMS = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "format": "json"}
MAP_API_SERVER = "http://static-maps.yandex.ru/1.x/"
FPS = 60
BLACK = (0, 0, 0)
SIZE = (600, 500)
ARROW_BUTTONS = {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT}


def format_coords(x, y):
    return f'{x},{y}'


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.text = text
        self.font = pygame.font.SysFont("Calibri", 30)

    def render(self, surface):
        pygame.draw.rect(surface, (190, 190, 190), self.rect)
        pygame.draw.rect(surface, (0, 255, 0), self.rect, width=1)
        text = self.font.render(self.text, True, (0, 255, 0))
        text_pos = (self.rect.x + (self.rect.width - text.get_width()) / 2, self.rect.y + 5)
        surface.blit(text, text_pos)


class MapModeSwitch(Button):
    map_view_modes = ['map', 'sat', 'skl']

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, 'map')
        self.map_view_mode = 0

    def click(self, mouse_pos):
        if self.rect.colliderect(pygame.Rect(*mouse_pos, 1, 1)):
            self.map_view_mode += 1
            if self.map_view_mode == len(self.map_view_modes):
                self.map_view_mode = 0
            self.text = self.map_view_modes[self.map_view_mode]
            return self.text
        return False


class App:
    _SPN_VALUES = (0.0005, 0.0007, 0.001, 0.0015, 0.003, 0.006, 0.1, 1, 2)

    def __init__(self):
        self.spn = 0.001
        self.focus = [37.53, 55.7]
        self.view_mode = 'map'
        self.map = self._load_map()
        self.mode_switch = MapModeSwitch(5, 5, 100, 40)
        self.move_speed = 0.1

    def _load_map(self):
        params = {
            "ll": format_coords(*self.focus),
            "spn": format_coords(self.spn, self.spn),
            "l": self.view_mode
        }
        response = requests.get(MAP_API_SERVER, params=params)
        with open('map.png', 'wb') as f:
            f.write(response.content)
        return pygame.transform.scale(pygame.image.load('map.png'), SIZE)

    def update(self):
        self.map = self._load_map()

    def _change_spn(self, direction):
        try:
            assert self.spn != self._SPN_VALUES[0] or direction == 1
            self.spn = self._SPN_VALUES[self._SPN_VALUES.index(self.spn) + direction]
            self.update()
        except IndexError:  # уже установлено максимальное значение
            return
        except AssertionError:  # уже установлено минимальное значение
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

    def on_click(self, mouse_pos):
        view_mode = self.mode_switch.click(mouse_pos)
        if view_mode:
            self.view_mode = view_mode
            self.update()

    def on_keypress(self, key):
        if key == pygame.K_PAGEDOWN:
            self._change_spn(1)
        elif key == pygame.K_PAGEUP:
            self._change_spn(-1)
        elif key in ARROW_BUTTONS:
            self._change_focus(key)

    def render(self, surface):
        self.mode_switch.render(surface)
        surface.blit(self.map, (0, 50))


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
            if event.type == pygame.MOUSEBUTTONDOWN:
                app.on_click(event.pos)
            elif event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)
        app.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
