import time
import sys
import os
import argparse
import signal
import atexit
import shutil
from typing import Optional

try:
    import colorama # tenta importar colorama, pro windows
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False # se nao tem, beleza

from ..config.fire_simulation_configuration import (
    FireSimulationConfig,
    PALETTES,
    DEFAULT_PALETTE_NAME,
    CLEAR_SCREEN,
    HIDE_CURSOR,
    SHOW_CURSOR,
    CURSOR_HOME,
    RESET,
    WIDTH,
    HEIGHT,
    FRAME_DELAY,
    MIN_WIDTH,
    MAX_WIDTH,
    MIN_HEIGHT,
    MAX_HEIGHT,
    MIN_FPS,
    MAX_FPS,
)
from ..core.fire_simulation_engine import FireSimulationEngine
from ..payloads.render_fire_display_engine import render_with_status


_terminal_restored = False # flag pra nao restaurar duas vezes

def restore_terminal():
    global _terminal_restored
    if _terminal_restored: # ja restaurou, sai
        return
    try:
        sys.stdout.write(SHOW_CURSOR + RESET) # mostra cursor e reseta cor
        sys.stdout.flush()
    except Exception:
        pass
    _terminal_restored = True # marca como restaurado


def setup_terminal():
    global _terminal_restored
    _terminal_restored = False # reseta flag

    atexit.register(restore_terminal) # registra pra restaurar quando sair

    def signal_handler(signum, frame): # handler pra sinal, tipo ctrl+c
        restore_terminal() # restaura terminal
        try:
            sys.stdout.write('\n') # pula linha
            sys.stdout.flush()
        except Exception:
            pass
        sys.exit(0) # sai

    try:
        signal.signal(signal.SIGINT, signal_handler) # ctrl+c
        signal.signal(signal.SIGTERM, signal_handler) # kill
    except Exception:
        pass # windows as vezes nao tem, ignora

    if COLORAMA_AVAILABLE: # se tem colorama
        try:
            colorama.init() # inicia colorama
        except Exception:
            pass

    try:
        sys.stdout.write(CLEAR_SCREEN + HIDE_CURSOR) # limpa tela e esconde cursor
        sys.stdout.flush()
    except Exception:
        pass


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='doomfire-terminal',
        description='DoomFire no terminal, fogo do doom, bem louco',
        epilog='Exemplo: python doomfire.py --width 80 --height 30 --palette blue --interactive',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-W', '--width', type=int, default=WIDTH, help=f'largura {MIN_WIDTH}-{MAX_WIDTH}') # largura
    parser.add_argument('-H', '--height', type=int, default=HEIGHT, help=f'altura {MIN_HEIGHT}-{MAX_HEIGHT}') # altura
    parser.add_argument('--fps', type=int, default=int(1/FRAME_DELAY), help=f'fps {MIN_FPS}-{MAX_FPS}') # fps
    parser.add_argument('-p', '--palette', type=str, default=DEFAULT_PALETTE_NAME, choices=sorted(set(PALETTES.keys())), help='paleta de cor') # paleta
    parser.add_argument('--no-wind', action='store_true', help='desliga vento') # sem vento
    parser.add_argument('--wind-intensity', type=int, default=1, choices=[0, 1, 2, 3], help='forca do vento 0 a 3') # forca vento
    parser.add_argument('--decay-min', type=int, default=0, help='decaimento minimo 0-5') # decay min
    parser.add_argument('--decay-max', type=int, default=2, help='decaimento maximo 0-5') # decay max
    parser.add_argument('--auto-resize', action='store_true', default=False, help='ajusta sozinho ao terminal') # auto resize
    parser.add_argument('--interactive', action='store_true', help='modo interativo, aperta tecla') # interativo
    parser.add_argument('--stats', action='store_true', help='mostra status com fps') # stats

    args = parser.parse_args() # parseia

    if not (MIN_WIDTH <= args.width <= MAX_WIDTH): # valida largura
        parser.error(f"width deve estar entre {MIN_WIDTH} e {MAX_WIDTH}")
    if not (MIN_HEIGHT <= args.height <= MAX_HEIGHT): # valida altura
        parser.error(f"height deve estar entre {MIN_HEIGHT} e {MAX_HEIGHT}")
    if not (MIN_FPS <= args.fps <= MAX_FPS): # valida fps
        parser.error(f"fps deve estar entre {MIN_FPS} e {MAX_FPS}")
    if not (0 <= args.decay_min <= args.decay_max <= 5): # valida decay
        parser.error("tem que ser 0 <= decay_min <= decay_max <= 5")

    return args


def build_config_from_args(args: argparse.Namespace) -> FireSimulationConfig:
    frame_delay = 1.0 / args.fps if args.fps > 0 else FRAME_DELAY # calcula delay pelo fps

    if args.auto_resize: # se auto resize ligado
        return FireSimulationConfig.from_terminal_size(
            width=args.width,
            height=args.height,
            frame_delay=frame_delay,
            palette_name=args.palette,
            wind_enabled=not args.no_wind,
            wind_intensity=args.wind_intensity,
            decay_min=args.decay_min,
            decay_max=args.decay_max,
            auto_resize=True,
        )
    else:
        return FireSimulationConfig(
            width=args.width,
            height=args.height,
            frame_delay=frame_delay,
            palette_name=args.palette,
            wind_enabled=not args.no_wind,
            wind_intensity=args.wind_intensity,
            decay_min=args.decay_min,
            decay_max=args.decay_max,
            auto_resize=args.auto_resize,
        )


class NonBlockingInput:
    def __init__(self):
        self.is_windows = os.name == 'nt' # ve se e windows
        self.old_settings = None

        if not self.is_windows: # se nao for windows
            try:
                import termios
                import tty
                self.termios = termios
                self.tty = tty
            except ImportError:
                self.termios = None

    def __enter__(self):
        if not self.is_windows and self.termios: # unix, seta cbreak
            try:
                import sys
                self.old_settings = self.termios.tcgetattr(sys.stdin)
                self.tty.setcbreak(sys.stdin.fileno())
            except Exception:
                pass
        return self

    def __exit__(self, *args):
        if not self.is_windows and self.termios and self.old_settings: # restaura terminal
            try:
                self.termios.tcsetattr(sys.stdin, self.termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass

    def get_key(self) -> Optional[str]:
        if self.is_windows: # windows usa msvcrt
            try:
                import msvcrt
                if msvcrt.kbhit(): # tem tecla
                    ch = msvcrt.getch() # pega tecla
                    try:
                        return ch.decode('utf-8', errors='ignore')
                    except Exception:
                        return None
            except ImportError:
                pass
            return None
        else: # linux, usa select
            try:
                import select
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []): # tem input
                    ch = sys.stdin.read(1) # le 1 char
                    return ch
            except Exception:
                pass
            return None


def execute_main_fire_animation_loop_controller(
    config: Optional[FireSimulationConfig] = None,
    interactive: bool = False,
    show_stats: bool = False,
) -> None:
    if config is None:
        config = FireSimulationConfig() # config padrao se nao passar

    setup_terminal() # prepara terminal

    engine = FireSimulationEngine(config) # cria engine
    last_resize_check = time.time() # ultimo check de resize
    palette_cycle = sorted(set(PALETTES.keys())) # lista de paletas
    palette_index = palette_cycle.index(config.palette_name) if config.palette_name in palette_cycle else 0 # index atual

    frame_times = [] # tempos de frame
    last_frame_time = time.time() # ultimo tempo

    try:
        if interactive: # modo interativo
            with NonBlockingInput() as nb_input: # input nao bloqueante
                while True: # loop infinito
                    if config.auto_resize and (time.time() - last_resize_check > 0.5): # checa resize a cada 0.5s
                        try:
                            term_size = shutil.get_terminal_size() # tamanho do terminal
                            new_w = min(term_size.columns, MAX_WIDTH) # nova largura
                            new_h = min(term_size.lines - (2 if show_stats else 1), MAX_HEIGHT) # nova altura
                            new_w = max(MIN_WIDTH, new_w) # garante minimo
                            new_h = max(MIN_HEIGHT, new_h)
                            if new_w != engine.config.width or new_h != engine.config.height: # mudou tamanho
                                engine.resize(new_w, new_h) # redimensiona
                                sys.stdout.write(CLEAR_SCREEN) # limpa tela
                        except Exception:
                            pass
                        last_resize_check = time.time() # atualiza tempo

                    key = nb_input.get_key() # pega tecla
                    if key:
                        if key.lower() == 'q' or key == '\x03': # q ou ctrl+c sai
                            break
                        elif key == '+' or key == '=': # + aumenta fogo
                            if engine.config.decay_max > 0:
                                from dataclasses import replace
                                new_max = max(0, engine.config.decay_max - 1)
                                engine.config = replace(engine.config, decay_max=new_max)
                        elif key == '-' or key == '_': # - diminui fogo
                            if engine.config.decay_max < 5:
                                from dataclasses import replace
                                new_max = min(5, engine.config.decay_max + 1)
                                engine.config = replace(engine.config, decay_max=new_max)
                        elif key.lower() == 'w': # w liga desliga vento
                            from dataclasses import replace
                            engine.config = replace(engine.config, wind_enabled=not engine.config.wind_enabled)
                        elif key.lower() == 'p': # p troca paleta
                            palette_index = (palette_index + 1) % len(palette_cycle)
                            try:
                                engine.set_palette(palette_cycle[palette_index])
                            except ValueError:
                                pass
                        elif key.lower() == 'r': # r reseta
                            engine.reset()
                            sys.stdout.write(CLEAR_SCREEN)

                    engine.propagate() # propaga fogo

                    if show_stats or interactive: # se mostra stats
                        now = time.time() # agora
                        dt = now - last_frame_time # delta
                        last_frame_time = now
                        frame_times.append(dt) # adiciona tempo
                        if len(frame_times) > 20:
                            frame_times.pop(0) # mantem so 20
                        avg_dt = sum(frame_times) / len(frame_times) if frame_times else config.frame_delay
                        real_fps = 1.0 / avg_dt if avg_dt > 0 else 0 # fps real
                        stats = engine.get_stats() # stats
                        status = f" FPS:{real_fps:.1f}/{config.fps:.0f} | {stats['width']}x{stats['height']} | Paleta:{engine.config.palette_name} | Vento:{'ON' if engine.config.wind_enabled else 'OFF'} | Decay:{engine.config.decay_max} | [+-]Altura [w]Vento [p]Paleta [r]Reset [q]Sair "
                        render_with_status(engine.grid, engine.config, status_line=status) # render com status
                    else:
                        engine.render() # render normal

                    time.sleep(engine.config.frame_delay) # espera
        else: # modo normal, nao interativo
            while True:
                if config.auto_resize and (time.time() - last_resize_check > 0.5): # checa resize
                    try:
                        term_size = shutil.get_terminal_size()
                        new_w = min(term_size.columns, MAX_WIDTH)
                        new_h = min(term_size.lines - (2 if show_stats else 1), MAX_HEIGHT)
                        new_w = max(MIN_WIDTH, new_w)
                        new_h = max(MIN_HEIGHT, new_h)
                        if new_w != engine.config.width or new_h != engine.config.height:
                            engine.resize(new_w, new_h)
                            sys.stdout.write(CLEAR_SCREEN)
                    except Exception:
                        pass
                    last_resize_check = time.time()

                engine.propagate() # propaga

                if show_stats: # se mostra stats
                    now = time.time()
                    dt = now - last_frame_time
                    last_frame_time = now
                    frame_times.append(dt)
                    if len(frame_times) > 20:
                        frame_times.pop(0)
                    avg_dt = sum(frame_times) / len(frame_times) if frame_times else config.frame_delay
                    real_fps = 1.0 / avg_dt if avg_dt > 0 else 0
                    stats = engine.get_stats()
                    status = f" Frame:{stats['frame']} FPS:{real_fps:.1f}/{config.fps:.0f} Active:{stats['active_percent']:.0f}% "
                    render_with_status(engine.grid, engine.config, status_line=status)
                else:
                    engine.render() # render

                time.sleep(engine.config.frame_delay) # dorme

    except KeyboardInterrupt:
        pass # ctrl+c sai de boa
    finally:
        restore_terminal() # restaura terminal sempre
        try:
            sys.stdout.write('\nDoomFire-Terminal encerrado. fogo apagado kkk\n') # mensagem final
            sys.stdout.flush()
        except Exception:
            pass


def bootstrap_main_animation_loop_controller():
    try:
        args = parse_arguments() # pega args
        config = build_config_from_args(args) # cria config
        execute_main_fire_animation_loop_controller(
            config=config,
            interactive=args.interactive,
            show_stats=args.stats or args.interactive,
        )
    except SystemExit:
        restore_terminal() # restaura se der sys.exit
        raise
    except Exception as e:
        restore_terminal() # restaura se der erro
        print(f"\nErro fatal: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    bootstrap_main_animation_loop_controller() # alias pra main


def control_main_animation_timing_loop():
    bootstrap_main_animation_loop_controller() # outro alias


if __name__ == "__main__":
    bootstrap_main_animation_loop_controller() # se rodar direto
