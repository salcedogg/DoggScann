import argparse
import socket
import threading

def scan_port(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((target_ip, port))
    if result == 0: 
        print(f"Port {port}: Open")
    sock.close()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Target host to scan")
    args = parser.parse_args()

    target_host = args.host
    target_ip = socket.gethostbyname(target_host)
    print(f"Scanning target {target_host} at IP address {target_ip}")

    # Scan ports using threads
    threads = []
    for port in range(1, 1025):
        t = threading.Thread(target=scan_port, args=(target_ip, port))
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

