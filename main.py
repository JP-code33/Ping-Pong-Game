import pygame
import asyncio
pygame.init()

WIDTH, HEIGHT = 700,500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
FPS = 60
WHITE = (255,255,255)
BLACK = (0,0,0)
CYAN = (0,255,255)
GRAY = (100,100,100)
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7
FONT = pygame.font.SysFont("comicsans", 50)
WINNING_SCORE = 10

class Paddle:
    COLOR = WHITE
    VEL = 4

    def __init__(self,x,y,width,height):
        self.x = self.original_x = x
        self.y = self.original_y = y 
        self.width = width
        self.height = height

    def draw(self,win):
        pygame.draw.rect(win,self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    MAX_VEL = 5
    COLOR = CYAN

    def __init__(self, x, y, radius):
        self.x = self.original_X = x 
        self.y = self.original_Y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_X
        self.y = self.original_Y
        self.y_vel = 0
        self.x_vel *= -1

def drawButton(win, text, x, y, width, height):
    pygame.draw.rect(win, CYAN, (x, y, width, height), border_radius=10)

    font = pygame.font.SysFont("comicsans", 30)
    textSurface = font.render(text, True, BLACK)

    WIN.blit(textSurface, (x + width // 2 - textSurface.get_width() // 2, y + height // 2 - textSurface.get_height() // 2))

async def mainMenu():
    while True:
        WIN.fill(BLACK)

        title = FONT.render("PING PONG", True, CYAN)

        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        friendButton = pygame.Rect(WIDTH//2 - 175, 200, 350, 70)
        computerButton = pygame.Rect(WIDTH//2 - 175, 300, 350, 70)

        drawButton(WIN, "Play with friend", friendButton.x, friendButton.y, friendButton.width, friendButton.height)
        drawButton(WIN, "Play against computer", computerButton.x, computerButton.y, computerButton.width, computerButton.height)

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
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

    ball.draw(win)

    pygame.display.update()

def handle_collision(ball, leftPaddle, rightPaddle):
    if ball.y + ball.radius >= HEIGHT:
        ball.y_vel *= -1
    elif ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if ball.y >= leftPaddle.y and ball.y <= leftPaddle.y + leftPaddle.height:
            if ball.x - ball.radius <= leftPaddle.x + leftPaddle.width:
                ball.x_vel *= -1
    
                middle_y = leftPaddle.y + leftPaddle.height / 2
                difference_in_y = middle_y - ball.y 
                reduction_factor = (leftPaddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * - y_vel
    else:
        if ball.y >= rightPaddle.y and ball.y <= rightPaddle.y + rightPaddle.height:
            if ball.x + ball.radius >= rightPaddle.x:
                ball.x_vel *= -1

                middle_y = rightPaddle.y +rightPaddle.height / 2
                difference_in_y = middle_y - ball.y 
                reduction_factor = (rightPaddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
 
def handle_paddle_movement(keys, leftPaddle, rightPaddle):
    if keys[pygame.K_w] and leftPaddle.y - leftPaddle.VEL >= 0:
        leftPaddle.move(up=True)
    if keys[pygame.K_s] and leftPaddle.y + leftPaddle.VEL + leftPaddle.height <= HEIGHT:
        leftPaddle.move(up=False)

    if keys[pygame.K_UP] and rightPaddle.y - rightPaddle.VEL >= 0:
        rightPaddle.move(up=True)
    if keys[pygame.K_DOWN] and rightPaddle.y + rightPaddle.VEL + rightPaddle.height <= HEIGHT:
        rightPaddle.move(up=False)

def handleComputer(paddle, ball):
    paddle_center = paddle.y + paddle.height / 2
    if paddle_center < ball.y - 10:
        paddle.move(up=False)
    elif paddle_center > ball.y + 10:
        paddle.move(up=True)

async def main(game_mode):
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

        keys = pygame.key.get_pressed() 
        handle_paddle_movement(keys, leftPaddle, rightPaddle)
        if game_mode == "computer":
            handleComputer(rightPaddle, ball)

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

    pygame.quit()

if __name__ == "__main__":
    game_mode = asyncio.run(mainMenu())

    if game_mode is not None:
        asyncio.run(main(game_mode))