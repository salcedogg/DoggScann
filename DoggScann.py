import argparse
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Barra de progreso

# Lock para sincronizar la salida en consola
print_lock = threading.Lock()

def scan_port(target_ip, port, timeout):
    """
    Escanea un puerto en una IP objetivo utilizando una conexión de socket.

    Args:
        target_ip (str): Dirección IP del objetivo.
        port (int): Puerto a escanear.
        timeout (float): Tiempo de espera para la conexión (en segundos).
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        with print_lock:
            if result == 0:
                print(f"Port {port}: Open")
        sock.close()
    except socket.error:
        pass  # Silenciar errores de conexión

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Host objetivo para escanear")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Tiempo de espera para las conexiones (en segundos)")
    parser.add_argument("-p", "--ports", type=str, default="1-1024", help="Puertos a escanear (e.g., 1-1024, 80, 443)")
    parser.add_argument("-th", "--threads", type=int, default=100, help="Número de threads simultáneos")
    args = parser.parse_args()

    # Resolver la dirección IP del host
    try:
        target_ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"No se pudo resolver la IP para el host: {args.host}")
        return

    print(f"Escaneando objetivo {args.host} en la IP {target_ip}")

    # Obtener el rango de puertos a escanear
    try:
        if "-" in args.ports:
            start_port, end_port = map(int, args.ports.split("-"))
        else:
            start_port = end_port = int(args.ports)
        if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
            raise ValueError
    except ValueError:
        print("Error: El rango de puertos debe estar entre 1 y 65535.")
        return

    timeout = args.timeout
    num_threads = args.threads

    # Barra de progreso
    total_ports = end_port - start_port + 1
    progress = tqdm(total=total_ports, desc="Escaneando Puertos", unit="port")

    # Usar un ThreadPoolExecutor para manejar threads
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(scan_port, target_ip, port, timeout): port for port in range(start_port, end_port + 1)}
        for future in as_completed(futures):
            progress.update(1)

    progress.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo del programa...")
