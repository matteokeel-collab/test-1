# Tetris en la Terminal

Este repositorio contiene una implementación sencilla del clásico juego **Tetris** escrita en Python utilizando la biblioteca estándar `curses`. El objetivo es ofrecer una versión jugable directamente en la terminal y un punto de partida claro para extender el proyecto.

## Requisitos

- Python 3.8 o superior
- Una terminal compatible con `curses` (Linux y macOS lo soportan de forma nativa. En Windows se recomienda jugar desde WSL o instalar la extensión `windows-curses`).

## Cómo jugar

1. Clona este repositorio y entra al directorio del proyecto.
2. Ejecuta el juego con:

   ```bash
   python tetris.py
   ```

3. Controla las piezas con las siguientes teclas:
   - `←` / `→`: mover la pieza actual.
   - `↑`: rotar la pieza.
   - `↓`: acelerar la caída.
   - `Espacio`: dejar caer la pieza al instante.
   - `q`: salir del juego.

4. El juego termina cuando las piezas alcanzan la parte superior del tablero.

## Estructura del proyecto

- `tetris.py`: contiene toda la lógica del juego, incluyendo la gestión del tablero, la generación de piezas, la detección de colisiones y el bucle principal con la interfaz en la terminal.

## Próximos pasos sugeridos

- Añadir un sistema de almacenamiento de puntuaciones máximas (high scores).
- Implementar pruebas unitarias para las funciones de rotación y detección de colisiones.
- Agregar efectos de sonido y colores para mejorar la experiencia de juego.
