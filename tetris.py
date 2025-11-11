"""Interfaz de Tetris basada en ``curses``.

Toda la lógica del juego reside en :mod:`tetris_engine`. Este script se
limita a gestionar la interacción con la terminal.
"""
from __future__ import annotations

import curses
import time
from typing import Tuple

from tetris_engine import DEFAULT_BOARD_HEIGHT, DEFAULT_BOARD_WIDTH, TetrisGame


def draw_board(stdscr: "curses._CursesWindow", game: TetrisGame) -> None:
    stdscr.clear()
    stdscr.addstr(
        0,
        0,
        "Tetris - Controles: ← → mover, ↑ rotar, ↓ caer suave, espacio caer rápido, q salir",
    )

    top_offset_y = 2
    left_offset_x = 2

    piece = game.current_piece
    ghost_cells = set()
    if piece is not None:
        shadow_y = game.get_shadow_y()
        if shadow_y is not None:
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        ghost_cells.add((shadow_y + y, piece.x + x))

    for y in range(game.height + 2):
        for x in range(game.width + 2):
            draw_y = top_offset_y + y
            draw_x = left_offset_x + x * 2
            if y == 0 or y == game.height + 1 or x == 0 or x == game.width + 1:
                stdscr.addstr(draw_y, draw_x, "##")
                continue

            board_y = y - 1
            board_x = x - 1
            cell = game.board[board_y][board_x]
            ch = "  "

            if piece is not None:
                rel_y = board_y - piece.y
                rel_x = board_x - piece.x
                if 0 <= rel_y < piece.height and 0 <= rel_x < piece.width and piece.shape[rel_y][rel_x]:
                    ch = "[]"
                elif (board_y, board_x) in ghost_cells and cell == " ":
                    ch = ".."
            if cell != " ":
                ch = "[]"

            stdscr.addstr(draw_y, draw_x, ch)

    info_y = top_offset_y
    info_x = left_offset_x + (game.width + 3) * 2
    stdscr.addstr(info_y, info_x, f"Puntuación: {game.score}")
    stdscr.addstr(info_y + 1, info_x, f"Nivel: {game.level}")
    stdscr.addstr(info_y + 2, info_x, f"Líneas: {game.lines_cleared}")

    stdscr.addstr(info_y + 4, info_x, "Siguiente:")
    for y, row in enumerate(game.next_piece.shape):
        line = "".join("[]" if cell else "  " for cell in row)
        stdscr.addstr(info_y + 5 + y, info_x, line)

    stdscr.refresh()


def game_over_screen(stdscr: "curses._CursesWindow", game: TetrisGame) -> None:
    stdscr.nodelay(False)
    stdscr.addstr(
        DEFAULT_BOARD_HEIGHT // 2,
        4,
        f"Juego terminado. Puntuación: {game.score}. Pulsa r para reiniciar o cualquier otra tecla para salir.",
    )
    key = stdscr.getch()
    if key in (ord("r"), ord("R")):
        game.reset()
        stdscr.nodelay(True)
        stdscr.timeout(0)
        run_loop(stdscr, game)


def handle_input(game: TetrisGame, key: int) -> Tuple[bool, bool]:
    """Procesa la entrada del usuario.

    Devuelve una tupla ``(forced_drop, quit_game)``.
    """

    forced_drop = False
    if key == ord("q"):
        return False, True
    if key == curses.KEY_LEFT:
        game.move(-1)
    elif key == curses.KEY_RIGHT:
        game.move(1)
    elif key == curses.KEY_DOWN:
        moved = game.soft_drop()
        if moved:
            forced_drop = True
    elif key == curses.KEY_UP:
        game.rotate(clockwise=True)
    elif key == ord(" "):
        game.hard_drop()
        forced_drop = True
    return forced_drop, False


def run_loop(stdscr: "curses._CursesWindow", game: TetrisGame) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    last_time = time.time()
    accumulator = 0.0

    while not game.game_over:
        now = time.time()
        accumulator += now - last_time
        last_time = now

        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key != -1:
            forced_drop, quit_game = handle_input(game, key)
            if quit_game:
                return
            if forced_drop:
                accumulator = 0.0

        target_speed = max(0.1, 0.6 - (game.level - 1) * 0.05)
        fall_speed = target_speed

        if accumulator >= fall_speed:
            accumulator = 0.0
            game.tick()

        draw_board(stdscr, game)
        time.sleep(0.01)

    draw_board(stdscr, game)
    game_over_screen(stdscr, game)


def main() -> None:
    game = TetrisGame(width=DEFAULT_BOARD_WIDTH, height=DEFAULT_BOARD_HEIGHT)
    curses.wrapper(lambda stdscr: run_loop(stdscr, game))


if __name__ == "__main__":
    main()
