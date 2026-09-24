# Modbus — Zero-Trust Hardening of a Modbus/TCP PLC (FrostyGoop-Inspired Lab)

## Overview
This module documents a hands-on OT security exercise: standing up a Modbus/TCP
control environment, reproducing the attack pattern behind the January 2024
FrostyGoop incident (Lviv district heating), identifying the architectural gaps
that allowed it, and applying compensating controls to a protocol that has no
native authentication, authorization, or encryption.

Companion write-ups: *Purple Thursday #02 — Zero Trust on Modbus* and
*Purple Thursday #03 — Zero-Trust Modbus: Hardening Modbus for Industrial
Environments* (LinkedIn).

## Objective
Modbus/TCP was designed in 1979 for a physically isolated wire. Any host that
can reach TCP/502 can read and write registers with no protocol-level check on
who is asking. This project shows, end to end:
1. What a realistic multi-tier IT/OT environment looks like
2. How an attacker moves from perimeter access to process manipulation when
   segmentation and protocol controls are absent
3. What compensating controls actually stop that same attack path
4. Proof — via a before/after replay of the identical attack — that the
   hardening works

## Lab Architecture
# Purple Thursday #3 — Rebuilding FrostyGoop: End-to-End Project Plan

> **Working Title:** *Rebuilding FrostyGoop: From Flat Network to Zero Trust in a Home Lab*  
> **Goal:** Build a small multi-tier IT/OT lab, execute a FrostyGoop-style attack path against it, document what went wrong, harden it, and prove the same attack no longer works — as evidence-backed content for Part 3.

---

## 📐 System Architecture & Network Topology

### High-Level Flow (ASCII)

```text
[ Kali Linux (Attacker) ]
           │
           ▼ (WAN Interface)
┌─────────────────────────────────────────────────────────┐
│ pfSense / OPNsense Gateway                              │
│ - WAN: Simulated Internet (NAT/Exposed Weak Service)    │
│ - LAN: 192.168.29.1                                     │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│ Management / IT Segment (192.168.29.0/24)               │
│ - Management Server VM (192.168.29.x)                   │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼ (Segmentation Boundary — Initially Allow-Any Modbus/IP)
┌─────────────────────────────────────────────────────────┐
│ Isolated OT Segment (192.168.100.0/24)                  │
│ - OpenPLC VM (192.168.100.x) — Heating Controller Analog│
│ - FUXA HMI VM / Neighbor (192.168.100.y)                │
│ - Node-RED Proxy (Added in Phase 4 Hardening)           │
└─────────────────────────────────────────────────────────┘
# Modbus Attack & Hardening Code

Companion code for Purple Thursday #01-#03. All scripts assume you are
running against a device **you own and control** in an isolated lab segment.

## Setup
```bash
pip install pymodbus pyshark
```
`pyshark` requires `tshark` installed (`apt install tshark` on Debian/Kali).

## scripts/ (attack + baseline)
- **attack_scan.py** — enumerates holding registers, input registers, and coils on a target with no authentication check. Run this first to confirm the device is reachable and to see what's exposed.
- **attack_write.py** — issues an unauthorized write (FC06/FC05) to tamper a register or coil. Run before hardening (expect success) and after (expect rejection).
- **baseline_capture.py** — captures/analyzes Modbus traffic to build the known-good baseline table (source IPs, function codes, registers touched) referenced in Phase 1 of the project plan.

## config/ (hardening)
- **harden_iptables.sh** — segmentation rule: allow-lists Modbus/TCP to the baselined management/HMI IP only, drops and logs everything else.
- **modbus_proxy.py** — standalone Python proxy that filters by source IP + function code before forwarding to the real PLC. Use this if you're not running Node-RED.
- **node_red_flow.json** — same filtering logic as a Node-RED flow (Import via the Node-RED menu). Update the `ALLOW_IPS`/`ALLOW_FCS` values and the PLC IP in the function/tcp-request nodes before deploying.
- **stunnel_modbus.conf** — wraps the Modbus session in TLS as a compensating transport control, for environments where OpenPLC doesn't support Modbus Security natively.

## Suggested test sequence
1. `python3 scripts/baseline_capture.py --iface eth0 --duration 300` — build the baseline while FUXA operates normally.
2. `python3 scripts/attack_scan.py --target <plc_ip>` then `attack_write.py` from Kali — confirm the attack succeeds pre-hardening.
3. Apply `harden_iptables.sh` and deploy `modbus_proxy.py` (or the Node-RED flow) in front of the PLC.
4. Re-run the identical `attack_write.py` command — confirm it is now rejected, and check `modbus_proxy_rejects.log` / the iptables log for the entry.
