import os

from analyzer.api.schema import ScreenResolution
from analyzer.utils.emulator_generate import generate_k_dict

EMULATOR_SCREEN = ScreenResolution(width=1440.0, height=2392.0)
K_DICT = generate_k_dict(
    path=os.path.join(os.path.dirname(__file__), 'emulator_data.txt')
    # path='emulator_data.txt'
)
