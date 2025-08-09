set -e

echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
until python - <<END
import os, socket
s = socket.socket()
try:
    s.connect((os.getenv("POSTGRES_HOST","db"), int(os.getenv("POSTGRES_PORT","5432"))))
    print("DB is reachable")
except Exception as e:
    raise SystemExit(1)
finally:
    s.close()
END
do
  echo "DB not ready, retrying..."
  sleep 1
done