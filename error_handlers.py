def handle_nasa_api_error(message: str) -> None:
    print(f"Ошибка API NASA: {message}")
    if "403" in message:
        print("Пожалуйста, проверьте ваш API ключ")

def handle_spacex_api_error(message: str) -> None:
    print(f"Ошибка API SpaceX: {message}")

def handle_download_error(message: str) -> None:
    print(f"Ошибка загрузки: {message}")

def handle_config_error(message: str) -> None:
    print(f"Ошибка конфигурации: {message}")

def handle_directory_error(message: str) -> None:
    print(f"Ошибка директории: {message}")

def handle_data_format_error(message: str) -> None:
    print(f"Ошибка формата данных: {message}")

def handle_connection_error(message: str) -> None:
    print(f"Ошибка соединения: {message}")