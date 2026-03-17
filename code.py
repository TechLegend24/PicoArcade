import board
import busio
import adafruit_ssd1306
import digitalio
import time
import random

# ---------------- OLED ----------------
i2c = busio.I2C(board.GP19, board.GP18)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

WIDTH = 128
HEIGHT = 32

# ---------------- BUTTONS ----------------
left = digitalio.DigitalInOut(board.GP16)
left.direction = digitalio.Direction.INPUT
left.pull = digitalio.Pull.UP

right = digitalio.DigitalInOut(board.GP26)
right.direction = digitalio.Direction.INPUT
right.pull = digitalio.Pull.UP

fire = digitalio.DigitalInOut(board.GP20)
fire.direction = digitalio.Direction.INPUT
fire.pull = digitalio.Pull.UP


# ---------------- INPUT ----------------
def pressed(btn):
    return not btn.value


# ---------------- STARFIELD ----------------
stars = [[random.randint(0,127), random.randint(0,31)] for _ in range(12)]

def draw_stars():
    for s in stars:
        display.pixel(s[0], s[1], 1)
        s[1] += 1
        if s[1] > 31:
            s[0] = random.randint(0,127)
            s[1] = 0


# ---------------- BOOT SCREEN ----------------
def boot():
    display.fill(0)
    display.text("PICO", 48, 8, 1)
    display.text("ARCADE", 40, 18, 1)
    display.show()
    time.sleep(1.5)


# ---------------- GAME OVER ----------------
def game_over(score):

    display.fill(0)
    display.text("GAME OVER", 30, 8, 1)
    display.text("SCORE:"+str(score), 30, 18, 1)
    display.show()
    time.sleep(2)


# ---------------- MENU ----------------
games = ["PONG", "BREAKOUT", "DODGER", "INVADERS", "MINI JUMP"]

def menu():

    sel = 0

    while True:

        if pressed(left):
            sel = (sel - 1) % len(games)
            time.sleep(0.2)

        if pressed(right):
            sel = (sel + 1) % len(games)
            time.sleep(0.2)

        if pressed(fire):
            time.sleep(0.2)
            return sel

        display.fill(0)

        draw_stars()

        display.text("PICO ARCADE", 20, 0, 1)
        display.hline(0,10,128,1)
        display.text(">"+games[sel], 30, 18, 1)

        display.show()


# ---------------- PONG ----------------
def pong():

    paddle = 54
    ballx = 60
    bally = 10
    dx = 2
    dy = 2
    score = 0

    while True:

        if pressed(left):
            paddle -= 3
        if pressed(right):
            paddle += 3

        paddle = max(0, min(108, paddle))

        ballx += dx
        bally += dy

        if ballx <= 0 or ballx >= 126:
            dx *= -1

        if bally <= 0:
            dy *= -1

        if paddle < ballx < paddle + 20 and bally >= 28:
            dy = -2
            score += 1

        if bally > 31:
            game_over(score)
            return

        display.fill(0)

        draw_stars()

        display.text(str(score),0,0,1)

        display.rect(paddle,30,20,2,1)
        display.fill_rect(ballx,bally,2,2,1)

        display.show()
        time.sleep(0.01)


# ---------------- BREAKOUT ----------------
def breakout():

    paddle = 50
    ballx = 60
    bally = 20
    dx = 2
    dy = -2
    score = 0

    bricks = [[c*16, r*6] for r in range(2) for c in range(8)]

    while True:

        if pressed(left):
            paddle -= 3
        if pressed(right):
            paddle += 3

        paddle = max(0, min(108, paddle))

        ballx += dx
        bally += dy

        if ballx <= 0 or ballx >= 126:
            dx *= -1

        if bally <= 0:
            dy *= -1

        if paddle < ballx < paddle + 20 and bally >= 27:
            dy = -2

        for b in bricks:

            if b[0] < ballx < b[0] + 14 and b[1] < bally < b[1] + 4:
                bricks.remove(b)
                dy *= -1
                score += 1
                break

        if bally > 31:
            game_over(score)
            return

        if len(bricks) == 0:
            game_over(score)
            return

        display.fill(0)

        display.text(str(score),0,0,1)

        for b in bricks:
            display.rect(b[0],b[1],14,4,1)

        display.rect(paddle,30,20,2,1)
        display.fill_rect(ballx,bally,2,2,1)

        display.show()

        time.sleep(0.01)


# ---------------- DODGER ----------------
def dodge():

    player = 60
    rocks = []
    score = 0

    while True:

        if pressed(left):
            player -= 3
        if pressed(right):
            player += 3

        player = max(0, min(120, player))

        if random.randint(0,10) == 0:
            rocks.append([random.randint(0,120),0])

        for r in rocks:
            r[1] += 3

        for r in rocks:
            if abs(r[0]-player) < 5 and abs(r[1]-28) < 5:
                game_over(score)
                return

        score += 1

        display.fill(0)

        display.text(str(score),0,0,1)

        display.fill_rect(player,28,6,3,1)

        for r in rocks:
            display.fill_rect(r[0],r[1],3,3,1)

        display.show()

        time.sleep(0.02)


# ---------------- INVADERS ----------------
def invaders():

    player = 60

    bullet_active = False
    bullet_x = 0
    bullet_y = 0

    enemies = [[10 + i*14, 5] for i in range(8)]

    direction = 1
    score = 0

    while True:

        if pressed(left):
            player -= 3
        if pressed(right):
            player += 3

        player = max(0, min(120, player))

        if pressed(fire) and not bullet_active:

            bullet_active = True
            bullet_x = player + 3
            bullet_y = 25

        if bullet_active:
            bullet_y -= 3

            if bullet_y < 0:
                bullet_active = False

        edge = False

        for e in enemies:
            e[0] += direction
            if e[0] < 0 or e[0] > WIDTH-6:
                edge = True

        if edge:
            direction *= -1
            for e in enemies:
                e[1] += 2

        if bullet_active:
            for e in enemies:

                if abs(bullet_x-e[0]) < 6 and abs(bullet_y-e[1]) < 5:
                    enemies.remove(e)
                    bullet_active = False
                    score += 1
                    break

        if len(enemies) == 0:
            game_over(score)
            return

        display.fill(0)

        display.text(str(score),0,0,1)

        display.fill_rect(player,28,6,3,1)

        if bullet_active:
            display.fill_rect(bullet_x,bullet_y,2,4,1)

        for e in enemies:
            display.rect(e[0],e[1],6,4,1)

        display.show()

        time.sleep(0.03)


# ---------------- MINI JUMP ----------------
def mini_jump():

    player_y = 28
    vel = 0
    obstacles = []
    score = 0

    while True:

        if pressed(fire) and player_y >= 28:
            vel = -5

        vel += 0.3
        player_y += vel

        if player_y > 28:
            player_y = 28
            vel = 0

        if random.randint(0,15) == 0:
            obstacles.append([128,28])

        for o in obstacles:
            o[0] -= 3

        for o in obstacles:
            if abs(o[0]-10) < 6 and abs(o[1]-player_y) < 6:
                game_over(score)
                return

        score += 1

        display.fill(0)

        display.text(str(score),0,0,1)

        display.fill_rect(10,int(player_y),5,4,1)

        for o in obstacles:
            display.fill_rect(o[0],o[1],4,4,1)

        display.show()

        time.sleep(0.02)


# ---------------- MAIN ----------------

boot()

while True:

    g = menu()

    if g == 0:
        pong()

    elif g == 1:
        breakout()

    elif g == 2:
        dodge()

    elif g == 3:
        invaders()

    elif g == 4:
        mini_jump()
