import argparse
import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# A lock to ensure that console output is not garbled by multiple threads
print_lock = threading.Lock()

def scan_port(target_ip, port, timeout):
    """
    Scans a single port and attempts to grab a service banner if it's open.
    Returns a tuple containing the port number, status ('Open' or 'Closed'), and the banner.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                banner = ""
                try:
                    sock.settimeout(2)  # Short timeout for receiving data
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                except (socket.timeout, socket.error):
                    pass  # No banner received, but the port is open
                return port, "Open", banner
    except socket.error:
        pass  # Ignore socket errors (e.g., connection refused)
    return port, "Closed", ""

def get_port_range(port_string):
    """
    Parses a port string (e.g., '1-1024' or '80,443,8080') into a set of unique ports.
    """
    ports = set()
    try:
        for part in port_string.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                if 1 <= start <= end <= 65535:
                    ports.update(range(start, end + 1))
                else:
                    raise ValueError("Port range is out of the valid range (1-65535).")
            else:
                port_num = int(part)
                if 1 <= port_num <= 65535:
                    ports.add(port_num)
                else:
                    raise ValueError("Port number is out of the valid range (1-65535).")
    except ValueError as e:
        with print_lock:
            print(f"Error: Invalid port specification. {e}")
        return None
    return sorted(list(ports))

def save_results(filename, results):
    """Saves the scan results to a file."""
    with open(filename, 'w') as f:
        f.write("Port,Status,Banner\n")
        for port, status, banner in results:
            if status == 'Open':
                f.write(f"{port},{status},{banner}\n")

def main():
    """Main function to parse arguments and orchestrate the scan."""
    parser = argparse.ArgumentParser(description="A fast and versatile port scanner.")
    parser.add_argument("host", help="Target host to scan.")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", help="Ports to scan (e.g., '1-1024', '80,443').")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout for each connection attempt.")
    parser.add_argument("-th", "--threads", type=int, default=100, help="Number of concurrent threads.")
    parser.add_argument("-o", "--output", type=str, help="Save the scan results to a file.")
    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"[!] Error: Could not resolve hostname: {args.host}")
        return

    print(f"[*] Scanning target {args.host} ({target_ip})")

    ports_to_scan = get_port_range(args.ports)
    if not ports_to_scan:
        return

    open_ports = []
    with tqdm(total=len(ports_to_scan), desc="Scanning Ports", unit="port") as progress_bar:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_port = {executor.submit(scan_port, target_ip, port, args.timeout): port for port in ports_to_scan}
            for future in as_completed(future_to_port):
                port, status, banner = future.result()
                if status == 'Open':
                    with print_lock:
                        print(f"[+] Port {port}: Open   Banner: {banner}")
                    open_ports.append((port, status, banner))
                progress_bar.update(1)

    if args.output:
        save_results(args.output, open_ports)
        print(f"\n[*] Scan results saved to {args.output}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Exiting program.")

