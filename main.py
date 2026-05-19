import asyncio
import pygame
import random
import sys
import platform

# Constants
WIDTH, HEIGHT = 800, 600
SNAKE_SIZE = 20
INITIAL_FPS = 7
MAX_FPS = 25
SPEED_INCREMENT = 0.5

# Colors
COLOR_BG = (20, 20, 30)
COLOR_DEFAULT_SNAKE = (50, 200, 50)
COLOR_DEFAULT_SNAKE_HEAD = (80, 255, 80)
COLOR_FOOD = (230, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_UI_BG = (40, 40, 60)
COLOR_ACCENT = (255, 200, 0)
COLOR_D_PAD = (255, 255, 255, 100)

# Localization
class Locale:
    def __init__(self):
        self.lang = 'it'
        self.translations = {
            'it': {
                'title': 'Snake Web',
                'score': 'Punteggio: {}',
                'high_score': 'Record: {}',
                'game_over': 'HAI PERSO!',
                'restart': 'Premi C per giocare o Q per uscire',
                'start': 'Premi SPAZIO per iniziare',
                'lang_toggle': 'L: Lingua (IT)',
                'resume': 'Premi P per riprendere',
                'paused': 'PAUSA',
            },
            'en': {
                'title': 'Snake Web',
                'score': 'Score: {}',
                'high_score': 'High Score: {}',
                'game_over': 'GAME OVER!',
                'restart': 'Press C to play or Q to quit',
                'start': 'Press SPACE to start',
                'lang_toggle': 'L: Language (EN)',
                'resume': 'Press P to resume',
                'paused': 'PAUSED',
            }
        }

    def get(self, key, *args):
        text = self.translations[self.lang].get(key, key)
        if args:
            return text.format(*args)
        return text

    def toggle(self):
        self.lang = 'en' if self.lang == 'it' else 'it'

locale = Locale()

class Snake:
    def __init__(self, sprites=None):
        self.length = 1
        self.positions = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.next_direction = self.direction
        self.score = 0
        self.color = COLOR_DEFAULT_SNAKE
        self.head_color = COLOR_DEFAULT_SNAKE_HEAD
        self.sprites = sprites

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        self.direction = self.next_direction
        cur = self.get_head_position()
        x, y = cur
        if self.direction == pygame.K_UP:
            y -= SNAKE_SIZE
        elif self.direction == pygame.K_DOWN:
            y += SNAKE_SIZE
        elif self.direction == pygame.K_LEFT:
            x -= SNAKE_SIZE
        elif self.direction == pygame.K_RIGHT:
            x += SNAKE_SIZE

        new = (x, y)
        if len(self.positions) > 2 and new in self.positions[2:]:
            return False
        elif x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
            return True

    def reset(self):
        self.length = 1
        self.positions = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.next_direction = self.direction
        self.score = 0
        self.color = COLOR_DEFAULT_SNAKE
        self.head_color = COLOR_DEFAULT_SNAKE_HEAD

    def change_color(self):
        # Generate a random bright color
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        self.color = (max(0, r-30), max(0, g-30), max(0, b-30))
        self.head_color = (r, g, b)

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            if self.sprites:
                if i == 0:
                    # Head sprite
                    sprite = self.sprites['head']
                    angle = 0
                    if self.direction == pygame.K_UP: angle = 0
                    elif self.direction == pygame.K_DOWN: angle = 180
                    elif self.direction == pygame.K_LEFT: angle = 90
                    elif self.direction == pygame.K_RIGHT: angle = -90

                    rotated_head = pygame.transform.rotate(sprite, angle)
                    # Apply tint
                    if self.head_color != COLOR_DEFAULT_SNAKE_HEAD:
                        temp = rotated_head.copy()
                        temp.fill(self.head_color, special_flags=pygame.BLEND_RGB_MULT)
                        surface.blit(temp, (p[0], p[1]))
                    else:
                        surface.blit(rotated_head, (p[0], p[1]))
                else:
                    # Body sprite (simplification: using a generic body part)
                    sprite = self.sprites['body']
                    if self.color != COLOR_DEFAULT_SNAKE:
                        temp = sprite.copy()
                        temp.fill(self.color, special_flags=pygame.BLEND_RGB_MULT)
                        surface.blit(temp, (p[0], p[1]))
                    else:
                        surface.blit(sprite, (p[0], p[1]))
            else:
                color = self.head_color if i == 0 else self.color
                r = pygame.Rect((p[0], p[1]), (SNAKE_SIZE, SNAKE_SIZE))
                pygame.draw.rect(surface, color, r, border_radius=4)

class Food:
    def __init__(self, snake_positions, sprite=None):
        self.position = (0, 0)
        self.sprite = sprite
        self.randomize_position(snake_positions)

    def randomize_position(self, snake_positions):
        while True:
            self.position = (random.randint(0, (WIDTH // SNAKE_SIZE) - 1) * SNAKE_SIZE,
                             random.randint(0, (HEIGHT // SNAKE_SIZE) - 1) * SNAKE_SIZE)
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        if self.sprite:
            surface.blit(self.sprite, (self.position[0], self.position[1]))
        else:
            r = pygame.Rect((self.position[0], self.position[1]), (SNAKE_SIZE, SNAKE_SIZE))
            pygame.draw.rect(surface, COLOR_FOOD, r, border_radius=10)

def get_high_score():
    try:
        if platform.system() == 'Emscripten':
            from js import localStorage
            hs = localStorage.getItem('snake_high_score')
            return int(hs) if hs else 0
        else:
            return 0 # Local storage not easily available in desktop without extra libs
    except:
        return 0

def set_high_score(score):
    try:
        if platform.system() == 'Emscripten':
            from js import localStorage
            localStorage.setItem('snake_high_score', str(score))
    except:
        pass

class VirtualDPad:
    def __init__(self):
        self.size = 60
        self.padding = 20
        self.color = (200, 200, 200, 100)
        self.active_color = (255, 255, 255, 180)

        # Center of the pad
        self.center_x = 120
        self.center_y = HEIGHT - 120

        self.buttons = {
            pygame.K_UP: pygame.Rect(self.center_x - self.size//2, self.center_y - self.size * 1.5, self.size, self.size),
            pygame.K_DOWN: pygame.Rect(self.center_x - self.size//2, self.center_y + self.size * 0.5, self.size, self.size),
            pygame.K_LEFT: pygame.Rect(self.center_x - self.size * 1.5, self.center_y - self.size//2, self.size, self.size),
            pygame.K_RIGHT: pygame.Rect(self.center_x + self.size * 0.5, self.center_y - self.size//2, self.size, self.size)
        }

    def draw(self, surface):
        for key, rect in self.buttons.items():
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, self.color, (0, 0, rect.width, rect.height), border_radius=10)

            # Draw arrows
            center = (rect.width // 2, rect.height // 2)
            if key == pygame.K_UP:
                pygame.draw.polygon(s, (255,255,255), [(center[0], 10), (10, rect.height-10), (rect.width-10, rect.height-10)])
            elif key == pygame.K_DOWN:
                pygame.draw.polygon(s, (255,255,255), [(center[0], rect.height-10), (10, 10), (rect.width-10, 10)])
            elif key == pygame.K_LEFT:
                pygame.draw.polygon(s, (255,255,255), [(10, center[1]), (rect.width-10, 10), (rect.width-10, rect.height-10)])
            elif key == pygame.K_RIGHT:
                pygame.draw.polygon(s, (255,255,255), [(rect.width-10, center[1]), (10, 10), (10, rect.height-10)])

            surface.blit(s, (rect.x, rect.y))

    def get_key(self, pos):
        for key, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return key
        return None

async def main():
    pygame.init()
    # Use a slightly smaller window if needed, but 800x600 is usually fine.
    # We can try to make it more responsive by checking window size in JS if we wanted to.
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Web - Jules")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("bahnschrift", 25)
    large_font = pygame.font.SysFont("bahnschrift", 50)

    # Load sprites
    snake_sprites = None
    food_sprite = None
    try:
        assets = pygame.image.load("assets.jpg").convert_alpha()
        # The sprite sheet is roughly 320x256.
        # Apple is at bottom left (roughly) -> Actually let's slice based on common sense from the image
        # Slices are 64x64
        food_sprite = pygame.transform.scale(assets.subsurface((0, 192, 64, 64)), (SNAKE_SIZE, SNAKE_SIZE))
        head_sprite = pygame.transform.scale(assets.subsurface((192, 0, 64, 64)), (SNAKE_SIZE, SNAKE_SIZE))
        body_sprite = pygame.transform.scale(assets.subsurface((192, 128, 64, 64)), (SNAKE_SIZE, SNAKE_SIZE))
        snake_sprites = {'head': head_sprite, 'body': body_sprite}
    except Exception as e:
        print(f"Could not load sprites: {e}")

    snake = Snake(sprites=snake_sprites)
    food = Food(snake.positions, sprite=food_sprite)
    high_score = get_high_score()
    dpad = VirtualDPad()
    fps = INITIAL_FPS

    is_mobile = False
    if platform.system() == 'Emscripten':
        try:
            from js import window
            if "Mobi" in window.navigator.userAgent:
                is_mobile = True
        except:
            pass

    state = "MENU" # MENU, PLAYING, GAME_OVER, PAUSED

    def draw_grid():
        for x in range(0, WIDTH, SNAKE_SIZE):
            pygame.draw.line(screen, (30, 30, 45), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, SNAKE_SIZE):
            pygame.draw.line(screen, (30, 30, 45), (0, y), (WIDTH, y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle Touch/Mouse events for D-pad
            if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN) and (is_mobile or state == "PLAYING"):
                pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (event.x * WIDTH, event.y * HEIGHT)

                if state == "MENU":
                    state = "PLAYING"
                    snake.reset()
                    fps = INITIAL_FPS
                elif state == "PLAYING":
                    key = dpad.get_key(pos)
                    if key:
                        if key == pygame.K_UP and snake.direction != pygame.K_DOWN:
                            snake.next_direction = pygame.K_UP
                        elif key == pygame.K_DOWN and snake.direction != pygame.K_UP:
                            snake.next_direction = pygame.K_DOWN
                        elif key == pygame.K_LEFT and snake.direction != pygame.K_RIGHT:
                            snake.next_direction = pygame.K_LEFT
                        elif key == pygame.K_RIGHT and snake.direction != pygame.K_LEFT:
                            snake.next_direction = pygame.K_RIGHT
                elif state == "GAME_OVER":
                    state = "PLAYING"
                    snake.reset()
                    food.randomize_position(snake.positions)

            elif event.type == pygame.KEYDOWN:
                if state == "MENU":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        snake.reset()
                        fps = INITIAL_FPS
                    elif event.key == pygame.K_l:
                        locale.toggle()
                elif state == "PLAYING":
                    if event.key == pygame.K_UP and snake.direction != pygame.K_DOWN:
                        snake.next_direction = pygame.K_UP
                    elif event.key == pygame.K_DOWN and snake.direction != pygame.K_UP:
                        snake.next_direction = pygame.K_DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != pygame.K_RIGHT:
                        snake.next_direction = pygame.K_LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != pygame.K_LEFT:
                        snake.next_direction = pygame.K_RIGHT
                    elif event.key == pygame.K_p:
                        state = "PAUSED"
                elif state == "PAUSED":
                    if event.key == pygame.K_p:
                        state = "PLAYING"
                elif state == "GAME_OVER":
                    if event.key == pygame.K_c:
                        state = "PLAYING"
                        snake.reset()
                        fps = INITIAL_FPS
                        food.randomize_position(snake.positions)
                    elif event.key == pygame.K_q:
                        state = "MENU"

        screen.fill(COLOR_BG)
        draw_grid()

        if state == "PLAYING":
            if not snake.update():
                state = "GAME_OVER"
                if snake.score > high_score:
                    high_score = snake.score
                    set_high_score(high_score)

            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 1

                # Speed increase
                fps = min(MAX_FPS, fps + SPEED_INCREMENT)

                # Color change every 5 food
                if snake.score % 5 == 0:
                    snake.change_color()

                food.randomize_position(snake.positions)

            snake.draw(screen)
            food.draw(screen)

            if is_mobile:
                dpad.draw(screen)

            score_text = font.render(locale.get('score', snake.score), True, COLOR_TEXT)
            screen.blit(score_text, (10, 10))

        elif state == "MENU":
            title = large_font.render(locale.get('title'), True, COLOR_ACCENT)
            start_msg = font.render(locale.get('start'), True, COLOR_TEXT)
            lang_msg = font.render(locale.get('lang_toggle'), True, COLOR_TEXT)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
            screen.blit(start_msg, (WIDTH // 2 - start_msg.get_width() // 2, HEIGHT // 2))
            screen.blit(lang_msg, (WIDTH // 2 - lang_msg.get_width() // 2, HEIGHT // 2 + 50))

        elif state == "PAUSED":
            snake.draw(screen)
            food.draw(screen)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0,0))
            pause_title = large_font.render(locale.get('paused'), True, COLOR_ACCENT)
            resume_msg = font.render(locale.get('resume'), True, COLOR_TEXT)
            screen.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(resume_msg, (WIDTH // 2 - resume_msg.get_width() // 2, HEIGHT // 2 + 20))

        elif state == "GAME_OVER":
            over_title = large_font.render(locale.get('game_over'), True, COLOR_FOOD)
            score_msg = font.render(locale.get('score', snake.score), True, COLOR_TEXT)
            hs_msg = font.render(locale.get('high_score', high_score), True, COLOR_ACCENT)
            restart_msg = font.render(locale.get('restart'), True, COLOR_TEXT)

            screen.blit(over_title, (WIDTH // 2 - over_title.get_width() // 2, HEIGHT // 3))
            screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 2))
            screen.blit(hs_msg, (WIDTH // 2 - hs_msg.get_width() // 2, HEIGHT // 2 + 40))
            screen.blit(restart_msg, (WIDTH // 2 - restart_msg.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(fps)

if __name__ == "__main__":
    asyncio.run(main())
