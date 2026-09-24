#!/usr/bin/env python3
"""
modbus_proxy.py - Function-code and source-aware Modbus/TCP proxy.

Sits between clients and the real PLC. Only forwards requests that match the
baselined allow-list (source IP + function code). Everything else is dropped
and logged - this is the protocol-layer control that a plain firewall cannot
provide, since firewalls don't parse Modbus function codes.

This is a Python equivalent of the Node-RED filtering flow referenced in the
project plan (config/node_red_flow.json) - use whichever fits your stack.

Usage:
    python3 modbus_proxy.py --listen-port 5020 --plc-host 192.168.100.50 \
        --allow-ip 192.168.29.X --allow-fc 3 4 6
"""
import argparse
import logging
import socket
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("modbus_proxy_rejects.log"), logging.StreamHandler()],
)


def get_function_code(data: bytes) -> int:
    # Modbus/TCP MBAP header is 7 bytes; function code is the next byte.
    if len(data) < 8:
        return -1
    return data[7]


def handle_client(client_sock, client_addr, plc_host, plc_port, allow_ips, allow_fcs):
    src_ip = client_addr[0]
    try:
        data = client_sock.recv(1024)
        if not data:
            return

        fc = get_function_code(data)

        if src_ip not in allow_ips:
            logging.warning(f"REJECTED - unauthorized source {src_ip} (FC{fc})")
            client_sock.close()
            return

        if fc not in allow_fcs:
            logging.warning(f"REJECTED - disallowed function code FC{fc} from {src_ip}")
            client_sock.close()
            return

        logging.info(f"ALLOWED - {src_ip} FC{fc}")
        plc_sock = socket.create_connection((plc_host, plc_port), timeout=5)
        plc_sock.sendall(data)
        response = plc_sock.recv(1024)
        client_sock.sendall(response)
        plc_sock.close()

    except Exception as e:
        logging.error(f"Error handling {src_ip}: {e}")
    finally:
        client_sock.close()


def run_proxy(listen_port, plc_host, plc_port, allow_ips, allow_fcs):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", listen_port))
    server.listen(5)
    logging.info(f"Modbus proxy listening on :{listen_port} -> {plc_host}:{plc_port}")
    logging.info(f"Allow-list: IPs={allow_ips} FCs={allow_fcs}")

    while True:
        client_sock, client_addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(client_sock, client_addr, plc_host, plc_port, allow_ips, allow_fcs),
            daemon=True,
        ).start()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Modbus function-code filtering proxy")
    p.add_argument("--listen-port", type=int, default=5020)
    p.add_argument("--plc-host", required=True)
    p.add_argument("--plc-port", type=int, default=502)
    p.add_argument("--allow-ip", nargs="+", required=True, help="Baselined client IP(s)")
    p.add_argument("--allow-fc", nargs="+", type=int, required=True, help="Allowed function codes")
    args = p.parse_args()

    run_proxy(args.listen_port, args.plc_host, args.plc_port, set(args.allow_ip), set(args.allow_fc))
