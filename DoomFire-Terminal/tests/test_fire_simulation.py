import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # adiciona src no path

from src.config.fire_simulation_configuration import (
    FireSimulationConfig,
    PALETTES,
    WIDTH,
    HEIGHT,
    INTENSITY_LEVELS,
    MIN_WIDTH,
    MAX_WIDTH,
    MIN_HEIGHT,
    MAX_HEIGHT,
)
from src.core.fire_simulation_engine import FireSimulationEngine, create_fire_grid
from src.collection.propagate_fire_grid_logic import propagate_fire_grid_logic, propagate
from src.payloads.render_fire_display_engine import get_render_stats


class TestFireSimulationConfig:
    def test_default_config_valid(self): # testa config padrao
        config = FireSimulationConfig()
        assert config.width == WIDTH
        assert config.height == HEIGHT
        assert config.intensity_levels == INTENSITY_LEVELS
        assert config.palette_name == "classic"
        assert len(config.palette) == INTENSITY_LEVELS

    def test_custom_dimensions(self): # testa tamanho custom
        config = FireSimulationConfig(width=80, height=30)
        assert config.width == 80
        assert config.height == 30

    def test_invalid_width_too_small(self): # largura muito pequena tem que dar erro
        with pytest.raises(ValueError):
            FireSimulationConfig(width=5, height=24)

    def test_invalid_width_too_large(self): # largura muito grande tem que dar erro
        with pytest.raises(ValueError):
            FireSimulationConfig(width=500, height=24)

    def test_invalid_height(self): # altura invalida
        with pytest.raises(ValueError):
            FireSimulationConfig(width=60, height=200)

    def test_invalid_palette(self): # paleta que nao existe
        with pytest.raises(ValueError):
            FireSimulationConfig(palette_name="inexistente")

    def test_all_palettes_valid(self): # todas paletas tem que ser validas
        for name in PALETTES.keys():
            config = FireSimulationConfig(palette_name=name)
            assert len(config.palette) == config.intensity_levels

    def test_fps_property(self): # testa fps
        config = FireSimulationConfig(frame_delay=0.05)
        assert config.fps == pytest.approx(20.0, rel=0.1)

    def test_from_terminal_size(self): # testa from_terminal_size
        config = FireSimulationConfig.from_terminal_size(width=60, height=24)
        assert MIN_WIDTH <= config.width <= MAX_WIDTH
        assert MIN_HEIGHT <= config.height <= MAX_HEIGHT


class TestCreateFireGrid:
    def test_grid_dimensions(self): # ve se grid tem tamanho certo
        grid = create_fire_grid(60, 24)
        assert len(grid) == 24
        assert len(grid[0]) == 60

    def test_grid_initial_values(self): # ve se valores iniciais tao ok
        grid = create_fire_grid(10, 5)
        for y in range(4): # tudo zero menos ultima linha
            assert all(cell == 0 for cell in grid[y])
        for cell in grid[4]: # ultima linha tem que ter fogo
            assert INTENSITY_LEVELS // 2 <= cell < INTENSITY_LEVELS

    def test_grid_small(self): # grid pequeno
        grid = create_fire_grid(10, 5)
        assert len(grid) == 5
        assert len(grid[0]) == 10

    def test_grid_large(self): # grid grande
        grid = create_fire_grid(100, 50)
        assert len(grid) == 50
        assert len(grid[0]) == 100


class TestPropagate:
    def test_propagate_changes_grid(self): # propaga tem que mudar grid
        config = FireSimulationConfig(width=20, height=10)
        engine = FireSimulationEngine(config)
        for _ in range(5):
            engine.propagate()
        active = sum(1 for row in engine.grid[:-1] for cell in row if cell > 0)
        assert active > 0 # tem que ter celula ativa

    def test_propagate_respects_bounds(self): # nao pode sair do limite
        config = FireSimulationConfig(width=10, height=5)
        engine = FireSimulationEngine(config)
        for _ in range(20):
            engine.propagate()
            for row in engine.grid:
                for cell in row:
                    assert 0 <= cell < config.intensity_levels

    def test_propagate_legacy_api(self): # api antiga ainda funciona
        grid = create_fire_grid(20, 10)
        propagate(grid, 20, 10)
        assert len(grid) == 10
        assert len(grid[0]) == 20

    def test_propagate_no_wind(self): # sem vento
        config = FireSimulationConfig(width=20, height=10, wind_enabled=False)
        grid = FireSimulationEngine(config).grid
        propagate_fire_grid_logic(grid, config)
        for row in grid:
            for cell in row:
                assert 0 <= cell < config.intensity_levels

    def test_propagate_custom_wind_intensity(self): # vento custom
        for wind_int in [0, 1, 2, 3]:
            config = FireSimulationConfig(width=15, height=8, wind_intensity=wind_int)
            grid = FireSimulationEngine(config).grid
            propagate_fire_grid_logic(grid, config)
            for row in grid:
                for cell in row:
                    assert 0 <= cell < config.intensity_levels


class TestFireSimulationEngine:
    def test_engine_creation(self): # cria engine
        config = FireSimulationConfig()
        engine = FireSimulationEngine(config)
        assert engine.grid is not None
        assert engine.frame_count == 0

    def test_engine_tick(self): # tick aumenta frame
        config = FireSimulationConfig(width=20, height=10)
        engine = FireSimulationEngine(config)
        initial_frame = engine.frame_count
        engine.propagate()
        assert engine.frame_count == initial_frame + 1

    def test_engine_reset(self): # reset zera tudo
        config = FireSimulationConfig(width=20, height=10)
        engine = FireSimulationEngine(config)
        for _ in range(5):
            engine.propagate()
        assert engine.frame_count == 5
        engine.reset()
        assert engine.frame_count == 0

    def test_engine_resize(self): # resize muda tamanho
        config = FireSimulationConfig(width=20, height=10)
        engine = FireSimulationEngine(config)
        engine.resize(30, 15)
        assert engine.config.width == 30
        assert engine.config.height == 15
        assert len(engine.grid) == 15
        assert len(engine.grid[0]) == 30

    def test_engine_palette_switch(self): # troca paleta
        config = FireSimulationConfig(palette_name="classic")
        engine = FireSimulationEngine(config)
        assert engine.config.palette_name == "classic"
        engine.set_palette("blue")
        assert engine.config.palette_name == "blue"

    def test_engine_stats(self): # stats
        config = FireSimulationConfig(width=10, height=5)
        engine = FireSimulationEngine(config)
        stats = engine.get_stats()
        assert "frame" in stats
        assert "width" in stats
        assert "height" in stats
        assert stats["width"] == 10
        assert stats["height"] == 5


class TestRenderStats:
    def test_stats_empty_grid(self): # grid vazio
        stats = get_render_stats([])
        assert stats["min"] == 0

    def test_stats_normal_grid(self): # grid normal
        grid = create_fire_grid(10, 5)
        stats = get_render_stats(grid)
        assert "min" in stats
        assert "max" in stats
        assert "avg" in stats
        assert "active_cells" in stats
        assert stats["total_cells"] == 50
        assert 0 <= stats["active_percent"] <= 100


class TestIntegration:
    def test_full_simulation_100_frames(self): # 100 frames sem crash, se crashar ferrou
        config = FireSimulationConfig(width=30, height=15, frame_delay=0.02)
        engine = FireSimulationEngine(config)
        for _ in range(100):
            engine.propagate()
        assert engine.frame_count == 100
        assert len(engine.grid) == 15
        assert len(engine.grid[0]) == 30

    def test_all_palettes_simulation(self): # cada paleta roda 10 frames
        for palette_name in PALETTES.keys():
            config = FireSimulationConfig(width=20, height=10, palette_name=palette_name)
            engine = FireSimulationEngine(config)
            for _ in range(10):
                engine.propagate()
            assert engine.frame_count == 10
