import pygame
import time
import random
import math
from os import listdir
from os.path import join, isfile

pygame.init()

WIDTH, HEIGHT = 1300, 700

GROUND_LEVEL = HEIGHT * 2/3
MAX_SKY_HEIGHT = HEIGHT // 8

FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DAYTIME_SECS = 20
NIGHTTIME_SECS = 20
SKYCHANGE_PERIOD = 2

dino_run_spritesheet = 'dino_run.png'
dino_duck_spritesheet = 'dino_duck.png'
dino_jump_spritesheet = 'dino_jump.png'
ptedoractyl_spritesheet = 'pterodactyl_spritesheet.png'
numbers_spritesheet = 'numbers.png'

ICON = pygame.image.load(join('assets', 'game_logo.png'))

win = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption('Dinosaur Game')
pygame.display.set_icon(ICON)



def load_sprite_sheet(dir1):
    path = join('assets', dir1)

    all_sprites = {}
    
    images = [file for file in listdir(path) if isfile(join(path, file))]

    num_sprites = 1

    for image in images:
        if image == dino_run_spritesheet:
            num_sprites = 2
        elif image == dino_duck_spritesheet:
            num_sprites = 2
        elif image == dino_jump_spritesheet:
            num_sprites = 1
        elif image == ptedoractyl_spritesheet:
            num_sprites = 2
        elif image == numbers_spritesheet:
            num_sprites = 10
        
        if num_sprites > 0:
            spritesheet = pygame.image.load(join(path, image)).convert_alpha()

            sprite_width = spritesheet.get_width() / num_sprites
            sprite_height = spritesheet.get_height()

            sprites = []

            for i in range(num_sprites):
                surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA, 32)
                sprite_rect = pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height)
                surface.blit(spritesheet, (0, 0), sprite_rect)
                sprites.append(surface)
            
            all_sprites[image.replace('.png', '')] = sprites

            num_sprites = 1
    
    return all_sprites

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



class Dino:
    GRAVITY = 3
    ANIMATION_DELAY = 5
    SPRITES = load_sprite_sheet('dino_sprites')

    def __init__(self):
        self.sprite = self.SPRITES['dino_run'][0]
        self.mask = pygame.mask.from_surface(self.sprite)
        self.height = self.sprite.get_height()
        self.x = 0
        self.base_groundy = GROUND_LEVEL + (self.sprite.get_height() * 0.3)
        self.y = 0
        self.groundy = GROUND_LEVEL - (self.sprite.get_height() * 0.7)
        self.x_vel = 0
        self.y_vel = 0
        self.jump_vel = -17
        self.fall_count = 0
        self.state = 'run'
        self.animation_count = 0
        self.score = self.Score()
    
    def set_xy(self, x, y):
        self.x = x
        self.y = y
    
    def jump(self):
        self.y_vel = self.jump_vel
    
    def loop(self, fps):
        if self.y < self.groundy:
            self.y_vel += (self.fall_count/fps) * self.GRAVITY
            self.fall_count += 2
        else:
            self.y = self.groundy
            self.fall_count = 0
        
        self.y += self.y_vel
    
    def update_sprite(self):
        if self.state == 'run':
            sprites = self.SPRITES['dino_run']
        elif self.state == 'duck':
            sprites = self.SPRITES['dino_duck']
        
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

        if self.y < self.groundy:
            self.animation_count = 0
            self.sprite = self.SPRITES['dino_jump'][0]
        
        self.mask = pygame.mask.from_surface(self.sprite)
    
    def draw(self):
        if self.state == 'run':
            win.blit(self.sprite, (self.x, self.y))
        elif self.state == 'duck':
            win.blit(self.sprite, (self.x, self.base_groundy - self.sprite.get_height()))
    
    class Score:
        SPRITES = load_sprite_sheet('score_sprites')

        def __init__(self):
            self.score = 0
            self.high_score = int(open(join('assets', 'high_score.txt'), 'r').read())
            self.sprites = []
            self.high_score_sprites = []
            self.score_image = None
            self.high_score_image = None
            self.score_image_width = 0
            self.score_digit_width = 0
            self.score_image_height = 0
            self.score_increment = 0.15
        
        def update_score(self):
            score_str = str(int(math.floor(self.score)))
            self.sprites = []
            for char in score_str:
                char_num = int(char)
                sprite = self.SPRITES['numbers'][char_num]
                self.sprites.append(sprite)
            
            if len(self.sprites) < 5:
                for i in range(5 - len(self.sprites)):
                    self.sprites.insert(0, self.SPRITES['numbers'][0])
            
            self.score_image_width = self.SPRITES['numbers'][0].get_width() * len(self.sprites)
            
            self.score_image_height = self.sprites[0].get_height()
            self.score_digit_width = self.sprites[0].get_width()
            
            self.score_image = pygame.Surface((self.score_image_width, self.score_image_height), pygame.SRCALPHA, 32)

            for i in range(len(self.sprites)):
                self.score_image.blit(self.sprites[i], (self.score_digit_width * i, 0))

            self.score += self.score_increment

            if self.score >= math.ceil((self.score - self.score_increment) / 100) * 100 and self.score >= 100:
                self.score_increment *= 1.1
                if self.score_increment > 1:
                    self.score_increment = 1
        
        def update_high_score(self):
            high_score_file = open(join('assets', 'high_score.txt'), 'r')
            previous_high_score = high_score_file.read()
            if self.score > int(previous_high_score):
                self.high_score = self.score
                new_high_score_file = open(join('assets', 'high_score.txt'), 'w')
                new_high_score_file.write(str(math.floor(self.high_score)))
            
            high_score_str = str(int(math.floor(self.high_score)))
            self.high_score_sprites = []
            for char in high_score_str:
                char_num = int(char)
                sprite = self.SPRITES['numbers'][char_num]
                self.high_score_sprites.append(sprite)
            
            if len(self.high_score_sprites) < 5:
                for i in range(5 - len(self.high_score_sprites)):
                    self.high_score_sprites.insert(0, self.SPRITES['numbers'][0])
            
            self.high_score_image_width = (self.SPRITES['numbers'][0].get_width() * len(self.high_score_sprites)) + (self.SPRITES['high_label'][0].get_width() * 2)
                
            self.high_score_sprites.insert(0, self.SPRITES['high_label'][0])
            
            self.high_score_image = pygame.Surface((self.high_score_image_width, self.score_image_height), pygame.SRCALPHA, 32)

            self.high_score_image.blit(self.high_score_sprites[0], (0, 0))
            for i in range(1, len(self.high_score_sprites)):
                self.high_score_image.blit(self.high_score_sprites[i], ((self.score_digit_width * i) + self.high_score_sprites[0].get_width(), 0))
        
        def draw_score(self):
            win.blit(self.score_image, (WIDTH - self.score_image.get_width() - 20, MAX_SKY_HEIGHT - self.score_image.get_height()))
            win.blit(self.high_score_image, (WIDTH - self.score_image.get_width() - self.high_score_image.get_width() - 20, MAX_SKY_HEIGHT - self.high_score_image.get_height()))


class Obstacle:
    SPRITES = load_sprite_sheet('obstacle_sprites')
    ANIMATION_DELAY = 15

    def __init__(self, vel):
        self.x = 0
        self.y = 0
        self.vel = vel
        self.spritesheet = random.choice(list(self.SPRITES))
        self.sprite = self.SPRITES[self.spritesheet][0]
        self.mask = pygame.mask.from_surface(self.sprite)
        self.height = self.sprite.get_height()
        self.animation_count = 0
    
    def set_xy(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self):
        win.blit(self.sprite, (self.x, self.y))
    
    def update_sprite(self, background):
        if len(self.SPRITES[self.spritesheet]) > 1:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.SPRITES[self.spritesheet])
            self.sprite = self.SPRITES[self.spritesheet][sprite_index]

            self.animation_count += 1
        
        self.vel = background.vel
        
        self.x -= self.vel

        self.mask = pygame.mask.from_surface(self.sprite)

class Background:
    SPRITES = load_sprite_sheet('background_sprites')

    def __init__(self, x, y):
        self.initialx = x
        self.x = x
        self.y = y
        self.vel = 10
        self.ground_image = self.SPRITES['ground'][0]
        self.cloud_image = self.SPRITES['cloud'][0]
        self.sky_state = 'night'
        self.sky_counter = 0
        self.sky_color = BLACK
        self.rgb_value = 0
        self.clouds = []
        self.cloud_vel = 5
    
    def move(self):
        self.x -= self.vel
    
    def draw(self):
        win.blit(self.ground_image, (self.x, self.y))
        win.blit(self.ground_image, (self.x + self.ground_image.get_width(), self.y))
        
        if self.x + self.ground_image.get_width() <= 0:
            self.x = self.initialx
        
        for cloud in self.clouds:
            win.blit(cloud['image'], (cloud['x_pos'], cloud['y_pos']))
    
    def update_sky(self):
        win.fill(self.sky_color)

        if self.sky_state == 'night':
            self.sky_color = BLACK
            if self.sky_counter / FPS >= NIGHTTIME_SECS:
                self.sky_state = 'becoming_day'
                self.sky_counter = 0
        
        if self.sky_state == 'day':
            self.sky_color = WHITE
            if self.sky_counter / FPS >= DAYTIME_SECS:
                self.sky_state = 'becoming_night'
                self.sky_counter = 0
        
        self.sky_counter += 1
        
        if self.sky_state == 'becoming_day':
            self.rgb_value += 255 / (FPS * SKYCHANGE_PERIOD)
            self.sky_color = (self.rgb_value, self.rgb_value, self.rgb_value)
            if self.rgb_value >= 255:
                self.rgb_value = 255
                self.sky_color = WHITE
                self.sky_state = 'day'
                self.sky_counter = 0
        
        if self.sky_state == 'becoming_night':
            self.rgb_value -= 255 / (FPS * SKYCHANGE_PERIOD)
            self.sky_color = (self.rgb_value, self.rgb_value, self.rgb_value)
            if self.rgb_value <= 0:
                self.rgb_value = 0
                self.sky_color = BLACK
                self.sky_state = 'night'
                self.sky_counter = 0
        
        if random.randint(1, FPS * 2) == 1 and len(self.clouds) <= 3:
            cloud = {
                'image': self.cloud_image,
                'x_pos': WIDTH,
                'y_pos': random.uniform(MAX_SKY_HEIGHT, float(GROUND_LEVEL - self.cloud_image.get_height() - 100))
            }
            self.clouds.append(cloud)
        
        for cloud in self.clouds:
            cloud['x_pos'] -= self.cloud_vel
            if cloud['x_pos'] + cloud['image'].get_width() <= 0:
                self.clouds.remove(cloud)


def main():
    run = True

    dino = Dino()
    dino.set_xy(30, GROUND_LEVEL - (dino.height * 0.7))
    background = Background(0, GROUND_LEVEL)

    obstacles = []

    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)

        background.update_sky()
        background.move()

        if dino.score.score >= math.ceil((dino.score.score - dino.score.score_increment) / 100) * 100 and dino.score.score >= 100:
            background.vel *= 1.1
            if background.vel > 30:
                background.vel = 30

        background.draw()

        dino.update_sprite()
        dino.loop(FPS)
        dino.draw()

        dino.score.update_score()
        dino.score.update_high_score()
        dino.score.draw_score()

        for obstacle in obstacles:
            obstacle.update_sprite(background)
            obstacle.draw()

            if obstacle.x + obstacle.sprite.get_width() < 0:
                obstacles.remove(obstacle)
        
        for obstacle in obstacles:
            if collide(dino, obstacle):
                pygame.display.flip()
                pygame.event.get()
                time.sleep(3)
                run = False
        
        if random.randint(1, FPS * 1.3) == 1:
            if len(obstacles) == 1:
                if obstacles[0].x <= WIDTH / 3:
                    obstacle = Obstacle(background.vel)
                    if obstacle.spritesheet != 'pterodactyl_spritesheet':
                        obstacle.set_xy(WIDTH, GROUND_LEVEL - (obstacle.height * 0.7))
                    elif obstacle.spritesheet == 'pterodactyl_spritesheet':
                        obstacle.set_xy(WIDTH, random.choice([dino.groundy - obstacle.height, dino.groundy + (dino.height / 6), GROUND_LEVEL - (obstacle.height * 0.7)]))
                    obstacles.append(obstacle)
            elif len(obstacles) == 0:
                obstacle = Obstacle(background.vel)
                if obstacle.spritesheet != 'pterodactyl_spritesheet':
                    obstacle.set_xy(WIDTH, GROUND_LEVEL - (obstacle.height * 0.7))
                elif obstacle.spritesheet == 'pterodactyl_spritesheet':
                    obstacle.set_xy(WIDTH, random.choice([dino.groundy - obstacle.height, dino.groundy + (dino.height / 6), GROUND_LEVEL - (obstacle.height * 0.7)]))
                obstacles.append(obstacle)

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_UP] and dino.y == dino.groundy and dino.state != 'duck':
            dino.jump()
        if keys_pressed[pygame.K_DOWN] and dino.y == dino.groundy:
            dino.state = 'duck'
        else:
            dino.state = 'run'
        
        if dino.y > dino.groundy:
            dino.y = dino.groundy
            dino.y_vel = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit()
        
        pygame.display.flip()
    
    quit()




main()

