
# Run the game
import pygame
import sys
import random
from sprites import Bird, Obstacle, PowerUp, ScoreKeeper, 

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Skyward Dash')

# Game function
def game():
    bird = Bird()
    score_keeper = ScoreKeeper()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(bird)
    all_sprites.add(score_keeper)
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        all_sprites.update()

        # Add obstacles and power-ups
        if random.randint(1, 100) == 1:
            obstacle_top = Obstacle(SCREEN_WIDTH)
            obstacle_bottom = Obstacle(SCREEN_WIDTH)
            obstacle_bottom.rect.y = obstacle_top.rect.bottom + Obstacle.GAP_SIZE
            obstacles.add(obstacle_top)
            obstacles.add(obstacle_bottom)
            all_sprites.add(obstacle_top)
            all_sprites.add(obstacle_bottom)
        if random.randint(1, 500) == 1:
            powerup = PowerUp(SCREEN_WIDTH)
            powerups.add(powerup)
            all_sprites.add(powerup)

        # Check collisions
        if pygame.sprite.spritecollideany(bird, obstacles, missiles) or pygame.sprite.spritecollideany(bird, missiles):

            running = False

        # Check power-up collection
        powerup_collected = pygame.sprite.spritecollideany(bird, powerups)
        if powerup_collected:
            powerup_collected.activate(bird)
            powerup_collected.kill()

        # Drawing
        screen.fill(WHITE)
        all_sprites.draw(screen)
        score_keeper.render(screen)
        pygame.display.flip()

        # Update the clock
        clock.tick(30)

# Introduction screen
def intro_screen():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    intro = False

        screen.fill(WHITE)
        font = pygame.font.Font(None, 36)
        text = font.render('Press SPACE to Start', True, (0, 0, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()



# Run the game
intro_screen()
game()
