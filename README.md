# Proxy Checker Script

### Donation ``` TRC20 - TRWzXZE16bgJg3eHa9n8q4ioZjMgKHwF9a ```
<img src="usdt.jpg" alt="Donation" width="150"/>

This script checks the speed and ping of a list of proxies provided in a CSV file. It logs the results and saves them to an output CSV file.

## Features

- Checks download speed of proxies.
- Checks ping response time of proxies.
- Logs results to a file.
- Supports retrying failed checks.
- Filters proxies based on previous results.

## Requirements

- Python 3.x
- `requests` library

## Installation

Install the required Python library using pip:

```sh
pip install requests
```

## Usage

1. Prepare a CSV file named `Proxypass.csv` with the proxy details in the following format:

    ```
    user:pass@proxyip:proxyport
    ```

2. Run the script:

    ```sh
    python responce_rpc.py
    ```

3. Follow the on-screen instructions:

    - Enter `1` to check all proxies.
    - Enter `2` to check only proxies with previous results of `ERROR`.

## Output

The script will generate an output CSV file named `ProxyResults.csv` with the following columns:

- `id`: Proxy ID
- `VM`: Virtual Machine (if applicable)
- `user`: Proxy username
- `pass`: Proxy password
- `proxyip`: Proxy IP address
- `proxyport`: Proxy port
- `speed_mbps`: Download speed in Mbps
- `ping`: Ping response time in milliseconds

### Special Values

- `NO_CONNECTION_PING` and `NO_CONNECTION_SPEED`: The proxy works but data could not be processed.
- `NOT_WORKING`: The proxy does not work.
- `ERROR_LOGIN`: There was an error logging in to the proxy.

## Logging

The script logs detailed information to a file named `proxy_check.log`.

## Example

Example output in `ProxyResults.csv`:

```csv
id;VM;user;pass;proxyip;proxyport;speed_mbps;ping
1;;user1;pass1;192.168.1.1;8080;10.5;150
2;;user2;pass2;192.168.1.2;8080;NOT_WORKING;NOT_WORKING
```

## Notes

- Ensure the proxies are formatted correctly in the input CSV file.
- The script uses a timeout of 100 seconds for each proxy check.
