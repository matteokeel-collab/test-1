"""Asistente simple para automatizar la pesca en Fish! (VRChat).

Uso rápido:
    python fish_auto.py --calibrar
    python fish_auto.py --tecla e --region 850,520,220,120

El script detecta un cambio brusco de brillo en una región de la pantalla
(normalmente donde aparece la alerta de mordida) y pulsa una tecla para recoger.
"""
from __future__ import annotations

import argparse
import statistics
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Tuple

Region = Tuple[int, int, int, int]


def _load_runtime_deps():
    try:
        import pyautogui
        from PIL import ImageGrab, ImageStat
    except ImportError as exc:  # pragma: no cover - dependencia opcional en tests
        raise SystemExit(
            "Faltan dependencias. Instala con: pip install pyautogui pillow"
        ) from exc
    return pyautogui, ImageGrab, ImageStat



@dataclass
class BiteDetector:
    """Detecta mordidas basándose en cambios de brillo medio."""

    window: int = 20
    threshold_delta: float = 22.0

    def __post_init__(self) -> None:
        if self.window < 3:
            raise ValueError("window debe ser >= 3")
        self._history: Deque[float] = deque(maxlen=self.window)

    def update(self, brightness: float) -> bool:
        if len(self._history) < self.window:
            self._history.append(brightness)
            return False

        baseline = statistics.fmean(self._history)
        self._history.append(brightness)
        return abs(brightness - baseline) >= self.threshold_delta


@dataclass
class AutoFishConfig:
    region: Region
    key: str = "e"
    interval_s: float = 0.07
    cooldown_s: float = 0.9
    threshold_delta: float = 22.0


class AutoFisher:
    def __init__(self, config: AutoFishConfig):
        self.config = config
        self.detector = BiteDetector(threshold_delta=config.threshold_delta)
        self._last_trigger = 0.0

    def _grab_brightness(self) -> float:
        _, ImageGrab, ImageStat = _load_runtime_deps()
        img = ImageGrab.grab(bbox=self.config.region)
        return ImageStat.Stat(img.convert("L")).mean[0]

    def tick(self, now: float | None = None) -> bool:
        now = now or time.time()
        brightness = self._grab_brightness()
        bite = self.detector.update(brightness)
        if not bite:
            return False
        if now - self._last_trigger < self.config.cooldown_s:
            return False

        pyautogui, _, _ = _load_runtime_deps()
        pyautogui.press(self.config.key)
        self._last_trigger = now
        return True

    def run(self) -> None:
        print("AutoFish activo. CTRL+C para salir.")
        while True:
            try:
                self.tick()
                time.sleep(self.config.interval_s)
            except KeyboardInterrupt:
                print("\nAutoFish detenido.")
                return


def parse_region(raw: str) -> Region:
    try:
        x, y, w, h = [int(part.strip()) for part in raw.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "La región debe tener formato x,y,ancho,alto"
        ) from exc
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("ancho y alto deben ser > 0")
    return x, y, x + w, y + h


def calibrate(seconds: int = 6) -> None:
    print("Calibración simple (sin clicks):")
    print("1) Sitúa la ventana del juego en primer plano.")
    print("2) Mueve el mouse sobre el área del aviso de mordida.")
    print("3) Espera a ver coordenadas y brillo para copiar en --region.")

    pyautogui, ImageGrab, ImageStat = _load_runtime_deps()
    end = time.time() + seconds
    while time.time() < end:
        x, y = pyautogui.position()
        sample = ImageGrab.grab(bbox=(x - 20, y - 20, x + 20, y + 20))
        brightness = ImageStat.Stat(sample.convert("L")).mean[0]
        print(f"x={x} y={y} brillo={brightness:.1f}", end="\r", flush=True)
        time.sleep(0.1)
    print("\nCalibración terminada.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auto pesca básica para Fish! (VRChat)")
    parser.add_argument(
        "--region",
        type=parse_region,
        default=parse_region("800,450,300,180"),
        help="Región de captura como x,y,ancho,alto",
    )
    parser.add_argument("--tecla", default="e", help="Tecla para recoger")
    parser.add_argument("--intervalo", type=float, default=0.07, help="Tiempo entre muestras")
    parser.add_argument("--cooldown", type=float, default=0.9, help="Espera mínima entre pulsaciones")
    parser.add_argument(
        "--umbral",
        type=float,
        default=22.0,
        help="Cambio mínimo de brillo para considerar mordida",
    )
    parser.add_argument("--calibrar", action="store_true", help="Ayuda para calibrar región")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.calibrar:
        calibrate()
        return

    config = AutoFishConfig(
        region=args.region,
        key=args.tecla,
        interval_s=max(args.intervalo, 0.02),
        cooldown_s=max(args.cooldown, 0.1),
        threshold_delta=max(args.umbral, 1.0),
    )
    AutoFisher(config).run()


if __name__ == "__main__":
    main()
