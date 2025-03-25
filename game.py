import pgzrun
from random import randint, choice
from math import sqrt
from pygame import Rect

# Configurações da tela
WIDTH = 800
HEIGHT = 600
TITLE = "Roguelike Survival"

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Estado do jogo
game_state = "menu"
score = 0
level = 1

# Configurações de áudio
music_on = False
sounds_on = True

class Hero:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.idle_images = ["hero_idle1", "hero_idle2", "hero_idle3", "hero_idle4"]
        self.walk_images = ["hero_walk1", "hero_walk2", "hero_walk3"]
        self.attack_images = ["hero_attack1", "hero_attack2", "hero_attack3", "hero_attack4", 
                             "hero_attack5", "hero_attack6", "hero_attack7", "hero_attack8", "hero_attack9"]
        self.current_image = 0
        self.animation_speed = 8
        self.frame = 0
        self.direction = "right"
        self.attack_cooldown = 0
        self.attack_range = 70
        self.health = 3
        self.is_attacking = False
        self.attack_frame = 0
        self.invincibility_timer = 0
        self.is_moving = False  # Controle para animação idle/walk

    def draw(self):
        # Seleciona a imagem apropriada baseada no estado
        if self.is_attacking:
            img = self.attack_images[self.attack_frame]
        elif self.is_moving:
            img = self.walk_images[self.current_image % len(self.walk_images)]
        else:
            img = self.idle_images[self.current_image % len(self.idle_images)]
        
       
        screen.blit(img, (self.x, self.y))
        
        # Barra de vida
        screen.draw.filled_rect(Rect(self.x-20, self.y-30, 40, 5), RED)
        screen.draw.filled_rect(Rect(self.x-20, self.y-30, 40*(self.health/3), 5), GREEN)
        img = (self.attack_images[self.attack_frame] if self.is_attacking else
                self.walk_images[self.current_image % len(self.walk_images)] if self.is_moving else
                self.idle_images[self.current_image % len(self.idle_images)])
            
    def update(self):
        # Atualiza invencibilidade
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        
        # Verifica movimento
        moving = False
        
        # Movimentação
        if keyboard.left:
            self.x -= self.speed
            self.direction = "left"
            moving = True
        if keyboard.right:
            self.x += self.speed
            self.direction = "right"
            moving = True
        if keyboard.up:
            self.y -= self.speed
            moving = True
        if keyboard.down:
            self.y += self.speed
            moving = True
            
        self.is_moving = moving  # Atualiza estado de movimento

        # Limites da tela
        self.x = max(0, min(WIDTH - 50, self.x))
        self.y = max(0, min(HEIGHT - 50, self.y))
        
        # Cooldown do ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Animação
        self.frame += 1
        if self.is_attacking:
            if self.frame % 5 == 0:
                self.attack_frame = (self.attack_frame + 1) % len(self.attack_images)
                if self.attack_frame == 0:
                    self.is_attacking = False
        elif self.frame % self.animation_speed == 0:
            if self.is_moving:
                # Animação de caminhada
                self.current_image = (self.current_image + 1) % len(self.walk_images)
            else:
                # Animação de idle
                self.current_image = (self.current_image + 1) % len(self.idle_images)

    def attack(self):
        if self.attack_cooldown <= 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_frame = 0
            self.attack_cooldown = 20
            if sounds_on:
                sounds.attack_sound.play()
            return True
        return False
    
    def take_damage(self):
        if self.invincibility_timer == 0:
            if sounds_on:
                sounds.lose.play()
            self.health -= 1
            self.invincibility_timer = 60  # 1 segundo de invencibilidade
            return self.health <= 0
        return False

class Enemy:
    def __init__(self):
        self.reset()
        self.images = ["skeleton_walk1", "skeleton_walk2"]
        self.current_image = 0
        self.animation_speed = 10
        self.frame = 0
        
    def reset(self):
        side = choice(["top", "right", "bottom", "left"])
        if side == "top":
            self.x, self.y = randint(0, WIDTH), -50
        elif side == "right":
            self.x, self.y = WIDTH + 50, randint(0, HEIGHT)
        elif side == "bottom":
            self.x, self.y = randint(0, WIDTH), HEIGHT + 50
        else:
            self.x, self.y = -50, randint(0, HEIGHT)
            
    def draw(self):
        screen.blit(self.images[self.current_image], (self.x, self.y))
        
    def update(self, hero):
        # Animação
        self.frame += 1
        if self.frame % self.animation_speed == 0:
            self.current_image = (self.current_image + 1) % len(self.images)
            
        # Movimento em direção ao herói
        dx = hero.x - self.x
        dy = hero.y - self.y
        dist = sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            self.x += dx/dist * 1.5
            self.y += dy/dist * 1.5

class PowerUp:
    def __init__(self, type):
        self.type = type
        self.image = "health_potion" if type == "health" else "speed_boost"
        self.x = randint(50, WIDTH-50)
        self.y = randint(50, HEIGHT-50)
        
    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        
    def apply(self, hero):
        if self.type == "health":
            hero.health = min(3, hero.health + 1)
        return True

# Inicialização do jogo
hero = Hero()
enemies = [Enemy() for _ in range(3)]
powerups = []
spawn_timer = 0
powerup_timer = 0

def reset_game():
    global score, level, enemies, powerups, spawn_timer, powerup_timer
    score = 0
    level = 1
    hero.reset()
    enemies = [Enemy() for _ in range(3)]
    powerups = []
    spawn_timer = 0
    powerup_timer = 0

def draw():
    screen.clear()
    screen.blit("dugeon_background", (0, 0))
    
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()

def draw_menu():
    screen.draw.text("Roguelike Survival", center=(WIDTH/2, HEIGHT/4), fontsize=60, color=YELLOW)
    screen.draw.text("Start Game", center=(WIDTH/2, HEIGHT/2), fontsize=40, color=GREEN)
    screen.draw.text(f"Music: {'On' if music_on else 'Off'}", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=40, color=BLUE)
    screen.draw.text("Exit", center=(WIDTH/2, HEIGHT/2 + 100), fontsize=40, color=RED)
    screen.draw.text("Use ARROWS to move, SPACE to attack", center=(WIDTH/2, HEIGHT-50), fontsize=20, color=WHITE)

def draw_game():
    for powerup in powerups:
        powerup.draw()
    
    for enemy in enemies:
        enemy.draw()
    
    hero.draw()
    
    screen.draw.text(f"Score: {int(score)}", topleft=(10, 10), fontsize=30, color=WHITE)
    screen.draw.text(f"Level: {level}", topleft=(10, 50), fontsize=30, color=WHITE)
    
    for i in range(3):
        color = RED if i < hero.health else (50, 0, 0)
        screen.draw.filled_circle((30 + i*40, HEIGHT-30), 15, color)

def draw_game_over():
    screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/3), fontsize=80, color=RED)
    screen.draw.text(f"Final Score: {int(score)}", center=(WIDTH/2, HEIGHT/2), fontsize=50, color=WHITE)
    screen.draw.text("Press SPACE to restart", center=(WIDTH/2, HEIGHT/2 + 100), fontsize=30, color=GREEN)
    
def update():
    global game_state, score, level, spawn_timer, powerup_timer
    
    if game_state == "playing":
        hero.update()
        
        for powerup in powerups[:]:
            if abs(hero.x - powerup.x) < 40 and abs(hero.y - powerup.y) < 40:
                if powerup.apply(hero):
                    powerups.remove(powerup)
        
        if hero.is_attacking and hero.attack_frame == 1:
            for enemy in enemies[:]:
                if sqrt((hero.x - enemy.x)**2 + (hero.y - enemy.y)**2) < hero.attack_range:
                    enemies.remove(enemy)
                    score += 10
                    if randint(1, 5) == 1:
                        powerups.append(PowerUp("health"))
        
        for enemy in enemies:
            enemy.update(hero)
            
            if abs(hero.x - enemy.x) < 30 and abs(hero.y - enemy.y) < 30:
                if hero.take_damage():
                    game_state = "game_over"
                    sounds.game_over_sound.play()
                    if music_on:
                        music.stop()
        
        spawn_timer += 1
        if spawn_timer >= 180 / level:
            if len(enemies) < 5 + level:
                enemies.append(Enemy())
            spawn_timer = 0
            
        powerup_timer += 1
        if powerup_timer >= 600:
            powerups.append(PowerUp("health" if randint(0, 1) == 0 else "speed"))
            powerup_timer = 0
            
        score += 0.1 * level
        if score > level * 100:
            level += 1
    
    elif game_state == "game_over" and keyboard.space:
        reset_game()
        game_state = "playing"

def on_mouse_down(pos):
    global game_state, music_on
    
    if game_state == "menu":
        if WIDTH/2 - 100 < pos[0] < WIDTH/2 + 100 and HEIGHT/2 - 20 < pos[1] < HEIGHT/2 + 20:
            sounds.background_game.stop()
            reset_game()
            game_state = "playing"
        elif WIDTH/2 - 100 < pos[0] < WIDTH/2 + 100 and HEIGHT/2 + 30 < pos[1] < HEIGHT/2 + 70:
            music_on = not music_on
            if music_on:
                sounds.background_game.play()
            else:
               sounds.background_game.stop()
        elif WIDTH/2 - 100 < pos[0] < WIDTH/2 + 100 and HEIGHT/2 + 80 < pos[1] < HEIGHT/2 + 120:
            quit()

def on_key_down(key):
    if game_state == "playing" and key == keys.SPACE:
        hero.attack()

# Inicia o jogo
reset_game()
pgzrun.go()