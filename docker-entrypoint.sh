#!/bin/bash
set -e

# Generate self-signed SSL certificate if it doesn't exist (for development)
if [ ! -f /etc/nginx/ssl/cert.pem ] || [ ! -f /etc/nginx/ssl/key.pem ]; then
    echo "Generating self-signed SSL certificate for development..."
    mkdir -p /etc/nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/key.pem \
        -out /etc/nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=YangYang/CN=localhost"
    chmod 600 /etc/nginx/ssl/key.pem
    chmod 644 /etc/nginx/ssl/cert.pem
    echo "Self-signed certificate generated. For production, mount proper certificates to /etc/nginx/ssl/"
fi

# Start uvicorn as non-root user in the background
echo "Starting FastAPI application..."
su -s /bin/bash -c "cd /app && uvicorn app:app --host 0.0.0.0 --port 8000" appuser &

# Wait a moment for the app to start
sleep 3

# Check if uvicorn is running
if ! pgrep -f "uvicorn app:app" > /dev/null; then
    echo "Error: FastAPI application failed to start"
    exit 1
fi

# Start nginx in the foreground
echo "Starting nginx..."
exec nginx -g "daemon off;"

