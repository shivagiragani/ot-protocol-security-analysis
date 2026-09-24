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