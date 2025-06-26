import argparse
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

print_lock = threading.Lock()

def scan_port(target_ip, port, timeout):
    """
    Scans a single port and attempts to grab a service banner if it's open.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            banner = ""
            try:
                # Set a short timeout for receiving data
                sock.settimeout(2)
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            except (socket.timeout, socket.error):
                # If no banner is received, we still know the port is open
                pass
            with print_lock:
                print(f"[+] Port {port}: Open   Banner: {banner}")
        sock.close()
    except socket.error:
        pass

def get_port_range(port_string):
    """
    Parses a port string which can contain ranges (e.g., 1-1024) and
    comma-separated ports (e.g., 80,443,8080) into a unique set of ports.

    Args:
        port_string (str): The string containing the port specification.

    Returns:
        set: A set of unique integer ports.
    """
    ports = set()
    try:
        # Split by comma first to handle multiple parts
        port_parts = port_string.split(',')
        for part in port_parts:
            part = part.strip()
            if "-" in part:
                start_port, end_port = map(int, part.split("-"))
                if 1 <= start_port <= end_port <= 65535:
                    ports.update(range(start_port, end_port + 1))
                else:
                    raise ValueError("Port range is out of valid range (1-65535).")
            else:
                port_num = int(part)
                if 1 <= port_num <= 65535:
                    ports.add(port_num)
                else:
                    raise ValueError("Port number is out of valid range (1-65535).")
    except ValueError as e:
        print(f"Error: Invalid port specification. {e}")
        return None # Return None to indicate an error
    return ports

def main():
    parser = argparse.ArgumentParser(description="A fast and versatile port scanner.")
    parser.add_argument("host", help="Target host to scan.")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout for each connection attempt in seconds.")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", help="Ports to scan (e.g., 1-1024, 80, 443, 8080)." )
    parser.add_argument("-th", "--threads", type=int, default=100, help="Number of concurrent threads to use for scanning.")
    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"[!] Error: Could not resolve hostname: {args.host}")
        return

    print(f"[*] Scanning target {args.host} ({target_ip})")

    ports_to_scan = get_port_range(args.ports)
    if ports_to_scan is None:
        return # Exit if port specification was invalid
    timeout = args.timeout
    num_threads = args.threads

    total_ports = len(ports_to_scan)
    progress_bar = tqdm(total=total_ports, desc="Scanning Ports", unit="port")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(scan_port, target_ip, port, timeout): port for port in ports_to_scan}
        for future in as_completed(futures):
            progress_bar.update(1)

    progress_bar.close()

if __name__ == "__main__":    try:        main()    except KeyboardInterrupt:        print("\n[*] Exiting program.")
