# GraphBot

AI-сервис для автоматического подбора и построения графиков по загруженным Excel-файлам. Анализирует структуру данных с помощью LLM (DeepSeek) и рекомендует оптимальные типы визуализаций.

## Возможности

- Загрузка Excel-файлов (.xlsx, .xls) через веб-интерфейс
- Автоматический анализ структуры и статистик данных
- Рекомендации 1–3 типов графиков с объяснением выбора (через DeepSeek API)
- Генерация графиков (bar, line, pie, histogram, scatter, area и др.) через Matplotlib
- Скачивание готовых визуализаций в PNG

## Стек технологий

| Компонент | Технологии |
|-----------|------------|
| Backend | FastAPI, Uvicorn |
| Данные | Pandas, openpyxl, NumPy |
| Графики | Matplotlib |
| LLM | DeepSeek API (api.intelligence.io.solutions) |
| Frontend | HTML, CSS, JavaScript (vanilla) |

## Структура проекта

```
├── app.py                 # FastAPI-приложение (эндпоинты /analyze, /build_chart)
├── main.py                # Точка входа — запуск Uvicorn-сервера
├── requirements.txt       # Зависимости
├── lib/
│   ├── data.py            # Анализ DataFrame: типы колонок, статистики
│   ├── graphs.py          # Генерация графиков через Matplotlib
│   ├── LLMRequests.py     # Запросы к DeepSeek API, валидация ответов
│   ├── prompt.py          # Системные и пользовательские промпты для LLM
│   ├── getModelsList.py   # Утилита для получения списка моделей
│   └── GptApiKey.txt      # API-ключ DeepSeek (не коммитить!)
├── templates/
│   ├── index.html         # Главная страница
│   └── how.html           # Страница «Как это работает»
├── static/
│   ├── style.css          # Стили
│   └── icons/             # Иконки
└── uploads/               # Временное хранилище загруженных файлов
```

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <url>
cd GraphBot
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Добавить API-ключ

Создайте (или отредактируйте) файл `lib/GptApiKey.txt` и вставьте в первую строку ваш API-ключ от [DeepSeek / IO Solutions](https://api.intelligence.io.solutions/).

### 4. Запустить сервер

```bash
python main.py
```

Сервер запустится на `http://localhost:8000`.

## API

| Метод | Эндпоинт | Описание |
|-------|-----------|----------|
| GET | `/` | Главная страница |
| POST | `/analyze` | Загрузка Excel-файла → анализ → рекомендации графиков |
| POST | `/build_chart` | Генерация PNG-графика по выбранной рекомендации |

### POST /analyze

**Запрос:** `multipart/form-data` с полем `file` (Excel-файл).

**Ответ:**
```json
{
  "session_id": "uuid",
  "recommendations": [
    {
      "type": "bar_chart",
      "why": "Объяснение выбора",
      "columns_used": ["col1", "col2"],
      "columns_used_with_text": ["col1"]
    }
  ]
}
```

### POST /build_chart

**Запрос:** `session_id` и `chart_index`.

**Ответ:** PNG-изображение графика.

## Как это работает

1. **Загрузка** — пользователь загружает Excel-файл
2. **Анализ** — бэкенд профилирует данные (типы колонок, статистики, пропуски)
3. **LLM** — профиль данных отправляется в DeepSeek, модель возвращает рекомендации в JSON
4. **Визуализация** — по выбору пользователя строится график через Matplotlib
5. **Результат** — график отображается в интерфейсе и доступен для скачивания
