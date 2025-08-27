import pgzrun
from pgzero.actor import Actor
from pygame.rect import Rect

# --- Game Configuration ---
WIDTH = 800
HEIGHT = 600
TITLE = "Coin Quest Climber"

# --- Game Constants ---
GRAVITY = 0.3
PLAYER_SPEED = 3
JUMP_STRENGTH = -10  

# --- Global Variables ---
game_state = 'menu'
sounds_on = True
player = None
platforms = []
enemies = []
coins = []

# --- Custom Classes for Movement and Animation ---

class AnimatedActor(Actor):
    def __init__(self, image_list, **kwargs):
        super().__init__(image_list[0], **kwargs)
        self.image_list = image_list
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        self.flip_x = False

    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 2) % len(self.image_list)

        frame_index = self.current_frame
        if self.flip_x:
            frame_index += 1

        if frame_index >= len(self.image_list):
            frame_index = 0

        self.image = self.image_list[frame_index]

class Player(AnimatedActor):
    def __init__(self, animations, **kwargs):
        super().__init__(animations['idle'], **kwargs)
        self.animations = animations
        self.velocity_y = 0
        self.on_ground = False

    def update(self):
        dx = 0
        if keyboard.left:
            dx = -PLAYER_SPEED
            self.flip_x = True
        elif keyboard.right:
            dx = PLAYER_SPEED
            self.flip_x = False
        self.x += dx

        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        self.on_ground = False

        for platform in platforms:
            if self.colliderect(platform) and self.velocity_y > 0:
                if self.bottom < platform.bottom + 10:
                    self.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True

        if dx == 0:
            self.image_list = self.animations['idle']
        else:
            self.image_list = self.animations['run']
        self.update_animation()

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            if sounds_on:
                sounds.jump.play()

class Enemy(AnimatedActor):
    def __init__(self, image_list, patrol_range, **kwargs):
        super().__init__(image_list, **kwargs)
        self.patrol_start = self.x - patrol_range
        self.patrol_end = self.x + patrol_range
        self.speed = 1

    def update(self):
        self.x += self.speed
        if self.x > self.patrol_end or self.x < self.patrol_start:
            self.speed *= -1
            self.flip_x = not self.flip_x
        self.update_animation()

def setup_level():
    global player, platforms, enemies, coins
    player_animations = {
        'idle': ['player_idle1', 'player_idle1_flipped'],
        'run': ['player_run1', 'player_run1_flipped', 'player_run2', 'player_run2_flipped']
    }

    platforms.clear()
    enemies.clear()
    coins.clear()

    # Plataformas para corresponder aos pisos visuais (verde/marrom)
    level_layout = [
        (0, HEIGHT - 20, WIDTH, 20),           # chão
        (100, 480, 220, 20),                   # plataforma 1
        (380, 340, 180, 20),                   # plataforma 2
        (500, 180, 120, 20),                   # plataforma 3
        (150, 180, 220, 20),                   # plataforma 4
        (300, 530, 200, 20)                    # ponte
    ]
    for p in level_layout:
        platforms.append(Rect(p))

    # Jogador começa sobre a ponte
    ponte = platforms[-1]
    player = Player(player_animations, pos=(ponte.centerx, ponte.top - 20))

    # Slimes sobre gramados
    enemy_frames = ['slime1', 'slime1_flipped', 'slime2', 'slime2_flipped']
    enemies.append(Enemy(enemy_frames, patrol_range=60, pos=(platforms[1].x + 50, platforms[1].top - 0)))
    enemies.append(Enemy(enemy_frames, patrol_range=60, pos=(platforms[4].x - 0, platforms[4].top - 10)))

    # Moedas posicionadas diretamente sobre os pisos visuais
    coins.append(Actor('coin', pos=(platforms[1].centerx, platforms[1].top - 10)))  # sobre plataforma 1
    coins.append(Actor('coin', pos=(platforms[2].centerx, platforms[2].top - 40)))  # sobre plataforma 2
    coins.append(Actor('coin', pos=(platforms[4].left + 5, platforms[4].top - 25)))  # sobre plataforma 4

start_button = Actor('button_start', pos=(WIDTH / 2, 250))
sound_button = Actor('button_sound_on', pos=(WIDTH / 2, 350))
exit_button = Actor('button_exit', pos=(WIDTH / 2, 450))
menu_buttons = [start_button, sound_button, exit_button]

def update():
    global game_state
    if game_state == 'playing':
        player.update()
        for enemy in enemies:
            enemy.update()
            if player.colliderect(enemy):
                game_state = 'game_over'
                if sounds_on:
                    sounds.lose.play()
        for coin in list(coins):
            if player.colliderect(coin):
                coins.remove(coin)
                if sounds_on:
                    sounds.collect.play()
        if not coins:
            game_state = 'menu'
        if player.top > HEIGHT:
            game_state = 'game_over'
            if sounds_on:
                sounds.lose.play()

def draw():
    screen.clear()
    screen.blit('background', (0, 0))
    if game_state == 'menu':
        screen.draw.text("Coin Quest Climber", center=(WIDTH / 2, 100), fontsize=90, color="red")
        for button in menu_buttons:
            button.draw()
    elif game_state == 'playing':
        for coin in coins:
            coin.draw()
        for enemy in enemies:
            enemy.draw()
        player.draw()
        screen.draw.text(f"Moedas: {len(coins)}", (10, 10), fontsize=30, color="white")
    elif game_state == 'game_over':
        screen.draw.text("FIM DE JOGO", center=(WIDTH / 2, HEIGHT / 2), fontsize=80, color="red")
        screen.draw.text("Pressione ENTER para voltar", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=40, color="white")

def on_key_down(key):
    global game_state
    if game_state == 'playing' and (key == keys.SPACE or key == keys.UP):
        player.jump()
    if game_state == 'game_over' and key == keys.RETURN:
        game_state = 'menu'

def on_mouse_down(pos):
    global game_state, sounds_on
    if game_state == 'menu':
        if start_button.collidepoint(pos):
            setup_level()
            game_state = 'playing'
            if sounds_on:
                music.play('theme_music')
        elif sound_button.collidepoint(pos):
            sounds_on = not sounds_on
            sound_button.image = 'button_sound_on' if sounds_on else 'button_sound_off'
            if sounds_on:
                music.unpause()
            else:
                music.pause()
        elif exit_button.collidepoint(pos):
            exit()

pgzrun.go()
