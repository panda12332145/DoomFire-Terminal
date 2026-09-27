import sys

try:
    from .execution.bootstrap_main_animation_loop_controller import (
        bootstrap_main_animation_loop_controller as new_main,
        execute_main_fire_animation_loop_controller,
        parse_arguments,
        build_config_from_args,
        restore_terminal,
        setup_terminal,
    )
    from .config.fire_simulation_configuration import FireSimulationConfig, FRAME_DELAY, WIDTH, HEIGHT
    from .core.fire_simulation_engine import FireSimulationEngine

    def main():
        if len(sys.argv) > 1: # se tem argumento usa novo main com cli
            new_main()
        else: # sem argumento roda padrao antigo, 60x24
            config = FireSimulationConfig(width=WIDTH, height=HEIGHT, frame_delay=FRAME_DELAY)
            execute_main_fire_animation_loop_controller(config=config, interactive=False, show_stats=False)

except ImportError as e:
    import time
    import os

    try:
        from .fire_engine import create_fire_grid, propagate, render, WIDTH, HEIGHT
    except ImportError:
        from fire_engine import create_fire_grid, propagate, render, WIDTH, HEIGHT

    FRAME_DELAY = 0.05 # delay padrao

    def main():
        print('\033[2J\033[?25l', end='') # limpa tela e esconde cursor
        try:
            grid = create_fire_grid(WIDTH, HEIGHT) # cria grid
            while True: # loop infinito
                propagate(grid, WIDTH, HEIGHT) # propaga
                render(grid) # renderiza
                time.sleep(FRAME_DELAY) # dorme
        except KeyboardInterrupt:
            pass # ctrl+c sai
        finally:
            print('\033[?25h', end='') # mostra cursor
            sys.stdout.flush()


if __name__ == "__main__":
    main() # roda main
