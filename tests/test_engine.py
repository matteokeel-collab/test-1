import unittest

from tetris_engine import Piece, TetrisGame


class TetrisEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = TetrisGame(width=4, height=4, seed=0)

    def test_line_clear_updates_score_and_level(self) -> None:
        self.game.lines_cleared = 9
        self.game.score = 0
        self.game.board[-1] = ["X", "X", "X", " "]

        piece = Piece(shape=[[1]], x=3, y=2, letter="I")
        self.game.current_piece = piece
        self.game.next_piece = Piece(shape=[[1]], x=0, y=-1, letter="I")

        moved = self.game.soft_drop()
        self.assertTrue(moved)
        moved = self.game.soft_drop()
        self.assertFalse(moved)

        self.assertEqual(self.game.lines_cleared, 10)
        self.assertEqual(self.game.level, 2)
        self.assertEqual(self.game.score, 100)
        self.assertEqual(self.game.board[-1], [" ", " ", " ", " "])

    def test_hard_drop_returns_distance_and_locks(self) -> None:
        piece = Piece(shape=[[1], [1]], x=1, y=0, letter="I")
        self.game.current_piece = piece
        self.game.next_piece = Piece(shape=[[1]], x=0, y=-1, letter="I")

        distance = self.game.hard_drop()
        self.assertEqual(distance, 2)
        self.assertEqual(self.game.board[2][1], "I")
        self.assertEqual(self.game.board[3][1], "I")
        self.assertIsNotNone(self.game.current_piece)

    def test_rotate_applies_wall_kick(self) -> None:
        piece = Piece(shape=[[1, 1, 1], [0, 1, 0]], x=0, y=0, letter="T")
        self.game.current_piece = piece
        self.game.next_piece = Piece(shape=[[1]], x=0, y=-1, letter="I")

        rotated = self.game.rotate(clockwise=True)
        self.assertTrue(rotated)
        self.assertEqual(piece.shape, [[0, 1], [1, 1], [0, 1]])
        self.assertGreaterEqual(piece.x, 0)


if __name__ == "__main__":
    unittest.main()
