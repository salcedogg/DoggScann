import socket  # Importing socket module

target_host = input("Enter the target host: ")  # User input of target host
target_ip = socket.gethostbyname(target_host)  # Get IP address of target host

# Print target information
print(f"Scanning target {target_host} at IP address {target_ip}")

# Loop through ports from 1 to 1024
for port in range(1, 1025):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket object
    # Set the timeout for each connection attempt
    sock.settimeout(0.5)
    # Attempt to connect to the port on the target
    result = sock.connect_ex((target_ip, port))
    if result == 0:
        # If the connection is successful, print that the port is open
        print(f"Port {port}: Open")
    sock.close()  # Close the socket object
