import socket
import threading
from tqdm import tqdm

# Define the target host
target_host = input("Enter the target host: ")

# Get the IP address of the target host
try:
    target_ip = socket.gethostbyname(target_host)
except socket.gaierror:
    print("Invalid hostname. Exiting...")
    exit()

# Print target information
print(f"Scanning target {target_host} at IP address {target_ip}\n")

# Define a dictionary of commonly used ports to scan
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
}

# Loop through the common ports and scan them
print("Scanning commonly used ports...\n")
for port, service in common_ports.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket object
    sock.settimeout(0.5)  # Set the timeout for each connection attempt
    result = sock.connect_ex((target_ip, port))  # Attempt to connect to the port on the target
    if result == 0:
        print(f"Port {port} ({service}): Open")
    sock.close()

# Define a function to scan a single port
def scan_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket object
    sock.settimeout(0.5)  # Set the timeout for each connection attempt
    result = sock.connect_ex((target_ip, port))  # Attempt to connect to the port on the target
    if result == 0:
        print(f"Port {port}: Open")
    sock.close()

# Loop through ports from 1 to 1024 and start a new thread for each port
print("\nScanning all ports...\n")
for port in tqdm(range(1, 1025)):
    thread = threading.Thread(target=scan_port, args=[port])
    thread.start()
