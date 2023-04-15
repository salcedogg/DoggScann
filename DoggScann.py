import argparse
import socket
import threading
import time

# Lock for synchronizing console output
print_lock = threading.Lock()

def scan_port(target_ip, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((target_ip, port))
    with print_lock:
        if result == 0:
            print(f"Port {port}: Open")
    sock.close()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Target host to scan")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout for socket connections (in seconds)")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", help="Ports to scan (e.g., 1-1024, 80, 443)")
    args = parser.parse_args()

    target_host = args.host
    target_ip = socket.gethostbyname(target_host)
    print(f"Scanning target {target_host} at IP address {target_ip}")

    # Extract port range from argument
    port_range = args.ports.split("-")
    if len(port_range) == 1:
        start_port = end_port = int(port_range[0])
    else:
        start_port = int(port_range[0])
        end_port = int(port_range[1])

    timeout = args.timeout

    # Scan ports using threads
    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(target_ip, port, timeout))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")

