"""Juego de Tetris para la terminal usando curses.

Este módulo implementa una versión simplificada del clásico Tetris.
Para jugar es necesario ejecutar el script en una terminal compatible
con la librería `curses`.
"""
from __future__ import annotations

import curses
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Sequence

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Representación de las piezas en matrices de 0 y 1.
TETROMINOES: Dict[str, List[List[int]]] = {
    "I": [[1, 1, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "Z": [[1, 1, 0], [0, 1, 1]],
}


@dataclass
class Piece:
    """Representa una pieza activa en el tablero."""

    shape: List[List[int]]
    x: int
    y: int
    letter: str

    @property
    def width(self) -> int:
        return len(self.shape[0])

    @property
    def height(self) -> int:
        return len(self.shape)


def rotate(shape: List[List[int]]) -> List[List[int]]:
    """Gira una pieza 90 grados en sentido horario."""
    return [list(row) for row in zip(*shape[::-1])]


def create_board() -> List[List[str]]:
    """Crea un tablero vacío."""
    return [[" "] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]


def collision(board: Sequence[Sequence[str]], shape: Sequence[Sequence[int]], offset_x: int, offset_y: int) -> bool:
    """Comprueba si la pieza colisiona con el tablero."""
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if not cell:
                continue
            board_x = offset_x + x
            board_y = offset_y + y
            if board_x < 0 or board_x >= BOARD_WIDTH:
                return True
            if board_y >= BOARD_HEIGHT:
                return True
            if board_y >= 0 and board[board_y][board_x] != " ":
                return True
    return False


def merge(board: List[List[str]], piece: Piece) -> None:
    """Coloca permanentemente la pieza en el tablero."""
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell and piece.y + y >= 0:
                board[piece.y + y][piece.x + x] = piece.letter


def clear_lines(board: List[List[str]]) -> int:
    """Elimina filas completas y devuelve cuántas se limpiaron."""
    remaining_rows = [row for row in board if " " in row]
    cleared = BOARD_HEIGHT - len(remaining_rows)
    while len(remaining_rows) < BOARD_HEIGHT:
        remaining_rows.insert(0, [" "] * BOARD_WIDTH)
    board[:] = remaining_rows
    return cleared


def new_piece() -> Piece:
    """Genera una nueva pieza aleatoria."""
    letter = random.choice(list(TETROMINOES.keys()))
    shape = [row[:] for row in TETROMINOES[letter]]
    x = BOARD_WIDTH // 2 - len(shape[0]) // 2
    y = -len(shape)  # Empieza fuera de la pantalla para permitir rotaciones.
    return Piece(shape=shape, x=x, y=y, letter=letter)


def draw_board(stdscr: "curses._CursesWindow", board: Sequence[Sequence[str]], piece: Piece | None, next_piece: Piece, score: int, level: int, lines: int) -> None:
    """Dibuja el tablero y la información adicional."""
    stdscr.clear()
    stdscr.addstr(0, 0, "Tetris - Controles: ← → mover, ↑ rotar, ↓ acelerar, espacio soltar, q salir")

    # Dibujar tablero con borde simple.
    top_offset_y = 2
    left_offset_x = 2
    for y in range(BOARD_HEIGHT + 2):
        for x in range(BOARD_WIDTH + 2):
            draw_y = top_offset_y + y
            draw_x = left_offset_x + x * 2
            if y == 0 or y == BOARD_HEIGHT + 1 or x == 0 or x == BOARD_WIDTH + 1:
                stdscr.addstr(draw_y, draw_x, "##")
            else:
                board_y = y - 1
                board_x = x - 1
                cell = board[board_y][board_x]
                active = False
                if piece is not None:
                    rel_y = board_y - piece.y
                    rel_x = board_x - piece.x
                    if 0 <= rel_y < piece.height and 0 <= rel_x < piece.width:
                        if piece.shape[rel_y][rel_x]:
                            active = True
                if active:
                    stdscr.addstr(draw_y, draw_x, "[]")
                elif cell != " ":
                    stdscr.addstr(draw_y, draw_x, "[]")
                else:
                    stdscr.addstr(draw_y, draw_x, "  ")

    # Información adicional.
    info_y = top_offset_y
    info_x = left_offset_x + (BOARD_WIDTH + 3) * 2
    stdscr.addstr(info_y, info_x, f"Puntuación: {score}")
    stdscr.addstr(info_y + 1, info_x, f"Nivel: {level}")
    stdscr.addstr(info_y + 2, info_x, f"Líneas: {lines}")

    stdscr.addstr(info_y + 4, info_x, "Siguiente:")
    for y, row in enumerate(next_piece.shape):
        line = "".join("[]" if cell else "  " for cell in row)
        stdscr.addstr(info_y + 5 + y, info_x, line)

    stdscr.refresh()


def game_over_screen(stdscr: "curses._CursesWindow", score: int) -> None:
    """Muestra el mensaje de fin del juego."""
    stdscr.nodelay(False)
    stdscr.addstr(BOARD_HEIGHT // 2, 5, f"Juego terminado. Puntuación: {score}. Presiona cualquier tecla para salir.")
    stdscr.getch()


def tetris(stdscr: "curses._CursesWindow") -> None:
    """Bucle principal del juego."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    board = create_board()
    current_piece = new_piece()
    next_piece = new_piece()
    score = 0
    level = 1
    lines_cleared = 0

    fall_speed = 0.6
    last_time = time.time()
    fall_accumulator = 0.0

    while True:
        now = time.time()
        fall_accumulator += now - last_time
        last_time = now

        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key == ord("q"):
            break
        elif key == curses.KEY_LEFT:
            if not collision(board, current_piece.shape, current_piece.x - 1, current_piece.y):
                current_piece.x -= 1
        elif key == curses.KEY_RIGHT:
            if not collision(board, current_piece.shape, current_piece.x + 1, current_piece.y):
                current_piece.x += 1
        elif key == curses.KEY_DOWN:
            if not collision(board, current_piece.shape, current_piece.x, current_piece.y + 1):
                current_piece.y += 1
                fall_accumulator = 0.0
        elif key == curses.KEY_UP:
            rotated = rotate(current_piece.shape)
            if not collision(board, rotated, current_piece.x, current_piece.y):
                current_piece.shape = rotated
        elif key == ord(" "):
            while not collision(board, current_piece.shape, current_piece.x, current_piece.y + 1):
                current_piece.y += 1
            fall_accumulator = fall_speed

        if fall_accumulator >= fall_speed:
            fall_accumulator = 0.0
            if not collision(board, current_piece.shape, current_piece.x, current_piece.y + 1):
                current_piece.y += 1
            else:
                merge(board, current_piece)
                cleared = clear_lines(board)
                if cleared:
                    lines_cleared += cleared
                    score += (cleared ** 2) * 100
                    level = lines_cleared // 10 + 1
                    fall_speed = max(0.1, 0.6 - (level - 1) * 0.05)
                current_piece = next_piece
                next_piece = new_piece()
                if collision(board, current_piece.shape, current_piece.x, current_piece.y):
                    draw_board(stdscr, board, None, next_piece, score, level, lines_cleared)
                    game_over_screen(stdscr, score)
                    return

        draw_board(stdscr, board, current_piece, next_piece, score, level, lines_cleared)


def main() -> None:
    """Punto de entrada del juego."""
    curses.wrapper(tetris)


if __name__ == "__main__":
    main()
