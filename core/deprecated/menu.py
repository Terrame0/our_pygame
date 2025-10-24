
import sys
from core.application import Application


pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
DARK_BLUE = (0, 30, 60)
LIGHT_BLUE = (0, 60, 120)
BLACK = (0, 0, 0)

FONT = pygame.font.Font("Elfboyclassic.ttf", 30)
TITLE_FONT = pygame.font.Font("BlockwayPixies.ttf", 60)


class Button:
    def __init__(self, text, pos, callback):
        self.text = text
        self.pos = pos
        self.callback = callback
        self.rect = pygame.Rect(pos[0], pos[1], 260, 50)
        self.hovered = False

    def draw(self, screen):
        pygame.draw.rect(screen, DARK_BLUE, self.rect)
        pygame.draw.rect(screen, LIGHT_BLUE, self.rect, 2)
        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            glow_text = FONT.render(self.text, True, (100, 100, 100))
            screen.blit(glow_text, (self.rect.x + 20 + offset[0], self.rect.y + 10 + offset[1]))
        label = FONT.render(self.text, True, WHITE)
        screen.blit(label, (self.rect.x + 20, self.rect.y + 10))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def handle_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)


class Dropdown:
    def __init__(self, text, pos, options, on_select):
        self.main_button = Button(text, pos, self.toggle)
        self.options = options
        self.on_select = on_select
        self.expanded = False
        self.buttons = []
        self.create_option_buttons(pos)

    def create_option_buttons(self, pos):
        self.buttons.clear()
        for i, (label, res) in enumerate(self.options):
            y = pos[1] + 60 + i * 50
            self.buttons.append(Button(label, (pos[0], y), lambda res=res: self.select(res)))

    def toggle(self):
        self.expanded = not self.expanded

    def select(self, resolution):
        self.expanded = False
        self.on_select(resolution)

    def draw(self, screen):
        self.main_button.draw(screen)
        if self.expanded:
            for btn in self.buttons:
                btn.draw(screen)

    def handle_click(self, mouse_pos):
        if self.main_button.is_clicked(mouse_pos):
            self.toggle()
            return True
        if self.expanded:
            for btn in self.buttons:
                if btn.is_clicked(mouse_pos):
                    btn.callback()
                    return True
        return False


class VolumeSlider:
    def __init__(self, pos, size):
        self.rect = pygame.Rect(pos, size)
        self.handle_radius = 10
        self.value = 0.5

    def draw(self, screen):
        pygame.draw.rect(screen, LIGHT_BLUE, self.rect)
        handle_x = self.rect.x + int(self.value * self.rect.width)
        handle_y = self.rect.centery
        pygame.draw.circle(screen, WHITE, (handle_x, handle_y), self.handle_radius)
        percent_text = FONT.render(f"Volume: {int(self.value * 100)}%", True, WHITE)
        screen.blit(percent_text, (self.rect.x, self.rect.y - 35))

    def update_from_mouse(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            rel_x = mouse_pos[0] - self.rect.x
            self.value = max(0.0, min(1.0, rel_x / self.rect.width))
            pygame.mixer.music.set_volume(self.value)


class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock
        self.running = True
        self.in_settings = False
        self.sound_on = True
        self.fullscreen = False
        self.volume = 0.5
        self.resolution = screen.get_size()

        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

        self.background_image = pygame.image.load("background.png").convert()
        self.background = self.scale_background(self.background_image, self.resolution)

        self.button_x_ratio = 0.4625
        self.button_y_ratios = [0.25, 0.3667, 0.4833]
        self.settings_y_ratios = [0.1333, 0.2333, 0.9]
        self.slider_y_ratio = 0.39
        self.dropdown_y_ratio = 0.45

        self.volume_slider = VolumeSlider(
            (
                int(self.button_x_ratio * self.resolution[0]),
                int(self.slider_y_ratio * self.resolution[1]),
            ),
            (260, 20),
        )
        self.volume_slider.value = self.volume

        self.main_buttons = [
            Button(
                "Play",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.button_y_ratios[0] * self.resolution[1]),
                ),
                self.play_game,
            ),
            Button(
                "Settings",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.button_y_ratios[1] * self.resolution[1]),
                ),
                self.open_settings,
            ),
            Button(
                "Exit",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.button_y_ratios[2] * self.resolution[1]),
                ),
                self.exit_game,
            ),
        ]

        self.settings_buttons = [
            Button(
                "Sound: On",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.settings_y_ratios[0] * self.resolution[1]),
                ),
                self.toggle_sound,
            ),
            Button(
                "Fullscreen: Off",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.settings_y_ratios[1] * self.resolution[1]),
                ),
                self.toggle_fullscreen,
            ),
            Button(
                "Back",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.settings_y_ratios[2] * self.resolution[1]),
                ),
                self.close_settings,
            ),
        ]

        self.resolution_dropdown = Dropdown(
            "Resolution",
            (
                int(self.button_x_ratio * self.resolution[0]),
                int(self.dropdown_y_ratio * self.resolution[1]),
            ),
            [
                ("640x480", (640, 480)),
                ("1280x720", (1280, 720)),
                ("1920x1080", (1920, 1080)),
                ("2560x1440", (2560, 1440)),
            ],
            self.set_resolution,
        )

    def scale_background(self, image, screen_size):
        img_width, img_height = image.get_size()
        screen_width, screen_height = screen_size
        scale = max(screen_width / img_width, screen_height / img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        scaled_image = pygame.transform.smoothscale(image, new_size)
        bg = pygame.Surface(screen_size)
        bg.blit(
            scaled_image,
            scaled_image.get_rect(center=(screen_width // 2, screen_height // 2)),
        )
        return bg

    def play_game(self):
        app_instance = Application()
        app_instance.run()

    def open_settings(self):
        self.in_settings = True

    def close_settings(self):
        self.in_settings = False

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.settings_buttons[0].text = f"Sound: {'On' if self.sound_on else 'Off'}"

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode(self.resolution, flags)
        self.background = self.scale_background(self.background_image, self.resolution)
        self.settings_buttons[1].text = f"Fullscreen: {'On' if self.fullscreen else 'Off'}"

    def set_resolution(self, new_res):
        self.resolution = new_res
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode(self.resolution, flags)

        self.volume_slider = VolumeSlider(
            (
                int(self.button_x_ratio * self.resolution[0]),
                int(self.slider_y_ratio * self.resolution[1]),
            ),
            (260, 20),
        )
        self.volume_slider.value = self.volume

        self.main_buttons = [
            Button(
                "Play",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.button_y_ratios[0] * self.resolution[1]),
                ),
                self.play_game,
            ),
            Button(
                "Settings",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.button_y_ratios[1] * self.resolution[1]),
                ),
                self.open_settings,
            ),
            Button(
                "Exit",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.button_y_ratios[2] * self.resolution[1]),
                ),
                self.exit_game,
            ),
        ]

        self.settings_buttons = [
            Button(
                "Sound: On",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.settings_y_ratios[0] * self.resolution[1]),
                ),
                self.toggle_sound,
            ),
            Button(
                "Fullscreen: Off",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.settings_y_ratios[1] * self.resolution[1]),
                ),
                self.toggle_fullscreen,
            ),
            Button(
                "Back",
                (
                    int(self.button_x_ratio * self.resolution[0]),
                    int(self.settings_y_ratios[2] * self.resolution[1]),
                ),
                self.close_settings,
            ),
        ]

        self.resolution_dropdown = Dropdown(
            "Resolution",
            (
                int(self.button_x_ratio * self.resolution[0]),
                int(self.dropdown_y_ratio * self.resolution[1]),
            ),
            [
                ("640x480", (640, 480)),
                ("1280x720", (1280, 720)),
                ("1920x1080", (1920, 1080)),
                ("2560x1440", (2560, 1440)),
            ],
            self.set_resolution,
        )

        self.background = self.scale_background(self.background_image, self.resolution)

    def exit_game(self):
        self.running = False
        sys.exit()

    def run(self):
        while self.running:
            self.screen.blit(self.background, (0, 0))

            title_text = TITLE_FONT.render("OnemanNoman", True, WHITE)
            for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                glow = TITLE_FONT.render("OnemanNoman", True, LIGHT_BLUE)
                self.screen.blit(
                    glow,
                    (
                        self.resolution[0] // 2 - title_text.get_width() // 2 + offset[0],
                        50 + offset[1],
                    ),
                )
            self.screen.blit(
                title_text, (self.resolution[0] // 2 - title_text.get_width() // 2, 50)
            )

            buttons = self.settings_buttons if self.in_settings else self.main_buttons

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.in_settings:
                        if self.resolution_dropdown.handle_click(event.pos):
                            continue
                        self.volume_slider.update_from_mouse(event.pos)
                    for button in buttons:
                        if button.is_clicked(event.pos):
                            button.callback()
                elif event.type == pygame.MOUSEMOTION:
                    for button in buttons:
                        button.handle_hover(event.pos)

            for button in buttons:
                button.draw(self.screen)

            if self.in_settings:
                self.volume_slider.draw(self.screen)
                self.resolution_dropdown.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)
