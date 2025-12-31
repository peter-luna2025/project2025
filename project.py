import pygame, random
import sys
import math
from PIL import Image,ImageOps

import os

os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
WIDTH, HEIGHT = 720, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1Card-Poker")
clock = pygame.time.Clock()
FPS = 60
STEP_DELAY = 2 # seconds per step

WHITE, BLACK, GRAY, GREEN, BLUE, GOLD, RED = (
    (255, 255, 255),
    (0, 0, 0),
    (200, 200, 200),
    (40, 160, 80),
    (50, 100, 220),
    (230, 190, 60),
    (200, 0, 0)
)
font = pygame.font.SysFont("arial", 28)

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["C", "D", "H", "S"]  # ordered lowest → highest
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}
SUIT_VALUE = {"C": 1, "D": 2, "H": 3, "S": 4}


def load_card_images():
    images = {}
    for r in RANKS:
        for s in SUITS:
            key = f"{r}{s}"
            path = f"assets/cards/{key}.png"
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (60, 90))
                images[key] = img
            except pygame.error as e:
                print(f"Could not load {path}: {e}")
    return images


def text_to_symbol(s):
    return {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}[s]


def card_text_to_display(c):
    return f"{c[:-1]}{text_to_symbol(c[-1])}"


def create_deck():
    return [f"{r}{s}" for r in RANKS for s in SUITS]


def card_value(card):
    """Return (rank, suit) tuple for comparison."""
    return (RANK_VALUE[card[:-1]], SUIT_VALUE[card[-1]])


class Button:
    def __init__(self, text, rect, bg=BLUE):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.bg = bg
        self.hover = False
        self.selected = False
        self.enabled = True

    def draw(self, surf):
        color = self.bg
        if not self.enabled:
            color = GRAY
        elif self.selected:
            color = GOLD
        elif self.hover:
            color = (
                min(self.bg[0] + 20, 255),
                min(self.bg[1] + 20, 255),
                min(self.bg[2] + 20, 255),
            )
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=8)
        label = font.render(self.text, True, WHITE)
        surf.blit(
            label,
            (
                self.rect.centerx - label.get_width() // 2,
                self.rect.centery - label.get_height() // 2,
            ),
        )

    def handle(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(e.pos)
        if (
            self.enabled
            and e.type == pygame.MOUSEBUTTONDOWN
            and e.button == 1
            and self.rect.collidepoint(e.pos)
        ):
            return True
        return False
        
class Game:
    def __init__(self):
        self.players = []
        self.tokens = {}
        self.pot = 0
        self.winner = None

    def is_valid_name(self, name):
        name = name.strip()

        # Must be at least 2 characters
        if len(name) < 2:
            return False

        # Reject "0" or numeric-only names
        if name == "0" or name.isnumeric():
            return False

        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False

        # Allowed characters: letters, spaces, hyphens, apostrophes
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
        if not all(c in allowed for c in name):
            return False

        return True


    def take_antes(self, ante):
        for name in self.players:
            self.tokens[name] -= ante
            self.pot += ante

    def award_pot(self, winner_name):
        self.tokens[winner_name] += self.pot
        self.pot = 0


class SetupRoutine:
    def __init__(self):
        self.target_count = None
        self.players = []
        self.tokens = {}
        self.pot = 0
        self.deck = []
        self.highcard_draws = {}
        self.winner = None
        self.step = 0
        self.timer = 0
        self.running = False
        self.game_over = False
        self.last_removed = []
        self.btn_restart = Button("Restart", (510, 570, 160, 42), bg=RED)
        self.btn_restart.enabled = False


        self.card_images = load_card_images()

        self.btn_2 = Button("2 players", (510, 120, 160, 42), bg=GREEN)
        self.btn_3 = Button("3 players", (510, 180, 160, 42), bg=GREEN)
        self.btn_4 = Button("4 players", (510, 240, 160, 42), bg=GREEN)
        self.btn_start = Button("Start Game", (510, 450, 160, 42), bg=BLUE)
        self.btn_start.enabled = False
        self.btn_add = Button("Add name", (510, 390, 160, 42), bg=BLUE)
        self.input_active = False
        self.input_text = ""
        self.btn_next = Button("Next Round", (510, 510, 160, 42), bg=GREEN)
        self.btn_next.enabled = False

    def is_valid_name(self, name):
        name = name.strip()

        if len(name) < 2:
            return False
        if name == "0" or name.isnumeric():
            return False
        if not any(c.isalpha() for c in name):
            return False

        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
        if not all(c in allowed for c in name):
            return False

        return True

    def add_player(self, name):
        name = name.strip()

        if not self.is_valid_name(name):
            print("Invalid name:", repr(name))
            return

        if name in self.players:
            print("Name already taken")
            return

        if len(self.players) >= self.target_count:
            return

        self.players.append(name)
        self.tokens[name] = 20
        self.update_start_enabled()


    # ---------------------------------------------------------
    # NEW: Proper ante + pot awarding methods
    # ---------------------------------------------------------
    def take_antes(self, ante):
        for name in self.players:
            if self.tokens[name] >= ante:
                self.tokens[name] -= ante
                self.pot += ante

    def award_pot(self, winner_name):
        self.tokens[winner_name] += self.pot
        self.pot = 0

    # ---------------------------------------------------------

    def set_player_count(self, n):
        self.target_count = n
        self.players = []
        self.tokens = {}
        self.pot = 0
        self.deck = []
        self.highcard_draws = {}
        self.winner = None
        self.step = 0
        self.timer = 0
        self.running = False

        for b in (self.btn_2, self.btn_3, self.btn_4):
            b.selected = False
        {2: self.btn_2, 3: self.btn_3, 4: self.btn_4}[n].selected = True

        if n in (3, 4):
            self.btn_start.enabled = True
        else:
            self.update_start_enabled()

    def update_start_enabled(self):
        if self.target_count == 2:
            self.btn_start.enabled = len(self.players) == 2 and not self.running
        elif self.target_count in (3, 4):
            self.btn_start.enabled = True

    def add_player(self, name):
        if self.target_count is None:
            return

        name = name.strip()

        if not self.is_valid_name(name):
            (f"Invalid name: {repr(name)}")
            return

        if name in self.players:
            print("Name already taken")
            return

        if len(self.players) >= self.target_count:
            return

        self.players.append(name)
        self.tokens[name] = 20
        self.update_start_enabled()

    def start_sequence(self):
        if not self.btn_start.enabled:
            return
        self.running = True
        self.step = 0
        self.timer = 0
        self.pot = 0
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.highcard_draws = {}
        self.winner = None

    def get_player_positions(self):
        pot_x, pot_y = 270, 260
        radius = 150

        angle_map = {
            1: [270],
            2: [270, 180],
            3: [270, 180, 90],
            4: [270, 180, 90, 0],
        }

        player_count = len(self.players)
        if player_count == 0:
            return []

        angles = angle_map[player_count]
        positions = []
        for deg in angles:
            rad = math.radians(deg)
            x = pot_x + int(radius * math.cos(rad))
            y = pot_y + int(radius * math.sin(rad))
            positions.append((x, y))

        return positions

    def draw(self, surf):
        surf.fill(WHITE)

        for b in (
            self.btn_2,
            self.btn_3,
            self.btn_4,
            self.btn_start,
            self.btn_add,
            self.btn_next,
        ):
            b.draw(surf)

        y = 60
        surf.blit(
            font.render(
                f"Players ({len(self.players)}/{self.target_count or '-'})", True, BLACK
            ),
            (50, y),
        )
        y += 40

        positions = self.get_player_positions()
        if len(positions) != len(self.players):
            return

        for idx, p in enumerate(self.players):
            x, y = positions[idx]

            card_width = 60
            card_height = 90

            if p in self.highcard_draws:
                card = self.highcard_draws[p]
                card_x = x - card_width // 2
                card_y = y

                if card in self.card_images:
                    surf.blit(self.card_images[card], (card_x, card_y))
                else:
                    pygame.draw.rect(
                        surf, GRAY, (card_x, card_y, card_width, card_height)
                    )
                    surf.blit(
                        font.render(card_text_to_display(card), True, BLACK),
                        (card_x + 10, card_y + card_height // 2),
                    )

                label = font.render(f"{p} ({self.tokens[p]}t)", True, BLACK)
                surf.blit(label, (x - label.get_width() // 2, card_y + card_height + 10))

            else:
                label = font.render(f"{p} ({self.tokens[p]}t)", True, BLACK)
                surf.blit(label, (x - label.get_width() // 2, y))

        if self.input_active:
            pygame.draw.rect(surf, GRAY, (460, 390, 210, 40), border_radius=6)
            pygame.draw.rect(surf, BLACK, (460, 390, 210, 40), 2, border_radius=6)
            surf.blit(font.render(f"Name: {self.input_text}", True, BLACK), (460, 390))

        msg = ""
        if not self.running:
            if self.target_count in (3, 4) and len(self.players) < self.target_count:
                msg = "Add names to start."
            elif self.target_count == 2 and len(self.players) < 2:
                msg = "Add both names to start."
        else:
            if self.step == 0:
                msg = "Shuffle deck"
            elif self.step == 1:
                msg = f"Ante tokens (Pot={self.pot})"
            elif self.step == 2:
                msg = "High card draw"
            elif self.step == 3:
                msg = "Determine winner"
            elif self.step == 4:
                msg = f"Winner is {self.winner}"
        if self.last_removed:
            elim_msg = font.render(
                f"Eliminated: {', '.join(self.last_removed)} (0 tokens)",
                True,
                RED
            )
            surf.blit(elim_msg, (50, HEIGHT - 100))

        if self.game_over:
            over_msg = font.render(
                f"GAME OVER! Winner: {self.players[0]}",
                True,
                RED
            )
            surf.blit(over_msg, (50, HEIGHT - 140))

        if msg:
            surf.blit(font.render(msg, True, BLACK), (50, HEIGHT - 40))

        pygame.draw.circle(surf, GOLD, (270, 260), 24)
        pot_label = font.render(str(self.pot), True, BLACK)
        surf.blit(pot_label, (270 - pot_label.get_width() // 2, 245))

    def update(self):
        self.update_start_enabled()
        if not self.running:
            return
        self.timer += 1

        if self.step == 0 and self.timer > FPS * STEP_DELAY:
            self.deck = create_deck()
            random.shuffle(self.deck)
            self.step = 1
            self.timer = 0

        elif self.step == 1 and self.timer > FPS * STEP_DELAY:
            self.pot = 0
            self.take_antes(5)      # <-- FIXED
            self.step = 2
            self.timer = 0

        elif self.step == 2 and self.timer > FPS * STEP_DELAY:
            self.highcard_draws = {}
            for name in self.players:
                self.highcard_draws[name] = self.deck.pop()
            self.step = 3
            self.timer = 0
            print("Deck size before draw:", len(self.deck))

        elif self.step == 3 and self.timer > FPS * STEP_DELAY:
            best = max(
                self.highcard_draws, key=lambda p: card_value(self.highcard_draws[p])
            )
            self.winner = best
            self.step = 4
            self.timer = 0

        elif self.step == 4 and self.timer > FPS * STEP_DELAY:
            self.award_pot(self.winner)

            removed = self.remove_bankrupt_players()   # <-- correct call
            if removed:
                self.last_removed = removed
            else:
                self.last_removed = []

        if len(self.players) == 1:
            self.game_over = True
            self.running = False
            self.btn_restart.enabled = True
            return

        self.btn_next.enabled = True

    def remove_bankrupt_players(self):
        removed = []
        for name in list(self.players):
            if self.tokens[name] <= 0:
                removed.append(name)
                del self.tokens[name]
                self.players.remove(name)
        return removed


        # If only one player remains → GAME OVER
        if len(self.players) == 1:
            self.game_over = True
            self.running = False
            self.btn_restart.enabled = True
            return

            self.btn_next.enabled = True

        if self.game_over:
            over_msg = font.render(f"GAME OVER! Winner: {self.players[0]}", True, RED)
            surf.blit(over_msg, (50, HEIGHT - 100))
            self.btn_restart.draw(surf)


    def handle_event(self, e):
        if self.btn_next.handle(e) and self.btn_next.enabled:
            self.start_sequence()
            self.btn_next.enabled = False

        if self.btn_2.handle(e):
            self.set_player_count(2)
        if self.btn_3.handle(e):
            self.set_player_count(3)
        if self.btn_4.handle(e):
            self.set_player_count(4)
        if self.btn_start.handle(e):
            self.start_sequence()
        if self.btn_add.handle(e):
            if self.target_count and len(self.players) < self.target_count:
                self.input_active = True
                self.input_text = ""
        if self.input_active and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                self.add_player(self.input_text.strip())
                self.input_active = False
                self.input_text = ""
            elif e.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < 16 and e.unicode.isprintable():
                    self.input_text += e.unicode

        if self.btn_restart.handle(e) and self.btn_restart.enabled:
            self.__init__()   # full reset
            return

def main():
    setup = SetupRoutine()
    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            setup.handle_event(e)
        setup.update()
        setup.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
