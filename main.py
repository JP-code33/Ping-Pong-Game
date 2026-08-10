import pygame
import asyncio
import random
import math
pygame.init()

WIDTH, HEIGHT = 900,600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
FPS = 60
WHITE = (255,255,255)
BLACK = (0,0,0)
CYAN = (0,255,255)
GRAY = (100,100,100)
DARK_BLUE = (5, 10, 25)
RED = (255, 0, 0)
BLUE = (0, 40, 70)
GLOWBLUE = (0, 100, 140)
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7
FONT = pygame.font.SysFont("comicsans", 50)
WINNING_SCORE = 10

class Paddle:
    COLOR = WHITE
    VEL = 5

    def __init__(self,x,y,width,height):
        self.x = self.original_x = x
        self.y = self.original_y = y 
        self.width = width
        self.height = height

    def draw(self,win):
        glowSurface = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)

        for i in range(12, 0, -2):
            alpha = int(35 *(1 - i / 12))
            pygame.draw.rect(glowSurface, (0, 255, 255, alpha), (15 - i, 15 - i, self.width + i * 2, self.height + i *2), border_radius=6 + i)
            WIN.blit(glowSurface, (self.x - 15, self.y - 15))
            pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height), border_radius=5)

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    MAX_VEL = 10
    START_VEL = 6
    COLOR = CYAN

    def __init__(self, x, y, radius):
        self.x = self.original_X = x 
        self.y = self.original_Y = y
        self.radius = radius
        self.x_vel = self.START_VEL
        self.y_vel = 0
        self.trail =[]
        self.hit_effect = None
        self.hit_effect_timer = 0

    def draw(self, win):

        for i , (trailX, trailY) in enumerate(self.trail):
            alpha = int(120 * (i / len(self.trail)))

            trailSurface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(trailSurface, (0, 255, 255, alpha), (self.radius * 2, self.radius * 2), max(2, self.radius - 2))
            WIN.blit(trailSurface, (trailX - self.radius * 2, trailY - self.radius * 2))


        glowSurface = pygame.Surface((self.radius * 8, self.radius * 8), pygame.SRCALPHA)
        center = self.radius * 4

        for size in range(self.radius * 4, self.radius, -2):
            alpha = int(40 * (1 - size / (self.radius * 4)))

            pygame.draw.circle(glowSurface, (0, 255, 255, alpha), (center, center), size)

        WIN.blit(glowSurface, (self.x - center, self.y - center))

        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

        if self.hit_effect_timer > 0:
            drawHitEffect(win, self.hit_effect[0], self.hit_effect[1])
            self.hit_effect_timer -= 1

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.trail.append((self.x, self.y))

        if len(self.trail) > 8:
            self.trail.pop

    def reset(self):
        self.x = self.original_X
        self.y = self.original_Y
        self.y_vel = 0
        self.x_vel *= -1
        self.trail.clear()
        self.hit_effect = None
        self.hit_effect_timer = 0

def drawButton(win, text, x, y, width, height, mouse_pos):
    buttonRect = pygame.Rect(x, y, width, height)

    hovered = buttonRect.collidepoint(mouse_pos)
    if hovered:
        color = (0, 220, 220)
        borderColor = WHITE

        glowSurface = pygame.Surface((width + 40, height + 40), pygame.SRCALPHA)

        for i in range(15, 0, -2):
            alpha = int(50 * (1 - i / 15))

            pygame.draw.rect(glowSurface, (0, 255, 255, alpha), (20 - i, 20 - i, width + i * 2, height + i * 2), border_radius=10 + i)
            WIN.blit(glowSurface, (x - 20, y - 20))
    else:
        color = (0, 150, 170)
        borderColor = CYAN

    pygame.draw.rect(win, color, buttonRect, border_radius=10)
    pygame.draw.rect(win, borderColor, buttonRect, width=2, border_radius=10)

    font = pygame.font.SysFont("comicsans", 28)

    textSurface = font.render(text, True, BLACK)
    WIN.blit(textSurface, (x + width // 2 - textSurface.get_width() // 2, y + height // 2 - textSurface.get_height() // 2))

def drawMenuBackground(win):
    win.fill(DARK_BLUE)

    for y in range(HEIGHT):
        ratio = y / HEIGHT

        r = int(5 + 5 * ratio)
        g = int(10 + 20 * ratio)
        b = int(25 + 35 * ratio)

        pygame.draw.line(win, (r, g, b), (0, y), (WIDTH, y))

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(win, (10, 35, 55), (0, y), (WIDTH, y), 1)

    for x in range(0, WIDTH, 50):
        pygame.draw.line(win, (10, 35, 55), (x, 10), (x, HEIGHT), 1)

def drawDecoration(win):
    centerX = WIDTH // 2
    centerY = 175

    pygame.draw.rect(win, RED, (centerX - 100, centerY - 18, 8, 36), border_radius=4)
    pygame.draw.rect(win, RED, (centerX + 90, centerY - 18, 8, 36), border_radius=4)
    pygame.draw.circle(win, WHITE, (centerX, centerY), 6)
    pygame.draw.line(win, (0, 100, 120), (centerX - 45, centerY), (centerX - 10, centerY), 2)

async def mainMenu():
    while True:
        mouse_pos = pygame.mouse.get_pos()
        drawMenuBackground(WIN)

        title = FONT.render("PING PONG", True, CYAN)

        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        drawDecoration(WIN)

        friendButton = pygame.Rect(WIDTH//2 - 175, 200, 350, 70)
        computerButton = pygame.Rect(WIDTH//2 - 175, 300, 350, 70)
        howToPlayButton = pygame.Rect(WIDTH//2 - 175, 400, 350, 70)

        drawButton(WIN, "Play with friend", friendButton.x, friendButton.y, friendButton.width, friendButton.height, mouse_pos)
        drawButton(WIN, "Play against computer", computerButton.x, computerButton.y, computerButton.width, computerButton.height, mouse_pos)
        drawButton(WIN, "How to play", howToPlayButton.x, howToPlayButton.y, howToPlayButton.width, howToPlayButton.height, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if friendButton.collidepoint(event.pos):
                        return "friend"
                    if computerButton.collidepoint(event.pos):
                        return "computer"
                    if howToPlayButton.collidepoint(event.pos):
                        await howToPlay()

        await asyncio.sleep(0)

async def howToPlay():
    while True:
        mouse_pos = pygame.mouse.get_pos()
        WIN.fill(BLACK)

        title = FONT.render("How to play", True, CYAN)

        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        instructions = [("Player 1:", "W & S"), ("Player 2:", "Up Arrow & Down Arrow"), 
                        ("Move:", "Use the paddle to hit the ball"), ("Score:", "Score 10 points and WIN!!"), 
                        ("Computer:", "Easy, Medium or Hard"), ("Ball speed:", "The ball gets faster!")]

        y = 120
        for heading, text in instructions:
            headingText = pygame.font.SysFont("comicsans", 25).render(heading, True, CYAN)
            textRender = pygame.font.SysFont("comicsans", 22).render(text, True, WHITE)

            WIN.blit(headingText, (100, y))
            WIN.blit(textRender, (300, y))
            y += 50

        backButton = pygame.Rect(WIDTH // 2 - 100, 430, 200, 50)
        drawButton(WIN, "Back", backButton.x, backButton.y, backButton.width, backButton.height, mouse_pos)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if backButton.collidepoint(event.pos):
                        return

        await asyncio.sleep(0)

def drawEasyDifficultyEffect(win, buttonRect, mouse_pos):
    if not buttonRect.collidepoint(mouse_pos):
        return 

    centerX = buttonRect.centerx
    centerY = buttonRect.centery

    green = (50, 255, 120)
    lightGreen = (120, 255, 190)

    bubbles = [(180, -20, 5), (-155, 15, 3), (-135, -35, 4), (-110, 45, 3), (180, -20, 5), (155, 15, 3), (135, -35, 4), (110, 45, 3), (-170, -55, 3), (170, -55, 3)]

    for offestX, offestY, radius in bubbles:
        pygame.draw.circle(win, green, (centerX + offestX, centerY + offestY), radius)
        pygame.draw.circle(win, lightGreen, (centerX + offestX, centerY + offestY), max(1, radius // 2))

def drawMediumDifficultyEffect(win, buttonRect, mouse_pos):
    if not buttonRect.collidepoint(mouse_pos):
            return 

    centerX = buttonRect.centerx
    centerY = buttonRect.centery 
    ticks = pygame.time.get_ticks()
    flicker = (ticks // 100) % 2

    yellow = (255, 220, 40)
    brightYellow = (255, 255, 150)

    if flicker == 0:
        color = yellow
    else:
        color = brightYellow

    leftLightning = [(centerX - 105, centerY - 35), (centerX - 75, centerY - 35), (centerX - 90, centerY - 5), (centerX - 65, centerY - 5), (centerX - 110, centerY + 40), (centerX - 92, centerY + 8), (centerX - 115, centerY + 8)]
    rightLightning = [(centerX + 105, centerY - 35), (centerX + 75, centerY - 35), (centerX + 90, centerY - 5), (centerX + 65, centerY - 5), (centerX + 110, centerY + 40), (centerX + 92, centerY + 8), (centerX + 115, centerY + 8)]

    pygame.draw.polygon(win, color, leftLightning)
    pygame.draw.polygon(win, color, rightLightning)

    pygame.draw.circle(win, brightYellow, (centerX, centerY), 4)

def drawHardDifficultyEffect(win, buttonRect, mouse_pos):
    if not buttonRect.collidepoint(mouse_pos):
        return

    centerX = buttonRect.centerx
    baseY = buttonRect.centery
    ticks = pygame.time.get_ticks()
    movement = int(5 * math.sin(ticks * 0.005))

    darkRed = (100, 0, 0)
    red = (255, 30, 30)

    leftHorn = [(centerX - 90, baseY + 10 + movement), (centerX - 125, baseY - 20 + movement), (centerX - 135, baseY - 55 + movement), (centerX - 115, baseY - 35 + movement), (centerX - 90, baseY - 5 + movement)]
    rightHorn = [(centerX + 90, baseY + 10 + movement), (centerX + 125, baseY - 20 + movement), (centerX + 135, baseY - 55 + movement), (centerX + 115, baseY - 35 + movement), (centerX + 90, baseY - 5 + movement)]

    pygame.draw.polygon(win, darkRed, leftHorn)
    pygame.draw.polygon(win, darkRed, rightHorn)

    pygame.draw.polygon(win, red, [(centerX - 91, baseY + 5 + movement), (centerX - 119, baseY - 20 + movement), (centerX - 128, baseY - 43 + movement), (centerX - 112, baseY - 27 + movement), (centerX - 91, baseY + movement)])
    pygame.draw.polygon(win, red, [(centerX + 91, baseY + 5 + movement), (centerX + 119, baseY - 20 + movement), (centerX + 128, baseY - 43 + movement), (centerX + 112, baseY - 27 + movement), (centerX + 91, baseY + movement)])

async def difficultyMenu():
    while True:
        mouse_pos = pygame.mouse.get_pos()
        WIN.fill(BLACK)

        title = FONT.render("Select difficulty", True, CYAN)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        easyButton = pygame.Rect(WIDTH // 2 - 150, 160, 300, 60)
        mediumButton = pygame.Rect(WIDTH // 2 - 150, 250, 300, 60)
        hardButton = pygame.Rect(WIDTH // 2 - 150, 340, 300, 60)

        drawEasyDifficultyEffect(WIN, easyButton, mouse_pos)
        drawButton(WIN, "Easy", easyButton.x, easyButton.y, easyButton.width, easyButton.height, mouse_pos)
        drawMediumDifficultyEffect(WIN, mediumButton, mouse_pos)
        drawButton(WIN, "Medium", mediumButton.x, mediumButton.y, mediumButton.width, mediumButton.height, mouse_pos)
        drawHardDifficultyEffect(WIN, hardButton, mouse_pos)
        drawButton(WIN, "Hard", hardButton.x, hardButton.y, hardButton.width, hardButton.height, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if easyButton.collidepoint(event.pos):
                        return "easy"
                    if mediumButton.collidepoint(event.pos):
                        return "medium"
                    if hardButton.collidepoint(event.pos):
                        return "hard"

        await asyncio.sleep(0)

def draw(win, paddles, ball, leftScore, rightScore):
    win.fill(BLACK)

    leftScoreText = FONT.render(f"{leftScore}", 1, WHITE)
    rightScoreText = FONT.render(f"{rightScore}", 1, WHITE)
    win.blit(leftScoreText, (WIDTH//4 - leftScoreText.get_width()//2, 20))
    win.blit(rightScoreText, (WIDTH * (3/4) - rightScoreText.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT//20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//30))

    ball.draw(win)

    pygame.display.update()

def drawHitEffect(win, x, y):
    glowSurface = pygame.Surface((100, 100), pygame.SRCALPHA)

    for radius in range(35, 5, -4):
        alpha = int(80 * (1 - radius / 35))

        pygame.draw.circle(glowSurface, (0, 255, 255, alpha), (50, 50), radius)

    WIN.blit(glowSurface, (x - 50, y - 50))

    for angle in range(0, 360, 45):
        rad = math.radians(angle)

        startX = x + math.cos(rad) * 8
        startY = y + math.sin(rad) * 8

        endX = x + math.cos(rad) * 28
        endY = y + math.sin(rad) * 28

        pygame.draw.line(win, WHITE, (startX, startY), (endX, endY), 3)

    pygame.draw.circle(win, CYAN, (x, y), 9)

def handle_collision(ball, leftPaddle, rightPaddle):
    if ball.y + ball.radius >= HEIGHT:
        ball.y_vel *= -1
    elif ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if ball.y >= leftPaddle.y and ball.y <= leftPaddle.y + leftPaddle.height:
            if ball.x - ball.radius <= leftPaddle.x + leftPaddle.width:
                ball.x_vel *= -1
                ball.hit_effect = (ball.x, ball.y)
                ball.hit_effect_timer = 15
                ball.x_vel *= 1.05
                ball.x_vel = min(abs(ball.x_vel), ball.MAX_VEL) * (1 if ball.x_vel > 0 else -1)
    
                middle_y = leftPaddle.y + leftPaddle.height / 2
                difference_in_y = middle_y - ball.y 
                reduction_factor = (leftPaddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                randomChange = random.uniform(-1.2, 1.2)
                ball.y_vel = -y_vel + randomChange

    else:
        if ball.y >= rightPaddle.y and ball.y <= rightPaddle.y + rightPaddle.height:
            if ball.x + ball.radius >= rightPaddle.x:
                ball.x_vel *= -1
                ball.hit_effect = (ball.x, ball.y)
                ball.hit_effect_timer = 15
                ball.x_vel *= 1.05
                ball.x_vel = min(abs(ball.x_vel), ball.MAX_VEL) * (1 if ball.x_vel > 0 else -1)

                middle_y = rightPaddle.y +rightPaddle.height / 2
                difference_in_y = middle_y - ball.y 
                reduction_factor = (rightPaddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                randomChange = random.uniform(-1.2, 1.2)
                ball.y_vel = -y_vel + randomChange
 
def handle_paddle_movement(keys, leftPaddle, rightPaddle):
    if keys[pygame.K_w] and leftPaddle.y - leftPaddle.VEL >= 0:
        leftPaddle.move(up=True)
    if keys[pygame.K_s] and leftPaddle.y + leftPaddle.VEL + leftPaddle.height <= HEIGHT:
        leftPaddle.move(up=False)

    if keys[pygame.K_UP] and rightPaddle.y - rightPaddle.VEL >= 0:
        rightPaddle.move(up=True)
    if keys[pygame.K_DOWN] and rightPaddle.y + rightPaddle.VEL + rightPaddle.height <= HEIGHT:
        rightPaddle.move(up=False)

def handleComputer(paddle, ball, difficulty):
    paddle_center = paddle.y + paddle.height / 2

    if difficulty == "easy":
        reactionDistance = 60
        computerSpeed = 2.5
        mistake = random.randint(-35, 35)
    elif difficulty == "medium":
        reactionDistance = 30
        computerSpeed = 3.5
        mistake = random.randint(-15, 15)
    else:
        reactionDistance = 10
        computerSpeed = 7
        mistake = random.randint(-5, 5)

    target_y = ball.y + mistake

    if paddle_center < target_y - reactionDistance:
        paddle.y += computerSpeed
    elif paddle_center > target_y + reactionDistance:
        paddle.y -= computerSpeed

async def pauseMenu():
    while True:
        mouse_pos = pygame.mouse.get_pos()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        WIN.blit(overlay, (0, 0))

        title = FONT.render("Paused", True, CYAN)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        resumeButton = pygame.Rect(WIDTH // 2 - 150, 200, 300, 60)
        drawButton(WIN, "Resume", resumeButton.x, resumeButton.y, resumeButton.width, resumeButton.height, mouse_pos)

        menuButton = pygame.Rect(WIDTH // 2 - 150, 290, 300, 60)
        drawButton(WIN, "Main Menu", menuButton.x, menuButton.y, menuButton.width, menuButton.height, mouse_pos)

        quitButton = pygame.Rect(WIDTH // 2 -150, 380, 300, 60)
        drawButton(WIN, "Quit", quitButton.x, quitButton.y, quitButton.width, quitButton.height, mouse_pos)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if resumeButton.collidepoint(event.pos):
                        return "resume"
                    if menuButton.collidepoint(event.pos):
                        return "menu"
                    if quitButton.collidepoint(event.pos):
                        return "quit"

        await asyncio.sleep(0)


async def main(game_mode, difficulty=None):
    run = True
    clock = pygame.time.Clock()

    leftPaddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    rightPaddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    leftScore = 0
    rightScore = 0

    while run:
        clock.tick(FPS)
        draw(WIN, [leftPaddle, rightPaddle], ball, leftScore, rightScore)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_result = await pauseMenu()

                    if pause_result == "quit":
                        run = False
                        break
                    elif pause_result == "menu":
                        return "menu"

        keys = pygame.key.get_pressed() 
        handle_paddle_movement(keys, leftPaddle, rightPaddle)
        if game_mode == "computer":
            handleComputer(rightPaddle, ball, difficulty)

        ball.move()
        handle_collision(ball, leftPaddle, rightPaddle)

        won = False

        if ball.x < 0:
            rightScore += 1
            ball.reset()
        elif ball.x > WIDTH:
            leftScore += 1
            ball.reset()

        if leftScore >= WINNING_SCORE:
            won = True
            win_text = "Left Player Won!"
        elif rightScore >= WINNING_SCORE:
            won = True
            win_text = "Right Player Won!"


        if won:
            text = FONT.render(win_text, 1, CYAN)
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            pygame.display.update()
            await asyncio.sleep(5)

            ball.reset()
            leftPaddle.reset()
            rightPaddle.reset()
            leftScore = 0
            rightScore = 0

        await asyncio.sleep(0)


if __name__ == "__main__":

    while True:
        game_mode = asyncio.run(mainMenu())

        if game_mode is None:
            break
        if game_mode == "friend":
            result = asyncio.run(main("friend"))
        elif game_mode == "computer":
            difficulty = asyncio.run(difficultyMenu())

            if difficulty is None:
                break

            result = asyncio.run(main("computer", difficulty))

            if result == "quit":
                break

        pygame.quit()