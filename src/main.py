"""Galaxy Flare: offline arcade shooter built with Pygame."""
from pathlib import Path
from random import Random

import pygame


WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_SPEED = 420
LASER_SPEED = 760
FIRE_INTERVAL = 0.22
SPAWN_INTERVAL = 0.75
INITIAL_LIVES = 3
ASSET_DIR = Path(__file__).resolve().parent.parent / "img"


def load_image(relative, size=None):
    path = ASSET_DIR / relative
    if not path.is_file():
        raise FileNotFoundError(f"Required game asset is missing: {path}")
    image = pygame.image.load(str(path)).convert_alpha()
    return pygame.transform.smoothscale(image, size) if size else image


class GalaxyFlare:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Galaxy Flare")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 38)
        self.large_font = pygame.font.Font(None, 90)
        self.background = load_image("galaxy.png", (WIDTH, HEIGHT))
        self.space = load_image("space.png", (WIDTH, HEIGHT))
        self.player_image = load_image("player.png", (80, 88))
        self.meteor_image = load_image("meteors/m1.png", (64, 64))
        self.laser_image = load_image("laser.png", (18, 44))
        self.star1 = load_image("lightStar1.png", (30, 30))
        self.star2 = load_image("lightStar2.png", (20, 20))
        self.rng = Random()
        self.stars = [
            (self.star1 if idx % 2 else self.star2,
             self.rng.randrange(WIDTH), self.rng.randrange(HEIGHT))
            for idx in range(65)
        ]
        self.reset()

    def reset(self):
        self.player_position = pygame.Vector2(
            WIDTH / 2 - self.player_image.get_width() / 2,
            HEIGHT - self.player_image.get_height() - 24,
        )
        self.lasers = []
        self.meteors = []
        self.score = 0
        self.lives = INITIAL_LIVES
        self.elapsed = 0.0
        self.fire_cooldown = 0.0
        self.spawn_cooldown = SPAWN_INTERVAL
        self.invulnerable_for = 0.0
        self.game_over = False

    def spawn_meteor(self):
        width = self.meteor_image.get_width()
        self.meteors.append({
            "position": pygame.Vector2(
                self.rng.randrange(0, WIDTH - width + 1),
                -self.meteor_image.get_height()
            ),
            "speed": self.rng.uniform(150, 250) + min(self.elapsed * 3, 220),
        })

    def fire(self):
        if self.fire_cooldown > 0 or self.game_over:
            return
        self.lasers.append(pygame.Vector2(
            self.player_position.x +
            (self.player_image.get_width() - self.laser_image.get_width()) / 2,
            self.player_position.y - self.laser_image.get_height(),
        ))
        self.fire_cooldown = FIRE_INTERVAL

    def update(self, seconds, keys):
        if self.game_over:
            return

        self.elapsed += seconds
        self.fire_cooldown = max(0.0, self.fire_cooldown - seconds)
        self.invulnerable_for = max(0.0, self.invulnerable_for - seconds)
        direction = pygame.Vector2(
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) -
            int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            int(keys[pygame.K_DOWN] or keys[pygame.K_s]) -
            int(keys[pygame.K_UP] or keys[pygame.K_w])
        )
        if direction.length_squared():
            direction.normalize_ip()
            self.player_position += direction * PLAYER_SPEED * seconds

        self.player_position.x = max(
            0, min(self.player_position.x, WIDTH - self.player_image.get_width())
        )
        self.player_position.y = max(
            0, min(self.player_position.y, HEIGHT - self.player_image.get_height())
        )

        if keys[pygame.K_SPACE]:
            self.fire()

        self.spawn_cooldown -= seconds
        while self.spawn_cooldown <= 0:
            self.spawn_meteor()
            self.spawn_cooldown += max(
                0.25, SPAWN_INTERVAL - self.elapsed * 0.004
            )

        for laser in self.lasers:
            laser.y -= LASER_SPEED * seconds
        self.lasers = [
            laser for laser in self.lasers
            if laser.y + self.laser_image.get_height() >= 0
        ]

        for meteor in self.meteors:
            meteor["position"].y += meteor["speed"] * seconds

        # Each laser destroys at most one meteor; removing objects by index
        # prevents a collision from granting duplicate points.
        remaining_meteors = []
        for meteor in self.meteors:
            meteor_rect = self.meteor_image.get_rect(
                topleft=(round(meteor["position"].x),
                         round(meteor["position"].y))
            )
            hit_index = next(
                (idx for idx, laser in enumerate(self.lasers)
                 if self.laser_image.get_rect(topleft=(
                     round(laser.x), round(laser.y)
                 )).colliderect(meteor_rect)),
                None
            )
            if hit_index is not None:
                self.lasers.pop(hit_index)
                self.score += 10
                continue

            if meteor_rect.top >= HEIGHT:
                continue

            player_rect = self.player_image.get_rect(
                topleft=(round(self.player_position.x),
                         round(self.player_position.y))
            )
            if self.invulnerable_for <= 0 and meteor_rect.colliderect(player_rect):
                self.lives -= 1
                self.invulnerable_for = 0.8
                if self.lives <= 0:
                    self.game_over = True
                continue
            remaining_meteors.append(meteor)
        self.meteors = remaining_meteors

    def draw(self):
        self.screen.blit(self.space, (0, 0))
        self.screen.blit(self.background, (0, 0))
        for image, x, y in self.stars:
            self.screen.blit(image, (x, y))
        for laser in self.lasers:
            self.screen.blit(self.laser_image, (round(laser.x), round(laser.y)))
        for meteor in self.meteors:
            self.screen.blit(self.meteor_image, (
                round(meteor["position"].x),
                round(meteor["position"].y)
            ))
        # Flash briefly after a collision to make invulnerability visible.
        if self.invulnerable_for <= 0 or int(self.invulnerable_for * 12) % 2 == 0:
            self.screen.blit(self.player_image, (
                round(self.player_position.x),
                round(self.player_position.y)
            ))

        score_text = self.font.render(f"Score: {self.score}", True, "white")
        lives_text = self.font.render(f"Lives: {self.lives}", True, "white")
        self.screen.blit(score_text, (24, 20))
        self.screen.blit(lives_text, (WIDTH - lives_text.get_width() - 24, 20))
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 9, 30, 205))
            self.screen.blit(overlay, (0, 0))
            headline = self.large_font.render("GAME OVER", True, "white")
            hint = self.font.render(
                f"Final score: {self.score}    R = restart    Esc = exit",
                True, "white"
            )
            self.screen.blit(headline, headline.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 55)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        pygame.display.flip()

    def run(self):
        running = True
        try:
            while running:
                # Cap unusually long frames so a suspended game does not
                # teleport the player or spawn dozens of meteors on resume.
                seconds = min(self.clock.tick(FPS) / 1000.0, 0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_r and self.game_over:
                            self.reset()
                if not running:
                    break
                self.update(seconds, pygame.key.get_pressed())
                self.draw()
        finally:
            pygame.quit()


if __name__ == "__main__":
    GalaxyFlare().run()
