import pygame
import random
import os

pygame.init()

# Constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Game")

# Load sprites
RUNNING = [
    pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png")),
]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png")),
]
SMALL_CACTUS = [
    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png")),
]
LARGE_CACTUS = [
    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png")),
]
PTERODACTYL = [
    pygame.image.load(os.path.join("Assets/Pterodactyl", "Pterodactyl1.png")),
    pygame.image.load(os.path.join("Assets/Pterodactyl", "Pterodactyl2.png")),
]
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# Global variables
points = 0
game_speed = 20
high_score = 0
obstacles = []
paused = False
FPS = 30

# Load high score from file
try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read().strip())
except (FileNotFoundError, ValueError, OSError):
    high_score = 0

# Classes
class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self, run_img, jump_img, duck_img, is_cactus=False, is_pterodactyl=False):
        self.is_cactus = is_cactus
        self.is_pterodactyl = is_pterodactyl
        # Mirror pterodactyl images if selected
        if self.is_pterodactyl:
            self.run_img = [pygame.transform.flip(img, True, False) for img in run_img]
            self.jump_img = pygame.transform.flip(jump_img, True, False)
            self.duck_img = [pygame.transform.flip(img, True, False) for img in duck_img]
        else:
            self.run_img = run_img
            self.jump_img = jump_img
            self.duck_img = duck_img
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        elif self.dino_run:
            self.run()
        elif self.dino_jump:
            self.jump()
        if not self.is_cactus and self.step_index >= 10:
            self.step_index = 0
        if (userInput[pygame.K_UP] or userInput[pygame.K_w]) and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif (userInput[pygame.K_DOWN] or userInput[pygame.K_s]) and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not self.dino_jump and not userInput[pygame.K_DOWN] and not userInput[pygame.K_s]:
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False
        mouse = pygame.mouse.get_pressed()
        if mouse[0] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif mouse[2] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False

    def duck(self):
        if self.is_cactus:
            self.image = self.duck_img[0]
        else:
            self.image = self.duck_img[self.step_index // 5]
            self.step_index += 1
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK

    def run(self):
        if self.is_cactus:
            self.image = self.run_img[0]
        else:
            self.image = self.run_img[self.step_index // 5]
            self.step_index += 1
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen):
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        global game_speed
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, images, type_index):
        self.images = images
        self.type_index = type_index
        self.image = self.images[self.type_index]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        global game_speed, obstacles
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            if self in obstacles:
                obstacles.remove(self)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class SmallCactus(Obstacle):
    def __init__(self, images):
        type_index = random.randint(0, 2)
        super().__init__(images, type_index)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, images):
        type_index = random.randint(0, 2)
        super().__init__(images, type_index)
        self.rect.y = 300

class Pterodactyl(Obstacle):
    def __init__(self, images):
        type_index = 0
        super().__init__(images, type_index)
        self.rect.y = 250
        self.step_index = 0

    def draw(self, screen):
        if self.step_index >= 10:
            self.step_index = 0
        screen.blit(self.images[self.step_index // 5], self.rect)
        self.step_index += 1

# Game functions
def main(selected_character="dino"):
    global points, game_speed, obstacles, high_score, paused
    clock = pygame.time.Clock()
    points = 0
    game_speed = 20
    obstacles = []
    paused = False
    x_pos_bg = 0
    y_pos_bg = 380
    font = pygame.font.Font('freesansbold.ttf', 20)
    if selected_character == "pterodactyl":
        player = Dinosaur(PTERODACTYL, PTERODACTYL[0], PTERODACTYL, is_pterodactyl=True)
    elif selected_character == "cactus":
        player = Dinosaur(SMALL_CACTUS, SMALL_CACTUS[0], SMALL_CACTUS, is_cactus=True)
    else:
        player = Dinosaur(RUNNING, JUMPING, DUCKING)
    cloud = Cloud()

    def score():
        global points, game_speed, high_score
        points += 1
        if points % 100 == 0:
            game_speed += 1
        if points > high_score:
            high_score = points
            try:
                with open("/home/pyodide/highscore.txt", "w") as file:
                    file.write(str(high_score))
            except OSError:
                pass  # Silently handle file write errors
        text = font.render(f"Points: {points}", True, (0, 0, 0))
        SCREEN.blit(text, (900, 50))
        high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
        SCREEN.blit(high_score_text, (50, 50))

    def pause_screen():
        SCREEN.fill((255, 255, 255))
        lines = ["Paused", "Press P to Resume", "Press Q to Quit"]
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))
            SCREEN.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 3 + i * 40))
        pygame.display.update()

    while True:
        if paused:
            pause_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    if event.key == pygame.K_q:
                        return
            clock.tick(FPS)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = True

        SCREEN.fill((255, 255, 255))
        x_pos_bg -= game_speed
        if x_pos_bg <= -BG.get_width():
            x_pos_bg = 0
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (x_pos_bg + BG.get_width(), y_pos_bg))
        cloud.update()
        cloud.draw(SCREEN)
        userInput = pygame.key.get_pressed()
        player.update(userInput)
        player.draw(SCREEN)
        if len(obstacles) == 0:
            rand_obstacle = random.choice([SmallCactus(SMALL_CACTUS), LargeCactus(LARGE_CACTUS), Pterodactyl(PTERODACTYL)])
            obstacles.append(rand_obstacle)
        for obstacle in list(obstacles):
            obstacle.update()
            obstacle.draw(SCREEN)
            if player.dino_rect.colliderect(obstacle.rect):
                death_screen(points, high_score, selected_character)
                return
        score()
        pygame.display.update()
        clock.tick(FPS)

def death_screen(points, high_score, selected_character):
    font = pygame.font.Font('freesansbold.ttf', 30)
    clock = pygame.time.Clock()
    while True:
        SCREEN.fill((255, 255, 255))
        lines = [f"Гру завершено! Рахунок: {points}.", "Натисни будь-яку клавішу, щоб спробувати ще раз"]
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))
            SCREEN.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 3 + i * 40))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                main(selected_character)
                return
        clock.tick(FPS)

def menu():
    font = pygame.font.Font('freesansbold.ttf', 30)
    input_text = ""
    input_active = True
    clock = pygame.time.Clock()
    while True:
        SCREEN.fill((255, 255, 255))
        title = font.render("Натисни Enter щоб почати гру!", True, (0, 0, 0))
        SCREEN.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 4))
        input_surface = font.render(input_text, True, (0, 0, 0))
        SCREEN.blit(input_surface, (SCREEN_WIDTH // 2 - input_surface.get_width() // 2, SCREEN_HEIGHT // 3))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        chosen_char = input_text.lower()
                        if chosen_char not in ["pterodactyl", "cactus", "dino"]:
                            chosen_char = "dino"
                        main(chosen_char)
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 15:
                            input_text += event.unicode
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    menu()