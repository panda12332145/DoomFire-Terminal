#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__)) # adiciona pasta atual no path

from src.execution.bootstrap_main_animation_loop_controller import bootstrap_main_animation_loop_controller # importa main novo

if __name__ == "__main__":
    bootstrap_main_animation_loop_controller() # roda
