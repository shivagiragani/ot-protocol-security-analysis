#!/usr/bin/env python3
"""
attack_scan.py - Modbus/TCP reconnaissance against a target in YOUR OWN lab.

Demonstrates the core Modbus/TCP weakness: no authentication means any host
that can reach TCP/502 can enumerate holding registers, input registers, and
coils with no check on who is asking.

Usage:
    python3 attack_scan.py --target 192.168.100.x --unit 1
"""
import argparse
from pymodbus.client import ModbusTcpClient


def scan(target: str, unit: int, count: int = 20):
    client = ModbusTcpClient(target)
    if not client.connect():
        print(f"[-] Could not connect to {target}:502")
        return

    print(f"[+] Connected to {target} (unit {unit}) - no credentials required")

    print("\n-- Holding Registers (FC03) --")
    rr = client.read_holding_registers(0, count, slave=unit)
    if not rr.isError():
        for i, val in enumerate(rr.registers):
            print(f"  reg[{i}] = {val}")
    else:
        print(f"  error: {rr}")

    print("\n-- Input Registers (FC04) --")
    rr = client.read_input_registers(0, count, slave=unit)
    if not rr.isError():
        for i, val in enumerate(rr.registers):
            print(f"  input[{i}] = {val}")
    else:
        print(f"  error: {rr}")

    print("\n-- Coils (FC01) --")
    rr = client.read_coils(0, count, slave=unit)
    if not rr.isError():
        for i, val in enumerate(rr.bits):
            print(f"  coil[{i}] = {val}")
    else:
        print(f"  error: {rr}")

    client.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Modbus/TCP recon (lab use only)")
    p.add_argument("--target", required=True, help="Target IP")
    p.add_argument("--unit", type=int, default=1, help="Modbus unit/slave ID")
    p.add_argument("--count", type=int, default=20, help="Number of registers/coils to read")
    args = p.parse_args()
    scan(args.target, args.unit, args.count)
