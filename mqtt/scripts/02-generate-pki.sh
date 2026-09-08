#!/bin/bash
# Step 3: PKI & TLS generation via OpenSSL
# Creates a local CA and a broker certificate signed by it.
set -e

sudo mkdir -p /etc/mosquitto/certs
cd /etc/mosquitto/certs

# 1. Generate CA key and self-signed certificate
sudo openssl req -new -x509 -days 365 -nodes -out ca.crt -keyout ca.key -subj "/CN=OT-Security-CA"

# 2. Generate broker private key and CSR
sudo openssl req -new -nodes -out server.csr -keyout server.key -subj "/CN=localhost"

# 3. Sign broker certificate using the CA
sudo openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# 4. Set directory and file permissions for the broker user
sudo chown -R mosquitto:mosquitto /etc/mosquitto/certs
sudo chmod 755 /etc/mosquitto/certs
sudo chmod 644 /etc/mosquitto/certs/ca.crt /etc/mosquitto/certs/server.crt
sudo chmod 600 /etc/mosquitto/certs/server.key /etc/mosquitto/certs/ca.key

echo "PKI setup complete: /etc/mosquitto/certs"
