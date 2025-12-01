# Playit with 1Password Integration

Docker container setup for running [playit.gg](https://playit.gg) tunneling service with automatic secret retrieval from 1Password using a service account.

## Overview

This setup provides:
- **Playit Agent**: Runs the official playit-agent (v0.16) to create secure tunnels
- **1Password Integration**: Automatically fetches the playit secret key from your 1Password vault
- **Python-based Secret Management**: Uses Python script to interact with 1Password CLI
- **Docker Compose**: Simple deployment with host networking
- **Persistent Storage**: Keeps playit configuration across container restarts

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Container                │
│                                         │
│  ┌────────────────────────────────┐    │
│  │    entrypoint.sh               │    │
│  │    (Orchestrates startup)      │    │
│  └──────────┬─────────────────────┘    │
│             │                           │
│             ▼                           │
│  ┌────────────────────────────────┐    │
│  │    fetch_secret.py             │    │
│  │    (Fetches from 1Password)    │    │
│  └──────────┬─────────────────────┘    │
│             │                           │
│             ▼                           │
│  ┌────────────────────────────────┐    │
│  │    playit-agent                │    │
│  │    (Runs with SECRET_KEY)      │    │
│  └────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │  1Password   │
   │    Vault     │
   └──────────────┘
```

## Prerequisites

1. **Docker and Docker Compose** installed on your system
2. **1Password Service Account** with access to the vault containing playit secrets
3. **OP_SERVICE_ACCOUNT_TOKEN** environment variable set (already configured in your `.bashrc`)

## Setup Instructions

### 1. Verify Environment Variable

Ensure your 1Password service account token is set:

```bash
echo $OP_SERVICE_ACCOUNT_TOKEN
```

If it's not set, add it to your `.bashrc` or export it:

```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"
```

### 2. Build the Docker Image

Navigate to the playit directory and build the image:

```bash
cd /home/agent/playit
docker-compose build
```

This will:
- Use the official `ghcr.io/playit-cloud/playit-agent:0.16` as base
- Install Python3 and 1Password CLI
- Copy the secret fetching scripts

### 3. Run the Container

Start the playit service:

```bash
docker-compose up -d
```

Or run in foreground to see logs:

```bash
docker-compose up
```

### 4. Verify It's Running

Check the container logs:

```bash
docker-compose logs -f playit
```

You should see:
- ✓ 1Password CLI version
- ✓ OP_SERVICE_ACCOUNT_TOKEN is set
- ✓ Secret retrieved successfully
- ✓ SECRET_KEY loaded
- Playit agent starting

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OP_SERVICE_ACCOUNT_TOKEN` | 1Password service account token | - | ✓ Yes |
| `PLAYIT_SECRET_REFERENCE` | 1Password secret reference path | `op://API Dev/Playit/credential` | No |

### 1Password Secret Reference

The secret is fetched from: `op://API Dev/Playit/credential`

Format: `op://[Vault Name]/[Item Name]/[Field Name]`

To use a different secret location, set the `PLAYIT_SECRET_REFERENCE` environment variable in `docker-compose.yml`.

### Network Mode

The container uses `network_mode: host` to allow playit direct access to host networking, which is required for the tunneling service to work properly.

### Data Persistence

Playit configuration and data are persisted in a Docker volume named `playit-data`, which maps to `/root/.playit` inside the container.

## File Structure

```
/home/agent/playit/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── fetch_secret.py         # Python script for 1Password integration
├── entrypoint.sh          # Container startup script
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Troubleshooting

### Container fails to start

1. **Check environment variable:**
   ```bash
   docker-compose exec playit env | grep OP_SERVICE_ACCOUNT_TOKEN
   ```

2. **Check 1Password CLI in container:**
   ```bash
   docker-compose exec playit op --version
   ```

3. **Manually test secret retrieval:**
   ```bash
   docker-compose exec playit python3 /app/fetch_secret.py
   ```

### Can't fetch secret from 1Password

- Verify your service account token is valid
- Ensure the service account has access to the "API Dev" vault
- Check that the item "Playit" exists in the vault with a "credential" field

### Playit agent not connecting

- Check playit logs: `docker-compose logs playit`
- Verify `SECRET_KEY` is being set correctly
- Ensure host networking is working properly

## Management Commands

### Start the service
```bash
docker-compose up -d
```

### Stop the service
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f playit
```

### Restart the service
```bash
docker-compose restart playit
```

### Rebuild after changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access container shell
```bash
docker-compose exec playit /bin/bash
```

## Security Best Practices

1. **Never commit secrets**: The `.env` file is gitignored to prevent accidental commits
2. **Use service accounts**: Service accounts provide limited, scoped access to 1Password
3. **Rotate tokens**: Regularly rotate your 1Password service account tokens
4. **Principle of least privilege**: Grant service accounts only the minimum required permissions
5. **Monitor access**: Review 1Password access logs periodically

## Updating

### Update playit agent version

Edit `Dockerfile` and change the base image version:
```dockerfile
FROM ghcr.io/playit-cloud/playit-agent:0.XX
```

Then rebuild:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update 1Password CLI version

Edit the `RUN` command in `Dockerfile` that downloads the 1Password CLI and change the version number, then rebuild.

## Support

- **Playit Documentation**: https://playit.gg/docs
- **1Password CLI Documentation**: https://developer.1password.com/docs/cli
- **1Password Service Accounts**: https://developer.1password.com/docs/service-accounts

## License

This configuration is provided as-is for use with playit.gg and 1Password services.
