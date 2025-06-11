import os
import logging

logger = logging.getLogger(__name__)

def get_env_variable(var_name: str) -> str | None:
    value = os.getenv(var_name)
    if not value:
        logger.error(f"{var_name} не найден в файле .env")
        return None
    return value