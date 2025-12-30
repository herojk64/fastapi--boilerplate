from .middlewares import middlewares_config
from .storage import mount_storage

SETUPS = [
    middlewares_config,
    mount_storage,
]
