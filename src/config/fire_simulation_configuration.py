from dataclasses import dataclass, field
from typing import Dict, List
import shutil

WIDTH: int = 60 # largura padrao, se botar muito grande, trava tudo kkk
HEIGHT: int = 24 # altura, nao exagera senao fica feio
INTENSITY_LEVELS: int = 30 # quantos nivel de fogo, 30 ja fica bonito
FRAME_DELAY: float = 0.05 # delay do frame, 0.05 da uns 20 fps, ta bom
MIN_WIDTH: int = 10 # minimo, se for menor que isso nem aparece
MAX_WIDTH: int = 200 # maximo, mais que isso meu pc chora
MIN_HEIGHT: int = 5 # minimo de altura, senao vira linha
MAX_HEIGHT: int = 100 # maximo, altura gigante, nao precisa
MIN_FPS: int = 1 # fps minimo, 1 ja e bem lento
MAX_FPS: int = 60 # fps maximo, mais que 60 e frescura

RESET = '\033[0m' # reseta cor, volta ao normal
CLEAR_SCREEN = '\033[2J' # limpa tela, some tudo
CURSOR_HOME = '\033[H' # cursor volta pro comeco, la em cima
HIDE_CURSOR = '\033[?25l' # esconde cursor, pra nao ficar piscando
SHOW_CURSOR = '\033[?25h' # mostra cursor de novo, quando sai

CLASSIC_DOOM_PALETTE: List[str] = [ # paleta classica, a do doom mesmo, preto ate branco
    '\033[30m',
    '\033[90m',
    '\033[90m',
    '\033[31m',
    '\033[31m',
    '\033[91m',
    '\033[91m',
    '\033[31m',
    '\033[33m',
    '\033[33m',
    '\033[93m',
    '\033[91m',
    '\033[93m',
    '\033[93m',
    '\033[91m',
    '\033[93m',
    '\033[93m',
    '\033[91m',
    '\033[93m',
    '\033[93m',
    '\033[91m',
    '\033[93m',
    '\033[97m',
    '\033[97m',
    '\033[97m',
    '\033[93m',
    '\033[97m',
    '\033[97m',
    '\033[97m',
    '\033[97m',
]

BLUE_FIRE_PALETTE: List[str] = [ # fogo azul, parece plasma, bem doido
    '\033[30m', '\033[90m', '\033[34m', '\033[34m', '\033[94m',
    '\033[34m', '\033[94m', '\033[34m', '\033[94m', '\033[36m',
    '\033[94m', '\033[36m', '\033[96m', '\033[94m', '\033[36m',
    '\033[96m', '\033[94m', '\033[96m', '\033[36m', '\033[96m',
    '\033[97m', '\033[96m', '\033[97m', '\033[96m', '\033[97m',
    '\033[97m', '\033[97m', '\033[97m', '\033[97m', '\033[97m',
]

GREEN_FIRE_PALETTE: List[str] = [ # fogo verde, tipo matrix, toxico, kkk
    '\033[30m', '\033[90m', '\033[32m', '\033[32m', '\033[92m',
    '\033[32m', '\033[92m', '\033[32m', '\033[92m', '\033[92m',
    '\033[92m', '\033[32m', '\033[92m', '\033[93m', '\033[92m',
    '\033[92m', '\033[93m', '\033[92m', '\033[93m', '\033[92m',
    '\033[93m', '\033[97m', '\033[93m', '\033[97m', '\033[97m',
    '\033[93m', '\033[97m', '\033[97m', '\033[97m', '\033[97m',
]

GRAYSCALE_PALETTE: List[str] = [ # preto e branco, retro, parece tv antiga
    '\033[30m', '\033[90m', '\033[90m', '\033[90m', '\033[90m',
    '\033[37m', '\033[37m', '\033[37m', '\033[37m', '\033[37m',
    '\033[37m', '\033[37m', '\033[37m', '\033[37m', '\033[37m',
    '\033[37m', '\033[97m', '\033[97m', '\033[97m', '\033[97m',
    '\033[97m', '\033[97m', '\033[97m', '\033[97m', '\033[97m',
    '\033[97m', '\033[97m', '\033[97m', '\033[97m', '\033[97m',
]

ORIGINAL_PALETTE: List[str] = [ # paleta original que eu usei no comeco, deixei pra compatibilidade
    '\033[30m', '\033[90m', '\033[33m', '\033[93m',
    '\033[93m', '\033[93m', '\033[91m', '\033[93m',
    '\033[91m', '\033[91m', '\033[93m', '\033[91m',
    '\033[97m', '\033[97m', '\033[97m', '\033[93m',
    '\033[91m', '\033[93m', '\033[93m', '\033[91m',
    '\033[93m', '\033[93m', '\033[91m', '\033[93m',
    '\033[91m', '\033[97m', '\033[97m', '\033[97m',
    '\033[97m', '\033[97m',
]

PALETTES: Dict[str, List[str]] = { # dicionario com todas paleta, facil de escolher
    'classic': CLASSIC_DOOM_PALETTE,
    'original': ORIGINAL_PALETTE,
    'doom': CLASSIC_DOOM_PALETTE,
    'blue': BLUE_FIRE_PALETTE,
    'plasma': BLUE_FIRE_PALETTE,
    'green': GREEN_FIRE_PALETTE,
    'matrix': GREEN_FIRE_PALETTE,
    'toxic': GREEN_FIRE_PALETTE,
    'grayscale': GRAYSCALE_PALETTE,
    'gray': GRAYSCALE_PALETTE,
    'mono': GRAYSCALE_PALETTE,
}

DEFAULT_PALETTE_NAME = 'classic' # paleta padrao, a classica mesmo

@dataclass
class FireSimulationConfig:
    width: int = WIDTH # largura que vai usar
    height: int = HEIGHT # altura que vai usar
    intensity_levels: int = INTENSITY_LEVELS # niveis de intensidade
    frame_delay: float = FRAME_DELAY # delay entre frames
    palette_name: str = DEFAULT_PALETTE_NAME # nome da paleta
    wind_enabled: bool = True # vento ligado ou nao
    wind_intensity: int = 1 # forca do vento, 0 a 3
    decay_min: int = 0 # decaimento minimo
    decay_max: int = 2 # decaimento maximo, quanto maior mais curto o fogo
    auto_resize: bool = True # se ajusta sozinho ao terminal

    palette: List[str] = field(init=False) # paleta resolvida, nao precisa passar

    def __post_init__(self): # roda depois do init, valida tudo
        self.validate_dimensions() # valida tamanho
        self.validate_frame_delay() # valida fps
        self.validate_wind() # valida vento
        self.validate_decay() # valida decaimento
        self.palette = self.resolve_palette() # pega paleta certa
        self.validate_palette() # valida paleta

    def validate_dimensions(self): # ve se largura e altura ta ok
        if not (MIN_WIDTH <= self.width <= MAX_WIDTH): # largura fora do limite
            raise ValueError(f"width deve estar entre {MIN_WIDTH} e {MAX_WIDTH}, recebido {self.width}")
        if not (MIN_HEIGHT <= self.height <= MAX_HEIGHT): # altura fora do limite
            raise ValueError(f"height deve estar entre {MIN_HEIGHT} e {MAX_HEIGHT}, recebido {self.height}")
        if self.width <= 0 or self.height <= 0: # negativo nao pode
            raise ValueError("width e height devem ser positivos")

    def validate_frame_delay(self): # ve se fps ta ok
        fps = 1.0 / self.frame_delay if self.frame_delay > 0 else 0 # calcula fps
        if not (MIN_FPS <= fps <= MAX_FPS): # fps fora
            raise ValueError(f"FPS derivado de frame_delay {fps:.1f} fora do intervalo {MIN_FPS}-{MAX_FPS}")
        if self.frame_delay <= 0: # delay negativo nao rola
            raise ValueError("frame_delay deve ser positivo")

    def validate_wind(self): # valida vento
        if not isinstance(self.wind_enabled, bool): # tem que ser bool
            raise ValueError("wind_enabled deve ser bool")
        if not (0 <= self.wind_intensity <= 3): # vento de 0 a 3
            raise ValueError("wind_intensity deve estar entre 0 e 3")

    def validate_decay(self): # valida decaimento
        if not (0 <= self.decay_min <= self.decay_max <= 5): # tem que ser 0 <= min <= max <=5
            raise ValueError("decay deve satisfazer 0 <= decay_min <= decay_max <= 5")

    def resolve_palette(self) -> List[str]: # pega paleta pelo nome
        name = self.palette_name.lower() # deixa minusculo
        if name not in PALETTES: # se nao existe
            available = ", ".join(sorted(set(PALETTES.keys()))) # lista disponivel
            raise ValueError(f"Paleta '{self.palette_name}' desconhecida. Disponiveis: {available}")
        return PALETTES[name] # retorna paleta

    def validate_palette(self): # ve se paleta tem tamanho certo
        if len(self.palette) != self.intensity_levels: # tamanho diferente
            raise ValueError(f"Paleta {self.palette_name} tem {len(self.palette)} cores mas intensity_levels={self.intensity_levels}")

    @property
    def fps(self) -> float: # calcula fps
        return 1.0 / self.frame_delay if self.frame_delay > 0 else 0

    @classmethod
    def from_terminal_size(cls, **kwargs): # cria config baseado no tamanho do terminal
        try:
            term_size = shutil.get_terminal_size() # pega tamanho do terminal
            w = min(term_size.columns, kwargs.get('width', WIDTH)) # largura, nao passa do terminal
            h = min(term_size.lines - 2, kwargs.get('height', HEIGHT)) # altura, deixa 2 linha livre
            w = max(MIN_WIDTH, w) # garante minimo
            h = max(MIN_HEIGHT, h) # garante minimo
            kwargs['width'] = w # seta largura
            kwargs['height'] = h # seta altura
        except Exception: # se der ruim ignora
            pass
        return cls(**kwargs) # retorna config

    def to_dict(self) -> dict: # transforma em dict, pra debug
        return {
            'width': self.width,
            'height': self.height,
            'intensity_levels': self.intensity_levels,
            'frame_delay': self.frame_delay,
            'fps': self.fps,
            'palette_name': self.palette_name,
            'wind_enabled': self.wind_enabled,
            'wind_intensity': self.wind_intensity,
            'decay_min': self.decay_min,
            'decay_max': self.decay_max,
            'auto_resize': self.auto_resize,
        }


ANSI_PALETTE = CLASSIC_DOOM_PALETTE # compatibilidade com codigo antigo
