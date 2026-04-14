"""
DJ's Games Hub — Flask Backend
================================
Provides REST API endpoints for:
  • AI move calculation (Tic Tac Toe, Ping Pong paddle, Chess)
  • Score persistence (SQLite via SQLAlchemy)
  • Tournament bracket management

Architecture:
  app.py           → Flask app factory, CORS, error handlers, route registration
  routes/games.py  → Game AI endpoints  (/api/games/*)
  routes/scores.py → Score CRUD         (/api/scores/*)
  routes/tourney.py→ Tournament logic   (/api/tournament/*)
  ai/tictactoe.py  → Minimax engine
  ai/chess_ai.py   → Chess evaluation & minimax
  ai/pingpong.py   → Paddle prediction logic

Run locally:
  pip install flask flask-cors flask-sqlalchemy
  python app.py

Deploy to Render / Railway / Heroku:
  Set env var PORT, use gunicorn: gunicorn app:app
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ── APP FACTORY ────────────────────────────
app = Flask(__name__)
CORS(app, origins=["https://djlexfolio.netlify.app", "http://localhost:*"])

# ── DATABASE CONFIG ────────────────────────
# SQLite for development; swap DATABASE_URL env var for PostgreSQL in production
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///games_hub.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ── MODELS ─────────────────────────────────
class Score(db.Model):
    """
    Stores per-game win records for players.
    player_name is simple string (no auth needed for a portfolio hub).
    """
    id          = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(50), nullable=False)
    game        = db.Column(db.String(30), nullable=False)
    wins        = db.Column(db.Integer, default=0)
    losses      = db.Column(db.Integer, default=0)
    draws       = db.Column(db.Integer, default=0)
    last_played = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def win_rate(self):
        total = self.wins + self.losses + self.draws
        return round(self.wins / total * 100, 1) if total > 0 else 0.0

    def to_dict(self):
        return {
            "id":          self.id,
            "player":      self.player_name,
            "game":        self.game,
            "wins":        self.wins,
            "losses":      self.losses,
            "draws":       self.draws,
            "win_rate":    self.win_rate,
            "last_played": self.last_played.isoformat()
        }


class Tournament(db.Model):
    """
    A mini-tournament between two named players across multiple games.
    bracket stores JSON string of game results.
    """
    id         = db.Column(db.Integer, primary_key=True)
    player1    = db.Column(db.String(50), nullable=False)
    player2    = db.Column(db.String(50), nullable=False)
    games_list = db.Column(db.String(200))   # comma-separated game names
    bracket    = db.Column(db.Text, default="[]")  # JSON list of round results
    winner     = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id":         self.id,
            "player1":    self.player1,
            "player2":    self.player2,
            "games":      self.games_list.split(",") if self.games_list else [],
            "bracket":    json.loads(self.bracket),
            "winner":     self.winner,
            "created_at": self.created_at.isoformat()
        }


# ── ROUTES: AI MOVES ──────────────────────
@app.route("/api/games/tictactoe/ai-move", methods=["POST"])
def tictactoe_ai_move():
    """
    Request body:
      { board: [null|'X'|'O', ...9], difficulty: 'easy'|'medium'|'hard' }
    Response:
      { move: int (0-8), score: int }

    The frontend sends the current board state; backend runs minimax and
    returns the best move index. This keeps heavy computation server-side
    and lets the frontend remain a pure renderer.
    """
    data       = request.get_json()
    board      = data.get("board", [None]*9)
    difficulty = data.get("difficulty", "hard")

    from ai.tictactoe import get_best_move
    move, score = get_best_move(board, difficulty)

    return jsonify({"move": move, "score": score})


@app.route("/api/games/pingpong/ai-paddle", methods=["POST"])
def pingpong_ai_paddle():
    """
    Request body:
      { ball: {x, y, vx, vy}, paddle: {y, h}, canvas_h: int, difficulty: str }
    Response:
      { target_y: float }   ← where the paddle's top should move toward

    In practice, Ping Pong runs entirely client-side (better for real-time).
    This endpoint is here for reference / alternative server-driven AI.
    """
    data = request.get_json()
    from ai.pingpong import predict_paddle_y
    target_y = predict_paddle_y(
        data["ball"], data["paddle"],
        data.get("canvas_h", 400),
        data.get("difficulty", "medium")
    )
    return jsonify({"target_y": target_y})


@app.route("/api/games/chess/ai-move", methods=["POST"])
def chess_ai_move():
    """
    Request body:
      { fen: str, depth: int }   ← FEN is standard chess board notation
    Response:
      { move: { from: str, to: str }, evaluation: float }

    FEN example: 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
    This lets you integrate Stockfish or your own engine later without
    changing the frontend API contract.
    """
    data  = request.get_json()
    fen   = data.get("fen")
    depth = data.get("depth", 3)

    from ai.chess_ai import get_best_move_fen
    result = get_best_move_fen(fen, depth)
    return jsonify(result)


# ── ROUTES: SCORES ─────────────────────────
@app.route("/api/scores", methods=["GET"])
def get_leaderboard():
    """
    GET /api/scores?game=tictactoe&limit=10
    Returns top players sorted by win rate.
    """
    game  = request.args.get("game")
    limit = int(request.args.get("limit", 10))
    query = Score.query
    if game:
        query = query.filter_by(game=game)
    scores = query.order_by(Score.wins.desc()).limit(limit).all()
    return jsonify([s.to_dict() for s in scores])


@app.route("/api/scores", methods=["POST"])
def record_score():
    """
    POST /api/scores
    Body: { player: str, game: str, result: 'win'|'loss'|'draw' }
    Creates or updates the player's record for that game.
    """
    data   = request.get_json()
    player = data.get("player", "Anonymous")
    game   = data.get("game")
    result = data.get("result")  # 'win' | 'loss' | 'draw'

    if not game or result not in ("win", "loss", "draw"):
        return jsonify({"error": "Invalid payload"}), 400

    record = Score.query.filter_by(player_name=player, game=game).first()
    if not record:
        record = Score(player_name=player, game=game)
        db.session.add(record)

    if result == "win":    record.wins   += 1
    elif result == "loss": record.losses += 1
    else:                  record.draws  += 1
    record.last_played = datetime.utcnow()

    db.session.commit()
    return jsonify(record.to_dict()), 201


# ── ROUTES: TOURNAMENT ─────────────────────
@app.route("/api/tournament", methods=["POST"])
def create_tournament():
    """
    POST /api/tournament
    Body: { player1: str, player2: str, games: [str, ...] }
    Creates a new tournament bracket.
    """
    import json
    data = request.get_json()
    t = Tournament(
        player1    = data["player1"],
        player2    = data["player2"],
        games_list = ",".join(data.get("games", ["tictactoe","pingpong","chess"]))
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@app.route("/api/tournament/<int:tid>/result", methods=["PATCH"])
def update_tournament_result(tid):
    """
    PATCH /api/tournament/:id/result
    Body: { game: str, winner: str }
    Adds a round result to the bracket and checks if tournament is complete.
    """
    import json
    t    = Tournament.query.get_or_404(tid)
    data = request.get_json()

    bracket = json.loads(t.bracket)
    bracket.append({"game": data["game"], "winner": data["winner"]})
    t.bracket = json.dumps(bracket)

    # Count wins
    p1_wins = sum(1 for r in bracket if r["winner"] == t.player1)
    p2_wins = sum(1 for r in bracket if r["winner"] == t.player2)
    games   = t.games_list.split(",")

    # Check if someone has a majority
    majority = len(games) // 2 + 1
    if p1_wins >= majority:   t.winner = t.player1
    elif p2_wins >= majority: t.winner = t.player2

    db.session.commit()
    return jsonify(t.to_dict())


@app.route("/api/tournament/<int:tid>", methods=["GET"])
def get_tournament(tid):
    t = Tournament.query.get_or_404(tid)
    return jsonify(t.to_dict())


# ── HEALTH CHECK ───────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "DJs Games Hub API"})


# ── ERROR HANDLERS ─────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── ENTRY POINT ────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
