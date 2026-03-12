# 🎮 DJ's Games Hub — DJLexFolio

A modular, branded 2-player games hub built with HTML/CSS/JS (frontend)
and Python Flask (backend AI & score persistence).

---

## Project Structure

```
DJsGamesHub/
│
├── index.html                  ← Hub landing page (game selector)
│
├── games/
│   ├── tictactoe.html          ← ✅ LIVE: Minimax AI + 2-player local
│   ├── pingpong.html           ← ✅ LIVE: Canvas pong + AI paddle
│   ├── chess.html              ← ✅ LIVE: Full rules chess + AI engine
│   ├── airhockey.html          ← 🔜 Scaffold ready
│   ├── snakes.html             ← 🔜 Scaffold ready
│   ├── pool.html               ← 🔜 Scaffold ready
│   ├── penalty.html            ← 🔜 Scaffold ready
│   ├── sumo.html               ← 🔜 Scaffold ready
│   ├── minigolf.html           ← 🔜 Scaffold ready
│   ├── racing.html             ← 🔜 Scaffold ready
│   └── sword.html              ← 🔜 Scaffold ready
│
└── backend/
    ├── app.py                  ← Flask app, routes, DB models
    ├── requirements.txt
    ├── ai/
    │   ├── tictactoe.py        ← Minimax + alpha-beta pruning
    │   ├── pingpong.py         ← Ball trajectory prediction
    │   └── chess_ai.py         ← Material eval + minimax (python-chess)
    └── routes/                 ← (extend here for new games)
```

---

## Architecture Overview

```
┌──────────────────────────────────┐
│  Browser (HTML/CSS/JS Canvas)    │  ← All rendering & input handling
│  - Game loop (requestAnimFrame)  │
│  - Keyboard/click input          │
│  - Canvas 2D drawing             │
└────────────┬─────────────────────┘
             │  HTTP POST (fetch API)
             │  e.g. POST /api/games/tictactoe/ai-move
             ▼
┌──────────────────────────────────┐
│  Flask Backend (Python)          │  ← Logic, AI, persistence
│  - Minimax AI (tictactoe/chess)  │
│  - Score recording (SQLite/PG)   │
│  - Tournament bracket tracking   │
└────────────┬─────────────────────┘
             │  SQLAlchemy ORM
             ▼
┌──────────────────────────────────┐
│  Database                        │
│  SQLite (dev) / PostgreSQL (prod)│
└──────────────────────────────────┘
```

**Why this split?**
- Frontend handles real-time rendering (60fps); Python can't do that in a browser
- Backend handles computationally expensive AI (minimax over large trees)
- Separation means you can upgrade AI independently without touching the UI
- Score data needs persistence across sessions → server-side DB

---

## Setup

### Frontend (pure HTML — no build step needed)
```bash
# Just open index.html in a browser
# Or serve locally:
npx serve .           # Node
python -m http.server # Python
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

---

## API Reference

### AI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/games/tictactoe/ai-move` | Get best Tic Tac Toe move |
| POST | `/api/games/pingpong/ai-paddle` | Get paddle target Y |
| POST | `/api/games/chess/ai-move` | Get best chess move from FEN |

**Tic Tac Toe AI request:**
```json
{
  "board": [null, "X", null, "O", null, null, null, null, null],
  "difficulty": "hard"
}
```
**Response:**
```json
{ "move": 4, "score": 8 }
```

**Chess AI request:**
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "depth": 3
}
```
**Response:**
```json
{ "from": "e7", "to": "e5", "evaluation": 0.05 }
```

### Score Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scores?game=chess&limit=10` | Leaderboard |
| POST | `/api/scores` | Record a game result |
| POST | `/api/tournament` | Create tournament |
| PATCH | `/api/tournament/:id/result` | Submit round result |
| GET | `/api/tournament/:id` | Get bracket |

---

## How Frontend Calls the Backend

In each game's HTML, after a move is made:

```javascript
// Example: Tic Tac Toe calling the AI endpoint
async function getAIMoveFromServer(board, difficulty) {
  const API = 'https://your-backend.railway.app'; // or localhost:5000
  const res  = await fetch(`${API}/api/games/tictactoe/ai-move`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ board, difficulty })
  });
  const data = await res.json();
  return data.move; // index 0-8
}

// Then use it in your game:
const move = await getAIMoveFromServer(board, 'hard');
playMove(move);
```

**Note:** The current tictactoe.html, pingpong.html, and chess.html
all include fully working **client-side AI** (no backend needed).
The backend AI is an optional upgrade for when you want server-side
processing, stronger engines (e.g. Stockfish for chess), or to
avoid exposing logic to the client.

---

## How to Add a New Game

### Step 1 — Frontend (`games/newgame.html`)
```html
<!-- Boilerplate structure every game uses: -->
<!DOCTYPE html>
<html>
<head>
  <!-- Same fonts/CSS variables as hub -->
</head>
<body>
  <!-- 1. Top nav with back link -->
  <!-- 2. Mode selector (2p / AI) -->
  <!-- 3. Scoreboard -->
  <!-- 4. Game canvas or board element -->
  <!-- 5. Controls legend -->

  <script>
    // Game state object
    let state = {};

    // Main loop (for real-time games):
    function loop() {
      update(); // physics, input
      draw();   // canvas rendering
      requestAnimationFrame(loop);
    }

    // Or turn handler (for turn-based games):
    function onMove(data) {
      applyMove(data);
      checkEndCondition();
      render();
      if (mode === 'ai') callAI();
    }

    // Optional: call backend for AI move
    async function callAI() {
      const res = await fetch('/api/games/newgame/ai-move', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ state: gameState })
      });
      const { move } = await res.json();
      onMove(move);
    }
  </script>
</body>
</html>
```

### Step 2 — Backend AI (`backend/ai/newgame.py`)
```python
def get_best_move(state: dict) -> dict:
    """
    Implement your AI logic here.
    state = whatever your frontend sends.
    Returns { move: ... }
    """
    pass
```

### Step 3 — Register Route (`backend/app.py`)
```python
@app.route("/api/games/newgame/ai-move", methods=["POST"])
def newgame_ai():
    from ai.newgame import get_best_move
    data = request.get_json()
    result = get_best_move(data)
    return jsonify(result)
```

### Step 4 — Add card to `index.html`
Copy an existing `.game-card` block and update:
- `href` → link to your new file
- `data-tags` → filter categories
- Icon, name, description, badges

---

## Real-Time Input Best Practices

For smooth 60fps gameplay in canvas games:

```javascript
// ✅ DO: Separate input state from rendering
const keys = {};
window.addEventListener('keydown', e => { keys[e.key] = true;  e.preventDefault(); });
window.addEventListener('keyup',   e => { keys[e.key] = false; });

function update() {
  // Read keys[] here — not in event listeners
  if (keys['ArrowUp']) paddle.y -= paddle.speed;
}

// ✅ DO: Use requestAnimationFrame (not setInterval)
function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop); // browser-synced, pauses when tab hidden
}

// ✅ DO: Delta-time for physics (frame-rate independent movement)
let lastTime = 0;
function gameLoop(timestamp) {
  const dt = (timestamp - lastTime) / 16.67; // normalized to 60fps
  lastTime = timestamp;
  update(dt);  // multiply velocities by dt
  draw();
  requestAnimationFrame(gameLoop);
}

// ✅ DO: Canvas sizing
function resize() {
  canvas.width  = canvas.offsetWidth;  // match CSS layout size
  canvas.height = canvas.offsetHeight;
}
window.addEventListener('resize', resize);

// ✅ DON'T: Create new objects in draw() — reuse them
// ✅ DON'T: Use innerHTML inside the game loop — use canvas
// ✅ DON'T: Call fetch() inside the game loop — debounce it
```

---

## Deployment

### Frontend → Netlify (recommended)
```bash
# 1. Push to GitHub
# 2. Connect repo on netlify.com
# 3. Build command: (none — static files)
# 4. Publish directory: /  (root, or /DJsGamesHub)
# 5. Set custom domain: games.djlexfolio.com
```

### Backend → Railway (easiest Python hosting)
```bash
# 1. Install Railway CLI: npm i -g @railway/cli
railway login
railway init
railway up

# 2. Add env vars in Railway dashboard:
#    DATABASE_URL = postgresql://... (Railway provides this)
#    PORT         = 5000

# 3. Add Procfile to backend/
echo "web: gunicorn app:app" > backend/Procfile
```

### Backend → Render (free tier available)
```
Service type: Web Service
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
Environment:   PORT=10000, DATABASE_URL=<your postgres url>
```

### CORS Configuration
In `app.py`, update the origins list:
```python
CORS(app, origins=[
    "https://djlexfolio.netlify.app",
    "https://games.djlexfolio.com",   # custom domain
    "http://localhost:*"              # local dev
])
```

---

## Branding Guide — "DJ's Games Hub"

**Visual identity:**
- Primary font:    Press Start 2P (headers, game titles)
- Secondary font:  Orbitron (UI labels, scores, buttons)
- Body font:       Rajdhani (descriptions, instructions)

**Color system:**
```css
--bg:      #04040d;   /* Deep space black */
--cyan:    #00f5ff;   /* Primary accent — interactive elements */
--magenta: #ff00aa;   /* Secondary accent — player 2, alerts */
--gold:    #ffd700;   /* Win states, tournaments */
--green:   #00ff88;   /* Live status, success */
--red:     #ff4455;   /* Danger, check, errors */
```

**Motion principles:**
- Cards lift on hover (translateY -6px)
- Buttons glow on hover (box-shadow with color)
- Pieces/tokens spring-in (cubic-bezier bounce)
- Scanline overlay on all pages (identity element)
- Starfield canvas on hub (ambient depth)

**Voice/copy:**
- Terse, uppercase labels: "PLAY NOW", "YOUR TURN", "CHECK!"
- Metrics displayed prominently: scores, win rates
- Status badges on each game: "● LIVE" vs "⧖ SOON"

---

## Roadmap

| Priority | Game | Complexity | Notes |
|----------|------|------------|-------|
| High | Air Hockey | Medium | Physics-based puck |
| High | Snakes | Medium | Grid collision |
| Medium | Pool | High | Ball-ball physics |
| Medium | Penalty Kicks | Low | Angle + power mechanic |
| Medium | Sumo | Medium | Push/force physics |
| Low | Minigolf | High | Procedural holes |
| Low | Racing | High | Top-down track |
| Low | Sword Duels | High | Side-scroll combat |

---

*Built by DJ · Part of DJLexFolio · Showcasing law, research & creative coding*
