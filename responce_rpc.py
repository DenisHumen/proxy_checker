import csv
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(filename='proxy_check.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def check_speed(proxy):
    url = 'http://ipv4.download.thinkbroadband.com/1MB.zip'
    start_time = time.time()
    try:
        response = requests.get(url, proxies=proxy, stream=True, timeout=100)
        response.raise_for_status()
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            total_bytes += len(chunk)
        end_time = time.time()
        speed_mbps = (total_bytes * 8) / (end_time - start_time) / 1_000_000
        return speed_mbps
    except requests.RequestException as e:
        logging.error(f"Speed check failed for proxy {proxy}: {e}")
        if response.status_code == 407:  
            return "ERROR_LOGIN"
        if "cannot access local variable 'response'" in str(e):
            return "NOT_WORKING"
        return None

def check_ping(proxy):
    rpc_url = 'https://endpoints.omniatech.io/v1/eth/mainnet/public'
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        start_time = time.time()
        response = requests.post(rpc_url, json=payload, headers=headers, proxies=proxy, timeout=100)
        end_time = time.time()
        if response.status_code == 200:
            response_time_ms = (end_time - start_time) * 1000
            return response_time_ms
        if response.status_code == 407: 
            return "ERROR_LOGIN"
        return None
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Ping check failed for proxy {proxy}: {e}")
        if "cannot access local variable 'response'" in str(e):
            return "NOT_WORKING"
        return None

def process_proxy(proxy):
    proxy_url = f"http://{proxy['user']}:{proxy['pass']}@{proxy['proxyip']}:{proxy['proxyport']}"
    proxy_dict = {
        'http': proxy_url,
        'https': proxy_url
    }
    attempts = 3
    for attempt in range(attempts):
        speed_mbps = check_speed(proxy_dict)
        ping = check_ping(proxy_dict)
        if speed_mbps == "ERROR_LOGIN" or ping == "ERROR_LOGIN":
            proxy['speed_mbps'] = "ERROR_LOGIN"
            proxy['ping'] = "ERROR_LOGIN"
            return proxy
        if speed_mbps == "NOT_WORKING" or ping == "NOT_WORKING":
            proxy['speed_mbps'] = "NOT_WORKING"
            proxy['ping'] = "NOT_WORKING"
            return proxy
        if speed_mbps is not None and ping is not None:
            proxy['speed_mbps'] = speed_mbps
            proxy['ping'] = ping
            return proxy
        if speed_mbps is None and ping is None:
            logging.warning(f"Attempt {attempt + 1} failed for proxy {proxy['id']}. Retrying...")
            time.sleep(1)
        else:
            proxy['speed_mbps'] = "NO_CONNECTION_SPEED"
            proxy['ping'] = "NO_CONNECTION_PING"
            return proxy
    proxy['speed_mbps'] = "ERROR"
    proxy['ping'] = "ERROR"
    return proxy

def load_proxies(input_file):
    proxies = []
    with open(input_file, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for idx, row in enumerate(reader):
            proxy_url = row[0]
            user_pass, proxy_ip_port = proxy_url.split('@')
            user, password = user_pass.split(':', 1)
            proxy_ip, proxy_port = proxy_ip_port.split(':', 1)
            proxies.append({
                'id': idx + 1,
                'user': user,
                'pass': password,
                'proxyip': proxy_ip,
                'proxyport': proxy_port,
                'speed_mbps': '',
                'ping': ''
            })
    return proxies

def save_results(output_file, proxies):
    with open(output_file, mode='w', newline='') as csvfile:
        fieldnames = ['id', 'VM', 'user', 'pass', 'proxyip', 'proxyport', 'speed_mbps', 'ping']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for proxy in proxies:
            writer.writerow(proxy)

def filter_proxies_with_empty_values(proxies):
    return [proxy for proxy in proxies if proxy['speed_mbps'] == '' or proxy['ping'] == '']

def filter_proxies_with_error(proxies):
    return [proxy for proxy in proxies if proxy['speed_mbps'] in ['ERROR', 'NO_CONNECTION_SPEED', 'ERROR_LOGIN'] or proxy['ping'] in ['ERROR', 'NO_CONNECTION_PING', 'ERROR_LOGIN']]

def load_existing_results(output_file):
    try:
        with open(output_file, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            return [row for row in reader]
    except FileNotFoundError:
        return []

def update_existing_results(existing_results, updated_proxies):
    updated_results = []
    for result in existing_results:
        for updated_proxy in updated_proxies:
            if result['id'] == updated_proxy['id']:
                result = updated_proxy
                break
        updated_results.append(result)
    return updated_results

def main():
    input_file = 'Proxypass.csv'
    output_file = 'ProxyResults.csv'

    proxies = load_proxies(input_file)
    existing_results = load_existing_results(output_file)

    print('NO_CONNECTION_PING и NO_CONNECTION_SPEED значит что не удалось обработать данные но прокси работает')
    print('\n\tNOT_WORKING значит что прокси не работает')
    
    choice = input("Введите 1 для проверки всех прокси, 2 для проверки прокси с результатами ERROR: ")
    if choice == '2':
        proxies = filter_proxies_with_error(existing_results)

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(process_proxy, proxy): proxy for proxy in proxies}
        updated_proxies = []
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                updated_proxies.append(result)
                print(f"Обработан прокси {result['id']} - Скорость: {result['speed_mbps']} Мбит/с, Пинг: {result['ping']} мс")
                if choice == '2':
                    existing_results = update_existing_results(existing_results, [result])
                    save_results(output_file, existing_results)
                else:
                    save_results(output_file, updated_proxies)
            except Exception as exc:
                logging.error(f"Proxy {proxy['id']} raised an exception: {exc}")
                print(f"Прокси {proxy['id']} вызвал исключение: {exc}")
                if "cannot access local variable 'response'" in str(exc):
                    proxy['speed_mbps'] = "NOT_WORKING"
                    proxy['ping'] = "NOT_WORKING"
                    updated_proxies.append(proxy)

    if choice != '2':
        save_results(output_file, updated_proxies)

if __name__ == "__main__":
    main()