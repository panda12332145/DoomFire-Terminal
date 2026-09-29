import random
from typing import List
from ..config.fire_simulation_configuration import FireSimulationConfig, INTENSITY_LEVELS


def propagate_fire_grid_logic(
    grid: List[List[int]],
    config: FireSimulationConfig,
) -> None:
    w = config.width # pega largura, da config
    h = config.height # pega altura
    max_intensity = config.intensity_levels - 1 # maximo de intensidade
    min_source = config.intensity_levels // 2 # minimo da fonte, pra nao apagar

    for y in range(h - 1): # percorre de baixo pra cima, menos a ultima linha
        row_below = grid[y + 1] # linha de baixo
        row_current = grid[y] # linha atual
        for x in range(w): # pra cada coluna
            if config.wind_enabled: # se vento ligado
                wind = random.randint(-config.wind_intensity, config.wind_intensity) # vento aleatorio, -1 a 1
                nx = x + wind # nova posicao com vento
                if nx < 0: # se passou da esquerda
                    nx = 0
                elif nx >= w: # se passou da direita
                    nx = w - 1
            else:
                nx = x # sem vento, fica reto

            decay = random.randint(config.decay_min, config.decay_max) # decaimento aleatorio
            new_val = row_below[nx] - decay # novo valor, pega de baixo menos decaimento

            if new_val < 0: # nao deixa negativo
                new_val = 0
            elif new_val > max_intensity: # nao deixa passar do maximo
                new_val = max_intensity

            row_current[x] = new_val # seta valor

    base_row = grid[h - 1] # ultima linha, fonte de calor
    for x in range(w): # pra cada coluna da base
        base_row[x] = random.randint(min_source, max_intensity) # randomiza de novo, pra manter fogo vivo


def propagate(
    grid: List[List[int]],
    w: int,
    h: int,
) -> None:
    config = FireSimulationConfig(width=w, height=h) # cria config com tamanho passado
    propagate_fire_grid_logic(grid, config) # chama logica nova


def propagate_with_custom_decay(
    grid: List[List[int]],
    config: FireSimulationConfig,
    decay_override: int = None,
) -> None:
    if decay_override is not None: # se tem override
        import dataclasses
        temp_config = dataclasses.replace(config, decay_min=0, decay_max=decay_override) # cria config temp com decay diferente
        propagate_fire_grid_logic(grid, temp_config) # propaga com decay custom
    else:
        propagate_fire_grid_logic(grid, config) # propaga normal
