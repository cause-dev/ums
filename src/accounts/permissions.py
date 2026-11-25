from accounts.constants import DEFAULT_ROLE_NAMES
from accounts.models import User


def has_role(user: User, role: str) -> bool:
    if not user.is_authenticated:
        return False

    if role not in DEFAULT_ROLE_NAMES:
        return False

    return user.groups.filter(name=role).exists()
