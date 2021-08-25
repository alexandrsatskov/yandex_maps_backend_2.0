import random
from typing import Any, Dict, Optional

import faker

fake = faker.Faker('ru_RU')


def generate_visited_place(
    user_email: Optional[str] = None,
    place_uid: Optional[str] = None,
    place_id: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Создает и возвращает пользовательское
    посещенное место, автоматически генерируя
    данные для не указанных полей.
    """
    if user_email is None:
        user_email = fake.email()

    if place_uid is None:
        place_uid = f'ymapsbm1://org?oid={random.randint(0, (10 ** 11) - 1)}'

    if place_id is None:
        place_id = random.randint(0, (10 ** 10) - 1)

    if latitude is None:
        latitude = float(fake.latitude())

    if longitude is None:
        longitude = float(fake.longitude())

    return locals()


def generate_user_feedback(
    user_email: Optional[str] = None,
    place_uid: Optional[str] = None,
    feedback_rate: Optional[int] = None,
    feedback_text: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Создает и возвращает пользовательский
    отзыв, автоматически генерируя данные
    для не указанных полей.
    """
    if user_email is None:
        user_email = fake.email()

    if place_uid is None:
        place_uid = f'ymapsbm1://org?oid={random.randint(0, (10 ** 11) - 1)}'

    if feedback_rate is None:
        feedback_rate = random.randint(0, 5)

    if feedback_text is None:
        feedback_text = fake.file_name()

    return locals()
