#!/bin/bash
set -e

DOMAIN="arabicacoffee.duckdns.org"
EMAIL="alievbakdoolot301@gmail.com"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

echo "=== Шаг 1: Создаём временный сертификат чтобы nginx запустился ==="
docker compose run --rm --entrypoint "sh -c '
  mkdir -p $CERT_PATH &&
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout $CERT_PATH/privkey.pem \
    -out $CERT_PATH/fullchain.pem \
    -subj \"/CN=localhost\"
'" certbot

echo "=== Шаг 2: Запускаем nginx ==="
docker compose up -d nginx

echo "=== Шаг 3: Удаляем временный сертификат ==="
docker compose run --rm --entrypoint "sh -c '
  rm -rf /etc/letsencrypt/live &&
  rm -rf /etc/letsencrypt/archive &&
  rm -rf /etc/letsencrypt/renewal
'" certbot

echo "=== Шаг 4: Получаем настоящий сертификат Let's Encrypt ==="
docker compose run --rm --entrypoint "certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email $EMAIL \
  -d $DOMAIN \
  --agree-tos \
  --no-eff-email" certbot

echo "=== Шаг 5: Перезагружаем nginx с новым сертификатом ==="
docker compose exec nginx nginx -s reload

echo ""
echo "=== Готово! SSL сертификат получен для $DOMAIN ==="
echo "Теперь запусти все сервисы: docker compose up -d"
