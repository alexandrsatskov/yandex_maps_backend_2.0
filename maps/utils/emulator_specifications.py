import os
from typing import Tuple

from maps.api.schema import ScreenResolution
from maps.utils.emulator_generate import generate_k_dict

# if not os.path.isabs(alembic_location):
#     PROJECT_PATH = Path(__file__).parent.parent.resolve()
#     config.set_main_option('script_location',
#                            os.path.join(base_path, alembic_location))

EMULATOR_SCREEN = ScreenResolution(width=1440.0, height=2392.0)
K_DICT = generate_k_dict(
    path=os.path.join(os.path.dirname(__file__), 'emulator_data.txt')
    # path='emulator_data.txt'
)


def get_screen_coordinate_bounds(
    device: ScreenResolution,
    latitude: float,
    longitude: float,
    zoom: float,
) -> Tuple:
    """
    Получить примерные географические
    координаты возле углов viewport'a

    :param device:
        Разрешение экрана в пикселях

    :param latitude:
        Центральная координата экрана, широта
    :param longitude:
        Центральная координата экрана, долгота

    :param zoom:
        Текущее значение приближения карты в приложении

    :return:
        Кортеж с граничными географическими значениями в формате:
        (tl_lat, tl_lon, br_lat, br_lon)
        **tl, br == top-left, bottom-right
    """
    zoom_float = zoom
    zoom_int = int(zoom_float)
    zoom_mod = 1 - (zoom_float % 1)

    # sr == screen resolution
    k_height_sr = device.height / EMULATOR_SCREEN.height
    k_width_sr = device.width / EMULATOR_SCREEN.width

    lat_quarter = (K_DICT[zoom_int]['lat_delta'] * k_height_sr) / 4
    lon_quarter = (K_DICT[zoom_int]['lon_delta'] * k_width_sr) / 4

    lat_additional = lat_quarter + (lat_quarter * zoom_mod)
    lon_additional = lon_quarter + (lon_quarter * zoom_mod)

    # Screen coordinate bounds
    # tl == top-left, br == bottom-right
    tl_lat = latitude + lat_additional
    tl_lon = longitude - lon_additional

    br_lat = latitude - lat_additional
    br_lon = longitude + lon_additional
    return tl_lat, tl_lon, br_lat, br_lon
