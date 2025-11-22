# Polygon Token API

Python API для работы с ERC20 токеном в сети Polygon. Предоставляет проверку балансов, топ держателей и информацию о токене. Включает сервер Flask для обработки HTTP-запросов и скрипт для проверки функциональности.

## Возможности

- **Уровень A**: Получение баланса одного адреса.
- **Уровень B**: Получение балансов нескольких адресов одновременно.
- **Уровень C**: Получение топ-адресов по балансу токена.
- **Уровень D**: Получение топ-адресов с датой последней транзакции.
- **Уровень E**: Получение информации о токене.
- **Уровень F**: Запуск сервера Flask для обработки HTTP-запросов.

## Требования

- Python 3.13+
- Web3.py
- Flask
- Requests
- Colorama
- Python-dotenv

## Установка

1. Клонируйте репозиторий:

```bash
git clone <repo_url>
cd <repo_folder>
```

2. Установите зависимости:

```bash
uv sync
```

3. Создайте файл `.env` (пример `.env.example` предоставлен):

```
SECRET_KEY=very-secret-key-to-add-someday
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO
POLYGON_RPC_URLS=https://rpc.ankr.com/polygon,https://1rpc.io/matic
TOKEN_ADDRESS=0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0
WEB3_REQUEST_TIMEOUT=10
WEB3_POOL_MAXSIZE=10
RATE_LIMIT_DEFAULT=60/minute
```

## Запуск сервера API

```bash
python main.py
```

Сервер будет доступен по адресу `http://127.0.0.1:8080`.

## Примеры запросов

- `GET /health` – статус сервера
- `GET /api/get_balance?address=<address>` – баланс одного адреса
- `POST /api/get_balance_batch` – балансы нескольких адресов
- `GET /api/get_top?n=<N>` – топ N держателей токена
- `GET /api/get_top_with_transactions?n=<N>` – топ N держателей с датой последней транзакции
- `GET /api/get_token_info` – информация о токене

## Проверка функциональности

Для проверки работы API используйте скрипт:

```bash
python scripts/check_functionality.py
```

## Примечания

- Взаимодействие с сетью Polygon через RPC.
- Используется ABI стандарта ERC20 для операций с токеном.
- Оптимизировано для быстрого выполнения и минимальной зависимости от внешних сервисов.
