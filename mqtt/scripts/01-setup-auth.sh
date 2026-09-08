#!/bin/bash
# Step 1: Authentication setup
# Disables anonymous access by requiring per-role credentials.
set -e

sudo mosquitto_passwd -c /etc/mosquitto/passwd sensor_node
sudo mosquitto_passwd /etc/mosquitto/passwd ot_operator

sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 600 /etc/mosquitto/passwd

echo "Auth setup complete: /etc/mosquitto/passwd"
