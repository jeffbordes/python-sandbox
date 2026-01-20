import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Match")

# Colors
BG_DARK = (15, 23, 42)
BG_MEDIUM = (30, 41, 59)
CARD_BLUE = (37, 99, 235)
CARD_BLUE_LIGHT = (59, 130, 246)
WHITE = (255, 255, 255)
GRAY = (148, 163, 184)
GREEN = (16, 185, 129)
GREEN_LIGHT = (52, 211, 153)
GREEN_BG = (6, 78, 59)
RED = (239, 68, 68)
PURPLE = (147, 51, 234)

# Fonts
try:
    FONT_LARGE = pygame.font.Font(None, 72)
    FONT_MEDIUM = pygame.font.Font(None, 48)
    FONT_SMALL = pygame.font.Font(None, 36)
    FONT_TINY = pygame.font.Font(None, 24)
except:
    FONT_LARGE = pygame.font.SysFont('arial', 54)
    FONT_MEDIUM = pygame.font.SysFont('arial', 36)
    FONT_SMALL = pygame.font.SysFont('arial', 27)
    FONT_TINY = pygame.font.SysFont('arial', 18)

# Card data
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

DIFFICULTIES = {
    'easy': {'pairs': 6, 'cols': 3, 'rows': 4, 'label': 'Easy', 'desc': '6 pairs'},
    'medium': {'pairs': 8, 'cols': 4, 'rows': 4, 'label': 'Medium', 'desc': '8 pairs'},
    'hard': {'pairs': 10, 'cols': 5, 'rows': 4, 'label': 'Hard', 'desc': '10 pairs'},
    'expert': {'pairs': 12, 'cols': 4, 'rows': 6, 'label': 'Expert', 'desc': '12 pairs'}
}


class Card:
    def __init__(self, rank, suit, pair_id, x, y, width, height):
        self.rank = rank
        self.suit = suit
        self.pair_id = pair_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.flipped = False
        self.matched = False
        self.flip_progress = 0  # 0 = back, 1 = front
        self.flip_speed = 0.15
        self.target_flip = 0
        
    def is_red(self):
        return self.suit in ['♥', '♦']
    
    def update(self):
        # Animate flip
        if self.flip_progress < self.target_flip:
            self.flip_progress = min(self.flip_progress + self.flip_speed, self.target_flip)
        elif self.flip_progress > self.target_flip:
            self.flip_progress = max(self.flip_progress - self.flip_speed, self.target_flip)
    
    def flip_to_front(self):
        self.target_flip = 1
        self.flipped = True
        
    def flip_to_back(self):
        self.target_flip = 0
        self.flipped = False
        
    def draw(self, surface):
        # Calculate flip scale (1 -> 0 -> 1 for flip effect)
        if self.flip_progress <= 0.5:
            scale = 1 - (self.flip_progress * 2)
            showing_front = False
        else:
            scale = (self.flip_progress - 0.5) * 2
            showing_front = True
        
        # Card dimensions with flip effect
        scaled_width = max(2, int(self.width * scale))
        x_offset = (self.width - scaled_width) // 2
        
        rect = pygame.Rect(self.x + x_offset, self.y, scaled_width, self.height)
        
        if showing_front:
            # Draw front of card
            if self.matched:
                bg_color = (236, 253, 245)
                border_color = GREEN
            else:
                bg_color = WHITE
                border_color = (229, 231, 235)
            
            pygame.draw.rect(surface, bg_color, rect, border_radius=8)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)
            
            if self.matched:
                # Glow effect
                glow_rect = rect.inflate(6, 6)
                pygame.draw.rect(surface, GREEN, glow_rect, 3, border_radius=10)
            
            # Draw rank and suit
            if scale > 0.3:  # Only draw text when card is mostly visible
                color = RED if self.is_red() else (31, 41, 55)
                
                # Rank
                rank_text = FONT_MEDIUM.render(self.rank, True, color)
                rank_rect = rank_text.get_rect(centerx=rect.centerx, centery=rect.centery - 15)
                surface.blit(rank_text, rank_rect)
                
                # Suit
                suit_text = FONT_SMALL.render(self.suit, True, color)
                suit_rect = suit_text.get_rect(centerx=rect.centerx, centery=rect.centery + 20)
                surface.blit(suit_text, suit_rect)
        else:
            # Draw back of card
            pygame.draw.rect(surface, CARD_BLUE, rect, border_radius=8)
            pygame.draw.rect(surface, CARD_BLUE_LIGHT, rect, 2, border_radius=8)
            
            # Inner border pattern
            inner_rect = rect.inflate(-12, -12)
            if inner_rect.width > 0 and inner_rect.height > 0:
                pygame.draw.rect(surface, (255, 255, 255, 50), inner_rect, 1, border_radius=4)
            
            # Question mark
            if scale > 0.3:
                q_text = FONT_SMALL.render("?", True, (255, 255, 255, 100))
                q_rect = q_text.get_rect(center=rect.center)
                surface.blit(q_text, q_rect)
    
    def contains_point(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and 
                self.y <= pos[1] <= self.y + self.height)


class Button:
    def __init__(self, x, y, width, height, text, subtitle=None, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.subtitle = subtitle
        self.color = color or (255, 255, 255, 20)
        self.hovered = False
        
    def draw(self, surface):
        # Background
        color = tuple(min(c + 20, 255) for c in self.color[:3]) if self.hovered else self.color
        if len(color) == 3:
            color = (*color, 255)
        
        # Create surface with alpha
        btn_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, (*color[:3], 30 if not self.hovered else 50), 
                        btn_surface.get_rect(), border_radius=12)
        pygame.draw.rect(btn_surface, (*WHITE, 40), 
                        btn_surface.get_rect(), 1, border_radius=12)
        surface.blit(btn_surface, self.rect)
        
        # Text
        text_surf = FONT_SMALL.render(self.text, True, WHITE)
        if self.subtitle:
            text_rect = text_surf.get_rect(centerx=self.rect.centerx, centery=self.rect.centery - 10)
            surface.blit(text_surf, text_rect)
            
            sub_surf = FONT_TINY.render(self.subtitle, True, GRAY)
            sub_rect = sub_surf.get_rect(centerx=self.rect.centerx, centery=self.rect.centery + 15)
            surface.blit(sub_surf, sub_rect)
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        
        # Arrow for menu buttons
        if self.subtitle:
            arrow = FONT_SMALL.render("→", True, GRAY if not self.hovered else WHITE)
            arrow_rect = arrow.get_rect(centery=self.rect.centery, right=self.rect.right - 20)
            surface.blit(arrow, arrow_rect)
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class MemoryGame:
    def __init__(self):
        self.state = 'menu'  # menu, playing, victory
        self.difficulty = None
        self.cards = []
        self.flipped = []
        self.matched_count = 0
        self.attempts = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.disabled = False
        self.disable_until = 0
        self.buttons = []
        self.setup_menu()
        
    def setup_menu(self):
        self.buttons = []
        difficulties = list(DIFFICULTIES.items())
        start_y = 280
        for i, (key, config) in enumerate(difficulties):
            btn = Button(
                SCREEN_WIDTH // 2 - 150,
                start_y + i * 70,
                300, 55,
                config['label'],
                config['desc']
            )
            btn.difficulty_key = key
            self.buttons.append(btn)
    
    def setup_victory_buttons(self):
        self.buttons = []
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - 150, 420, 300, 50,
            "Play Again", color=GREEN
        ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - 150, 485, 300, 50,
            "Change Difficulty"
        ))
        self.buttons[0].action = 'play_again'
        self.buttons[1].action = 'menu'
    
    def start_game(self, difficulty_key):
        self.difficulty = difficulty_key
        config = DIFFICULTIES[difficulty_key]
        self.matched_count = 0
        self.attempts = 0
        self.flipped = []
        self.disabled = False
        self.start_time = time.time()
        
        # Create deck
        all_cards = [(rank, suit) for suit in SUITS for rank in RANKS]
        random.shuffle(all_cards)
        selected = all_cards[:config['pairs']]
        
        deck = []
        for i, (rank, suit) in enumerate(selected):
            deck.append((rank, suit, i))
            deck.append((rank, suit, i))
        random.shuffle(deck)
        
        # Calculate card layout
        cols, rows = config['cols'], config['rows']
        padding = 20
        top_margin = 120
        gap = 10
        
        available_width = SCREEN_WIDTH - padding * 2
        available_height = SCREEN_HEIGHT - top_margin - padding - 50
        
        card_width = (available_width - gap * (cols - 1)) // cols
        card_height = (available_height - gap * (rows - 1)) // rows
        
        # Maintain aspect ratio (roughly 3:4)
        max_card_width = int(card_height * 0.7)
        if card_width > max_card_width:
            card_width = max_card_width
            
        # Center the grid
        grid_width = card_width * cols + gap * (cols - 1)
        grid_height = card_height * rows + gap * (rows - 1)
        start_x = (SCREEN_WIDTH - grid_width) // 2
        start_y = top_margin + (available_height - grid_height) // 2
        
        # Create card objects
        self.cards = []
        for i, (rank, suit, pair_id) in enumerate(deck):
            row = i // cols
            col = i % cols
            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)
            self.cards.append(Card(rank, suit, pair_id, x, y, card_width, card_height))
        
        self.state = 'playing'
        self.buttons = []
        
    def handle_click(self, pos):
        if self.state == 'menu':
            for btn in self.buttons:
                if btn.is_clicked(pos):
                    self.start_game(btn.difficulty_key)
                    return
                    
        elif self.state == 'playing':
            # Back button
            if pygame.Rect(20, 15, 80, 30).collidepoint(pos):
                self.state = 'menu'
                self.setup_menu()
                return
                
            if self.disabled:
                return
                
            for i, card in enumerate(self.cards):
                if card.contains_point(pos) and not card.flipped and not card.matched:
                    card.flip_to_front()
                    self.flipped.append(i)
                    
                    if len(self.flipped) == 2:
                        self.attempts += 1
                        self.disabled = True
                        
                        card1 = self.cards[self.flipped[0]]
                        card2 = self.cards[self.flipped[1]]
                        
                        if card1.pair_id == card2.pair_id:
                            # Match!
                            self.disable_until = time.time() + 0.5
                        else:
                            # No match
                            self.disable_until = time.time() + 0.9
                    return
                    
        elif self.state == 'victory':
            for btn in self.buttons:
                if btn.is_clicked(pos):
                    if btn.action == 'play_again':
                        self.start_game(self.difficulty)
                    else:
                        self.state = 'menu'
                        self.setup_menu()
                    return
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for btn in self.buttons:
            btn.update(mouse_pos)
            
        if self.state == 'playing':
            self.elapsed_time = time.time() - self.start_time
            
            for card in self.cards:
                card.update()
            
            # Check if disable period is over
            if self.disabled and time.time() >= self.disable_until:
                card1 = self.cards[self.flipped[0]]
                card2 = self.cards[self.flipped[1]]
                
                if card1.pair_id == card2.pair_id:
                    card1.matched = True
                    card2.matched = True
                    self.matched_count += 1
                else:
                    card1.flip_to_back()
                    card2.flip_to_back()
                
                self.flipped = []
                self.disabled = False
                
                # Check for victory
                if self.matched_count == DIFFICULTIES[self.difficulty]['pairs']:
                    self.state = 'victory'
                    self.setup_victory_buttons()
    
    def draw_gradient_bg(self, color1, color2):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = tuple(int(color1[i] + (color2[i] - color1[i]) * ratio) for i in range(3))
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def draw_menu(self):
        self.draw_gradient_bg(BG_DARK, BG_MEDIUM)
        
        # Title
        emoji = FONT_LARGE.render("🃏", True, WHITE)
        screen.blit(emoji, emoji.get_rect(centerx=SCREEN_WIDTH // 2, centery=100))
        
        title = FONT_LARGE.render("Memory Match", True, WHITE)
        screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=170))
        
        subtitle = FONT_TINY.render("Find all the matching pairs", True, GRAY)
        screen.blit(subtitle, subtitle.get_rect(centerx=SCREEN_WIDTH // 2, centery=220))
        
        for btn in self.buttons:
            btn.draw(screen)
    
    def draw_game(self):
        self.draw_gradient_bg(BG_DARK, BG_MEDIUM)
        
        # Header
        back_text = FONT_TINY.render("← Menu", True, GRAY)
        screen.blit(back_text, (20, 20))
        
        title = FONT_SMALL.render("Memory Match", True, WHITE)
        screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, centery=25))
        
        # Stats bar
        config = DIFFICULTIES[self.difficulty]
        stats_rect = pygame.Rect(50, 55, SCREEN_WIDTH - 100, 50)
        
        # Stats background
        pygame.draw.rect(screen, (255, 255, 255), stats_rect, border_radius=10)
        
        # Progress bar
        progress_rect = pygame.Rect(stats_rect.x + 10, stats_rect.y + 8, stats_rect.width - 20, 6)
        pygame.draw.rect(screen, (229, 231, 235), progress_rect, border_radius=3)
        
        progress = self.matched_count / config['pairs']
        if progress > 0:
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, 
                                   int(progress_rect.width * progress), progress_rect.height)
            pygame.draw.rect(screen, GREEN, fill_rect, border_radius=3)
        
        # Stats text
        stats_y = stats_rect.y + 32
        
        # Matches
        matches_text = FONT_SMALL.render(f"{self.matched_count}/{config['pairs']}", True, GREEN)
        screen.blit(matches_text, matches_text.get_rect(centerx=stats_rect.x + stats_rect.width // 6, centery=stats_y))
        matches_label = FONT_TINY.render("MATCHES", True, GRAY)
        screen.blit(matches_label, matches_label.get_rect(centerx=stats_rect.x + stats_rect.width // 6, centery=stats_y + 18))
        
        # Attempts
        attempts_text = FONT_SMALL.render(str(self.attempts), True, CARD_BLUE)
        screen.blit(attempts_text, attempts_text.get_rect(centerx=stats_rect.centerx, centery=stats_y))
        attempts_label = FONT_TINY.render("ATTEMPTS", True, GRAY)
        screen.blit(attempts_label, attempts_label.get_rect(centerx=stats_rect.centerx, centery=stats_y + 18))
        
        # Time
        mins = int(self.elapsed_time) // 60
        secs = int(self.elapsed_time) % 60
        time_str = f"{mins}:{secs:02d}"
        time_text = FONT_SMALL.render(time_str, True, PURPLE)
        screen.blit(time_text, time_text.get_rect(centerx=stats_rect.x + stats_rect.width * 5 // 6, centery=stats_y))
        time_label = FONT_TINY.render("TIME", True, GRAY)
        screen.blit(time_label, time_label.get_rect(centerx=stats_rect.x + stats_rect.width * 5 // 6, centery=stats_y + 18))
        
        # Draw cards
        for card in self.cards:
            card.draw(screen)
    
    def draw_victory(self):
        self.draw_gradient_bg(GREEN_BG, (6, 95, 70))
        
        config = DIFFICULTIES[self.difficulty]
        perfect = config['pairs']
        
        if self.attempts == perfect:
            emoji, message, sub = "🏆", "Perfect Score!", "Incredible memory!"
        elif self.attempts <= perfect * 1.5:
            emoji, message, sub = "⭐", "Excellent!", "Great memory skills"
        elif self.attempts <= perfect * 2:
            emoji, message, sub = "👍", "Good Job!", "Nice work"
        else:
            emoji, message, sub = "💪", "Complete!", "Keep practicing"
        
        # Emoji
        emoji_text = FONT_LARGE.render(emoji, True, WHITE)
        screen.blit(emoji_text, emoji_text.get_rect(centerx=SCREEN_WIDTH // 2, centery=120))
        
        # Message
        msg_text = FONT_LARGE.render(message, True, WHITE)
        screen.blit(msg_text, msg_text.get_rect(centerx=SCREEN_WIDTH // 2, centery=190))
        
        sub_text = FONT_SMALL.render(sub, True, GREEN_LIGHT)
        screen.blit(sub_text, sub_text.get_rect(centerx=SCREEN_WIDTH // 2, centery=240))
        
        # Stats box
        box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 280, 300, 100)
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (255, 255, 255, 25), box_surface.get_rect(), border_radius=12)
        screen.blit(box_surface, box_rect)
        
        # Attempts
        att_text = FONT_MEDIUM.render(str(self.attempts), True, WHITE)
        screen.blit(att_text, att_text.get_rect(centerx=box_rect.x + 75, centery=box_rect.y + 40))
        att_label = FONT_TINY.render("Attempts", True, GREEN_LIGHT)
        screen.blit(att_label, att_label.get_rect(centerx=box_rect.x + 75, centery=box_rect.y + 70))
        
        # Divider
        pygame.draw.line(screen, (255, 255, 255, 50), 
                        (box_rect.centerx, box_rect.y + 20), 
                        (box_rect.centerx, box_rect.y + 80), 1)
        
        # Time
        mins = int(self.elapsed_time) // 60
        secs = int(self.elapsed_time) % 60
        time_str = f"{mins}:{secs:02d}"
        time_text = FONT_MEDIUM.render(time_str, True, WHITE)
        screen.blit(time_text, time_text.get_rect(centerx=box_rect.x + 225, centery=box_rect.y + 40))
        time_label = FONT_TINY.render("Time", True, GREEN_LIGHT)
        screen.blit(time_label, time_label.get_rect(centerx=box_rect.x + 225, centery=box_rect.y + 70))
        
        # Buttons
        for btn in self.buttons:
            btn.draw(screen)
    
    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'victory':
            self.draw_victory()


def main():
    clock = pygame.time.Clock()
    game = MemoryGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
