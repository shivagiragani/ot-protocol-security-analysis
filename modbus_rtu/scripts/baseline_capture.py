#!/usr/bin/env python3
"""
baseline_capture.py - Capture and summarize Modbus/TCP traffic to build a
known-good baseline (source IPs, function codes, poll interval).

Requires: pip install pyshark  (wraps tshark)
Run tcpdump/tshark with sufficient privileges, or pre-capture a pcap and
point this script at the file with --pcap.

Usage (live capture, 5 minutes):
    sudo python3 baseline_capture.py --iface eth0 --duration 300

Usage (analyze existing pcap):
    python3 baseline_capture.py --pcap baseline.pcap
"""
import argparse
from collections import Counter, defaultdict

import pyshark


def summarize(packets):
    sources = Counter()
    func_codes = Counter()
    registers_by_client = defaultdict(set)

    for pkt in packets:
        if "modbus" not in pkt:
            continue
        src = pkt.ip.src
        sources[src] += 1
        try:
            fc = pkt.modbus.func_code
            func_codes[fc] += 1
        except AttributeError:
            continue
        try:
            reg = pkt.modbus.reference_num
            registers_by_client[src].add(reg)
        except AttributeError:
            pass

    print("\n=== Baseline Summary ===")
    print("\nClients seen (source IP : packet count):")
    for ip, cnt in sources.most_common():
        print(f"  {ip}: {cnt}")

    print("\nFunction codes observed:")
    for fc, cnt in func_codes.most_common():
        print(f"  FC{fc}: {cnt}")

    print("\nRegisters touched per client:")
    for ip, regs in registers_by_client.items():
        print(f"  {ip}: {sorted(regs)}")

    print("\n>>> Anything outside this table during the attack/validation phases")
    print(">>> is, by definition, anomalous.\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Modbus baseline capture/analysis")
    p.add_argument("--iface", help="Interface for live capture")
    p.add_argument("--duration", type=int, default=300, help="Live capture duration (sec)")
    p.add_argument("--pcap", help="Existing pcap file to analyze instead of live capture")
    args = p.parse_args()

    if args.pcap:
        cap = pyshark.FileCapture(args.pcap, display_filter="modbus")
    elif args.iface:
        cap = pyshark.LiveCapture(interface=args.iface, display_filter="modbus")
        cap.sniff(timeout=args.duration)
    else:
        print("[-] Specify --iface for live capture or --pcap for a file")
        exit(1)

    summarize(cap)
