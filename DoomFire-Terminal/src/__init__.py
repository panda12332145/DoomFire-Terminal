__version__ = "2.0.0" # versao
__author__ = "Panda12332145" # autor

from .config.fire_simulation_configuration import FireSimulationConfig, PALETTES # importa config
from .core.fire_simulation_engine import FireSimulationEngine # importa engine

__all__ = ["FireSimulationConfig", "FireSimulationEngine", "PALETTES"]
