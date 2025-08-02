import pygame
import sys

WIDTH, HEIGHT = 800, 600


class GameOverScreen:
    def __init__(self, score):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game Over")
        self.score = score

        # Load or create image
        try:
            self.image = pygame.image.load("background.png").convert_alpha()
        except:
            self.image = pygame.Surface((400, 300))
            self.image.fill((40, 40, 60))
            font = pygame.font.SysFont(None, 48)
            text = font.render("IMAGE NOT FOUND", True, (220, 220, 220))
            self.image.blit(text, text.get_rect(center=(200, 150)))

        # Position image
        self.img_rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        # Create fonts
        self.title_font = pygame.font.SysFont(None, 80)
        self.score_font = pygame.font.SysFont(None, 60)
        self.message_font = pygame.font.SysFont(None, 36)

        # Create text surfaces
        self.title_surf = self.title_font.render("GAME OVER", True, (220, 50, 50))
        self.score_surf = self.score_font.render(
            f"Final Score: {self.score}", True, (240, 240, 100)
        )
        self.message_surf = self.message_font.render("Press ESC to exit", True, (180, 180, 220))

        # Position text
        self.title_rect = self.title_surf.get_rect(center=(WIDTH // 2, 100))
        self.score_rect = self.score_surf.get_rect(center=(WIDTH // 2, 180))
        self.message_rect = self.message_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50))

        self.run()

    def run(self):
        clock = pygame.time.Clock
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Solid background
            self.screen.fill((10, 10, 40))

            # Draw image with border
            pygame.draw.rect(self.screen, (100, 100, 140), self.img_rect.inflate(4, 4), 2)
            self.screen.blit(self.image, self.img_rect)

            # Draw text directly
            self.screen.blit(self.title_surf, self.title_rect)
            self.screen.blit(self.score_surf, self.score_rect)
            self.screen.blit(self.message_surf, self.message_rect)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
