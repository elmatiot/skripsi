#!/bin/sh
# Generate self-signed TLS cert with SANs (idempotent: regenerate only if missing).
# Hasilnya tersimpan di volume `tls_certs` yg di-mount ke /etc/nginx/certs di nginx container.

set -e

CERT_DIR=/certs
CERT_FILE="$CERT_DIR/fullchain.pem"
KEY_FILE="$CERT_DIR/privkey.pem"

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "[certgen] Cert sudah ada di $CERT_DIR, skip."
    exit 0
fi

echo "[certgen] Generating self-signed cert..."
echo "[certgen] CN  = $CERT_CN"
echo "[certgen] SAN = $CERT_SANS"

apk add --no-cache openssl >/dev/null

openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
    -keyout "$KEY_FILE" \
    -out    "$CERT_FILE" \
    -subj   "/C=ID/ST=DKI/L=Jakarta/O=Skripsi/CN=${CERT_CN}" \
    -addext "subjectAltName=${CERT_SANS}" \
    -addext "keyUsage=digitalSignature,keyEncipherment" \
    -addext "extendedKeyUsage=serverAuth,clientAuth"

chmod 644 "$CERT_FILE"
chmod 600 "$KEY_FILE"

echo "[certgen] Done."
ls -la "$CERT_DIR"
