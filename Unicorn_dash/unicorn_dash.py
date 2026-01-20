#!/usr/bin/env python3
"""
🦄 UNICORN DASH - A magical endless runner game
Guide your unicorn over obstacles and collect stars!
Controls: SPACE or UP arrow to jump, 1-2-3 for difficulty, R to restart, Q to quit
"""

import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
GROUND_HEIGHT = 60
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# Sky gradient colors
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (255, 182, 193)

# Ground colors
GRASS_GREEN = (34, 139, 34)
GRASS_LIGHT = (50, 205, 50)
DIRT_BROWN = (139, 90, 43)

# Unicorn colors
UNICORN_WHITE = (255, 250, 250)
UNICORN_CREAM = (255, 245, 238)
UNICORN_PINK = (255, 182, 193)
UNICORN_PURPLE = (186, 85, 211)
UNICORN_GOLD = (255, 215, 0)
MANE_COLORS = [(255, 105, 180), (255, 182, 193), (186, 85, 211), (138, 43, 226), (75, 0, 130)]

# Obstacle colors
ROCK_GRAY = (105, 105, 105)
ROCK_DARK = (70, 70, 70)
CRYSTAL_PURPLE = (148, 0, 211)
CRYSTAL_BLUE = (0, 191, 255)
DRAGON_RED = (178, 34, 34)
DRAGON_ORANGE = (255, 140, 0)

# Effect colors
STAR_GOLD = (255, 223, 0)
SPARKLE_WHITE = (255, 255, 255)
RAINBOW_COLORS = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]

# Difficulty settings
DIFFICULTIES = {
    'EASY': {
        'name': 'Easy',
        'initial_speed': 7,
        'max_speed': 12,
        'speed_increment': 0.0008,
        'min_obstacle_gap': 90,
        'gravity': 0.7,
        'jump_strength': -16,
        'color': (100, 200, 100)
    },
    'NORMAL': {
        'name': 'Normal',
        'initial_speed': 9,
        'max_speed': 16,
        'speed_increment': 0.0012,
        'min_obstacle_gap': 70,
        'gravity': 0.85,
        'jump_strength': -17,
        'color': (200, 200, 100)
    },
    'HARD': {
        'name': 'Hard',
        'initial_speed': 12,
        'max_speed': 22,
        'speed_increment': 0.002,
        'min_obstacle_gap': 50,
        'gravity': 1.0,
        'jump_strength': -18,
        'color': (200, 100, 100)
    }
}


class Particle:
    """Sparkle/magic particle effect"""
    
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.color = color if color else random.choice([STAR_GOLD, SPARKLE_WHITE, UNICORN_PINK, UNICORN_PURPLE])
        self.size = random.randint(2, 5)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.vx = random.uniform(-2, 0)
        self.vy = random.uniform(-2, 2)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, int(self.size * (self.life / self.max_life)))
        
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            
    def is_dead(self):
        return self.life <= 0


class RainbowTrail:
    """Rainbow trail segment behind unicorn"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 30
        self.max_life = 30
        
    def update(self, speed):
        self.x -= speed * 0.5
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / self.max_life
            height = 4
            for i, color in enumerate(RAINBOW_COLORS):
                y_pos = self.y + i * height - len(RAINBOW_COLORS) * height // 2
                faded_color = tuple(int(c * alpha) for c in color)
                pygame.draw.rect(screen, faded_color, (int(self.x), int(y_pos), 8, height))
                
    def is_dead(self):
        return self.life <= 0


class Unicorn:
    """The player-controlled unicorn character"""
    
    def __init__(self, difficulty):
        self.width = 70
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.velocity_y = 0
        self.is_jumping = False
        self.difficulty = difficulty
        self.leg_timer = 0
        self.leg_state = 0
        self.mane_offset = 0
        self.particles = []
        self.rainbow_trail = []
        self.sparkle_timer = 0
        
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = DIFFICULTIES[self.difficulty]['jump_strength']
            self.is_jumping = True
            # Burst of particles on jump
            for _ in range(10):
                self.particles.append(Particle(self.x + 20, self.y + self.height - 10))
            
    def update(self, game_speed):
        # Apply gravity
        gravity = DIFFICULTIES[self.difficulty]['gravity']
        self.velocity_y += gravity
        self.y += self.velocity_y
        
        # Ground collision
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.velocity_y = 0
            self.is_jumping = False
            
        # Animate legs
        if not self.is_jumping:
            self.leg_timer += 1
            if self.leg_timer > 4:
                self.leg_timer = 0
                self.leg_state = (self.leg_state + 1) % 4
                
        # Animate mane
        self.mane_offset = math.sin(pygame.time.get_ticks() * 0.01) * 3
        
        # Spawn particles
        self.sparkle_timer += 1
        if self.sparkle_timer > 3:
            self.sparkle_timer = 0
            self.particles.append(Particle(
                self.x + random.randint(20, 50),
                self.y + random.randint(10, 40)
            ))
            
        # Rainbow trail when running
        if not self.is_jumping and random.random() < 0.3:
            self.rainbow_trail.append(RainbowTrail(self.x, self.y + self.height // 2))
            
        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]
        
        # Update rainbow trail
        for r in self.rainbow_trail:
            r.update(game_speed)
        self.rainbow_trail = [r for r in self.rainbow_trail if not r.is_dead()]
                
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        
        # Draw rainbow trail first (behind unicorn)
        for r in self.rainbow_trail:
            r.draw(screen)
        
        # Draw particles
        for p in self.particles:
            p.draw(screen)
        
        # === BODY ===
        # Main body (elegant oval)
        body_points = []
        for i in range(20):
            angle = i * math.pi / 10
            bx = x + 35 + math.cos(angle) * 28
            by = y + 35 + math.sin(angle) * 18
            body_points.append((bx, by))
        pygame.draw.polygon(screen, UNICORN_WHITE, body_points)
        pygame.draw.polygon(screen, UNICORN_CREAM, body_points, 2)
        
        # === LEGS ===
        leg_positions = [
            (x + 18, y + 45),  # Back left
            (x + 28, y + 45),  # Back right
            (x + 48, y + 45),  # Front left
            (x + 58, y + 45),  # Front right
        ]
        
        leg_offsets = [0, 0, 0, 0]
        if not self.is_jumping:
            # Running animation
            if self.leg_state == 0:
                leg_offsets = [-5, 5, 5, -5]
            elif self.leg_state == 1:
                leg_offsets = [0, 0, 0, 0]
            elif self.leg_state == 2:
                leg_offsets = [5, -5, -5, 5]
            else:
                leg_offsets = [0, 0, 0, 0]
        else:
            # Tucked legs while jumping
            leg_offsets = [-8, -8, 8, 8]
            
        for i, (lx, ly) in enumerate(leg_positions):
            # Leg
            pygame.draw.rect(screen, UNICORN_WHITE, (lx, ly + leg_offsets[i], 6, 18))
            # Hoof
            pygame.draw.ellipse(screen, UNICORN_PINK, (lx - 1, ly + 16 + leg_offsets[i], 8, 6))
            
        # === NECK & HEAD ===
        # Neck
        neck_points = [(x + 55, y + 25), (x + 65, y + 5), (x + 75, y + 5), (x + 65, y + 30)]
        pygame.draw.polygon(screen, UNICORN_WHITE, neck_points)
        
        # Head
        pygame.draw.ellipse(screen, UNICORN_WHITE, (x + 60, y - 5, 30, 22))
        
        # Snout
        pygame.draw.ellipse(screen, UNICORN_CREAM, (x + 80, y + 2, 15, 12))
        
        # Nostril
        pygame.draw.circle(screen, UNICORN_PINK, (x + 90, y + 8), 2)
        
        # Eye
        pygame.draw.ellipse(screen, WHITE, (x + 70, y + 2, 10, 8))
        pygame.draw.circle(screen, (50, 0, 80), (x + 74, y + 5), 3)
        pygame.draw.circle(screen, WHITE, (x + 75, y + 4), 1)  # Eye sparkle
        
        # Eyelashes
        pygame.draw.line(screen, BLACK, (x + 72, y), (x + 70, y - 3), 1)
        pygame.draw.line(screen, BLACK, (x + 75, y), (x + 75, y - 4), 1)
        pygame.draw.line(screen, BLACK, (x + 78, y + 1), (x + 80, y - 2), 1)
        
        # === HORN ===
        horn_base = (x + 75, y - 3)
        horn_tip = (x + 85, y - 25)
        # Horn with spiral
        pygame.draw.polygon(screen, UNICORN_GOLD, [
            (horn_base[0] - 4, horn_base[1]),
            horn_tip,
            (horn_base[0] + 4, horn_base[1])
        ])
        # Spiral lines on horn
        for i in range(4):
            hy = horn_base[1] - i * 5
            hx = horn_base[0] + i * 2
            pygame.draw.line(screen, (255, 245, 0), (hx - 3 + i, hy), (hx + 2 - i * 0.5, hy - 2), 1)
        
        # Horn glow
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, 50), (10, 10), 10)
        screen.blit(glow_surf, (int(horn_tip[0]) - 10, int(horn_tip[1]) - 10))
        
        # === MANE ===
        mane_y_offset = self.mane_offset
        for i, color in enumerate(MANE_COLORS):
            mane_x = x + 50 - i * 6
            mane_y = y + 5 + mane_y_offset + i * 2
            # Flowing mane strands
            points = [
                (mane_x + 10, mane_y),
                (mane_x - 5, mane_y + 8),
                (mane_x - 10 - i * 2, mane_y + 15 + i * 3),
                (mane_x - 5, mane_y + 10),
                (mane_x + 5, mane_y + 5)
            ]
            pygame.draw.polygon(screen, color, points)
            
        # === TAIL ===
        tail_wave = math.sin(pygame.time.get_ticks() * 0.008) * 5
        for i, color in enumerate(MANE_COLORS):
            tail_points = [
                (x + 8, y + 30),
                (x - 10 - i * 3 + tail_wave, y + 35 + i * 4),
                (x - 15 - i * 4 + tail_wave * 1.5, y + 45 + i * 5),
                (x - 5 - i * 2 + tail_wave * 0.5, y + 40 + i * 3),
                (x + 5, y + 35)
            ]
            pygame.draw.polygon(screen, color, tail_points)
            
        # === EAR ===
        ear_points = [(x + 68, y - 2), (x + 72, y - 12), (x + 76, y - 2)]
        pygame.draw.polygon(screen, UNICORN_WHITE, ear_points)
        pygame.draw.polygon(screen, UNICORN_PINK, [(x + 70, y - 2), (x + 72, y - 8), (x + 74, y - 2)])
        
    def get_rect(self):
        """Return collision rectangle (adjusted for fairness)"""
        return pygame.Rect(self.x + 15, self.y + 10, self.width - 25, self.height - 15)


class Rock:
    """Rock obstacle"""
    
    def __init__(self, x, variant=None):
        self.variant = variant if variant else random.choice(['small', 'medium', 'large', 'crystal'])
        
        if self.variant == 'small':
            self.width = 30
            self.height = 35
        elif self.variant == 'medium':
            self.width = 40
            self.height = 50
        elif self.variant == 'large':
            self.width = 55
            self.height = 65
        else:  # crystal
            self.width = 35
            self.height = 55
            
        self.x = x
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.glow_offset = random.random() * math.pi * 2
        
    def update(self, speed):
        self.x -= speed
        
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        
        if self.variant == 'crystal':
            # Magical crystal obstacle
            glow = abs(math.sin(pygame.time.get_ticks() * 0.005 + self.glow_offset)) * 0.5 + 0.5
            
            # Crystal glow
            glow_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.polygon(glow_surf, (148, 0, 211, int(50 * glow)), [
                (self.width // 2 + 10, 5),
                (5, self.height + 10),
                (self.width + 15, self.height + 10)
            ])
            screen.blit(glow_surf, (x - 10, y - 10))
            
            # Main crystal
            pygame.draw.polygon(screen, CRYSTAL_PURPLE, [
                (x + self.width // 2, y),
                (x, y + self.height),
                (x + self.width, y + self.height)
            ])
            # Crystal facets
            pygame.draw.polygon(screen, CRYSTAL_BLUE, [
                (x + self.width // 2, y),
                (x + self.width // 4, y + self.height * 0.6),
                (x + self.width // 2, y + self.height)
            ])
            # Highlight
            pygame.draw.line(screen, WHITE, 
                           (x + self.width // 2, y + 5), 
                           (x + self.width // 3, y + self.height // 2), 2)
        else:
            # Regular rock
            # Shadow
            pygame.draw.ellipse(screen, (50, 50, 50, 100), 
                              (x - 5, y + self.height - 10, self.width + 10, 15))
            
            # Main rock body
            rock_points = [
                (x + self.width * 0.1, y + self.height),
                (x, y + self.height * 0.6),
                (x + self.width * 0.2, y + self.height * 0.2),
                (x + self.width * 0.5, y),
                (x + self.width * 0.8, y + self.height * 0.15),
                (x + self.width, y + self.height * 0.5),
                (x + self.width * 0.9, y + self.height)
            ]
            pygame.draw.polygon(screen, ROCK_GRAY, rock_points)
            
            # Rock highlights
            highlight_points = [
                (x + self.width * 0.3, y + self.height * 0.3),
                (x + self.width * 0.5, y + self.height * 0.1),
                (x + self.width * 0.6, y + self.height * 0.25),
                (x + self.width * 0.45, y + self.height * 0.4)
            ]
            pygame.draw.polygon(screen, (130, 130, 130), highlight_points)
            
            # Rock cracks
            pygame.draw.line(screen, ROCK_DARK, 
                           (x + self.width * 0.3, y + self.height * 0.5),
                           (x + self.width * 0.5, y + self.height * 0.8), 2)
            pygame.draw.line(screen, ROCK_DARK,
                           (x + self.width * 0.6, y + self.height * 0.3),
                           (x + self.width * 0.7, y + self.height * 0.6), 2)
            
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 10, self.width - 10, self.height - 10)
    
    def is_off_screen(self):
        return self.x + self.width < 0


class Dragon:
    """Flying dragon obstacle"""
    
    def __init__(self, x):
        self.width = 60
        self.height = 40
        self.x = x
        # Dragons fly at different heights
        self.y = random.choice([
            SCREEN_HEIGHT - GROUND_HEIGHT - 100,
            SCREEN_HEIGHT - GROUND_HEIGHT - 140,
            SCREEN_HEIGHT - GROUND_HEIGHT - 180
        ])
        self.wing_timer = 0
        self.wing_angle = 0
        self.fire_particles = []
        
    def update(self, speed):
        self.x -= speed * 1.3  # Dragons are faster
        self.wing_timer += 1
        self.wing_angle = math.sin(self.wing_timer * 0.3) * 30
        
        # Fire breath particles
        if random.random() < 0.3:
            self.fire_particles.append({
                'x': self.x - 10,
                'y': self.y + 20 + random.randint(-5, 5),
                'life': 15,
                'size': random.randint(3, 8)
            })
            
        # Update fire particles
        for p in self.fire_particles:
            p['x'] -= speed * 0.5
            p['life'] -= 1
            p['size'] = max(1, p['size'] - 0.3)
        self.fire_particles = [p for p in self.fire_particles if p['life'] > 0]
            
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        
        # Draw fire particles
        for p in self.fire_particles:
            color = DRAGON_ORANGE if p['life'] > 8 else DRAGON_RED
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), int(p['size']))
        
        # Body
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 15, y + 15, 35, 20))
        
        # Head
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 40, y + 10, 22, 18))
        
        # Snout
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 55, y + 15, 12, 10))
        
        # Eye
        pygame.draw.circle(screen, (255, 255, 0), (x + 50, y + 16), 4)
        pygame.draw.circle(screen, BLACK, (x + 51, y + 16), 2)
        
        # Horns
        pygame.draw.polygon(screen, DRAGON_ORANGE, [
            (x + 45, y + 10), (x + 42, y), (x + 48, y + 8)
        ])
        pygame.draw.polygon(screen, DRAGON_ORANGE, [
            (x + 52, y + 10), (x + 52, y + 2), (x + 56, y + 10)
        ])
        
        # Wings
        wing_y_offset = math.sin(math.radians(self.wing_angle)) * 15
        
        # Upper wing
        wing_points = [
            (x + 25, y + 15),
            (x + 15, y - 10 + wing_y_offset),
            (x + 35, y - 5 + wing_y_offset),
            (x + 40, y + 15)
        ]
        pygame.draw.polygon(screen, DRAGON_ORANGE, wing_points)
        
        # Wing membrane lines
        pygame.draw.line(screen, DRAGON_RED, (x + 25, y + 15), (x + 20, y - 5 + wing_y_offset), 2)
        pygame.draw.line(screen, DRAGON_RED, (x + 30, y + 15), (x + 30, y - 3 + wing_y_offset), 2)
        
        # Tail
        tail_points = [
            (x + 15, y + 22),
            (x, y + 18),
            (x - 10, y + 25),
            (x + 5, y + 28),
            (x + 15, y + 28)
        ]
        pygame.draw.polygon(screen, DRAGON_RED, tail_points)
        
        # Tail spike
        pygame.draw.polygon(screen, DRAGON_ORANGE, [
            (x - 10, y + 25), (x - 18, y + 20), (x - 5, y + 28)
        ])
        
        # Legs
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 20, y + 30, 8, 12))
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 35, y + 30, 8, 12))
        
    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 10, self.width - 15, self.height - 15)
    
    def is_off_screen(self):
        return self.x + self.width < 0


class Cloud:
    """Background cloud decoration"""
    
    def __init__(self, x=None):
        self.x = x if x else random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
        self.y = random.randint(40, 150)
        self.speed = random.uniform(0.3, 1.0)
        self.size = random.choice(['small', 'medium', 'large'])
        self.color = random.choice([
            (255, 255, 255),
            (255, 240, 245),
            (240, 248, 255)
        ])
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        
        if self.size == 'small':
            pygame.draw.ellipse(screen, self.color, (x, y, 50, 25))
            pygame.draw.ellipse(screen, self.color, (x + 20, y - 10, 35, 30))
            pygame.draw.ellipse(screen, self.color, (x + 40, y, 40, 22))
        elif self.size == 'medium':
            pygame.draw.ellipse(screen, self.color, (x, y, 60, 30))
            pygame.draw.ellipse(screen, self.color, (x + 25, y - 15, 45, 38))
            pygame.draw.ellipse(screen, self.color, (x + 55, y, 50, 28))
        else:
            pygame.draw.ellipse(screen, self.color, (x, y, 70, 35))
            pygame.draw.ellipse(screen, self.color, (x + 30, y - 18, 55, 45))
            pygame.draw.ellipse(screen, self.color, (x + 65, y, 60, 32))
            pygame.draw.ellipse(screen, self.color, (x + 100, y + 5, 45, 25))
            
    def is_off_screen(self):
        return self.x < -180


class Star:
    """Background twinkling star"""
    
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(20, 180)
        self.twinkle_offset = random.random() * math.pi * 2
        self.size = random.randint(1, 3)
        
    def draw(self, screen):
        brightness = abs(math.sin(pygame.time.get_ticks() * 0.003 + self.twinkle_offset))
        color = tuple(int(255 * brightness) for _ in range(3))
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)


class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🦄 Unicorn Dash - Magical Endless Runner!")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            self.font_large = pygame.font.SysFont('Arial', 72, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', 48, bold=True)
            self.font_small = pygame.font.SysFont('Arial', 28)
            self.font_tiny = pygame.font.SysFont('Arial', 22)
        except:
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 32)
            self.font_tiny = pygame.font.Font(None, 24)
        
        self.difficulty = 'NORMAL'
        self.high_scores = {'EASY': 0, 'NORMAL': 0, 'HARD': 0}
        self.stars = [Star() for _ in range(15)]
        self.reset_game()
        
    def reset_game(self):
        """Reset game state"""
        self.unicorn = Unicorn(self.difficulty)
        self.obstacles = []
        self.clouds = [Cloud(random.randint(100, 800)) for _ in range(4)]
        self.score = 0
        self.game_speed = DIFFICULTIES[self.difficulty]['initial_speed']
        self.game_over = False
        self.obstacle_timer = 0
        self.ground_offset = 0
        self.show_menu = True
        self.menu_particles = []
        
    def spawn_obstacle(self):
        """Spawn a new obstacle"""
        diff = DIFFICULTIES[self.difficulty]
        
        # Increase dragon probability as score increases
        dragon_chance = min(0.35, self.score / 4000)
        
        # Crystal chance
        crystal_chance = 0.2
        
        if random.random() < dragon_chance and self.score > 300:
            self.obstacles.append(Dragon(SCREEN_WIDTH + 50))
        elif random.random() < crystal_chance:
            self.obstacles.append(Rock(SCREEN_WIDTH + 50, 'crystal'))
        else:
            self.obstacles.append(Rock(SCREEN_WIDTH + 50))
            
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.show_menu:
                    if event.key == pygame.K_1:
                        self.difficulty = 'EASY'
                        self.show_menu = False
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_2:
                        self.difficulty = 'NORMAL'
                        self.show_menu = False
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_3:
                        self.difficulty = 'HARD'
                        self.show_menu = False
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.show_menu = False
                        self.reset_game()
                        self.show_menu = False
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.game_over:
                        self.reset_game()
                        self.show_menu = False
                    else:
                        self.unicorn.jump()
                elif event.key == pygame.K_r:
                    self.reset_game()
                    self.show_menu = False
                elif event.key == pygame.K_m:
                    self.show_menu = True
                elif event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_1 and self.game_over:
                    self.difficulty = 'EASY'
                    self.reset_game()
                    self.show_menu = False
                elif event.key == pygame.K_2 and self.game_over:
                    self.difficulty = 'NORMAL'
                    self.reset_game()
                    self.show_menu = False
                elif event.key == pygame.K_3 and self.game_over:
                    self.difficulty = 'HARD'
                    self.reset_game()
                    self.show_menu = False
        
        # Allow holding space/up for continuous jumping
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not self.game_over and not self.show_menu:
            self.unicorn.jump()
            
        return True
        
    def update(self):
        """Update game state"""
        if self.game_over or self.show_menu:
            # Update menu particles
            if random.random() < 0.2:
                self.menu_particles.append(Particle(
                    random.randint(0, SCREEN_WIDTH),
                    random.randint(0, SCREEN_HEIGHT)
                ))
            for p in self.menu_particles:
                p.update()
            self.menu_particles = [p for p in self.menu_particles if not p.is_dead()]
            return
            
        diff = DIFFICULTIES[self.difficulty]
        
        # Update unicorn
        self.unicorn.update(self.game_speed)
        
        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(self.game_speed)
            
        # Remove off-screen obstacles
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]
        
        # Spawn new obstacles
        self.obstacle_timer += 1
        gap = max(diff['min_obstacle_gap'], 100 - self.score // 150)
        if self.obstacle_timer > gap:
            self.obstacle_timer = 0
            self.spawn_obstacle()
            
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
        self.clouds = [c for c in self.clouds if not c.is_off_screen()]
        if len(self.clouds) < 5 and random.random() < 0.008:
            self.clouds.append(Cloud())
            
        # Check collisions
        unicorn_rect = self.unicorn.get_rect()
        for obstacle in self.obstacles:
            if unicorn_rect.colliderect(obstacle.get_rect()):
                self.game_over = True
                if self.score > self.high_scores[self.difficulty]:
                    self.high_scores[self.difficulty] = self.score
                return
                
        # Update score and speed
        self.score += 1
        self.game_speed = min(
            diff['max_speed'],
            diff['initial_speed'] + self.score * diff['speed_increment']
        )
        
        # Update ground animation
        self.ground_offset = (self.ground_offset + self.game_speed) % 30
        
    def draw_gradient_sky(self):
        """Draw gradient sky background"""
        for y in range(SCREEN_HEIGHT - GROUND_HEIGHT):
            ratio = y / (SCREEN_HEIGHT - GROUND_HEIGHT)
            r = int(SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio)
            g = int(SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio)
            b = int(SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
    def draw_ground(self):
        """Draw the ground with grass texture"""
        # Dirt layer
        pygame.draw.rect(self.screen, DIRT_BROWN, 
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT + 15, SCREEN_WIDTH, GROUND_HEIGHT - 15))
        
        # Grass layer
        pygame.draw.rect(self.screen, GRASS_GREEN,
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 18))
        
        # Grass blades
        for i in range(-1, SCREEN_WIDTH // 15 + 2):
            x = i * 15 - int(self.ground_offset / 2)
            grass_height = 8 + (i % 3) * 3
            pygame.draw.line(self.screen, GRASS_LIGHT,
                           (x, SCREEN_HEIGHT - GROUND_HEIGHT),
                           (x - 3, SCREEN_HEIGHT - GROUND_HEIGHT - grass_height), 2)
            pygame.draw.line(self.screen, GRASS_GREEN,
                           (x + 5, SCREEN_HEIGHT - GROUND_HEIGHT),
                           (x + 7, SCREEN_HEIGHT - GROUND_HEIGHT - grass_height + 2), 2)
                           
        # Ground texture
        for i in range(-1, SCREEN_WIDTH // 25 + 2):
            x = i * 25 - int(self.ground_offset)
            y = SCREEN_HEIGHT - GROUND_HEIGHT + 25
            pygame.draw.circle(self.screen, (120, 70, 35), (x, y), 3)
            pygame.draw.circle(self.screen, (100, 60, 30), (x + 12, y + 15), 2)
            
    def draw_ui(self):
        """Draw score and UI elements"""
        diff = DIFFICULTIES[self.difficulty]
        
        # Score with shadow
        score_text = self.font_small.render(f"SCORE: {self.score}", True, DARK_GRAY)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        # High score
        hi_text = self.font_tiny.render(f"BEST: {self.high_scores[self.difficulty]}", True, GRAY)
        self.screen.blit(hi_text, (SCREEN_WIDTH - 200, 50))
        
        # Difficulty indicator
        diff_text = self.font_tiny.render(f"MODE: {diff['name']}", True, diff['color'])
        self.screen.blit(diff_text, (20, 20))
        
        # Speed indicator
        max_speed = diff['max_speed']
        init_speed = diff['initial_speed']
        speed_pct = int((self.game_speed - init_speed) / (max_speed - init_speed) * 100)
        speed_text = self.font_tiny.render(f"SPEED: {speed_pct}%", True, GRAY)
        self.screen.blit(speed_text, (20, 45))
        
        # Speed bar
        bar_width = 100
        bar_height = 8
        pygame.draw.rect(self.screen, GRAY, (20, 70, bar_width, bar_height), 1)
        fill_width = int(bar_width * speed_pct / 100)
        bar_color = (100, 200, 100) if speed_pct < 50 else (200, 200, 100) if speed_pct < 80 else (200, 100, 100)
        pygame.draw.rect(self.screen, bar_color, (20, 70, fill_width, bar_height))
        
    def draw_menu(self):
        """Draw the main menu"""
        # Draw background
        self.draw_gradient_sky()
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
            
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)
            
        self.draw_ground()
        
        # Draw particles
        for p in self.menu_particles:
            p.draw(self.screen)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((255, 240, 245))
        self.screen.blit(overlay, (0, 0))
        
        # Title with rainbow effect
        title = "UNICORN DASH"
        title_y = 80
        for i, char in enumerate(title):
            color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            char_surf = self.font_large.render(char, True, color)
            x = SCREEN_WIDTH // 2 - 250 + i * 40
            y = title_y + math.sin(pygame.time.get_ticks() * 0.005 + i * 0.5) * 5
            self.screen.blit(char_surf, (x, y))
        
        # Unicorn emoji
        emoji_text = self.font_large.render("🦄", True, WHITE)
        self.screen.blit(emoji_text, (SCREEN_WIDTH // 2 - 30, title_y + 70))
        
        # Difficulty selection
        diff_y = 220
        select_text = self.font_small.render("SELECT DIFFICULTY:", True, DARK_GRAY)
        select_rect = select_text.get_rect(center=(SCREEN_WIDTH // 2, diff_y))
        self.screen.blit(select_text, select_rect)
        
        for i, (key, diff) in enumerate(DIFFICULTIES.items()):
            y = diff_y + 45 + i * 45
            text = f"[{i+1}] {diff['name']}"
            color = diff['color']
            
            # Highlight current difficulty
            if key == self.difficulty:
                pygame.draw.rect(self.screen, color, 
                               (SCREEN_WIDTH // 2 - 100, y - 5, 200, 35), 
                               border_radius=10)
                text_color = WHITE
            else:
                text_color = color
                
            diff_text = self.font_small.render(text, True, text_color)
            diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, y + 10))
            self.screen.blit(diff_text, diff_rect)
            
            # Speed indicator
            speed_info = f"Speed: {diff['initial_speed']}-{diff['max_speed']}"
            speed_text = self.font_tiny.render(speed_info, True, GRAY)
            speed_rect = speed_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30))
            # self.screen.blit(speed_text, speed_rect)
        
        # Instructions
        inst_y = 420
        instructions = [
            "SPACE / UP = Jump  |  R = Restart  |  M = Menu  |  Q = Quit",
            "Press 1, 2, or 3 to select difficulty and start!"
        ]
        for i, inst in enumerate(instructions):
            inst_text = self.font_tiny.render(inst, True, GRAY)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y + i * 25))
            self.screen.blit(inst_text, inst_rect)
        
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((255, 240, 245))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        go_text = self.font_large.render("GAME OVER", True, (180, 80, 120))
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(go_text, go_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Score: {self.score}", True, DARK_GRAY)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # New high score notification
        if self.score >= self.high_scores[self.difficulty] and self.score > 0:
            new_hi = self.font_small.render("✨ NEW HIGH SCORE! ✨", True, UNICORN_GOLD)
            new_hi_rect = new_hi.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45))
            self.screen.blit(new_hi, new_hi_rect)
        
        # Difficulty info
        diff = DIFFICULTIES[self.difficulty]
        diff_text = self.font_tiny.render(f"Difficulty: {diff['name']}", True, diff['color'])
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(diff_text, diff_rect)
        
        # Restart instructions
        restart_text = self.font_tiny.render("SPACE = Play Again | 1/2/3 = Change Difficulty | M = Menu", True, GRAY)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.screen.blit(restart_text, restart_rect)
        
    def draw(self):
        """Render the game"""
        if self.show_menu:
            self.draw_menu()
            pygame.display.flip()
            return
            
        # Gradient sky background
        self.draw_gradient_sky()
        
        # Draw stars (subtle)
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)
            
        # Draw ground
        self.draw_ground()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Draw unicorn
        self.unicorn.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    print("\n🦄 UNICORN DASH 🦄")
    print("=" * 50)
    print("A magical endless runner game!")
    print("=" * 50)
    print("\nControls:")
    print("  SPACE / UP ARROW - Jump")
    print("  1 / 2 / 3 - Select difficulty")
    print("  R - Restart")
    print("  M - Return to Menu")
    print("  Q - Quit")
    print("\n" + "=" * 50)
    print("Jump over rocks, crystals, and dragons!")
    print("The longer you survive, the faster it gets!")
    print("=" * 50 + "\n")
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
