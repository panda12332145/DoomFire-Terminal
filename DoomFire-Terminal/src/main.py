import time
import os
from .fire_engine import create_fire_grid, propagate, render, WIDTH, HEIGHT

FRAME_DELAY = 0.05  # segundos entre frames


def main():
    print('\033[2J\033[?25l', end='')  # Limpa tela e esconde cursor
    try:
        grid = create_fire_grid(WIDTH, HEIGHT)
        while True:
            propagate(grid, WIDTH, HEIGHT)
            render(grid)
            time.sleep(FRAME_DELAY)
    except KeyboardInterrupt:
        pass
    finally:
        print('\033[?25h')  # Restaura cursor


if __name__ == "__main__":
    main()
