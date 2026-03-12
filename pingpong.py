"""
ai/pingpong.py
===============
Server-side ping pong paddle AI.
Used only when calling the /api/games/pingpong/ai-paddle endpoint.
In normal play the client-side JS handles this for latency reasons.

The AI predicts where the ball will be when it reaches the paddle's X,
accounting for wall bounces, then adds a difficulty-based error offset.
"""

import random


def predict_ball_y(ball: dict, canvas_h: int, target_x: float) -> float:
    """
    Simulate ball trajectory until it reaches target_x.
    Accounts for top/bottom wall bounces.

    Returns: predicted Y position at target_x
    """
    x,  y  = ball['x'],  ball['y']
    vx, vy = ball['vx'], ball['vy']

    MAX_ITERS = 200
    for _ in range(MAX_ITERS):
        # How many steps until ball reaches target_x?
        if abs(vx) < 0.001:
            break
        steps = (target_x - x) / vx
        if steps <= 0:
            break

        # Project Y
        proj_y = y + vy * steps

        # Reflect off top/bottom walls
        while proj_y < 0 or proj_y > canvas_h:
            if proj_y < 0:
                proj_y  = -proj_y
                vy      = -vy
            if proj_y > canvas_h:
                proj_y  = 2 * canvas_h - proj_y
                vy      = -vy

        return proj_y

    return canvas_h / 2  # fallback to center


def predict_paddle_y(
    ball:       dict,
    paddle:     dict,
    canvas_h:   int  = 400,
    difficulty: str  = 'medium'
) -> float:
    """
    Returns the Y position the paddle top should move toward.

    Difficulty effects:
      easy:   Large random error (±80px)
      medium: Moderate error (±30px), only tracks when ball approaching
      hard:   Small error (±8px), always tracks
    """
    paddle_x = paddle.get('x', canvas_h)  # right paddle X

    # Only track when ball is coming toward this paddle
    if ball['vx'] < 0 and difficulty != 'hard':
        # Ball moving away — drift to center
        return canvas_h / 2 - paddle['h'] / 2

    pred_y = predict_ball_y(ball, canvas_h, paddle_x)

    # Apply difficulty error
    errors = {'easy': 80, 'medium': 30, 'hard': 8}
    err    = (random.random() * 2 - 1) * errors.get(difficulty, 30)

    target_center = pred_y + err
    return max(0, min(canvas_h - paddle['h'], target_center - paddle['h'] / 2))
