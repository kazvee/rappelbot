# RappelBot 🐿️

Lightweight reminder service that sends push notifications through Gotify.

Runs on a VPS using Docker. RappelBot checks a JSON reminder file and sends notifications when reminders are due.

## Features

- Python reminder service
- Docker + Docker Compose
- Gotify push notifications
- Multiple users
- Individual or `ALL` notifications
- Timezone support
- JSON configuration
- No database required
- Automatic restart after VPS reboot

## Requirements

- VPS or Linux server
- Docker
- Docker Compose
- Gotify server
- Gotify application tokens

## Setup

Copy example files:

```bash
cp example.config.json config.json
cp example.env .env
cp example.reminders.json reminders.json
```

Edit:

- `config.json` → Gotify URL and user tokens
- `.env` → timezone and broadcast settings
- `reminders.json` → reminders

Example `.env`:

```env
TIMEZONE=America/New_York
BROADCAST_RECIPIENT=ALL
```

## Docker

Build and start:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f rappelbot
```

Restart:

```bash
docker compose restart rappelbot
```

Stop:

```bash
docker compose down
```

## Gotify Docker Network

RappelBot and Gotify run in separate containers and share a Docker network.

Create the network once:

```bash
docker network create rappelbot-network
```

Example `config.json`:

```json
{
  "gotify_url": "http://gotify:80"
}
```

RappelBot does not need a public port.

## Updating

After changing Python code:

```bash
docker compose up -d --build
```

After changing configuration files:

```bash
docker compose restart rappelbot
```

## Troubleshooting

View logs:

```bash
docker compose logs --tail=100 rappelbot
```

Check containers:

```bash
docker compose ps
```

Check Docker networks:

```bash
docker network ls
```

## Manual Gotify Test

```bash
curl "http://your-gotify-server/message?token=YOUR_TOKEN" \
-F "title=Test" \
-F "message=Hello from RappelBot"
```