# Сборка
FROM node:21.7.1-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# Финальный этап: только копирование
FROM alpine:3.19
# Копируем билд внутрь образа
COPY --from=build /app/build /frontend_artifacts
# Команда при запуске: копируем из образа в примонтированный Volume
CMD ["cp", "-rp", "/frontend_artifacts/.", "/var/www/frontend/"]
