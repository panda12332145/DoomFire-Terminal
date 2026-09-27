import random
from typing import List, Optional

from ..config.fire_simulation_configuration import (
    FireSimulationConfig,
    INTENSITY_LEVELS,
    WIDTH,
    HEIGHT,
)
from ..collection.propagate_fire_grid_logic import propagate_fire_grid_logic
from ..payloads.render_fire_display_engine import render_fire_display_engine, get_render_stats


class FireSimulationEngine:

    def __init__(self, config: Optional[FireSimulationConfig] = None):
        self.config = config or FireSimulationConfig() # se nao passar config usa padrao
        self.grid: List[List[int]] = self.create_fire_grid() # cria grid inicial
        self.frame_count: int = 0 # contador de frames

    def create_fire_grid(self) -> List[List[int]]:
        w = self.config.width # largura
        h = self.config.height # altura
        max_int = self.config.intensity_levels - 1 # maximo
        min_source = self.config.intensity_levels // 2 # minimo da fonte

        grid = [[0] * w for _ in range(h)] # cria matriz zerada
        for x in range(w): # pra cada coluna da base
            grid[h - 1][x] = random.randint(min_source, max_int) # esquenta base
        return grid # retorna grid

    def create_fire_grid_with_dimensions(self, w: int, h: int) -> List[List[int]]:
        max_int = self.config.intensity_levels - 1 # maximo
        min_source = self.config.intensity_levels // 2 # minimo
        grid = [[0] * w for _ in range(h)] # matriz zerada
        for x in range(w):
            grid[h - 1][x] = random.randint(min_source, max_int) # esquenta
        return grid

    def propagate(self) -> None:
        propagate_fire_grid_logic(self.grid, self.config) # propaga fogo
        self.frame_count += 1 # incrementa frame

    def render(self) -> None:
        render_fire_display_engine(self.grid, self.config) # renderiza

    def tick(self) -> None:
        self.propagate() # avanca
        self.render() # desenha

    def reset(self) -> None:
        self.grid = self.create_fire_grid() # cria grid novo
        self.frame_count = 0 # zera contador

    def resize(self, new_width: int, new_height: int) -> None:
        from dataclasses import replace
        self.config = replace(self.config, width=new_width, height=new_height) # troca tamanho na config
        self.config = FireSimulationConfig( # recria config pra validar
            width=new_width,
            height=new_height,
            intensity_levels=self.config.intensity_levels,
            frame_delay=self.config.frame_delay,
            palette_name=self.config.palette_name,
            wind_enabled=self.config.wind_enabled,
            wind_intensity=self.config.wind_intensity,
            decay_min=self.config.decay_min,
            decay_max=self.config.decay_max,
            auto_resize=self.config.auto_resize,
        )
        self.grid = self.create_fire_grid() # cria grid novo com tamanho novo

    def get_stats(self) -> dict:
        stats = get_render_stats(self.grid) # pega stats do render
        stats.update({
            "frame": self.frame_count, # frame atual
            "width": self.config.width, # largura
            "height": self.config.height, # altura
            "fps_target": self.config.fps, # fps alvo
            "palette": self.config.palette_name, # paleta
            "wind": self.config.wind_enabled, # vento ligado
        })
        return stats

    def set_palette(self, palette_name: str) -> None:
        new_config = FireSimulationConfig( # cria config nova com paleta diferente
            width=self.config.width,
            height=self.config.height,
            intensity_levels=self.config.intensity_levels,
            frame_delay=self.config.frame_delay,
            palette_name=palette_name,
            wind_enabled=self.config.wind_enabled,
            wind_intensity=self.config.wind_intensity,
            decay_min=self.config.decay_min,
            decay_max=self.config.decay_max,
            auto_resize=self.config.auto_resize,
        )
        self.config = new_config # troca config


def create_fire_grid(w: int, h: int) -> List[List[int]]:
    try:
        temp_config = FireSimulationConfig(width=w, height=h) # valida tamanho
        min_source = temp_config.intensity_levels // 2
        max_int = temp_config.intensity_levels - 1
    except ValueError:
        min_source = INTENSITY_LEVELS // 2 # fallback
        max_int = INTENSITY_LEVELS - 1

    grid = [[0] * w for _ in range(h)] # cria grid
    for x in range(w):
        grid[h - 1][x] = random.randint(min_source, max_int) # esquenta base
    return grid


def generate_fire_grid_propagation_render_engine(w: int = WIDTH, h: int = HEIGHT) -> FireSimulationEngine:
    config = FireSimulationConfig(width=w, height=h) # config com tamanho
    return FireSimulationEngine(config) # retorna engine


from ..config.fire_simulation_configuration import (
    WIDTH as WIDTH,
    HEIGHT as HEIGHT,
    INTENSITY_LEVELS as INTENSITY_LEVELS,
    ANSI_PALETTE as ANSI_PALETTE,
    RESET as RESET,
    CLASSIC_DOOM_PALETTE,
    ORIGINAL_PALETTE,
)

from ..collection.propagate_fire_grid_logic import propagate as propagate
from ..payloads.render_fire_display_engine import render as render
