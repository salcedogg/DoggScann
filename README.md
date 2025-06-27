# DoggScann

A fast and versatile port scanner written in Python.

## Description

DoggScann is a command-line tool that allows you to scan a target host for open ports. It supports specifying a range of ports, setting a timeout for connections, and using multiple threads for faster scanning. You can also save the scan results to a file.

## Features

*   Scan a single port or a range of ports.
*   Scan a list of ports.
*   Adjustable timeout for connection attempts.
*   Multi-threaded scanning for improved performance.
*   Save scan results to a file.
*   Attempts to grab service banners.

## Usage

To use DoggScann, run the script from your terminal with the following command:

```bash
python3 DoggScann_refactored.py <target_host> [options]
```

### Arguments

*   `target_host`: The target host to scan (e.g., `scanme.nmap.org`).

### Options

*   `-p, --ports`: The ports to scan. You can specify a range (e.g., `1-1024`), a list of ports (e.g., `80,443,8080`), or a combination. Defaults to `1-1024`.
*   `-t, --timeout`: The timeout for each connection attempt in seconds. Defaults to `0.5`.
*   `-th, --threads`: The number of concurrent threads to use for scanning. Defaults to `100`.
*   `-o, --output`: The file to save the scan results to.

### Examples

*   Scan the most common ports on `scanme.nmap.org`:

    ```bash
    python3 DoggScann_refactored.py scanme.nmap.org
    ```

*   Scan a specific range of ports:

    ```bash
    python3 DoggScann_refactored.py scanme.nmap.org -p 1-200
    ```

*   Scan specific ports and save the results to a file:

    ```bash
    python3 DoggScann_refactored.py scanme.nmap.org -p 80,443,8080 -o scan_results.txt
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
