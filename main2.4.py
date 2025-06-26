import pgzrun
import random

WIDTH = 1920
HEIGHT = 1080


# Estados do Jogo
MENU = 'menu'
PLAYING = 'playing'
WIN = 'win'
OVER = 'game over'

# Menu
start_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 - 50, 200, 50)
music_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 20, 200, 50)
exit_button = Rect(WIDTH / 2 - 100, HEIGHT / 2 + 100, 200, 50)
music_on = True

GAME_STATE = MENU

# Animação da Heroina
class Hero:
    def __init__(self):
        # Posição e física
        GROUND_Y = HEIGHT * 0.7
        self.x = WIDTH / 4
        self.y = GROUND_Y
        self.speed = 6
        self.is_jumping = False
        self.jump_velocity = 0
        self.facing_right = True
        self.is_attacking = False
        self.attack_cooldown = 0
        
        #Animações
        self.animations = {
            'idle_right': {'images': ['idle_1','idle_2', 'idle_3'], 'speed': 0.2, 'index': 0},
            'run_right': {'images': ['run_1', 'run_2', 'run_3', 'run_4', 'run_5', 'run_6', 'run_7', 'run_8'], 'speed': 0.1, 'index': 0},
            'run_back': {'images': ['run_back_1', 'run_back_2', 'run_back_3', 'run_back_4', 'run_back_5', 'run_back_6', 'run_back_7', 'run_back_8'], 'speed': 0.1, 'index': 0},
            'jump': {'images': ['jump_2', 'jump_2', 'jump_3'], 'speed': 0.15, 'index': 0},
            'attack': {'images': ['attack1', 'attack2', 'attack3', 'attack4', 'attack5', 'attack6', 'attack7', 'attack8', 'attack9', 'attack10', 'attack11', 'attack12'], 
                      'speed': 0.08, 'index': 0, 'loop': False}
        }
        
        self.current_animation = 'idle_right'
        self.animation_time = 0
        self.actor = Actor(self.animations[self.current_animation]['images'][0])
        self.actor.pos = (self.x, self.y)
    
    def update_animation(self, dt):
        anim = self.animations[self.current_animation]
        self.animation_time += dt
        
        if self.animation_time >= anim['speed']:
            self.animation_time = 0
            
            if 'loop' in anim and not anim['loop'] and anim['index'] == len(anim['images']) - 1:
                self.is_attacking = False
                self.set_default_animation()
            else:
                anim['index'] = (anim['index'] + 1) % len(anim['images'])
                self.actor.image = anim['images'][anim['index']]
    
    def set_default_animation(self):
        if self.is_jumping:
            self.current_animation = 'jump'
        elif keyboard.right:
            self.current_animation = 'run_right'
        elif keyboard.left:
            self.current_animation = 'run_back'
        else:
            self.current_animation = 'idle_right'
    
    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_animation = 'attack'
            self.animations['attack']['index'] = 0
            try:
                sounds.attack.play()
            except:
                pass
    
    def update(self, dt):
        if keyboard.right:
            self.facing_right = True
        elif keyboard.left:
            self.facing_right = False
        
        if not self.is_attacking:
            self.set_default_animation()
        
        self.actor.pos = (self.x, self.y)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
    
    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self):
        # Posição física
        self.x = WIDTH + 100  # Começa fora da tela à direita
        self.y = HEIGHT * 0.7 
        self.speed = 7  # Velocidade do inimigo
        
        # Animação de corrida
        self.animations = {
            'run': {
                'images': ['enemy_run_1', 'enemy_run_2', 'enemy_run_3', 'enemy_run_4', 
                          'enemy_run_5', 'enemy_run_6', 'enemy_run_7', 'enemy_run_8'],
                'speed': 0.1, 
                'index': 0
            }
        }
        
        self.current_animation = 'run'
        self.animation_time = 0
        self.actor = Actor(self.animations['run']['images'][0])
        self.actor.pos = (self.x, self.y)
    
    def update_animation(self, dt): 
        anim = self.animations[self.current_animation]
        self.animation_time += dt
        
        if self.animation_time >= anim['speed']:
            self.animation_time = 0
            anim['index'] = (anim['index'] + 1) % len(anim['images'])
            self.actor.image = anim['images'][anim['index']]
    
    def update(self, dt):
        # Movimento da direita para esquerda
        self.x -= self.speed
        self.actor.pos = (self.x, self.y)
        self.update_animation(dt)
        
        # Reseta a posição quando sair da tela
        if self.x < -100:
            self.x = WIDTH + random.randint(100, 500)
    
    def draw(self):
        self.actor.draw()


# Constantes do Jogo
GROUND_Y = HEIGHT * 0.90
BACKGROUND_SCROLL_SPEED = 1.0 
gravity = 1
jump_strength = 25

# Criando a heroina e o inimigo
hero = Hero()
enemy=Enemy()

obstacle = Actor('bush') 
obstacle.pos = WIDTH + 400, GROUND_Y - obstacle.height / 2

# Variaveis do Jogo
MAX_LIVES = 5
lives = MAX_LIVES
distance_walked = 0
background_x_offset = 0
WIN_DISTANCE = 10000

def init_game_state():
    global hero, GAME_STATE, distance_walked, background_x_offset, lives
    hero = Hero()
    distance_walked = 0
    background_x_offset = 0  # Resetando o offset do background
    lives = MAX_LIVES
    obstacle.left = WIDTH + random.randint(400, 800)
    GAME_STATE = MENU
    if music_on:
        music.play('background_music')

def update(dt):
    global GAME_STATE, distance_walked, background_x_offset, lives
    
    if GAME_STATE == PLAYING:
        hero.update(dt)
        hero.update_animation(dt)
        enemy.update(dt)  # Atualiza o inimigo
        
        if keyboard.right:
            if hero.x < WIDTH / 2:
                hero.x += hero.speed
            else:
                distance_walked += hero.speed
                background_x_offset -= hero.speed * 1.5  # Move o background mais devagar
        elif keyboard.left:
            hero.x -= hero.speed
            distance_walked = max(0, distance_walked - hero.speed)
            background_x_offset += hero.speed * 2  # Move o background mais devagar
        
        # Mantém o herói sempre visível na tela
        hero.x = max(50, min(WIDTH - 50, hero.x))

        if hero.is_jumping:
            hero.y += hero.jump_velocity
            hero.jump_velocity += gravity
            
            if hero.y >= GROUND_Y - hero.actor.height / 2:
                hero.y = GROUND_Y - hero.actor.height / 2
                hero.is_jumping = False
                hero.jump_velocity = 0
        
        if keyboard.up and not hero.is_jumping:
            hero.is_jumping = True
            hero.jump_velocity = -jump_strength
        
        if keyboard.z and not hero.is_attacking:
            hero.attack()
        
        obstacle.x -= 8
        if obstacle.right < 0:
            obstacle.left = WIDTH + random.randint(450, 700)
        
        # Colisões com o obstáculo
        if hero.actor.colliderect(obstacle) and not hero.is_jumping and not hero.is_attacking:
            lives -= 1
            sounds.hit.play()
            obstacle.left = WIDTH + random.randint(450, 890)
        
        # Colisões com o inimigo 
        if hero.actor.colliderect(enemy.actor) and not hero.is_jumping and not hero.is_attacking:
            sounds.hit.play()
            enemy.x = WIDTH + random.randint(725, 1642)  
        
        if hero.is_attacking and hero.actor.colliderect(enemy.actor):
            enemy.x = WIDTH + random.randint(600, 1200)  
            if lives < MAX_LIVES:
                lives += 1
        
        if lives <= 0:
            GAME_STATE = OVER
            music.stop()
        
        if distance_walked >= WIN_DISTANCE:
            GAME_STATE = WIN
            music.stop()
            sounds.win.play()


def draw():
    screen.clear()
    screen.blit('background', (background_x_offset % WIDTH - WIDTH, 0))
    screen.blit('background', (background_x_offset % WIDTH, 0))
    
    if GAME_STATE == MENU:
        screen.draw.filled_rect(start_button, (0, 200, 0))
        screen.draw.text("Iniciar", center=start_button.center, color="white", fontsize=40)
        screen.draw.filled_rect(music_button, (0, 0, 200))
        screen.draw.text(f"Música {'(ON)' if music_on else '(OFF)'}", center=music_button.center, color="white", fontsize=40)
        screen.draw.filled_rect(exit_button, (200, 0, 0))
        screen.draw.text("CORRER PARA VENCER", center=(WIDTH/2, HEIGHT/2-150), color="blue", fontsize=90)
        screen.draw.text("Sair", center=exit_button.center, color="white", fontsize=40)

    elif GAME_STATE == PLAYING:
        hero.draw()
        obstacle.draw()
        enemy.draw()
        screen.draw.text(f"Distância: {int(distance_walked)}/{WIN_DISTANCE}", (10, 10), color="white", fontsize=40)
        screen.draw.text(f"Vidas: {lives}", (10, 50), color="red", fontsize=40)
    elif GAME_STATE == WIN:
        screen.draw.text("Você Ganhou!", center=(WIDTH/2, HEIGHT/2-50), color="green", fontsize=120)
        screen.draw.text(f"Distância Final: {WIN_DISTANCE}", center=(WIDTH/2, HEIGHT/2+20), color="white", fontsize=60)
        screen.draw.text("Pressione R para REINICIAR", center=(WIDTH/2, HEIGHT/2+150), color="green", fontsize=50)
        screen.draw.text("Pressione S para SAIR PARA O MENU", center=(WIDTH/2, HEIGHT/2+100), color= "red", fontsize=50)
            
        
    elif GAME_STATE == OVER:
        screen.draw.text("FIM DE JOGO!\n Você Perdeu!", center=(WIDTH/2, HEIGHT/2-50), color="red", fontsize=120)
        screen.draw.text(f"Distância Final: {distance_walked}", center=(WIDTH/2, HEIGHT/2+60), color="white", fontsize=60)
        screen.draw.text("Pressione R para REINICIAR", center=(WIDTH/2, HEIGHT/2+150), color="green", fontsize=50)
        screen.draw.text("Pressione S para SAIR PARA O MENU", center=(WIDTH/2, HEIGHT/2+100), color="red", fontsize=50)
            

def on_key_down(key):
    global GAME_STATE
    if (GAME_STATE == WIN or GAME_STATE == OVER) and key == keys.R:
        init_game_state()
        GAME_STATE = PLAYING
    if (GAME_STATE == WIN or GAME_STATE == OVER) and key == keys.S:
        init_game_state()
        GAME_STATE = MENU

def on_mouse_down(pos):
    global GAME_STATE, music_on
    if GAME_STATE == MENU:
        if start_button.collidepoint(pos):
            init_game_state()
            GAME_STATE = PLAYING
        elif exit_button.collidepoint(pos):
            exit()
        elif music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.play('background_music')
            else:
                music.stop()


pgzrun.go()
