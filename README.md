# NASA NEO ETL Pipeline

Учебный проект для **сбора, хранения и анализа данных об околоземных астероидах** с использованием NASA NeoWs API, Python и SQLite. Лабораторная работа № 1.

Данные запрашиваются через NASA API, сохраняются в JSON, затем загружаются в реляционную базу. Для анализа предусмотрено шесть SQL-запросов.

---

## Особенности реализации

- **Поэтапная обработка:** `extract.py` → `load_to_db.py` → `queries.py`.
- **Сбор по интервалам до 7 дней:** в коде задан период с 01.01.2024 по 30.09.2026.
- **Две связанные таблицы:** сведения об астероидах отделены от событий сближения.
- **Защита от повторных вставок:** уникальные ключи и `ON CONFLICT DO NOTHING`.

## Схема базы данных

```text
asteroids (1)                          close_approaches (M)
┌──────────────────────────┐          ┌──────────────────────────────────┐
│ id [PK]                  │          │ id [PK]                          │
│ name                     │          │ neo_id [FK → asteroids.id]       │
│ absolute_magnitude_h     │          │ close_approach_date              │
│ diameter_km_min / max    │─── 1:M ──│ epoch_date_close_approach        │
│ is_potentially_hazardous │          │ velocity_kmh                     │
│ is_sentry_object         │          │ miss_distance_km                 │
│ nasa_jpl_url             │          │ orbiting_body                    │
└──────────────────────────┘          └──────────────────────────────────┘
```

События сближения дополнительно уникальны по паре `(neo_id, epoch_date_close_approach)`.

## Структура проекта

```text
PDA-Lab1/
├── extract.py        # получение JSON от NASA NeoWs
├── db.py             # описание таблиц SQLite
├── load_to_db.py     # преобразование и загрузка данных
├── queries.py        # шесть аналитических SQL-запросов
├── requirements.txt  # зависимости проекта
├── .gitignore
└── README.md
```

## Установка и запуск

```bash
git clone https://github.com/ZhukovaE/PDA-Lab1.git
cd PDA-Lab1
python -m venv .venv
pip install -r requirements.txt
```

Перед запуском активируйте окружение (`.venv\Scripts\Activate.ps1` для Windows или `source .venv/bin/activate` для Linux/macOS) и создайте в корне проекта файл `.env` со строкой:

```dotenv
NASA_API_KEY=ваш_ключ_NASA
```

Выполните команды последовательно:

```bash
python extract.py       # получить данные в data/
python load_to_db.py    # создать и заполнить nasa_neo.db
python queries.py       # вывести результаты SQL-запросов
```

Аналитика включает шесть запросов: статистика сближений по годам, топ-10 самых быстрых сближений, сравнение потенциально опасных и неопасных астероидов, распределение сближений по дистанционным корзинам, топ-5 крупных астероидов с повторными сближениями, а также топ-3 самых быстрых сближений в каждом году (оконная функция `RANK() OVER`).

Источник данных: [NASA Open APIs](https://api.nasa.gov/). Исходный код предназначен для учебной работы; ключ API и локальные выгрузки не следует публиковать.