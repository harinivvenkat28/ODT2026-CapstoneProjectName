from machine import Pin
import neopixel
import network
import socket
import time
import random

WIDTH  = 10
HEIGHT = 12
N      = WIDTH * HEIGHT

led = neopixel.NeoPixel(Pin(23), N)

left_btn  = Pin(21, Pin.IN, Pin.PULL_UP)
right_btn = Pin(4,  Pin.IN, Pin.PULL_UP)
start_btn = Pin(27, Pin.IN, Pin.PULL_UP)

pieces = [
    [(0,0),(0,1),(0,2),(0,3)],  # 0 - I
    [(0,0),(0,1),(1,0),(1,1)],  # 1 - O
    [(0,0),(0,1),(0,2),(1,1)],  # 2 - T
    [(0,1),(0,2),(1,0),(1,1)],  # 3 - S
    [(0,0),(0,1),(1,1),(1,2)],  # 4 - Z
    [(0,0),(1,0),(1,1),(1,2)],  # 5 - J
    [(0,2),(1,0),(1,1),(1,2)]   # 6 - L
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

speed = 0.2

next_piece_index = -1

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='bob', password='12345678')

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tetris Piece Selector</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#111;color:#fff;font-family:monospace;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:16px}
h1{font-size:1rem;letter-spacing:3px;color:#888;margin-bottom:24px;text-transform:uppercase}
.card{background:#1a1a1a;border:2px solid #333;border-radius:12px;padding:24px 20px;width:100%;max-width:320px;display:flex;flex-direction:column;align-items:center;gap:18px}
.card.confirmed{border-color:#0f0;box-shadow:0 0 16px #0f08}
.piece-name{font-size:1.2rem;letter-spacing:2px;font-weight:bold;min-height:1.5rem}
.nav-row{display:flex;align-items:center;gap:16px;width:100%}
.nav-btn{background:#222;border:2px solid #444;color:#ccc;font-size:1.4rem;width:48px;height:48px;border-radius:8px;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;text-decoration:none;user-select:none}
.nav-btn:active{background:#333}
.grid-wrap{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px}
.grid-row{display:flex;gap:2px}
.cell{width:28px;height:28px;border-radius:3px}
.empty{background:#0d0d0d;border:1px solid #1e1e1e}
.select-btn{width:100%;padding:14px;font-size:1rem;font-weight:bold;letter-spacing:1px;border:none;border-radius:8px;cursor:pointer;background:#444;color:#fff;text-transform:uppercase;transition:background 0.1s}
.select-btn:active{background:#555}
.select-btn.sent{background:#0a7a0a;color:#0f0}
.status{font-size:0.75rem;color:#0f0;letter-spacing:1px;min-height:1rem}
</style>
</head>
<body>
<h1>Next Piece</h1>
<div class="card" id="card">
  <div class="piece-name" id="pname">I-Piece</div>
  <div class="nav-row">
    <a class="nav-btn" id="btnPrev">&#8249;</a>
    <div class="grid-wrap" id="grid"></div>
    <a class="nav-btn" id="btnNext">&#8250;</a>
  </div>
  <a class="select-btn" id="selbtn">Select This Piece</a>
  <div class="status" id="status"></div>
</div>

<script>
var pieces=[
  {name:"I-Piece",color:"#0ff",grid:[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]},
  {name:"O-Piece",color:"#ff0",grid:[[0,1,1,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]]},
  {name:"T-Piece",color:"#a0f",grid:[[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]},
  {name:"S-Piece",color:"#0f0",grid:[[0,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]]},
  {name:"Z-Piece",color:"#f00",grid:[[1,1,0,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]]},
  {name:"J-Piece",color:"#00f",grid:[[1,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]},
  {name:"L-Piece",color:"#f80",grid:[[0,0,1,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]}
];

var idx = 0;

function draw() {
  var p = pieces[idx];
  document.getElementById('pname').style.color = p.color;
  document.getElementById('pname').textContent = p.name;
  var g = document.getElementById('grid');
  g.innerHTML = '';
  for (var r = 0; r < 4; r++) {
    var row = document.createElement('div');
    row.className = 'grid-row';
    for (var c = 0; c < 4; c++) {
      var cell = document.createElement('div');
      cell.className = 'cell';
      cell.style.background = p.grid[r][c] ? p.color : '#0d0d0d';
      if (!p.grid[r][c]) cell.style.border = '1px solid #1e1e1e';
      row.appendChild(cell);
    }
    g.appendChild(row);
  }
  document.getElementById('status').textContent = '';
  document.getElementById('selbtn').textContent = 'Select This Piece';
  document.getElementById('selbtn').className = 'select-btn';
}

document.getElementById('btnPrev').onclick = function() {
  idx = (idx + 6) % 7;
  draw();
};

document.getElementById('btnNext').onclick = function() {
  idx = (idx + 1) % 7;
  draw();
};

document.getElementById('selbtn').onclick = function() {
  fetch('/set?idx=' + idx)
    .then(function(r) { return r.text(); })
    .then(function() {
      document.getElementById('card').classList.add('confirmed');
      document.getElementById('selbtn').classList.add('sent');
      document.getElementById('selbtn').textContent = 'Queued!';
      document.getElementById('status').textContent = pieces[idx].name.toUpperCase() + ' SELECTED';
    });
};

draw();
</script>
</body>
</html>"""

server = socket.socket()
server.bind(('0.0.0.0', 80))
server.listen(1)
server.setblocking(False)   # <-- does NOT pause the game loop

print("Web server ready!")

def pixel(r, c):
    if r % 2 == 0:
        return r * WIDTH + c
    else:
        return r * WIDTH + (WIDTH - 1 - c)

def new_grid():
    return [[(0,0,0) for _ in range(WIDTH)] for _ in range(HEIGHT)]

def check_web():
    # This function checks if Player 2 sent a request
    global next_piece_index
    try:
        conn, addr = server.accept()
        request = conn.recv(512).decode('utf-8')

        # Check if Player 2 selected a piece  
        if '/set?idx=' in request:
            idx_str = request.split('/set?idx=')[1].split(' ')[0].strip()
            next_piece_index = int(idx_str)
            print("Player 2 chose piece index:", next_piece_index)
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK")

        else:
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.sendall(html)

        conn.close()
    except:
        pass   # no connection this tick — that is fine, game keeps going

def wait_start():
    # Wait for start button, keep checking web requests while waiting
    while start_btn.value() == 1:
        check_web()   # still handle web requests in the menu
        for i in range(N):
            led[i] = (0, 0, 50)
        led.write()
        time.sleep(0.1)

grid = new_grid()
wait_start()

while True:

    # Pick next piece 
    # If Player 2 chose a piece, use that. Otherwise pick random.
    if next_piece_index != -1:
        piece_id = next_piece_index
        next_piece_index = -1   # reset so next spawn is random again
        print("Using Player 2 choice:", piece_id)
    else:
        piece_id = random.randint(0, 6)

    piece = pieces[piece_id]
    color = colors[piece_id]

    row = 0
    col = WIDTH // 2 - 2

    # Game over check 
    game_over = False
    for b in piece:
        r = row + b[0]
        c = col + b[1]
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            if grid[r][c] != (0,0,0):
                game_over = True

    if game_over:
        for _ in range(10):
            for i in range(N):
                led[i] = (255, 0, 0)
            led.write()
            time.sleep(0.2)
            for i in range(N):
                led[i] = (0, 0, 0)
            led.write()
            time.sleep(0.2)

        grid = new_grid()
        next_piece_index = -1
        wait_start()
        continue

    falling = True

    # Piece fall loop 
    while falling:

        # Check web requests every tick (does NOT freeze game)
        check_web()

        # Clear screen
        for i in range(N):
            led[i] = (0, 0, 0)

        # Move left
        if left_btn.value() == 0:
            ok = True
            for b in piece:
                r = row + b[0]
                c = col + b[1] - 1
                if c < 0:
                    ok = False
                elif 0 <= r < HEIGHT:
                    if grid[r][c] != (0,0,0):
                        ok = False
            if ok:
                col -= 1

        # Move right
        if right_btn.value() == 0:
            ok = True
            for b in piece:
                r = row + b[0]
                c = col + b[1] + 1
                if c >= WIDTH:
                    ok = False
                elif 0 <= r < HEIGHT:
                    if grid[r][c] != (0,0,0):
                        ok = False
            if ok:
                col += 1

        # Draw placed blocks
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] != (0,0,0):
                    led[pixel(r,c)] = grid[r][c]

        # Draw current falling piece
        for b in piece:
            r = row + b[0]
            c = col + b[1]
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                led[pixel(r,c)] = color

        led.write()
        time.sleep(speed)

        # Check if piece can move down
        can_move = True
        for b in piece:
            r = row + b[0] + 1
            c = col + b[1]
            if r >= HEIGHT:
                can_move = False
            elif r >= 0:
                if grid[r][c] != (0,0,0):
                    can_move = False

        if can_move:
            row += 1
        else:
            # Lock piece into grid
            for b in piece:
                r = row + b[0]
                c = col + b[1]
                if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                    grid[r][c] = color

            # Clear full lines
            new = new_grid()
            new_r = HEIGHT - 1
            for r in range(HEIGHT-1, -1, -1):
                if (0,0,0) in grid[r]:   # row is not full
                    new[new_r] = grid[r]
                    new_r -= 1
            grid = new
            falling = False
