import os

from maps.api.schema import ScreenResolution
from maps.utils.emulator_generate import generate_k_dict

# if not os.path.isabs(alembic_location):
#     PROJECT_PATH = Path(__file__).parent.parent.resolve()
#     config.set_main_option('script_location',
#                            os.path.join(base_path, alembic_location))

EMULATOR_SCREEN = ScreenResolution(width=1440.0, height=2392.0)
K_DICT = generate_k_dict(
    path='emulator_data.txt'
)
