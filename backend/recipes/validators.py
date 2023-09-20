
import re

from django.core.exceptions import ValidationError

from foodgram.settings import RESERVED_NAMES, USERNAME_PATTERN

UNAVAILABLE_NAME = 'Недоступное имя пользователя: {0}'
UNACCEPTABLE_SYMBOLS = 'Запрещенные символы: {0}'


def validate_username(value):
    if value in RESERVED_NAMES:
        raise ValidationError(UNAVAILABLE_NAME.format(value))
    if (symbols := ''.join(set(re.sub(
            USERNAME_PATTERN, '', value)))):
        raise ValidationError(UNACCEPTABLE_SYMBOLS.format(symbols))
    return value
