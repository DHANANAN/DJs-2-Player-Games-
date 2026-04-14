"""
ai/tictactoe.py
================
Minimax algorithm with alpha-beta pruning for Tic Tac Toe.

Why Minimax?
  Tic Tac Toe is a zero-sum, perfect information game with a small
  state space (at most 9! = 362,880 terminal states). Minimax explores
  the entire game tree to find the provably optimal move.

  With alpha-beta pruning we skip branches that can't possibly improve
  our result, typically cutting the search tree roughly in half.

Difficulty levels:
  easy:   Random move 70% of the time; minimax 30%
  medium: Block immediate threats; else random
  hard:   Full minimax (never loses)
"""

import random
from typing import Optional


# ── TYPES & CONSTANTS ──────────────────────
Board = list[Optional[str]]   # 9 cells: None | 'X' | 'O'

WIN_LINES: list[tuple[int,int,int]] = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # cols
    (0,4,8),(2,4,6)            # diagonals
]


def check_winner(board: Board) -> Optional[str]:
    """Return 'X', 'O', or None."""
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def get_empty(board: Board) -> list[int]:
    return [i for i, v in enumerate(board) if v is None]


# ── MINIMAX ────────────────────────────────
def minimax(
    board: Board,
    is_maximizing: bool,     # True = AI's turn (maximizer, plays 'O')
    depth: int,
    alpha: float,
    beta:  float,
) -> dict:
    """
    Returns: { 'score': int, 'index': int }

    Score convention:
      +10 - depth  →  AI ('O') wins (prefers faster wins)
      -10 + depth  →  Human ('X') wins (prefers slower losses)
       0           →  Draw
    """
    winner = check_winner(board)
    if winner == 'O': return {'score':  10 - depth, 'index': -1}
    if winner == 'X': return {'score': -10 + depth, 'index': -1}

    empty = get_empty(board)
    if not empty:     return {'score': 0,            'index': -1}

    best_score = float('-inf') if is_maximizing else float('inf')
    best_index = -1

    for i in empty:
        board[i] = 'O' if is_maximizing else 'X'
        result   = minimax(board, not is_maximizing, depth + 1, alpha, beta)
        board[i] = None

        if is_maximizing:
            if result['score'] > best_score:
                best_score = result['score']
                best_index = i
            alpha = max(alpha, best_score)
        else:
            if result['score'] < best_score:
                best_score = result['score']
                best_index = i
            beta = min(beta, best_score)

        # Alpha-beta prune
        if beta <= alpha:
            break

    return {'score': best_score, 'index': best_index}


def find_winning_move(board: Board, player: str) -> int:
    """Find an immediate win/block for `player`. Returns index or -1."""
    for i in get_empty(board):
        board[i] = player
        if check_winner(board):
            board[i] = None
            return i
        board[i] = None
    return -1


# ── PUBLIC API ─────────────────────────────
def get_best_move(board: Board, difficulty: str = 'hard') -> tuple[int, int]:
    """
    Entry point called by the Flask route.
    Returns (move_index, score).
    """
    empty = get_empty(board)
    if not empty:
        return -1, 0

    if difficulty == 'easy':
        # Mostly random — occasionally uses minimax for variety
        if random.random() > 0.3:
            return random.choice(empty), 0
        result = minimax(board, True, 0, float('-inf'), float('inf'))
        return result['index'], result['score']

    if difficulty == 'medium':
        # Greedy: win if possible, block if necessary, else random
        win   = find_winning_move(board, 'O')
        if win != -1:   return win, 10
        block = find_winning_move(board, 'X')
        if block != -1: return block, -1
        # Prefer center, then corners, then edges
        for preferred in [4, 0, 2, 6, 8, 1, 3, 5, 7]:
            if board[preferred] is None:
                return preferred, 0

    # HARD: full minimax
    result = minimax(board, True, 0, float('-inf'), float('inf'))
    return result['index'], result['score']


# ── CLI TEST ───────────────────────────────
if __name__ == '__main__':
    # Quick test: empty board — AI should pick center (index 4)
    test_board = [None] * 9
    move, score = get_best_move(test_board, 'hard')
    print(f"Best move on empty board: {move} (score {score})")  # Expect 4

    # Test: AI should win immediately
    test_board2 = ['O','O',None,'X','X',None,None,None,None]
    move2, _ = get_best_move(test_board2, 'hard')
    print(f"AI winning move: {move2}")  # Expect 2
