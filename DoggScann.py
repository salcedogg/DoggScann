import argparse
import socket
import threading
import time

# Lock for synchronizing console output
print_lock = threading.Lock()

def scan_port(target_ip, port, timeout):
    """
    Function to scan a single port on a target IP address using a socket connection.

    Args:
        target_ip (str): Target IP address to scan.
        port (int): Port number to scan.
        timeout (float): Timeout for socket connection (in seconds).
    """
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the timeout for the socket connection
    sock.settimeout(timeout)
    # Attempt to connect to the target IP and port
    result = sock.connect_ex((target_ip, port))
    # Acquire the print lock to synchronize console output
    with print_lock:
        # If the result is 0, the port is open
        if result == 0:
            print(f"Port {port}: Open")
    # Close the socket connection
    sock.close()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Target host to scan")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout for socket connections (in seconds)")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", help="Ports to scan (e.g., 1-1024, 80, 443)")
    args = parser.parse_args()

    # Extract target host, IP address, port range, and timeout from command-line arguments
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
        # Create a thread for each port and pass it to the scan_port function
        t = threading.Thread(target=scan_port, args=(target_ip, port, timeout))
        threads.append(t)
        # Start the thread
        t.start()

    # Wait for all threads to finish
    for t in threads:
        # Join the thread, blocking the main thread until all threads have finished
        t.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Catch KeyboardInterrupt (Ctrl+C) to gracefully exit the program
        print("\nExiting...")
