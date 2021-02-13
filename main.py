import pygame
import requests
import pyperclip
from threading import Thread

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
    return f"{x},{y}"


def make_coords(coords):
    return list(map(float, coords.split()))


class Button:
    def __init__(self, x, y, width, height, text, command=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if command is not None:
            self.command = command
        else:
            self.command = lambda: None
        self.rect = pygame.Rect(x, y, width, height)
        self._init_ui()
        self.font = pygame.font.SysFont("Calibri", 30)
        self._set_text(text)

    def _init_ui(self):
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 150, 0, 100))
        subimage = pygame.Surface((self.width - 4, self.height - 4))
        subimage.fill((255, 255, 255, 100))
        self.image.blit(subimage, (2, 2))

    def _set_text(self, text):
        self.text = self.font.render(text, True, (0, 255, 0))
        self.text_pos = (self.x + (self.width - self.text.get_width()) / 2, self.y + 5)

    def click(self):
        self.command()

    def render(self, surface):
        surface.blit(self.image, (self.x, self.y))
        surface.blit(self.text, self.text_pos)


class MapModeSwitch(Button):
    map_view_modes = ["map", "sat", "skl"]

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "map")
        self.map_view_mode = 0

    def click(self):
        self.map_view_mode += 1
        if self.map_view_mode == len(self.map_view_modes):
            self.map_view_mode = 0
        view_mode = self.map_view_modes[self.map_view_mode]
        self._set_text(view_mode)
        return view_mode


class InputField:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self._init_ui()
        self.font = pygame.font.SysFont("Calibri", 30)
        self.text = ''
        self.last_pressed_key = None
        self.renderable_text = self.font.render('', True, (0, 255, 0))
        self.text_pos = (x + 5, y + 5)
        self.input_active = False
        Thread(target=self._play_input_animation, daemon=True).start()

    def _init_ui(self):
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 150, 0, 100))
        subimage = pygame.Surface((self.width - 4, self.height - 4))
        subimage.fill((255, 255, 255, 100))
        self.image.blit(subimage, (2, 2))

    def _play_input_animation(self):
        text_cursor = pygame.Surface((3, 30))
        text_cursor.fill((0, 0, 0))
        absence_text_cursor = pygame.Surface((3, 30))
        absence_text_cursor.fill((255, 255, 255, 100))
        while True:
            if self.input_active:
                pygame.time.delay(500)
                text_cursor_x_pos = 5 + self.renderable_text.get_width()
                self.image.blit(text_cursor, (text_cursor_x_pos, 5))
                text_length = len(self.text)
                delay_time = 500
                while len(self.text) == text_length and delay_time > 0:
                    pygame.time.delay(10)
                    delay_time -= 10
                self.image.blit(absence_text_cursor, (text_cursor_x_pos, 5))

    def activate(self):
        self.input_active = True

    def deactivate(self):
        self.input_active = False

    def clear(self):
        self.text = ''
        self.renderable_text = self.font.render('', True, (0, 255, 0))

    def input(self, event):
        if event.key == pygame.K_BACKSPACE and self.text:
            self.text = self.text[:-1]
        elif event.key == pygame.K_v and self.last_pressed_key == pygame.K_LCTRL:
            self.text += pyperclip.paste()
            self.last_pressed_key = pygame.K_v
        elif event.key == pygame.K_RETURN:
            return True
        else:
            self.last_pressed_key = event.key
            self.text += event.unicode
        self.renderable_text = self.font.render(self.text, True, (0, 255, 0))
        text_width, text_height = self.renderable_text.get_size()
        if text_width > self.width - 15:
            self.renderable_text = self.renderable_text.subsurface(
                (text_width - self.width + 15, 0, self.width - 15, text_height)
            )
        return None

    def get_text(self):
        return self.text

    def render(self, surface):
        surface.blit(self.image, (self.x, self.y))
        surface.blit(self.renderable_text, self.text_pos)


class App:
    _spn_values = (0.0005, 0.0007, 0.001, 0.0015, 0.003, 0.006, 0.1, 1, 2)
    _geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    _apikey = "40d1649f-0493-4b70-98ba-98533de7710b"

    def __init__(self):
        self.spn = 0.001
        self.focus = [37.53, 55.7]
        self.view_mode = "map"
        self.map = self._load_map()
        self.mode_switch = MapModeSwitch(0, 5, 100, 40)
        self.search_field = InputField(105, 5, 350, 40)
        self.search_field.activate()
        self.clear_search_field_btn = Button(460, 5, 40, 40, 'C', command=self.search_field.clear)
        self.search_btn = Button(505, 5, 90, 40, "Искать", command=self._search_object_by_address)
        self.move_speed = 0.1

    def _load_map(self, labels=()):
        params = {
            "ll": format_coords(*self.focus),
            "spn": format_coords(self.spn, self.spn),
            "l": self.view_mode,
            "pt": '~'.join(format_coords(*label) + ",pm2dgl" for label in labels)
        }
        response = requests.get(MAP_API_SERVER, params=params)
        with open("map.png", "wb") as f:
            f.write(response.content)
        return pygame.transform.scale(pygame.image.load("map.png"), SIZE)

    def update(self, labels=()):
        self.map = self._load_map(labels)

    def _search_object_by_address(self):
        address = self.search_field.get_text()
        request_params = {
            "apikey": self._apikey,
            "geocode": address,
            "format": "json"}
        response = requests.get(self._geocoder_api_server, params=request_params)
        if response:
            json_response = response.json()
            try:
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                coords = make_coords(toponym["Point"]["pos"])
                self.focus = coords
                self.update([coords])
            except IndexError:  # если ничего не нашлось
                return

    def _change_spn(self, direction):
        try:
            assert self.spn != self._spn_values[0] or direction == 1
            self.spn = self._spn_values[self._spn_values.index(self.spn) + direction]
            self.update()
        except IndexError:  # уже установлено максимальное значение
            return
        except AssertionError:  # уже установлено минимальное значение
            return

    def _change_focus(self, key):
        step = [0, 0]
        if key == pygame.K_UP:
            step[1] = self.move_speed * self.spn
        elif key == pygame.K_DOWN:
            step[1] = -self.move_speed * self.spn
        elif key == pygame.K_LEFT:
            step[0] = -self.move_speed * self.spn
        elif key == pygame.K_RIGHT:
            step[0] = self.move_speed * self.spn
        self.focus[0] += step[0]
        self.focus[1] += step[1]
        self.update()

    def _click_buttons(self, mouse_pos):
        click_rect = pygame.Rect(*mouse_pos, 1, 1)
        if click_rect.colliderect(self.search_field):
            self.search_field.activate()
            return
        else:
            self.search_field.deactivate()
        if click_rect.colliderect(self.mode_switch):
            view_mode = self.mode_switch.click()
            self.view_mode = view_mode
            self.update()
            return
        if click_rect.colliderect(self.clear_search_field_btn):
            self.clear_search_field_btn.click()
        if click_rect.colliderect(self.search_btn.rect):
            self.search_btn.click()

    def on_click(self, mouse_pos):
        self._click_buttons(mouse_pos)

    def on_keypress(self, event):
        key = event.key
        if key == pygame.K_PAGEDOWN:
            self._change_spn(1)
        elif key == pygame.K_PAGEUP:
            self._change_spn(-1)
        elif key in ARROW_BUTTONS:
            self._change_focus(key)
        elif self.search_field.input_active:
            if self.search_field.input(event):
                self._search_object_by_address()

    def render_buttons(self, surface):
        self.mode_switch.render(surface)
        self.search_field.render(surface)
        self.clear_search_field_btn.render(surface)
        self.search_btn.render(surface)

    def render(self, surface):
        self.render_buttons(surface)
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
                app.on_keypress(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                app.on_click(event.pos)
            elif event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)
        app.render(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
