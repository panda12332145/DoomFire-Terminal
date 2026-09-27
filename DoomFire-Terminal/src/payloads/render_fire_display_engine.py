from typing import List
import sys
import shutil

from ..config.fire_simulation_configuration import (
    FireSimulationConfig,
    RESET,
    CURSOR_HOME,
    CLASSIC_DOOM_PALETTE,
)


def render_fire_display_engine(
    grid: List[List[int]],
    config: FireSimulationConfig,
    use_colorama: bool = False,
) -> None:
    palette = config.palette # pega paleta da config
    rows = [] # lista de linhas
    reset = RESET # alias pro reset, pra ficar rapido
    for row in grid: # pra cada linha do grid
        line = ''.join(f"{palette[cell]}█{reset}" for cell in row) # junta tudo com cor e bloco
        rows.append(line) # adiciona linha

    output = CURSOR_HOME + '\n'.join(rows) # junta tudo com cursor no home
    sys.stdout.write(output) # escreve
    sys.stdout.flush() # flush pra aparecer na hora


def render(
    grid: List[List[int]],
) -> None:
    from ..config.fire_simulation_configuration import FireSimulationConfig
    config = FireSimulationConfig() # config padrao
    h = len(grid) # altura do grid
    w = len(grid[0]) if h > 0 else config.width # largura
    if w != config.width or h != config.height: # se tamanho diferente
        try:
            config = FireSimulationConfig(width=w, height=h) # tenta criar config com tamanho do grid
        except ValueError:
            pass # se der erro usa padrao mesmo
    render_fire_display_engine(grid, config) # renderiza


def render_with_status(
    grid: List[List[int]],
    config: FireSimulationConfig,
    status_line: str = "",
) -> None:
    palette = config.palette # paleta
    reset = RESET # reset
    rows = [''.join(f"{palette[cell]}█{reset}" for cell in row) for row in grid] # renderiza grid

    if status_line: # se tem status
        status = status_line[:config.width].ljust(config.width) # corta e alinha
        rows.append(f"{RESET}{status}") # adiciona status

    output = CURSOR_HOME + '\n'.join(rows) # junta
    output += '\033[J' # limpa resto da tela
    sys.stdout.write(output) # escreve
    sys.stdout.flush() # flush


def get_render_stats(grid: List[List[int]]) -> dict:
    if not grid or not grid[0]: # se grid vazio
        return {"min": 0, "max": 0, "avg": 0, "active_cells": 0}

    flat = [cell for row in grid for cell in row] # achata grid
    total = len(flat) # total de celulas
    active = sum(1 for c in flat if c > 0) # quantas ativas
    return {
        "min": min(flat) if flat else 0, # minimo
        "max": max(flat) if flat else 0, # maximo
        "avg": sum(flat) / total if total else 0, # media
        "active_cells": active, # ativas
        "total_cells": total, # total
        "active_percent": (active / total * 100) if total else 0, # porcentagem ativa
    }
