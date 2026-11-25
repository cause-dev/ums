DEFAULT_ROLES = (
    ("Admin", "Application administration"),
    ("Manager", "User management"),
    ("Editor", "Content management"),
    ("Viewer", "Read-only content access"),
)

DEFAULT_ROLE_NAMES = tuple(name for name, _ in DEFAULT_ROLES)
