"""Command-line Tic Tac Toe game."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence


@dataclass
class Board:
    squares: List[str]

    @classmethod
    def empty(cls) -> "Board":
        return cls([" "] * 9)

    def place(self, index: int, token: str) -> None:
        if not (0 <= index < 9):
            raise ValueError("index must be between 0 and 8")
        if self.squares[index] != " ":
            raise ValueError("That square is already taken.")
        self.squares[index] = token

    def winner(self) -> Optional[str]:
        lines: Sequence[Sequence[int]] = (
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        )
        for a, b, c in lines:
            if self.squares[a] == self.squares[b] == self.squares[c] != " ":
                return self.squares[a]
        return None

    def is_full(self) -> bool:
        return all(square != " " for square in self.squares)

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        rows = [self.squares[i : i + 3] for i in range(0, 9, 3)]
        rendered_rows = [" | ".join(row) for row in rows]
        divider = "\n---+---+---\n"
        return divider.join(rendered_rows)


def prompt_move(player: str, board: Board, input_func=input) -> int:
    while True:
        try:
            raw = input_func(f"Jugador {player}, elige una casilla (1-9): ")
            index = int(raw) - 1
            board.place(index, player)
            return index
        except ValueError as err:
            print(f"Entrada inválida: {err}")
        except (TypeError, EOFError, KeyboardInterrupt):
            print("Entrada cancelada. Finalizando juego.")
            raise SystemExit(1)


def play() -> None:
    print("Bienvenido a Tic Tac Toe!\n")
    board = Board.empty()
    players = ["X", "O"]
    turn = 0

    while True:
        current_player = players[turn % 2]
        print(board)
        prompt_move(current_player, board)

        winner = board.winner()
        if winner:
            print(board)
            print(f"\n¡Felicidades! El jugador {winner} ha ganado.")
            break

        if board.is_full():
            print(board)
            print("\nEs un empate.")
            break

        turn += 1


if __name__ == "__main__":
    play()
