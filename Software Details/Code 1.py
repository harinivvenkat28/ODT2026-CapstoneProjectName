
from machine import Pin
import neopixel
import time
import random

WIDTH = 12
HEIGHT = 14
N = WIDTH * HEIGHT   # 168 total LEDs

my_neo = neopixel.NeoPixel(Pin(23), 300)

left_btn  = Pin(12, Pin.IN, Pin.PULL_UP)
right_btn = Pin(13, Pin.IN, Pin.PULL_UP)

pieces = [
    [(0,0),(0,1),(0,2),(0,3)],  # I
    [(0,0),(0,1),(1,0),(1,1)],  # O
    [(0,0),(0,1),(0,2),(1,1)],  # T
    [(0,1),(0,2),(1,0),(1,1)],  # S
    [(0,0),(0,1),(1,1),(1,2)],  # Z
    [(0,0),(1,0),(1,1),(1,2)],  # J
    [(0,2),(1,0),(1,1),(1,2)]   # L
]

colors = [
    (0,   0,   255),   # I - blue
    (255, 0,   0  ),   # O - red
    (255, 255, 0  ),   # T - yellow
    (0,   255, 0  ),   # S - green
    (255, 0,   255),   # Z - pink
    (0,   255, 255),   # J - cyan
    (255, 165, 0  )    # L - orange
]

base_delay = 0.2

def make_grid():
    g = []
    r = 0
    while r < HEIGHT:
        row = []
        c = 0
        while c < WIDTH:
            row = row + [(0, 0, 0)]
            c = c + 1
        g = g + [row]
        r = r + 1
    return g


grid = make_grid()

while True:

    piece_index = random.randint(0, len(pieces) - 1)
    piece       = pieces[piece_index]
    piece_color = colors[piece_index]

    row = 0
    col = 4

    game_over = False

    for b in piece:
        r = row + b[0]
        c = col + b[1]

        if r >= 0 and r < HEIGHT and c >= 0 and c < WIDTH:
            if grid[r][c] != (0, 0, 0):
                game_over = True

    if game_over:

        t = 0
        while t < 10:

            i = 0
            while i < N:
                my_neo[i] = (255, 0, 0)
                i = i + 1
            my_neo.write()
            time.sleep(0.2)

            i = 0
            while i < N:
                my_neo[i] = (0, 0, 0)
                i = i + 1
            my_neo.write()
            time.sleep(0.2)

            t = t + 1

        # Reset the grid and start again
        grid = make_grid()
        continue

    falling = True

    while falling:

        # Clear all LEDs
        i = 0
        while i < N:
            my_neo[i] = (0, 0, 0)
            i = i + 1

        if left_btn.value() == 0:
            can_go_left = True
            for b in piece:
                if col + b[1] - 1 < 0:
                    can_go_left = False
            if can_go_left:
                col = col - 1

        if right_btn.value() == 0:
            can_go_right = True
            for b in piece:
                if col + b[1] + 1 >= WIDTH:
                    can_go_right = False
            if can_go_right:
                col = col + 1

        r = 0
        while r < HEIGHT:
            c = 0
            while c < WIDTH:
                if grid[r][c] != (0, 0, 0):
                    my_neo[r * WIDTH + c] = grid[r][c]
                c = c + 1
            r = r + 1

      
        for b in piece:
            r = row + b[0]
            c = col + b[1]

            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                my_neo[r * WIDTH + c] = piece_color

        # Push all LED colors to the strip
        my_neo.write()
        time.sleep(base_delay)

        can_move = True

        for b in piece:
            r = row + b[0] + 1
            c = col + b[1]

            if r >= HEIGHT:
                can_move = False
            elif r >= 0 and grid[r][c] != (0, 0, 0):
                can_move = False

        if can_move:
            row = row + 1

        else:

            for b in piece:
                r = row + b[0]
                c = col + b[1]

                if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                    grid[r][c] = piece_color

            new_grid = make_grid()

            new_r = HEIGHT - 1
            r     = HEIGHT - 1

            while r >= 0:

                full = True
                c = 0

                while c < WIDTH:
                    if grid[r][c] == (0, 0, 0):
                        full = False
                    c = c + 1

                if full == False:

                    c = 0
                    while c < WIDTH:
                        new_grid[new_r][c] = grid[r][c]
                        c = c + 1

                    new_r = new_r - 1

                r = r - 1

            grid = new_grid
            falling = False