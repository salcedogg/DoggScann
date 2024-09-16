import argparse
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

print_lock = threading.Lock()

def scan_port(target_ip, port, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        with print_lock:
            if result == 0:
                print(f"Port {port}: Open")
        sock.close()
    except socket.error:
        pass

def get_port_range(port_string):
    """
    Devuelve un conjunto de puertos a escanear para evitar duplicados.

    Args:
        port_string (str): Cadena que contiene el rango de puertos o puertos individuales.

    Returns:
        set: Conjunto de puertos únicos.
    """
    ports = set()
    try:
        if "-" in port_string:
            start_port, end_port = map(int, port_string.split("-"))
            ports.update(range(start_port, end_port + 1))
        else:
            ports.add(int(port_string))
    except ValueError:
        print("Error: El rango de puertos debe estar entre 1 y 65535.")
    return ports

def main():
    parser = argparse.ArgumentParser(description="Escáner de puertos con manejo de duplicados")
    parser.add_argument("host", help="Host objetivo para escanear")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Tiempo de espera para las conexiones")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", help="Rango de puertos a escanear (ejemplo: 1-1024, 80, 443)")
    parser.add_argument("-th", "--threads", type=int, default=100, help="Número de threads simultáneos")
    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"No se pudo resolver la IP para el host: {args.host}")
        return

    print(f"Escaneando objetivo {args.host} en la IP {target_ip}")

    ports_to_scan = get_port_range(args.ports)
    timeout = args.timeout
    num_threads = args.threads

    total_ports = len(ports_to_scan)
    progress_bar = tqdm(total=total_ports, desc="Escaneando Puertos", unit="port")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(scan_port, target_ip, port, timeout): port for port in ports_to_scan}
        for future in as_completed(futures):
            progress_bar.update(1)

    progress_bar.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo del programa...")
