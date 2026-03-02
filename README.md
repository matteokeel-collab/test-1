## Requisitos

- Python 3.8 o superior

## Juegos incluidos

- `tic_tac_toe.py`: Tic Tac Toe en terminal.
- `tetris.py`: Tetris en terminal (usa `curses`).
- `fish_auto.py`: asistente básico de auto-pesca para el minijuego **Fish!** en VRChat.

## Fish! Auto (VRChat)

Este script usa una estrategia sencilla y robusta:

1. Captura una región pequeña de pantalla donde aparece el indicador de mordida.
2. Calcula el brillo medio de esa región.
3. Si detecta un cambio brusco (pico de brillo), pulsa una tecla (`e` por defecto).

> Nota: como los mundos de VRChat pueden cambiar UI/efectos, el script es **configurable**
> (región, umbral y cooldown) para que lo ajustes a tu setup.

### Instalación de dependencias

```bash
pip install pyautogui pillow
```

### Calibración rápida

```bash
python fish_auto.py --calibrar
```

Mueve el mouse sobre la zona del aviso de mordida y toma las coordenadas aproximadas.
Luego define la región con formato `x,y,ancho,alto`.

### Ejecución

```bash
python fish_auto.py --region 850,520,220,120 --tecla e --umbral 22 --cooldown 0.9
```

Parámetros principales:

- `--region`: región donde mirar el indicador.
- `--tecla`: tecla a pulsar cuando pica.
- `--umbral`: sensibilidad al cambio de brillo (más bajo = más sensible).
- `--cooldown`: tiempo mínimo entre pulsaciones para evitar spam.

## Cómo jugar

### Tic Tac Toe

```bash
python tic_tac_toe.py
```

### Tetris

```bash
python tetris.py
```
