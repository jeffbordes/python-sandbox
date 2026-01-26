#!/usr/bin/env python3
"""
🦄 UNICORN DASH ENHANCED - A magical endless runner game
Guide your unicorn over obstacles and collect stars!
Controls: SPACE/UP to jump (double jump!), DOWN to duck, P to pause, R to restart, Q to quit
"""

import pygame
import random
import sys
import math
import json
import os

# Initialize Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# =============================================================================
# CONFIGURATION - Externalized for easy tuning
# =============================================================================
CONFIG = {
    'screen': {
        'width': 900,
        'height': 500,
        'ground_height': 60,
        'fps': 60
    },
    'unicorn': {
        'width': 70,
        'height': 60,
        'x_position': 100,
        'duck_height': 35,
        'max_jumps': 2  # Double jump enabled
    },
    'collectibles': {
        'star_value': 50,
        'coin_value': 25,
        'spawn_chance': 0.015,
        'powerup_spawn_chance': 0.005
    },
    'powerups': {
        'shield_duration': 300,  # frames
        'magnet_duration': 400,
        'magnet_range': 150
    },
    'audio': {
        'enabled': True,
        'music_volume': 0.3,
        'sfx_volume': 0.5
    },
    'effects': {
        'screen_shake_intensity': 8,
        'screen_shake_duration': 15,
        'death_animation_duration': 60
    }
}

# Screen settings from config
SCREEN_WIDTH = CONFIG['screen']['width']
SCREEN_HEIGHT = CONFIG['screen']['height']
GROUND_HEIGHT = CONFIG['screen']['ground_height']
FPS = CONFIG['screen']['fps']

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

# Collectible colors
COIN_GOLD = (255, 200, 50)
COIN_SHINE = (255, 245, 180)
SHIELD_BLUE = (100, 180, 255)
MAGNET_RED = (255, 80, 80)

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

# High score file path
HIGH_SCORE_FILE = os.path.join(os.path.expanduser('~'), '.unicorn_dash_scores.json')


# =============================================================================
# SOUND MANAGER - Generates procedural sounds using pygame
# =============================================================================
class SoundManager:
    """Manages game audio with procedurally generated sounds"""
    
    def __init__(self):
        self.enabled = CONFIG['audio']['enabled']
        self.sfx_volume = CONFIG['audio']['sfx_volume']
        self.sounds = {}
        
        if self.enabled:
            self._generate_sounds()
    
    def _generate_sounds(self):
        """Generate procedural sound effects"""
        sample_rate = 22050
        
        # Jump sound - quick rising tone
        self.sounds['jump'] = self._create_tone(sample_rate, 0.15, [400, 600, 800], 'triangle')
        
        # Double jump - higher pitch
        self.sounds['double_jump'] = self._create_tone(sample_rate, 0.12, [600, 900, 1100], 'triangle')
        
        # Coin collect - pleasant chime
        self.sounds['coin'] = self._create_tone(sample_rate, 0.2, [880, 1100, 1320], 'sine')
        
        # Star collect - sparkly sound
        self.sounds['star'] = self._create_tone(sample_rate, 0.25, [1000, 1200, 1400, 1600], 'sine')
        
        # Power-up collect
        self.sounds['powerup'] = self._create_tone(sample_rate, 0.4, [400, 500, 600, 800, 1000], 'sine')
        
        # Hit/death sound - descending harsh tone
        self.sounds['hit'] = self._create_tone(sample_rate, 0.3, [300, 200, 100], 'square')
        
        # Duck/slide sound
        self.sounds['duck'] = self._create_noise(sample_rate, 0.1)
        
    def _create_tone(self, sample_rate, duration, frequencies, wave_type='sine'):
        """Create a tone with frequency sweep"""
        n_samples = int(sample_rate * duration)
        buf = []
        
        for i in range(n_samples):
            t = i / sample_rate
            # Interpolate frequency
            freq_idx = min(int(t / duration * len(frequencies)), len(frequencies) - 1)
            freq = frequencies[freq_idx]
            
            # Generate waveform
            if wave_type == 'sine':
                sample = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'triangle':
                sample = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
            elif wave_type == 'square':
                sample = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            else:
                sample = math.sin(2 * math.pi * freq * t)
            
            # Apply envelope (fade out)
            envelope = 1 - (i / n_samples)
            sample = sample * envelope * 0.3
            
            # Convert to 16-bit
            buf.append(int(sample * 32767))
        
        # Create sound from buffer
        import array
        sound_array = array.array('h', buf)
        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(self.sfx_volume)
        return sound
    
    def _create_noise(self, sample_rate, duration):
        """Create a short noise burst"""
        n_samples = int(sample_rate * duration)
        buf = []
        
        for i in range(n_samples):
            sample = random.uniform(-0.2, 0.2) * (1 - i / n_samples)
            buf.append(int(sample * 32767))
        
        import array
        sound_array = array.array('h', buf)
        sound = pygame.mixer.Sound(buffer=sound_array)
        sound.set_volume(self.sfx_volume * 0.5)
        return sound
    
    def play(self, sound_name):
        """Play a sound by name"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()


# =============================================================================
# PARTICLE EFFECTS
# =============================================================================
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
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            
    def is_dead(self):
        return self.life <= 0


class CollectParticle(Particle):
    """Particle effect for collecting items"""
    
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, 1)
        self.life = random.randint(15, 30)
        self.max_life = self.life


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


# =============================================================================
# COLLECTIBLES
# =============================================================================
class Collectible:
    """Base class for collectible items"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.collected = False
        self.float_offset = random.random() * math.pi * 2
        self.rotation = 0
        
    def update(self, speed):
        self.x -= speed
        self.rotation += 3
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        return self.x + self.width < 0


class Star(Collectible):
    """Star collectible - worth more points"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.value = CONFIG['collectibles']['star_value']
        self.width = 30
        self.height = 30
        
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        float_y = y + math.sin(pygame.time.get_ticks() * 0.008 + self.float_offset) * 5
        
        # Draw glow
        glow_size = 20 + math.sin(pygame.time.get_ticks() * 0.01) * 3
        glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 223, 0, 80), (int(glow_size), int(glow_size)), int(glow_size))
        screen.blit(glow_surf, (x + self.width // 2 - glow_size, float_y + self.height // 2 - glow_size))
        
        # Draw star shape
        center_x = x + self.width // 2
        center_y = int(float_y) + self.height // 2
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90 + self.rotation)
            radius = 12 if i % 2 == 0 else 6
            px = center_x + math.cos(angle) * radius
            py = center_y + math.sin(angle) * radius
            points.append((px, py))
        
        pygame.draw.polygon(screen, STAR_GOLD, points)
        pygame.draw.polygon(screen, (255, 245, 200), points, 2)


class Coin(Collectible):
    """Coin collectible - standard points"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.value = CONFIG['collectibles']['coin_value']
        
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        float_y = y + math.sin(pygame.time.get_ticks() * 0.008 + self.float_offset) * 4
        
        # Spinning effect - width changes
        spin = abs(math.sin(pygame.time.get_ticks() * 0.008))
        width = max(4, int(self.width * spin))
        
        center_x = x + self.width // 2
        center_y = int(float_y) + self.height // 2
        
        # Draw coin
        pygame.draw.ellipse(screen, COIN_GOLD, (center_x - width // 2, center_y - 10, width, 20))
        if width > 8:
            pygame.draw.ellipse(screen, COIN_SHINE, (center_x - width // 4, center_y - 6, width // 2, 12), 2)


# =============================================================================
# POWER-UPS
# =============================================================================
class PowerUp:
    """Base class for power-ups"""
    
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.type = powerup_type
        self.float_offset = random.random() * math.pi * 2
        self.collected = False
        
    def update(self, speed):
        self.x -= speed
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        return self.x + self.width < 0
    
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        float_y = y + math.sin(pygame.time.get_ticks() * 0.006 + self.float_offset) * 6
        
        # Pulsing glow
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 0.5 + 0.5
        glow_size = int(25 + pulse * 10)
        
        if self.type == 'shield':
            color = SHIELD_BLUE
            glow_color = (100, 180, 255, int(80 * pulse))
        else:  # magnet
            color = MAGNET_RED
            glow_color = (255, 100, 100, int(80 * pulse))
        
        # Draw glow
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (x + self.width // 2 - glow_size, int(float_y) + self.height // 2 - glow_size))
        
        # Draw icon
        center_x = x + self.width // 2
        center_y = int(float_y) + self.height // 2
        
        if self.type == 'shield':
            # Shield icon
            shield_points = [
                (center_x, center_y - 12),
                (center_x + 12, center_y - 6),
                (center_x + 10, center_y + 8),
                (center_x, center_y + 14),
                (center_x - 10, center_y + 8),
                (center_x - 12, center_y - 6)
            ]
            pygame.draw.polygon(screen, color, shield_points)
            pygame.draw.polygon(screen, WHITE, shield_points, 2)
        else:
            # Magnet icon
            pygame.draw.arc(screen, color, (center_x - 10, center_y - 10, 20, 20), 0, math.pi, 5)
            pygame.draw.rect(screen, color, (center_x - 10, center_y - 2, 6, 12))
            pygame.draw.rect(screen, color, (center_x + 4, center_y - 2, 6, 12))
            pygame.draw.rect(screen, MAGNET_RED, (center_x - 10, center_y + 6, 6, 4))
            pygame.draw.rect(screen, SHIELD_BLUE, (center_x + 4, center_y + 6, 6, 4))


# =============================================================================
# UNICORN PLAYER
# =============================================================================
class Unicorn:
    """The player-controlled unicorn character"""
    
    def __init__(self, difficulty):
        self.width = CONFIG['unicorn']['width']
        self.height = CONFIG['unicorn']['height']
        self.normal_height = self.height
        self.duck_height = CONFIG['unicorn']['duck_height']
        self.x = CONFIG['unicorn']['x_position']
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.jump_count = 0
        self.max_jumps = CONFIG['unicorn']['max_jumps']
        self.difficulty = difficulty
        self.leg_timer = 0
        self.leg_state = 0
        self.mane_offset = 0
        self.particles = []
        self.rainbow_trail = []
        self.sparkle_timer = 0
        
        # Power-up states
        self.shield_active = False
        self.shield_timer = 0
        self.magnet_active = False
        self.magnet_timer = 0
        
        # Death animation
        self.is_dying = False
        self.death_timer = 0
        self.death_rotation = 0
        self.death_velocity_y = -10
        self.death_velocity_x = 2
        
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        
    def jump(self, sound_manager=None):
        if self.is_dying:
            return False
            
        if self.is_ducking:
            self.stand_up()
            return False
            
        if self.jump_count < self.max_jumps:
            self.velocity_y = DIFFICULTIES[self.difficulty]['jump_strength']
            self.is_jumping = True
            self.jump_count += 1
            
            # Play appropriate sound
            if sound_manager:
                if self.jump_count == 1:
                    sound_manager.play('jump')
                else:
                    sound_manager.play('double_jump')
            
            # Burst of particles on jump
            for _ in range(10 if self.jump_count == 1 else 15):
                self.particles.append(Particle(self.x + 20, self.y + self.height - 10))
            
            return True
        return False
    
    def duck(self, sound_manager=None):
        if not self.is_jumping and not self.is_ducking and not self.is_dying:
            self.is_ducking = True
            self.height = self.duck_height
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            if sound_manager:
                sound_manager.play('duck')
            return True
        return False
    
    def stand_up(self):
        if self.is_ducking:
            self.is_ducking = False
            self.height = self.normal_height
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            
    def start_death_animation(self):
        self.is_dying = True
        self.death_timer = CONFIG['effects']['death_animation_duration']
        self.death_velocity_y = -8
        
    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = CONFIG['powerups']['shield_duration']
        
    def activate_magnet(self):
        self.magnet_active = True
        self.magnet_timer = CONFIG['powerups']['magnet_duration']
        
    def update(self, game_speed):
        # Death animation
        if self.is_dying:
            self.death_timer -= 1
            self.death_rotation += 15
            self.death_velocity_y += 0.5
            self.y += self.death_velocity_y
            self.x += self.death_velocity_x
            return
        
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
            self.jump_count = 0
            
            # Auto stand up when landing
            if self.is_ducking and not pygame.key.get_pressed()[pygame.K_DOWN]:
                self.stand_up()
            
        # Animate legs
        if not self.is_jumping and not self.is_ducking:
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
        
        # Update power-up timers
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                
        if self.magnet_active:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet_active = False
                
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        
        # Apply death rotation if dying
        if self.is_dying:
            self._draw_dying(screen, x, y)
            return
        
        # Draw rainbow trail first (behind unicorn)
        for r in self.rainbow_trail:
            r.draw(screen)
        
        # Draw particles
        for p in self.particles:
            p.draw(screen)
        
        # Draw shield effect if active
        if self.shield_active:
            shield_alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.02))
            shield_surf = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surf, (100, 180, 255, shield_alpha), 
                              (0, 0, self.width + 30, self.height + 30))
            screen.blit(shield_surf, (x - 15, y - 15))
        
        # Draw the unicorn (normal or ducking)
        if self.is_ducking:
            self._draw_ducking(screen, x, y)
        else:
            self._draw_normal(screen, x, y)
            
    def _draw_dying(self, screen, x, y):
        """Draw unicorn during death animation"""
        # Create a rotated surface
        surf = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
        
        # Draw simplified unicorn on surface
        center_x, center_y = self.width // 2 + 20, self.height // 2 + 20
        
        # Body
        pygame.draw.ellipse(surf, UNICORN_WHITE, (center_x - 25, center_y - 10, 50, 30))
        
        # Head
        pygame.draw.ellipse(surf, UNICORN_WHITE, (center_x + 15, center_y - 20, 25, 20))
        
        # X eyes (knocked out)
        pygame.draw.line(surf, BLACK, (center_x + 22, center_y - 15), (center_x + 28, center_y - 9), 2)
        pygame.draw.line(surf, BLACK, (center_x + 28, center_y - 15), (center_x + 22, center_y - 9), 2)
        
        # Rotate the surface
        rotated = pygame.transform.rotate(surf, self.death_rotation)
        rect = rotated.get_rect(center=(x + self.width // 2, y + self.height // 2))
        screen.blit(rotated, rect)
        
        # Falling particles
        if random.random() < 0.5:
            self.particles.append(Particle(x + random.randint(0, self.width), 
                                          y + random.randint(0, self.height),
                                          UNICORN_PINK))
        
        for p in self.particles:
            p.draw(screen)
            
    def _draw_ducking(self, screen, x, y):
        """Draw unicorn in ducking pose"""
        # Flattened body
        pygame.draw.ellipse(screen, UNICORN_WHITE, (x + 5, y + 5, 60, 25))
        
        # Head (lowered)
        pygame.draw.ellipse(screen, UNICORN_WHITE, (x + 50, y, 25, 18))
        
        # Eye
        pygame.draw.ellipse(screen, WHITE, (x + 58, y + 4, 8, 6))
        pygame.draw.circle(screen, (50, 0, 80), (x + 61, y + 6), 2)
        
        # Horn (angled forward)
        pygame.draw.polygon(screen, UNICORN_GOLD, [
            (x + 70, y + 2),
            (x + 85, y - 5),
            (x + 72, y + 8)
        ])
        
        # Tucked legs
        for lx in [x + 15, x + 25, x + 40, x + 50]:
            pygame.draw.ellipse(screen, UNICORN_WHITE, (lx, y + 22, 8, 12))
            pygame.draw.ellipse(screen, UNICORN_PINK, (lx, y + 30, 8, 5))
            
        # Compressed mane
        for i, color in enumerate(MANE_COLORS[:3]):
            pygame.draw.ellipse(screen, color, (x + 35 - i * 8, y + 2, 12, 10))
            
    def _draw_normal(self, screen, x, y):
        """Draw unicorn in normal pose"""
        # === BODY ===
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
            (x + 18, y + 45),
            (x + 28, y + 45),
            (x + 48, y + 45),
            (x + 58, y + 45),
        ]
        
        leg_offsets = [0, 0, 0, 0]
        if not self.is_jumping:
            if self.leg_state == 0:
                leg_offsets = [-5, 5, 5, -5]
            elif self.leg_state == 1:
                leg_offsets = [0, 0, 0, 0]
            elif self.leg_state == 2:
                leg_offsets = [5, -5, -5, 5]
            else:
                leg_offsets = [0, 0, 0, 0]
        else:
            leg_offsets = [-8, -8, 8, 8]
            
        for i, (lx, ly) in enumerate(leg_positions):
            pygame.draw.rect(screen, UNICORN_WHITE, (lx, ly + leg_offsets[i], 6, 18))
            pygame.draw.ellipse(screen, UNICORN_PINK, (lx - 1, ly + 16 + leg_offsets[i], 8, 6))
            
        # === NECK & HEAD ===
        neck_points = [(x + 55, y + 25), (x + 65, y + 5), (x + 75, y + 5), (x + 65, y + 30)]
        pygame.draw.polygon(screen, UNICORN_WHITE, neck_points)
        
        pygame.draw.ellipse(screen, UNICORN_WHITE, (x + 60, y - 5, 30, 22))
        pygame.draw.ellipse(screen, UNICORN_CREAM, (x + 80, y + 2, 15, 12))
        pygame.draw.circle(screen, UNICORN_PINK, (x + 90, y + 8), 2)
        
        # Eye
        pygame.draw.ellipse(screen, WHITE, (x + 70, y + 2, 10, 8))
        pygame.draw.circle(screen, (50, 0, 80), (x + 74, y + 5), 3)
        pygame.draw.circle(screen, WHITE, (x + 75, y + 4), 1)
        
        # Eyelashes
        pygame.draw.line(screen, BLACK, (x + 72, y), (x + 70, y - 3), 1)
        pygame.draw.line(screen, BLACK, (x + 75, y), (x + 75, y - 4), 1)
        pygame.draw.line(screen, BLACK, (x + 78, y + 1), (x + 80, y - 2), 1)
        
        # === HORN ===
        horn_base = (x + 75, y - 3)
        horn_tip = (x + 85, y - 25)
        pygame.draw.polygon(screen, UNICORN_GOLD, [
            (horn_base[0] - 4, horn_base[1]),
            horn_tip,
            (horn_base[0] + 4, horn_base[1])
        ])
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
        if self.is_ducking:
            return pygame.Rect(self.x + 10, self.y + 5, self.width - 15, self.height - 5)
        return pygame.Rect(self.x + 15, self.y + 10, self.width - 25, self.height - 15)


# =============================================================================
# OBSTACLES
# =============================================================================
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
            glow = abs(math.sin(pygame.time.get_ticks() * 0.005 + self.glow_offset)) * 0.5 + 0.5
            
            glow_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.polygon(glow_surf, (148, 0, 211, int(50 * glow)), [
                (self.width // 2 + 10, 5),
                (5, self.height + 10),
                (self.width + 15, self.height + 10)
            ])
            screen.blit(glow_surf, (x - 10, y - 10))
            
            pygame.draw.polygon(screen, CRYSTAL_PURPLE, [
                (x + self.width // 2, y),
                (x, y + self.height),
                (x + self.width, y + self.height)
            ])
            pygame.draw.polygon(screen, CRYSTAL_BLUE, [
                (x + self.width // 2, y),
                (x + self.width // 4, y + self.height * 0.6),
                (x + self.width // 2, y + self.height)
            ])
            pygame.draw.line(screen, WHITE, 
                           (x + self.width // 2, y + 5), 
                           (x + self.width // 3, y + self.height // 2), 2)
        else:
            pygame.draw.ellipse(screen, (50, 50, 50, 100), 
                              (x - 5, y + self.height - 10, self.width + 10, 15))
            
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
            
            highlight_points = [
                (x + self.width * 0.3, y + self.height * 0.3),
                (x + self.width * 0.5, y + self.height * 0.1),
                (x + self.width * 0.6, y + self.height * 0.25),
                (x + self.width * 0.45, y + self.height * 0.4)
            ]
            pygame.draw.polygon(screen, (130, 130, 130), highlight_points)
            
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
    """Flying dragon obstacle - can be ducked under at certain heights"""
    
    def __init__(self, x, force_high=False):
        self.width = 60
        self.height = 40
        self.x = x
        
        # Dragons fly at different heights - some can be ducked under
        if force_high:
            # High flying dragon - must duck
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 60
            self.can_duck_under = True
        else:
            self.y = random.choice([
                SCREEN_HEIGHT - GROUND_HEIGHT - 60,   # Low - duck under
                SCREEN_HEIGHT - GROUND_HEIGHT - 100,  # Medium - jump
                SCREEN_HEIGHT - GROUND_HEIGHT - 140,  # High - easy jump
            ])
            self.can_duck_under = self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - 70
            
        self.wing_timer = 0
        self.wing_angle = 0
        self.fire_particles = []
        
    def update(self, speed):
        self.x -= speed * 1.3
        self.wing_timer += 1
        self.wing_angle = math.sin(self.wing_timer * 0.3) * 30
        
        if random.random() < 0.3:
            self.fire_particles.append({
                'x': self.x - 10,
                'y': self.y + 20 + random.randint(-5, 5),
                'life': 15,
                'size': random.randint(3, 8)
            })
            
        for p in self.fire_particles:
            p['x'] -= speed * 0.5
            p['life'] -= 1
            p['size'] = max(1, p['size'] - 0.3)
        self.fire_particles = [p for p in self.fire_particles if p['life'] > 0]
            
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        
        for p in self.fire_particles:
            color = DRAGON_ORANGE if p['life'] > 8 else DRAGON_RED
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), int(p['size']))
        
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 15, y + 15, 35, 20))
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 40, y + 10, 22, 18))
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 55, y + 15, 12, 10))
        
        pygame.draw.circle(screen, (255, 255, 0), (x + 50, y + 16), 4)
        pygame.draw.circle(screen, BLACK, (x + 51, y + 16), 2)
        
        pygame.draw.polygon(screen, DRAGON_ORANGE, [
            (x + 45, y + 10), (x + 42, y), (x + 48, y + 8)
        ])
        pygame.draw.polygon(screen, DRAGON_ORANGE, [
            (x + 52, y + 10), (x + 52, y + 2), (x + 56, y + 10)
        ])
        
        wing_y_offset = math.sin(math.radians(self.wing_angle)) * 15
        
        wing_points = [
            (x + 25, y + 15),
            (x + 15, y - 10 + wing_y_offset),
            (x + 35, y - 5 + wing_y_offset),
            (x + 40, y + 15)
        ]
        pygame.draw.polygon(screen, DRAGON_ORANGE, wing_points)
        
        pygame.draw.line(screen, DRAGON_RED, (x + 25, y + 15), (x + 20, y - 5 + wing_y_offset), 2)
        pygame.draw.line(screen, DRAGON_RED, (x + 30, y + 15), (x + 30, y - 3 + wing_y_offset), 2)
        
        tail_points = [
            (x + 15, y + 22),
            (x, y + 18),
            (x - 10, y + 25),
            (x + 5, y + 28),
            (x + 15, y + 28)
        ]
        pygame.draw.polygon(screen, DRAGON_RED, tail_points)
        
        pygame.draw.polygon(screen, DRAGON_ORANGE, [
            (x - 10, y + 25), (x - 18, y + 20), (x - 5, y + 28)
        ])
        
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 20, y + 30, 8, 12))
        pygame.draw.ellipse(screen, DRAGON_RED, (x + 35, y + 30, 8, 12))
        
    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 10, self.width - 15, self.height - 15)
    
    def is_off_screen(self):
        return self.x + self.width < 0


# =============================================================================
# BACKGROUND ELEMENTS
# =============================================================================
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


class BackgroundStar:
    """Background twinkling star (renamed to avoid conflict with collectible Star)"""
    
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(20, 180)
        self.twinkle_offset = random.random() * math.pi * 2
        self.size = random.randint(1, 3)
        
    def draw(self, screen):
        brightness = abs(math.sin(pygame.time.get_ticks() * 0.003 + self.twinkle_offset))
        color = tuple(int(255 * brightness) for _ in range(3))
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)


# =============================================================================
# MAIN GAME CLASS
# =============================================================================
class Game:
    """Main game class with all improvements"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🦄 Unicorn Dash Enhanced - Magical Endless Runner!")
        self.clock = pygame.time.Clock()
        
        # Pre-render sky gradient for optimization
        self.sky_surface = self._create_sky_gradient()
        
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
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Load high scores from file
        self.high_scores = self._load_high_scores()
        
        self.difficulty = 'NORMAL'
        self.background_stars = [BackgroundStar() for _ in range(15)]
        
        # Screen shake effect
        self.screen_shake = 0
        self.shake_offset = (0, 0)
        
        # Pause state
        self.paused = False
        
        self.reset_game()
        
    def _create_sky_gradient(self):
        """Pre-render the sky gradient for better performance"""
        sky = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
        for y in range(SCREEN_HEIGHT - GROUND_HEIGHT):
            ratio = y / (SCREEN_HEIGHT - GROUND_HEIGHT)
            r = int(SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio)
            g = int(SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio)
            b = int(SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio)
            pygame.draw.line(sky, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return sky
    
    def _load_high_scores(self):
        """Load high scores from file"""
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'EASY': 0, 'NORMAL': 0, 'HARD': 0}
    
    def _save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f)
        except Exception as e:
            print(f"Could not save high scores: {e}")
        
    def reset_game(self):
        """Reset game state"""
        self.unicorn = Unicorn(self.difficulty)
        self.obstacles = []
        self.collectibles = []
        self.powerups = []
        self.clouds = [Cloud(random.randint(100, 800)) for _ in range(4)]
        self.score = 0
        self.coins_collected = 0
        self.game_speed = DIFFICULTIES[self.difficulty]['initial_speed']
        self.game_over = False
        self.obstacle_timer = 0
        self.ground_offset = 0
        self.show_menu = True
        self.menu_particles = []
        self.collect_particles = []
        self.paused = False
        self.screen_shake = 0
        
    def trigger_screen_shake(self):
        """Start screen shake effect"""
        self.screen_shake = CONFIG['effects']['screen_shake_duration']
        
    def spawn_obstacle(self):
        """Spawn a new obstacle"""
        diff = DIFFICULTIES[self.difficulty]
        
        dragon_chance = min(0.35, self.score / 4000)
        crystal_chance = 0.2
        
        if random.random() < dragon_chance and self.score > 300:
            # Sometimes spawn a low dragon that can be ducked under
            force_high = random.random() < 0.3
            self.obstacles.append(Dragon(SCREEN_WIDTH + 50, force_high))
        elif random.random() < crystal_chance:
            self.obstacles.append(Rock(SCREEN_WIDTH + 50, 'crystal'))
        else:
            self.obstacles.append(Rock(SCREEN_WIDTH + 50))
            
    def spawn_collectible(self):
        """Spawn stars and coins"""
        # Determine y position (can be in air or on ground)
        y_options = [
            SCREEN_HEIGHT - GROUND_HEIGHT - 50,   # Ground level
            SCREEN_HEIGHT - GROUND_HEIGHT - 100,  # Low air
            SCREEN_HEIGHT - GROUND_HEIGHT - 150,  # High air
        ]
        y = random.choice(y_options)
        
        # Star or coin
        if random.random() < 0.3:
            self.collectibles.append(Star(SCREEN_WIDTH + 50, y))
        else:
            self.collectibles.append(Coin(SCREEN_WIDTH + 50, y))
            
    def spawn_powerup(self):
        """Spawn power-ups"""
        y = SCREEN_HEIGHT - GROUND_HEIGHT - random.randint(80, 140)
        powerup_type = random.choice(['shield', 'magnet'])
        self.powerups.append(PowerUp(SCREEN_WIDTH + 50, y, powerup_type))
            
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_high_scores()
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.show_menu:
                    if event.key == pygame.K_1:
                        self.difficulty = 'EASY'
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_2:
                        self.difficulty = 'NORMAL'
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_3:
                        self.difficulty = 'HARD'
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_q:
                        self._save_high_scores()
                        return False
                        
                elif self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_1:
                        self.difficulty = 'EASY'
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_2:
                        self.difficulty = 'NORMAL'
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_3:
                        self.difficulty = 'HARD'
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_m:
                        self.show_menu = True
                    elif event.key == pygame.K_q:
                        self._save_high_scores()
                        return False
                        
                else:  # Normal gameplay
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if not self.paused:
                            self.unicorn.jump(self.sound_manager)
                    elif event.key == pygame.K_DOWN:
                        if not self.paused:
                            self.unicorn.duck(self.sound_manager)
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        self.show_menu = False
                    elif event.key == pygame.K_m:
                        self.show_menu = True
                    elif event.key == pygame.K_q:
                        self._save_high_scores()
                        return False
                        
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and not self.game_over and not self.show_menu:
                    self.unicorn.stand_up()
        
        # Continuous key presses
        keys = pygame.key.get_pressed()
        if not self.game_over and not self.show_menu and not self.paused:
            if keys[pygame.K_DOWN]:
                self.unicorn.duck(self.sound_manager)
            
        return True
        
    def update(self):
        """Update game state"""
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
            intensity = CONFIG['effects']['screen_shake_intensity']
            self.shake_offset = (
                random.randint(-intensity, intensity),
                random.randint(-intensity, intensity)
            )
        else:
            self.shake_offset = (0, 0)
        
        if self.show_menu or self.paused:
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
            
        if self.game_over:
            # Continue death animation
            if self.unicorn.is_dying:
                self.unicorn.update(self.game_speed)
                if self.unicorn.death_timer <= 0:
                    self.unicorn.is_dying = False
            return
            
        diff = DIFFICULTIES[self.difficulty]
        
        # Update unicorn
        self.unicorn.update(self.game_speed)
        
        # Magnet effect - attract nearby collectibles
        if self.unicorn.magnet_active:
            magnet_range = CONFIG['powerups']['magnet_range']
            unicorn_center = (self.unicorn.x + self.unicorn.width // 2, 
                            self.unicorn.y + self.unicorn.height // 2)
            for collectible in self.collectibles:
                dx = unicorn_center[0] - collectible.x
                dy = unicorn_center[1] - collectible.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < magnet_range and dist > 0:
                    speed = 8 * (1 - dist / magnet_range)
                    collectible.x += dx / dist * speed
                    collectible.y += dy / dist * speed
        
        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(self.game_speed)
            
        # Remove off-screen obstacles
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]
        
        # Update collectibles
        for collectible in self.collectibles:
            collectible.update(self.game_speed)
        self.collectibles = [c for c in self.collectibles if not c.is_off_screen() and not c.collected]
        
        # Update power-ups
        for powerup in self.powerups:
            powerup.update(self.game_speed)
        self.powerups = [p for p in self.powerups if not p.is_off_screen() and not p.collected]
        
        # Spawn new obstacles
        self.obstacle_timer += 1
        gap = max(diff['min_obstacle_gap'], 100 - self.score // 150)
        if self.obstacle_timer > gap:
            self.obstacle_timer = 0
            self.spawn_obstacle()
            
        # Spawn collectibles
        if random.random() < CONFIG['collectibles']['spawn_chance']:
            self.spawn_collectible()
            
        # Spawn power-ups (rarer)
        if random.random() < CONFIG['collectibles']['powerup_spawn_chance'] and self.score > 200:
            self.spawn_powerup()
            
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
        self.clouds = [c for c in self.clouds if not c.is_off_screen()]
        if len(self.clouds) < 5 and random.random() < 0.008:
            self.clouds.append(Cloud())
        
        # Update collect particles
        for p in self.collect_particles:
            p.update()
        self.collect_particles = [p for p in self.collect_particles if not p.is_dead()]
            
        # Check collisions with obstacles
        unicorn_rect = self.unicorn.get_rect()
        for obstacle in self.obstacles:
            if unicorn_rect.colliderect(obstacle.get_rect()):
                # Check for shield
                if self.unicorn.shield_active:
                    self.unicorn.shield_active = False
                    self.unicorn.shield_timer = 0
                    self.obstacles.remove(obstacle)
                    # Particle burst
                    for _ in range(20):
                        self.collect_particles.append(
                            CollectParticle(obstacle.x + 20, obstacle.y + 20, SHIELD_BLUE))
                else:
                    self.trigger_screen_shake()
                    self.sound_manager.play('hit')
                    self.unicorn.start_death_animation()
                    self.game_over = True
                    if self.score > self.high_scores[self.difficulty]:
                        self.high_scores[self.difficulty] = self.score
                        self._save_high_scores()
                    return
                    
        # Check collisions with collectibles
        for collectible in self.collectibles:
            if unicorn_rect.colliderect(collectible.get_rect()):
                collectible.collected = True
                self.score += collectible.value
                self.coins_collected += 1
                
                # Play sound and spawn particles
                if isinstance(collectible, Star):
                    self.sound_manager.play('star')
                    for _ in range(15):
                        self.collect_particles.append(
                            CollectParticle(collectible.x, collectible.y, STAR_GOLD))
                else:
                    self.sound_manager.play('coin')
                    for _ in range(10):
                        self.collect_particles.append(
                            CollectParticle(collectible.x, collectible.y, COIN_GOLD))
                        
        # Check collisions with power-ups
        for powerup in self.powerups:
            if unicorn_rect.colliderect(powerup.get_rect()):
                powerup.collected = True
                self.sound_manager.play('powerup')
                
                if powerup.type == 'shield':
                    self.unicorn.activate_shield()
                    for _ in range(20):
                        self.collect_particles.append(
                            CollectParticle(powerup.x, powerup.y, SHIELD_BLUE))
                else:
                    self.unicorn.activate_magnet()
                    for _ in range(20):
                        self.collect_particles.append(
                            CollectParticle(powerup.x, powerup.y, MAGNET_RED))
                
        # Update score and speed
        self.score += 1
        self.game_speed = min(
            diff['max_speed'],
            diff['initial_speed'] + self.score * diff['speed_increment']
        )
        
        # Update ground animation
        self.ground_offset = (self.ground_offset + self.game_speed) % 30
        
    def draw_ground(self):
        """Draw the ground with grass texture"""
        pygame.draw.rect(self.screen, DIRT_BROWN, 
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT + 15, SCREEN_WIDTH, GROUND_HEIGHT - 15))
        
        pygame.draw.rect(self.screen, GRASS_GREEN,
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 18))
        
        for i in range(-1, SCREEN_WIDTH // 15 + 2):
            x = i * 15 - int(self.ground_offset / 2)
            grass_height = 8 + (i % 3) * 3
            pygame.draw.line(self.screen, GRASS_LIGHT,
                           (x, SCREEN_HEIGHT - GROUND_HEIGHT),
                           (x - 3, SCREEN_HEIGHT - GROUND_HEIGHT - grass_height), 2)
            pygame.draw.line(self.screen, GRASS_GREEN,
                           (x + 5, SCREEN_HEIGHT - GROUND_HEIGHT),
                           (x + 7, SCREEN_HEIGHT - GROUND_HEIGHT - grass_height + 2), 2)
                           
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
        
        # Coins collected
        coin_text = self.font_tiny.render(f"COINS: {self.coins_collected}", True, COIN_GOLD)
        self.screen.blit(coin_text, (SCREEN_WIDTH - 200, 75))
        
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
        
        # Power-up indicators
        indicator_y = 95
        if self.unicorn.shield_active:
            remaining = self.unicorn.shield_timer / CONFIG['powerups']['shield_duration']
            pygame.draw.rect(self.screen, SHIELD_BLUE, (20, indicator_y, int(100 * remaining), 8))
            shield_text = self.font_tiny.render("SHIELD", True, SHIELD_BLUE)
            self.screen.blit(shield_text, (20, indicator_y + 10))
            indicator_y += 35
            
        if self.unicorn.magnet_active:
            remaining = self.unicorn.magnet_timer / CONFIG['powerups']['magnet_duration']
            pygame.draw.rect(self.screen, MAGNET_RED, (20, indicator_y, int(100 * remaining), 8))
            magnet_text = self.font_tiny.render("MAGNET", True, MAGNET_RED)
            self.screen.blit(magnet_text, (20, indicator_y + 10))
        
    def draw_menu(self):
        """Draw the main menu"""
        self.screen.blit(self.sky_surface, (0, 0))
        
        for star in self.background_stars:
            star.draw(self.screen)
            
        for cloud in self.clouds:
            cloud.draw(self.screen)
            
        self.draw_ground()
        
        for p in self.menu_particles:
            p.draw(self.screen)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((255, 240, 245))
        self.screen.blit(overlay, (0, 0))
        
        # Title with rainbow effect
        title = "UNICORN DASH"
        title_y = 60
        for i, char in enumerate(title):
            color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            char_surf = self.font_large.render(char, True, color)
            x = SCREEN_WIDTH // 2 - 250 + i * 40
            y = title_y + math.sin(pygame.time.get_ticks() * 0.005 + i * 0.5) * 5
            self.screen.blit(char_surf, (x, y))
        
        # Enhanced subtitle
        subtitle = self.font_small.render("✨ ENHANCED EDITION ✨", True, UNICORN_PURPLE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, title_y + 70))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Unicorn emoji
        emoji_text = self.font_large.render("🦄", True, WHITE)
        self.screen.blit(emoji_text, (SCREEN_WIDTH // 2 - 30, title_y + 95))
        
        # Difficulty selection
        diff_y = 220
        select_text = self.font_small.render("SELECT DIFFICULTY:", True, DARK_GRAY)
        select_rect = select_text.get_rect(center=(SCREEN_WIDTH // 2, diff_y))
        self.screen.blit(select_text, select_rect)
        
        for i, (key, diff) in enumerate(DIFFICULTIES.items()):
            y = diff_y + 40 + i * 40
            text = f"[{i+1}] {diff['name']}"
            color = diff['color']
            
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
        
        # Instructions
        inst_y = 390
        instructions = [
            "SPACE/UP = Jump (Double Jump!)  |  DOWN = Duck",
            "P = Pause  |  R = Restart  |  M = Menu  |  Q = Quit",
            "Collect ⭐ Stars & 🪙 Coins | Get 🛡️ Shields & 🧲 Magnets!",
            "Press 1, 2, or 3 to select difficulty and start!"
        ]
        for i, inst in enumerate(instructions):
            inst_text = self.font_tiny.render(inst, True, GRAY)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y + i * 25))
            self.screen.blit(inst_text, inst_rect)
        
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((255, 240, 245))
        self.screen.blit(overlay, (0, 0))
        
        go_text = self.font_large.render("GAME OVER", True, (180, 80, 120))
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(go_text, go_rect)
        
        score_text = self.font_medium.render(f"Score: {self.score}", True, DARK_GRAY)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)
        
        coins_text = self.font_small.render(f"Coins Collected: {self.coins_collected}", True, COIN_GOLD)
        coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(coins_text, coins_rect)
        
        if self.score >= self.high_scores[self.difficulty] and self.score > 0:
            new_hi = self.font_small.render("✨ NEW HIGH SCORE! ✨", True, UNICORN_GOLD)
            new_hi_rect = new_hi.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55))
            self.screen.blit(new_hi, new_hi_rect)
        
        diff = DIFFICULTIES[self.difficulty]
        diff_text = self.font_tiny.render(f"Difficulty: {diff['name']}", True, diff['color'])
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(diff_text, diff_rect)
        
        restart_text = self.font_tiny.render("SPACE = Play Again | 1/2/3 = Change Difficulty | M = Menu", True, GRAY)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 125))
        self.screen.blit(restart_text, restart_rect)
        
    def draw_pause(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((100, 100, 150))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font_small.render("Press P to Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(resume_text, resume_rect)
        
    def draw(self):
        """Render the game"""
        # Create render surface for screen shake
        render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if self.show_menu:
            self.draw_menu()
            pygame.display.flip()
            return
        
        # Draw sky (pre-rendered for optimization)
        render_surface.blit(self.sky_surface, (0, 0))
        
        # Draw background stars
        for star in self.background_stars:
            star.draw(render_surface)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(render_surface)
            
        # Draw ground
        # Temporarily swap screen reference for ground drawing
        original_screen = self.screen
        self.screen = render_surface
        self.draw_ground()
        self.screen = original_screen
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(render_surface)
            
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(render_surface)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(render_surface)
            
        # Draw collect particles
        for p in self.collect_particles:
            p.draw(render_surface)
            
        # Draw unicorn
        self.unicorn.draw(render_surface)
        
        # Apply screen shake and blit to actual screen
        self.screen.blit(render_surface, self.shake_offset)
        
        # Draw UI (not affected by shake)
        self.draw_ui()
        
        # Draw pause overlay
        if self.paused:
            self.draw_pause()
        
        # Draw game over screen
        if self.game_over and not self.unicorn.is_dying:
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


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    """Entry point"""
    print("\n🦄 UNICORN DASH ENHANCED 🦄")
    print("=" * 55)
    print("A magical endless runner game with new features!")
    print("=" * 55)
    print("\nControls:")
    print("  SPACE / UP ARROW  - Jump (press again for double jump!)")
    print("  DOWN ARROW        - Duck (avoid low-flying dragons)")
    print("  P                 - Pause game")
    print("  1 / 2 / 3         - Select difficulty")
    print("  R                 - Restart")
    print("  M                 - Return to Menu")
    print("  Q                 - Quit")
    print("\nCollectibles:")
    print("  ⭐ Stars           - 50 points")
    print("  🪙 Coins           - 25 points")
    print("\nPower-ups:")
    print("  🛡️ Shield          - Survive one hit")
    print("  🧲 Magnet          - Attract nearby collectibles")
    print("\n" + "=" * 55)
    print("Jump and duck to avoid obstacles!")
    print("Collect stars and coins for bonus points!")
    print("High scores are saved automatically!")
    print("=" * 55 + "\n")
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
