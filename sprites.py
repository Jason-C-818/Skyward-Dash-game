import pygame
import sys
import random
import pygame.mixer

class SkywardDashGame:
    # Constants
    BIRD_HEIGHT = 70
    BIRD_WIDTH = 120
    SMALL_BIRD_HEIGHT = 50
    SMALL_BIRD_WIDTH = 90
    OBSTACLE_WIDTH = 140
    OBSTACLE_HEIGHT = 300
    GAP_SIZE = 230
    GRAVITY = 1.0
    JUMP_STRENGTH = 10
    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 800
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    SHRINK_DURATION = 5000
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    MISSILE_WIDTH = 40
    MISSILE_HEIGHT = 20

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()  # Initialize mixer with default values
        except pygame.error:
            print("Warning: Audio device may not be available.")
            # Handle case where audio initialization fails

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption('Skyward Dash')

        self.load_assets()
        self.loading_screen()
        self.intro_screen()

    def load_assets(self): #loading all the assets
        self.background_image = pygame.image.load('img/forest.jpg')
        self.background_image = pygame.transform.scale(self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.background_image_intro = self.background_image
        self.background_image_game_over = pygame.image.load('img/gameover.jpg')
        self.background_image_game_over = pygame.transform.scale(self.background_image_game_over, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.powerup_image = pygame.image.load('img/cookie.png')
        self.powerup_image = pygame.transform.scale(self.powerup_image, (30, 30))
        self.loading_image = pygame.image.load('img/loading.jpg')
        self.loading_image = pygame.transform.scale(self.loading_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.bird_image = pygame.image.load('img/bird.png')
        self.bird_image = pygame.transform.scale(self.bird_image, (self.BIRD_WIDTH, self.BIRD_HEIGHT))
        self.small_bird_image = pygame.transform.scale(self.bird_image, (self.SMALL_BIRD_WIDTH, self.SMALL_BIRD_HEIGHT))
        self.obstacle_image = pygame.image.load('img/pillar.png')
        self.obstacle_image = pygame.transform.scale(self.obstacle_image, (self.OBSTACLE_WIDTH, self.OBSTACLE_HEIGHT))
        

        self.background_music = pygame.mixer.Sound('sound/background_music.ogg')
        self.hit_sound = pygame.mixer.Sound('sound/collison.ogg')
        self.collect_sound = pygame.mixer.Sound('sound/collect.ogg')
        self.level_up_sound = pygame.mixer.Sound('sound/level_up.ogg')
        self.game_over_music = pygame.mixer.Sound('sound/game_over.ogg')
        self.jump_sound = pygame.mixer.Sound('sound/jump.ogg')

    class Bird(pygame.sprite.Sprite): #bird class
        def __init__(self, game):
            super().__init__()
            self.game = game
            self.jump_sound = game.jump_sound
            self.image = game.bird_image
            self.rect = self.image.get_rect()
            self.rect.center = (100, game.SCREEN_HEIGHT // 2)
            self.velocity = 0
            self.shrunk = False
            self.shrink_start_time = 0

        def update(self): #bird movement
            self.velocity += self.game.GRAVITY
            self.rect.y += int(self.velocity)

            if self.rect.top < 0:
                self.rect.top = 0
                self.velocity = 0

            if self.rect.bottom > self.game.SCREEN_HEIGHT:
                self.rect.bottom = self.game.SCREEN_HEIGHT
                self.velocity = 0

            if self.shrunk and pygame.time.get_ticks() - self.shrink_start_time > self.game.SHRINK_DURATION:
                self.reset_size()

        def jump(self):
            self.velocity = -self.game.JUMP_STRENGTH
            self.jump_sound.play()

        def shrink(self):
            self.image = self.game.small_bird_image
            self.rect = self.image.get_rect(center=self.rect.center)
            self.shrunk = True
            self.shrink_start_time = pygame.time.get_ticks()

        def reset_size(self):
            self.image = self.game.bird_image
            self.rect = self.image.get_rect(center=self.rect.center)
            self.shrunk = False

    class HighScoreManager: #highscore manager class
        def __init__(self):
            self.high_score = 0

        def update(self, score):
            if score > self.high_score:
                self.high_score = score

        def get_high_score(self):
            return self.high_score

    class PowerUp(pygame.sprite.Sprite): #powers up class
        def __init__(self, game, x):
            super().__init__()
            self.game = game
            self.collect_sound = game.collect_sound
            self.image = game.powerup_image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = random.randint(0, game.SCREEN_HEIGHT - 30)

        def activate(self, bird):
            bird.shrink()
            self.collect_sound.play()

        def update(self):
            self.rect.x -= 5
            if self.rect.right < 0:
                self.kill()

    class ScoreKeeper: #score keeper class
        def __init__(self, game, high_score_manager):
            self.game = game
            self.font = pygame.font.Font(None, 36)
            self.score = 0
            self.high_score_manager = high_score_manager

        def update(self):
            self.score += 1

        def reset(self):
            self.high_score_manager.update(self.score)
            self.score = 0

        def render(self):
            text = self.font.render(f'Score: {self.score}', True, self.game.WHITE)
            self.game.screen.blit(text, (10, 10))

    class Missile(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface([MISSILE_WIDTH, MISSILE_HEIGHT])
            self.image.fill((255, 0, 0))  # Red color
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

        def update(self):
            self.rect.x -= 10
            if self.rect.x < -MISSILE_WIDTH:
                self.kill()


    class Obstacle(pygame.sprite.Sprite): #obstacle class
        def __init__(self, game, x, y, is_top):
            super().__init__()
            self.game = game
            self.image = game.obstacle_image
            self.rect = self.image.get_rect()
            self.rect.x = x
            if is_top:
                self.rect.bottom = y - game.GAP_SIZE // 2
            else:
                self.rect.top = y + game.GAP_SIZE // 2

        def update(self):
            self.rect.x -= 5
            if self.rect.right < 0:
                self.kill()

    def draw_button(self, text, x, y, width, height):
        font = pygame.font.Font(None, 36)
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.BLUE, button_rect)
        text_surf = font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        return button_rect

    def button_clicked(self, button_rect, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if button_rect.collidepoint(event.pos):
                return True
        return False

    def loading_screen(self):
        loading = True
        start_time = pygame.time.get_ticks()

        while loading:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(self.loading_image, (0, 0))
            font = pygame.font.Font(None, 48)
            text = font.render('Welcome to Skyward Dash', True, (255, 255, 255))
            self.screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, self.SCREEN_HEIGHT // 2 - text.get_height() // 2))

            pygame.display.flip()

            if pygame.time.get_ticks() - start_time > 3000:
                loading = False

        self.background_music.play(-1)

    def game(self, speed_multiplier):
        bird = self.Bird(self)
        high_score_manager = self.HighScoreManager()
        score_keeper = self.ScoreKeeper(self, high_score_manager)
        all_sprites = pygame.sprite.Group()
        all_sprites.add(bird)
        obstacles = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        missiles = pygame.sprite.Group()

        clock = pygame.time.Clock()
        running = True

        # Obstacle spawn timer
        obstacle_timer = 0
        obstacle_interval = 1500 // speed_multiplier  # Milliseconds between obstacles

        # Power-up spawn timer
        powerup_timer = 0
        powerup_interval = 8000  # Milliseconds between power-ups

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()

            all_sprites.update()

            # Increment the timers
            obstacle_timer += clock.get_time()
            powerup_timer += clock.get_time()

            # Check if it's time to spawn a new obstacle
            if obstacle_timer >= obstacle_interval:
                y = random.randint(self.GAP_SIZE, self.SCREEN_HEIGHT - self.GAP_SIZE)
                obstacle_top = self.Obstacle(self, self.SCREEN_WIDTH, y, True)
                obstacle_bottom = self.Obstacle(self, self.SCREEN_WIDTH, y, False)
                obstacles.add(obstacle_top)
                obstacles.add(obstacle_bottom)
                all_sprites.add(obstacle_top)
                all_sprites.add(obstacle_bottom)
                obstacle_timer = 0  # Reset the timer

            # Check if it's time to spawn a new power-up
            if powerup_timer >= powerup_interval:
                while True:
                    powerup_x = self.SCREEN_WIDTH
                    powerup_y = random.randint(0, self.SCREEN_HEIGHT - 30)
                    collision = False

                    for obstacle in obstacles:
                        if (
                            powerup_x < obstacle.rect.right + 100 and
                            powerup_x > obstacle.rect.left - 100 and
                            powerup_y < obstacle.rect.bottom + 100 and
                            powerup_y > obstacle.rect.top - 100
                        ):
                            collision = True
                            break

                    if not collision:
                        powerup = self.PowerUp(self, powerup_x)
                        powerup.rect.y = powerup_y
                        powerups.add(powerup)
                        all_sprites.add(powerup)
                        break

                powerup_timer = 0  # Reset the timer

            # Collision detection (check for pixel-perfect collision)
            if self.check_pixel_collision(bird, obstacles):
                self.hit_sound.play()
                self.background_music.stop()
                running = False

            powerup_collected = pygame.sprite.spritecollideany(bird, powerups)
            if powerup_collected:
                powerup_collected.activate(bird)
                powerup_collected.kill()

            score_keeper.update()

            self.screen.blit(self.background_image, (0, 0))
            all_sprites.draw(self.screen)
            score_keeper.render()
            pygame.display.flip()

            clock.tick(30 * speed_multiplier)

            if score_keeper.score >= 1000:
                running = False
                self.level_up_screen(speed_multiplier)

        self.game_over_screen(score_keeper)

    def check_pixel_collision(self, bird, obstacles):
        """
        Checks for pixel-perfect collision between the bird and any obstacle.
        """
        bird_mask = pygame.mask.from_surface(bird.image)
        for obstacle in obstacles:
            obstacle_mask = pygame.mask.from_surface(obstacle.image)
            offset = (obstacle.rect.x - bird.rect.x, obstacle.rect.y - bird.rect.y)
            if bird_mask.overlap(obstacle_mask, offset):
                return True
        return False

    class GameOverScreen: #game over screen class
        def __init__(self, game, score_keeper):
            self.game = game
            self.score_keeper = score_keeper
            self.font = pygame.font.Font(None, 36)

        def display(self):
            game_over = True
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.game.button_clicked(restart_button, event):
                            game_over = False
                            self.game.background_music.play(-1)
                            self.game.game(1)
                        elif self.game.button_clicked(back_to_home_button, event):
                            game_over = False
                            self.game.background_music.play(-1)
                            self.game.intro_screen()
                        elif self.game.button_clicked(exit_button, event):
                            pygame.quit()
                            sys.exit()

                self.game.screen.blit(self.game.background_image_game_over, (0, 0))
                text = self.font.render('Game Over', True, (255, 255, 255))
                self.game.screen.blit(text, (self.game.SCREEN_WIDTH // 2 - text.get_width() // 2, self.game.SCREEN_HEIGHT // 4))

                # Display current score and high score
                score_text = self.font.render(f'Score: {self.score_keeper.score}', True, (255, 255, 255))
                self.game.screen.blit(score_text, (self.game.SCREEN_WIDTH // 2 - score_text.get_width() // 2, self.game.SCREEN_HEIGHT // 2))

                high_score_text = self.font.render(f'High Score: {self.score_keeper.high_score_manager.get_high_score()}', True, (255, 255, 255))
                self.game.screen.blit(high_score_text, (self.game.SCREEN_WIDTH // 2 - text.get_width() // 2, self.game.SCREEN_HEIGHT // 3))
#all the buttons
                restart_button = self.game.draw_button('Restart', self.game.SCREEN_WIDTH // 2 - self.game.BUTTON_WIDTH // 2, self.game.SCREEN_HEIGHT // 2 - self.game.BUTTON_HEIGHT // 2, self.game.BUTTON_WIDTH, self.game.BUTTON_HEIGHT)
                back_to_home_button = self.game.draw_button('Back to Home', self.game.SCREEN_WIDTH // 2 - self.game.BUTTON_WIDTH // 2, self.game.SCREEN_HEIGHT // 2 + self.game.BUTTON_HEIGHT, self.game.BUTTON_WIDTH, self.game.BUTTON_HEIGHT)
                exit_button = self.game.draw_button('Exit', self.game.SCREEN_WIDTH // 2 - self.game.BUTTON_WIDTH // 2, self.game.SCREEN_HEIGHT // 2 + 2.5 * self.game.BUTTON_HEIGHT, self.game.BUTTON_WIDTH, self.game.BUTTON_HEIGHT)

                pygame.display.flip()

    def game_over_screen(self, score_keeper):
        self.game_over_music.play()

        game_over_screen = self.GameOverScreen(self, score_keeper)
        game_over_screen.display()

    def level_up_screen(self, current_speed_multiplier):
        self.level_up_sound.play()
        level_up = True
        while level_up:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_clicked(advance_button, event):
                        level_up = False
                        self.game(current_speed_multiplier + 1)
                    elif self.button_clicked(exit_button, event):
                        pygame.quit()
                        sys.exit()

            self.screen.fill(self.WHITE)
            font = pygame.font.Font(None, 36)
            text = font.render('Level Up!', True, (0, 0, 0))
            self.screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, self.SCREEN_HEIGHT // 4))

            advance_button = self.draw_button('Advance', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 - self.BUTTON_HEIGHT // 2, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            exit_button = self.draw_button('Exit', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 + self.BUTTON_HEIGHT, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

            pygame.display.flip()

    def instructions_screen(self):
        instructions = True
        while instructions:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_clicked(back_button, event):
                        instructions = False
                        self.intro_screen()

            self.screen.fill(self.WHITE)
            font = pygame.font.Font(None, 36)
            lines = [
                "How to Play:",
                "1. Press SPACE to jump.",
                "2. Avoid obstacles.",
                "3. Collect cookie to shrink.",
                "4. Survive as long as possible to score points.",
                "5. Keep reaching the score 1000 in order to move to the next level."
            ]
            for i, line in enumerate(lines):
                text = font.render(line, True, (0, 0, 0))
                self.screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, self.SCREEN_HEIGHT // 4 + i * 40))

            back_button = self.draw_button('Back', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 2 * self.BUTTON_HEIGHT, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            pygame.display.flip()

    def intro_screen(self):
        intro = True
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_clicked(start_button, event):
                        intro = False
                        self.game(1)
                    elif self.button_clicked(fast_button, event):
                        intro = False
                        self.game(2)
                    elif self.button_clicked(how_to_play_button, event):
                        intro = False
                        self.instructions_screen()
                    elif self.button_clicked(exit_button, event):
                        pygame.quit()
                        sys.exit()

            self.screen.blit(self.background_image_intro, (0, 0))
            font = pygame.font.Font(None, 45)
            text = font.render('Skyward Dash', True, (255, 255, 255))
            self.screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, self.SCREEN_HEIGHT // 4))

            start_button = self.draw_button('Start Game', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 - self.BUTTON_HEIGHT // 2, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            fast_button = self.draw_button('Harder Game', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 + self.BUTTON_HEIGHT, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            how_to_play_button = self.draw_button('How to Play', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 2.5 * self.BUTTON_HEIGHT, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            exit_button = self.draw_button('Exit', self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 4 * self.BUTTON_HEIGHT, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

            pygame.display.flip()

SkywardDashGame()

