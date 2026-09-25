import random

WIDTH = 60
HEIGHT = 24
INTENSITY_LEVELS = 30

ANSI_PALETTE = [
    '\033[30m', '\033[90m', '\033[33m', '\033[93m',
    '\033[93m', '\033[93m', '\033[91m', '\033[93m',
    '\033[91m', '\033[91m', '\033[93m', '\033[91m',
    '\033[97m', '\033[97m', '\033[97m', '\033[93m',
    '\033[91m', '\033[93m', '\033[93m', '\033[91m',
    '\033[93m', '\033[93m', '\033[91m', '\033[93m',
    '\033[91m', '\033[97m', '\033[97m', '\033[97m',
    '\033[97m', '\033[97m',
]
RESET = '\033[0m'


def create_fire_grid(w: int, h: int) -> list[list[int]]:
    grid = [[0] * w for _ in range(h)]
    for x in range(w):
        grid[h - 1][x] = random.randint(INTENSITY_LEVELS // 2, INTENSITY_LEVELS - 1)
    return grid


def propagate(grid: list[list[int]], w: int, h: int):
    for y in range(h - 1):
        for x in range(w):
            wind = random.randint(-1, 1)
            nx = max(0, min(w - 1, x + wind))
            grid[y][x] = max(0, min(INTENSITY_LEVELS - 1, grid[y + 1][nx] - random.randint(0, 2)))
    for x in range(w):
        grid[h - 1][x] = random.randint(INTENSITY_LEVELS // 2, INTENSITY_LEVELS - 1)


def render(grid: list[list[int]]):
    rows = []
    for row in grid:
        line = ''.join(f"{ANSI_PALETTE[cell]}█{RESET}" for cell in row)
        rows.append(line)
    print('\033[H' + '\n'.join(rows), end='', flush=True)
