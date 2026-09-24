#!/bin/bash
# harden_iptables.sh
# Segmentation hardening for the OT segment (Phase 4.2 of the project plan).
# Run on the host in front of OpenPLC (or on OpenPLC's own Linux host).
#
# Replace with your actual baselined client IP(s) from Phase 1.
MGMT_IP="192.168.29.X"      # Management Server / FUXA host, from your baseline
OT_IFACE="eth0"              # interface facing the OT segment

echo "[*] Flushing existing rules on port 502..."
iptables -D INPUT -p tcp --dport 502 -j ACCEPT 2>/dev/null
iptables -D INPUT -p tcp --dport 502 -j DROP 2>/dev/null

echo "[*] Allowing Modbus/TCP only from baselined management/HMI host: $MGMT_IP"
iptables -A INPUT -i "$OT_IFACE" -p tcp --dport 502 -s "$MGMT_IP" -j ACCEPT

echo "[*] Logging and dropping everything else on port 502..."
iptables -A INPUT -i "$OT_IFACE" -p tcp --dport 502 \
    -j LOG --log-prefix "MODBUS-BLOCKED: " --log-level 4
iptables -A INPUT -i "$OT_IFACE" -p tcp --dport 502 -j DROP

echo "[+] Rules applied. Verify with: iptables -L INPUT -v -n --line-numbers"
echo "[+] Blocked attempts will appear in: journalctl -k | grep MODBUS-BLOCKED"
