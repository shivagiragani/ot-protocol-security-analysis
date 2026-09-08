# MQTT — Zero-Trust Hardening of a Mosquitto Broker

Part of the [ot-protocol-security-analysis](../) series.

**Scenario:** A Mosquitto MQTT broker simulating Purdue Model Level 1 (field
sensors) to Level 2 (supervisory) messaging, hardened from an open,
anonymous, plaintext default into an authenticated, least-privilege,
TLS-encrypted deployment — with the access controls validated under live
traffic.

**Environment:** Kali Linux, Mosquitto MQTT Broker v2.x

## Contents

- `config/mosquitto.conf` — broker config enforcing TLS + auth + ACLs
- `config/aclfile` — least-privilege topic scoping per role
- `scripts/01-setup-auth.sh` — password file + permissions
- `scripts/02-generate-pki.sh` — local CA + broker cert generation
- `scripts/03-validate.sh` — subscriber/publisher validation commands
- `captures/` — Wireshark PCAPs (plaintext vs. TLS), if included

## Key finding

Mosquitto enforces ACL denials by silently dropping the payload at the
broker — there's no client-side error on an unauthorized publish.
Validating that an ACL actually works requires watching the *subscriber*
side to confirm the message never arrives, not just checking for errors
on the publisher.

Full write-up: [Medium article — link once published]

## IEC 62443 mapping

- **FR1** (Identification & Authentication) — per-role credentials via `mosquitto_passwd`
- **FR2** (Use Control) — topic-scoped ACLs enforcing least privilege
- **FR4** (Data Confidentiality) — TLS 1.2+ in transit via local PKI

## Reproducing

```bash
chmod +x scripts/*.sh
sudo ./scripts/01-setup-auth.sh
sudo ./scripts/02-generate-pki.sh
sudo cp config/mosquitto.conf /etc/mosquitto/conf.d/test.conf
sudo cp config/aclfile /etc/mosquitto/aclfile
sudo chown mosquitto:mosquitto /etc/mosquitto/aclfile
sudo chmod 600 /etc/mosquitto/aclfile
sudo systemctl restart mosquitto
./scripts/03-validate.sh
```

> Passwords below are placeholders — set your own before running.
