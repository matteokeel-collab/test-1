"""Motor principal del juego de Tetris.

Este módulo separa la lógica del juego de la interfaz basada en
``curses`` para facilitar las pruebas y permitir futuras extensiones.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import random


DEFAULT_BOARD_WIDTH = 10
DEFAULT_BOARD_HEIGHT = 20

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


def rotate_clockwise(shape: Sequence[Sequence[int]]) -> List[List[int]]:
    """Devuelve una copia de la figura girada 90 grados en sentido horario."""

    return [list(row) for row in zip(*shape[::-1])]


class TetrisGame:
    """Gestiona el estado interno de una partida de Tetris."""

    width: int
    height: int

    def __init__(
        self,
        *,
        width: int = DEFAULT_BOARD_WIDTH,
        height: int = DEFAULT_BOARD_HEIGHT,
        seed: int | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.random = random.Random(seed)

        self.board: List[List[str]] = self._create_board()
        self.lines_cleared = 0
        self.score = 0
        self.level = 1
        self.game_over = False

        self.current_piece: Piece | None = None
        self.next_piece: Piece = self._generate_piece()
        self.spawn_piece()

    # ------------------------------------------------------------------
    # Creación y comprobación de piezas
    # ------------------------------------------------------------------
    def _create_board(self) -> List[List[str]]:
        return [[" "] * self.width for _ in range(self.height)]

    def _generate_piece(self) -> Piece:
        letter = self.random.choice(list(TETROMINOES))
        shape = [row[:] for row in TETROMINOES[letter]]
        x = self.width // 2 - len(shape[0]) // 2
        y = -len(shape)
        return Piece(shape=shape, x=x, y=y, letter=letter)

    def spawn_piece(self) -> None:
        """Coloca la siguiente pieza en juego."""

        self.current_piece = self.next_piece
        self.next_piece = self._generate_piece()
        if self.current_piece is not None and self._collides(
            self.current_piece.shape, self.current_piece.x, self.current_piece.y
        ):
            self.game_over = True

    def _collides(self, shape: Sequence[Sequence[int]], offset_x: int, offset_y: int) -> bool:
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if not cell:
                    continue
                board_x = offset_x + x
                board_y = offset_y + y
                if board_x < 0 or board_x >= self.width:
                    return True
                if board_y >= self.height:
                    return True
                if board_y >= 0 and self.board[board_y][board_x] != " ":
                    return True
        return False

    # ------------------------------------------------------------------
    # Acciones del jugador
    # ------------------------------------------------------------------
    def move(self, dx: int) -> bool:
        """Intenta mover la pieza activa horizontalmente."""

        if self.game_over or self.current_piece is None:
            return False
        new_x = self.current_piece.x + dx
        if not self._collides(self.current_piece.shape, new_x, self.current_piece.y):
            self.current_piece.x = new_x
            return True
        return False

    def rotate(self, clockwise: bool = True) -> bool:
        """Gira la pieza activa.

        Se aplican pequeños *wall kicks* para permitir la rotación junto a
        las paredes del tablero.
        """

        if self.game_over or self.current_piece is None:
            return False

        piece = self.current_piece
        rotated = rotate_clockwise(piece.shape)
        if not clockwise:
            rotated = rotate_clockwise(rotate_clockwise(rotate_clockwise(piece.shape)))

        # Intentamos pequeñas correcciones para evitar colisiones en muros.
        for offset_x, offset_y in ((0, 0), (-1, 0), (1, 0), (0, -1)):
            if not self._collides(rotated, piece.x + offset_x, piece.y + offset_y):
                piece.shape = [row[:] for row in rotated]
                piece.x += offset_x
                piece.y += offset_y
                return True
        return False

    def soft_drop(self) -> bool:
        """Avanza la pieza una fila. Si no puede, se bloquea."""

        if self.game_over or self.current_piece is None:
            return False
        piece = self.current_piece
        if not self._collides(piece.shape, piece.x, piece.y + 1):
            piece.y += 1
            return True
        self._lock_piece()
        return False

    def hard_drop(self) -> int:
        """Deja caer la pieza hasta la posición final y la bloquea."""

        if self.game_over or self.current_piece is None:
            return 0
        piece = self.current_piece
        dropped = 0
        while not self._collides(piece.shape, piece.x, piece.y + 1):
            piece.y += 1
            dropped += 1
        self._lock_piece()
        return dropped

    def tick(self) -> None:
        """Actualiza la partida aplicando la gravedad."""

        self.soft_drop()

    # ------------------------------------------------------------------
    # Gestión del tablero y puntuaciones
    # ------------------------------------------------------------------
    def _lock_piece(self) -> None:
        if self.current_piece is None:
            return
        piece = self.current_piece
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell and piece.y + y >= 0:
                    self.board[piece.y + y][piece.x + x] = piece.letter
        cleared = self._clear_lines()
        if cleared:
            self.lines_cleared += cleared
            self.score += (cleared**2) * 100
            self.level = self.lines_cleared // 10 + 1
        self.spawn_piece()

    def _clear_lines(self) -> int:
        remaining_rows = [row for row in self.board if " " in row]
        cleared = self.height - len(remaining_rows)
        while len(remaining_rows) < self.height:
            remaining_rows.insert(0, [" "] * self.width)
        self.board[:] = remaining_rows
        return cleared

    # ------------------------------------------------------------------
    # Información para la interfaz
    # ------------------------------------------------------------------
    def get_shadow_y(self) -> int | None:
        """Calcula la posición final si se dejara caer la pieza."""

        if self.current_piece is None or self.game_over:
            return None
        y = self.current_piece.y
        while not self._collides(self.current_piece.shape, self.current_piece.x, y + 1):
            y += 1
        return y

    def iter_board_with_piece(self) -> Iterable[Iterable[str]]:
        """Genera la representación del tablero incluyendo la pieza activa."""

        shadow_y = self.get_shadow_y()
        ghost_cells = set()
        if (
            self.current_piece is not None
            and shadow_y is not None
            and shadow_y != self.current_piece.y
        ):
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        ghost_cells.add((shadow_y + y, self.current_piece.x + x))

        for board_y in range(self.height):
            row: List[str] = []
            for board_x in range(self.width):
                cell = self.board[board_y][board_x]
                overlay = cell
                if self.current_piece is not None:
                    rel_y = board_y - self.current_piece.y
                    rel_x = board_x - self.current_piece.x
                    if 0 <= rel_y < self.current_piece.height and 0 <= rel_x < self.current_piece.width:
                        if self.current_piece.shape[rel_y][rel_x]:
                            overlay = "[]"
                    if overlay == cell and (board_y, board_x) in ghost_cells:
                        overlay = ".."
                if overlay == " ":
                    overlay = cell
                row.append(overlay)
            yield row

    def reset(self) -> None:
        """Reinicia la partida conservando la misma instancia de RNG."""

        self.board = self._create_board()
        self.lines_cleared = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        self.current_piece = None
        self.next_piece = self._generate_piece()
        self.spawn_piece()
