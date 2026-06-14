# Study Library Project

## Быстрый старт для разработчиков CRUD и REST API

### Как запустить проект

1. Откройте терминал в корне проекта.
2. Выполните:
   ```bash
   docker compose up -d
   ```
3. MongoDB будет доступна на `mongodb://localhost:27017`.
4. REST API будет доступен на `http://localhost:3000`.
5. Swagger-документация FastAPI будет доступна на `http://localhost:3000/docs`.

> Сервис использует коллекции `authors`, `genres`, `publishers`, `books` в базе `electrolibrary`.

### Серверная часть

Серверная часть реализована на Python с использованием FastAPI и PyMongo.

Основные возможности:
- CRUD для книг, авторов, жанров и издательств,
- получение книги вместе с авторами, жанрами и издательством,
- фильтрация книг по названию, году, автору, жанру и издательству,
- сортировка и пагинация списков,
- сохранение данных в MongoDB,
- запуск через Docker Compose.

### Структура данных

- База: `electrolibrary`
- Коллекции:
  - `authors`
  - `genres`
  - `publishers`
  - `books`

#### `authors`

Поля:
- `author_name` — имя автора
- `author_nickname` — псевдоним
- `email`
- `social_media_link`

#### `genres`

Поля:
- `genre_name`

#### `publishers`

Поля:
- `publisher_name`
- `publisher_city`
- `email`
- `publisher_website`

#### `books`

Поля:
- `title`
- `year`
- `isbn`
- `publisher_id` — ссылка на `_id` документа в `publishers`
- `author_ids` — массив `_id` документов из `authors`
- `genre_ids` — массив `_id` документов из `genres`

### Основные связи

- `books.publisher_id` → `publishers._id`
- `books.author_ids` → `authors._id`
- `books.genre_ids` → `genres._id`

### Индексы, которые уже создаются при инициализации

- `books.title`
- `books.isbn` уникальный
- `books.year`
- `books.publisher_id`
- `books.author_ids`
- `books.genre_ids`
- `books.year, title`
- `books.publisher_id, year`
- `authors.author_name`
- `genres.genre_name`
- `publishers.publisher_name`

### Рекомендации для REST API

- `/api/books`:
  - GET — список книг
  - GET `/:id` — книга с авторами/жанрами/издателем
  - POST — добавление книги с `author_ids`, `genre_ids`, `publisher_id`
  - PUT/PATCH — обновление книги
  - DELETE — удаление книги

- `/api/authors`, `/api/genres`, `/api/publishers`:
  - GET, POST, PUT/PATCH, DELETE

### Фильтрация, сортировка и пагинация книг

Примеры запросов:

```bash
GET /api/books?search=1984
GET /api/books?year=1949
GET /api/books?yearFrom=1930&yearTo=1950
GET /api/books?author_id=OBJECT_ID
GET /api/books?genre_id=OBJECT_ID
GET /api/books?publisher_id=OBJECT_ID
GET /api/books?sort=year&order=desc&page=1&limit=10
```

Для справочников авторов, жанров и издательств доступен поиск через `q`:

```bash
GET /api/authors?q=orwell
GET /api/genres?q=fantasy
GET /api/publishers?q=penguin
```

### Примеры JSON для создания

#### Новый автор

```json
{
  "author_name": "Имя Фамилия",
  "author_nickname": null,
  "email": "author@mail.com",
  "social_media_link": "https://example.com/profile"
}
```

#### Новая книга

```json
{
  "title": "Название книги",
  "year": 2025,
  "isbn": "978-1-234-56789-0",
  "author_ids": ["OBJECT_ID_1", "OBJECT_ID_2"],
  "genre_ids": ["OBJECT_ID_3"],
  "publisher_id": "OBJECT_ID_4"
}
```

### Полезные заметки

- `ObjectId` генерируется MongoDB автоматически при вставке.
- В `database/init/init.js` сиды создаются автоматически внутри init-скрипта.
- Если нужно проверить данные вручную, подключайтесь к `electrolibrary` через `mongosh`.

### Полезные команды

```bash
docker compose ps

docker compose logs --tail=50

docker compose down -v
```

---

## Контакты

Если потребуется уточнить схему или связи, задавайте вопросы в команде — я помогу описать дополнительные API-пути.
