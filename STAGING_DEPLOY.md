# Staging deploy checklist

## 1. Environment

Create `.env` on the server from `.env.production.example`.

For staging without HTTPS you can use:

```env
DEBUG=False
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

For production with HTTPS use:

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Required values:

```env
SECRET_KEY=<long-random-secret>
ALLOWED_HOSTS=<domain-or-ip>
CSRF_TRUSTED_ORIGINS=https://<domain>
CORS_ALLOWED_ORIGINS=https://<frontend-domain>
POSTGRES_DB=arabica_db
POSTGRES_USER=arabica_user
POSTGRES_PASSWORD=<strong-password>
REDIS_URL=redis://redis:6379/1
CHANNEL_REDIS_URL=redis://redis:6379/2
TWILIO_ACCOUNT_SID=<twilio-sid>
TWILIO_AUTH_TOKEN=<twilio-token>
TWILIO_VERIFY_SERVICE_SID=<twilio-verify-service>
```

## 2. Build and run

```bash
docker compose --env-file .env build
docker compose --env-file .env up -d
docker compose --env-file .env ps
```

## 3. Server checks

```bash
docker compose --env-file .env exec django python manage.py check
docker compose --env-file .env exec django python manage.py check --deploy
docker compose --env-file .env logs -f django
```

## 4. CRM smoke test

1. Create or verify a staff user in Django Admin.
2. Create `CafeMembership` for the user with role `staff`.
3. Create or verify couriers for the same cafe with role `courier`.
4. Open `/admin/login/` and log in as staff.
5. Open `/crm/orders/`.
6. Create an active order for the same cafe.
7. Confirm the order appears without page reload.
8. Change status from CRM and confirm the board updates.

## 5. WebSocket check

In browser DevTools, Network tab:

- request URL: `/ws/crm/orders/`
- expected status: `101 Switching Protocols`
- messages should include `orders.snapshot`

If WebSocket does not connect:

1. Check that the app runs through Daphne/ASGI.
2. Check Nginx upgrade headers.
3. Check Redis availability.
4. Check that the logged-in user has staff membership.
