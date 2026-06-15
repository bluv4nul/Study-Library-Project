# ElectroLibrary Frontend

Клиентская часть мини-приложения «Электронная библиотека» на Vue 3 + Vite.

## Запуск отдельно

```bash
cd frontend
npm install
npm run dev
```

По умолчанию фронтенд обращается к API:

```env
VITE_API_URL=http://localhost:3000/api
```

## Запуск через Docker Compose

Добавьте сервис в корневой `docker-compose.yaml`:

```yaml
  frontend:
    build:
      context: ./frontend
    ports:
      - 5173:80
    depends_on:
      - api
```

После этого запустите:

```bash
docker compose up -d --build
```

Фронтенд будет доступен по адресу: `http://localhost:5173`.
