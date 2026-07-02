import urllib.request
import urllib.error
import concurrent.futures
import re
import base64
import json
import time
import sys
import os

# --- TERMINAL COLORS ---
class C:
    NEON = '\033[92m'    # Light Green
    DARK = '\033[32m'    # Dark Green
    CYAN = '\033[96m'    # Cyan
    RED = '\033[91m'     # Red
    YELLOW = '\033[93m'  # Yellow
    RESET = '\033[0m'    # Reset
    BOLD = '\033[1m'     # Bold

# --- CONFIGURATION & SOURCES ---
SOURCES = {
    'http': [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'https://fastly.jsdelivr.net/gh/proxygenerator1/ProxyGenerator@main/MostStable/http.txt',
        'https://fastly.jsdelivr.net/gh/TheSpeedX/PROXY-List@master/http.txt',
        'https://fastly.jsdelivr.net/gh/monosans/proxy-list@main/proxies/http.txt',
        'https://fastly.jsdelivr.net/gh/roosterkid/openproxylist@main/HTTPS_RAW.txt',
        'https://fastly.jsdelivr.net/gh/prxchk/proxy-list@main/http.txt',
        'https://fastly.jsdelivr.net/gh/Zaeem20/FREE_PROXIES_LIST@master/http.txt',
        'https://fastly.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt',
        'https://fastly.jsdelivr.net/gh/VPSLabCloud/VPSLab-Free-Proxy-List@main/http_all.txt'
    ],
    'socks4': [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all',
        'https://fastly.jsdelivr.net/gh/proxygenerator1/ProxyGenerator@main/MostStable/socks4.txt',
        'https://fastly.jsdelivr.net/gh/TheSpeedX/PROXY-List@master/socks4.txt',
        'https://fastly.jsdelivr.net/gh/monosans/proxy-list@main/proxies/socks4.txt',
        'https://fastly.jsdelivr.net/gh/roosterkid/openproxylist@main/SOCKS4_RAW.txt',
        'https://fastly.jsdelivr.net/gh/prxchk/proxy-list@main/socks4.txt',
        'https://fastly.jsdelivr.net/gh/Zaeem20/FREE_PROXIES_LIST@master/socks4.txt',
        'https://fastly.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt',
        'https://fastly.jsdelivr.net/gh/VPSLabCloud/VPSLab-Free-Proxy-List@main/socks4_all.txt'
    ],
    'socks5': [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all',
        'https://fastly.jsdelivr.net/gh/proxygenerator1/ProxyGenerator@main/MostStable/socks5.txt',
        'https://fastly.jsdelivr.net/gh/TheSpeedX/PROXY-List@master/socks5.txt',
        'https://fastly.jsdelivr.net/gh/monosans/proxy-list@main/proxies/socks5.txt',
        'https://fastly.jsdelivr.net/gh/roosterkid/openproxylist@main/SOCKS5_RAW.txt',
        'https://fastly.jsdelivr.net/gh/prxchk/proxy-list@main/socks5.txt',
        'https://fastly.jsdelivr.net/gh/Zaeem20/FREE_PROXIES_LIST@master/socks5.txt',
        'https://fastly.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt',
        'https://fastly.jsdelivr.net/gh/VPSLabCloud/VPSLab-Free-Proxy-List@main/socks5_all.txt'
    ],
    'mtproto': [
        'https://fastly.jsdelivr.net/gh/yebekhe/MTProtoCollector@main/proxy/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/hookzof/socks5_list@master/tg/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/mishakorzik/Free-Proxies@main/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/ALIILAPRO/MTProtoProxy@main/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/ts-sf/mtproto-proxy-list@main/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/SlavaBaturin/telegram-mtproto-proxies@master/proxies.txt',
        'https://fastly.jsdelivr.net/gh/whoahaow/rjsxrd@main/MTProto.txt',
        'https://fastly.jsdelivr.net/gh/MustafaBaqer/VestraNet-Nodes@main/protocols/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/Leon406/Sub@master/sub/share/mtp',
        'https://fastly.jsdelivr.net/gh/Bardiafa/Free-V2ray-Config@main/Splitted-By-Protocol/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/tbbatbb/Proxy@master/dist/mtproto.txt',
        'https://fastly.jsdelivr.net/gh/peasoft/NoMoreWalls@master/list_mtproto.txt'
    ],
    'v2ray': [
        'https://fastly.jsdelivr.net/gh/barry-jelly/Free_Proxy_Daily@master/V2Ray/v2ray.txt',
        'https://fastly.jsdelivr.net/gh/Pawdroid/Free-servers@main/sub',
        'https://fastly.jsdelivr.net/gh/mahdibland/ShadowsocksAggregator@master/Eternity',
        'https://fastly.jsdelivr.net/gh/Leon406/Sub@master/sub/share/v2',
        'https://fastly.jsdelivr.net/gh/mfuu/v2ray@master/v2ray',
        'https://fastly.jsdelivr.net/gh/MatinGhanbari/v2ray-configs@main/subscriptions/v2ray/all_sub.txt',
        'https://fastly.jsdelivr.net/gh/Au1rxx/free-vpn-subscriptions@main/output/v2ray-base64.txt',
        'https://fastly.jsdelivr.net/gh/sevcator/5ubscrpt10n@main/protocols/vl.txt',
        'https://fastly.jsdelivr.net/gh/yitong2333/proxy-minging@main/v2ray.txt'
    ]
}

# --- PARSING LOGIC ---
def fetch_url(url, category):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            text = response.read().decode('utf-8', errors='ignore')
            return text, category
    except Exception:
        return "", category

def process_text(text, category):
    matches = []
    if category == 'mtproto':
        mtp_regex = re.compile(r'(?:https://t\.me/proxy\?|tg://proxy\?)?server=([a-zA-Z0-9.-]+)&port=(\d+)&secret=([a-zA-Z0-9_\-%=]+)', re.IGNORECASE)
        for match in mtp_regex.finditer(text):
            server, port, secret = match.groups()
            if 32 <= len(secret) <= 34 and not secret.lower().startswith('ee'):
                matches.append(f"tg://proxy?server={server}&port={port}&secret={secret}")
    
    elif category == 'v2ray':
        decoded_text = text
        if re.match(r'^[a-zA-Z0-9+/=\s\n\r]+$', text.strip()) and len(text.strip()) > 100:
            try:
                decoded_text = base64.b64decode(text.strip().replace(r'\s', '')).decode('utf-8', errors='ignore')
            except Exception:
                pass
        
        v2_regex = re.compile(r'(?:vmess|vless|trojan|ss)://[a-zA-Z0-9._~:/?#@!$&\'()*+,;=%-]+')
        matches = v2_regex.findall(decoded_text)
        
    else:
        ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}\b')
        raw_matches = ip_regex.findall(text)
        for ip_str in raw_matches:
            try:
                ip, port = ip_str.split(':')
                parts = [int(p) for p in ip.split('.')]
                if all(p <= 255 for p in parts) and int(port) <= 65535:
                    matches.append(ip_str)
            except Exception:
                pass
                
    return matches

# --- UI HELPERS ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = fr"""{C.NEON}{C.BOLD}
  ____ ___ _ __     __ _____  ____  ____  _   _  _     _     _____  ____  
 / ___|_ _| |\ \   / /| ____||  _ \| __ )| | | || |   | |   | ____||_   _| 
 \___ \| | | | \ \ / / |  _|  | |_) |  _ \| | | || |   | |   |  _|    | |   
  ___) | | | |__\ V /  | |___ |  _ <| |_) | |_| || |___| |___| |___   | |   
 |____/___||_____\_/   |_____||_| \_\____/ \___/ |_____|_____|_____|  |_|   
                                                                            
{C.CYAN} :: PROXY ENGINE v7.0 :: {C.DARK}LIVE MULTI-API AGGREGATOR{C.RESET}
 {C.YELLOW}Developed by:{C.RESET} @Silverbullets_bot
 {C.YELLOW}Telegram:{C.RESET}     https://t.me/Silverbullets_bot
"""
    print(banner)

def draw_progress_bar(completed, total, bar_length=35):
    percent = float(completed) / total
    arrow = '█' * int(round(percent * bar_length))
    spaces = '░' * (bar_length - len(arrow))
    sys.stdout.write(f"\r {C.BOLD}{C.CYAN}[{C.NEON}{arrow}{C.DARK}{spaces}{C.CYAN}]{C.RESET} {int(percent * 100)}%  {C.YELLOW}({completed}/{total} nodes){C.RESET}")
    sys.stdout.flush()

# --- SAFE MIXED SORTING ---
def sort_key(item):
    ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', item)
    if ip_match:
        # Group 0 puts IPs first, then sorts by numerical blocks
        return (0, tuple(int(x) for x in ip_match.group(0).split('.')), item)
    # Group 1 puts protocol links second, sorting them alphabetically
    return (1, (), item)

# --- MAIN ENGINE ---
def main():
    clear_screen()
    print_banner()
    
    print(f"{C.BOLD} Select Target Protocol:{C.RESET}")
    print(f" {C.NEON}[1]{C.RESET} ALL PROTOCOLS (MIXED)")
    print(f" {C.NEON}[2]{C.RESET} HTTP / HTTPS")
    print(f" {C.NEON}[3]{C.RESET} SOCKS4")
    print(f" {C.NEON}[4]{C.RESET} SOCKS5")
    print(f" {C.NEON}[5]{C.RESET} MTPROTO (Standard)")
    print(f" {C.NEON}[6]{C.RESET} V2RAY (VLESS / VMESS / TROJAN)\n")
    
    choice = input(f" {C.CYAN}>{C.RESET} Enter your choice (1-6): ").strip()
    
    options = {
        '1': list(SOURCES.keys()), '2': ['http'], '3': ['socks4'],
        '4': ['socks5'], '5': ['mtproto'], '6': ['v2ray']
    }
    
    targets = options.get(choice, list(SOURCES.keys()))
    tasks = []
    master_set = set()
    counts = {k: 0 for k in SOURCES.keys()}
    
    for cat in targets:
        for url in SOURCES[cat]:
            tasks.append((url, cat))
            
    print(f"\n{C.BOLD}{C.NEON}[+]{C.RESET} Launching query handshake across {len(tasks)} cluster nodes...\n")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_url = {executor.submit(fetch_url, url, cat): (url, cat) for url, cat in tasks}
        
        completed = 0
        draw_progress_bar(0, len(tasks))
        for future in concurrent.futures.as_completed(future_to_url):
            text, cat = future.result()
            if text:
                proxies = process_text(text, cat)
                for p in proxies:
                    if p not in master_set:
                        master_set.add(p)
                        counts[cat] += 1
            
            completed += 1
            draw_progress_bar(completed, len(tasks))

    time_taken = round(time.time() - start_time, 2)
    print(f"\n\n{C.BOLD}{C.NEON}[+]{C.RESET} Extraction complete in {time_taken} seconds.")

    if not master_set:
        print(f"\n{C.RED}[!] NO PROXIES FOUND. Target lists completely unreachable.{C.RESET}")
        return

    # Uses the updated safe structure to prevent type comparison errors
    sorted_proxies = sorted(list(master_set), key=sort_key)

    date_str = time.strftime("%Y-%m-%d")
    txt_filename = f"Silverbullet_Proxies_{date_str}.txt"
    json_filename = f"Silverbullet_Proxies_{date_str}.json"

    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_proxies))
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(sorted_proxies, f, indent=2)

    print(f"\n{C.CYAN} ┌──────────────────────────────────────────┐{C.RESET}")
    print(f"{C.CYAN} │ {C.BOLD}{C.NEON}SYSTEM STATISTICS{C.RESET}{C.CYAN}                        │{C.RESET}")
    print(f"{C.CYAN} ├──────────────────────────────────────────┤{C.RESET}")
    for cat in targets:
        print(f"{C.CYAN} │ {C.RESET}{cat.upper():<10} : {C.YELLOW}{counts[cat]:<25}{C.CYAN} │{C.RESET}")
    print(f"{C.CYAN} ├──────────────────────────────────────────┤{C.RESET}")
    print(f"{C.CYAN} │ {C.BOLD}TOTAL UNIQUE{C.RESET} : {C.NEON}{len(master_set):<25}{C.CYAN} │{C.RESET}")
    print(f"{C.CYAN} └──────────────────────────────────────────┘{C.RESET}")

    print(f"\n{C.BOLD}{C.NEON}[ SUCCESS ]{C.RESET} Matrices exported to current directory:")
    print(f"  {C.CYAN}→{C.RESET} {txt_filename}")
    print(f"  {C.CYAN}→{C.RESET} {json_filename}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C.RED}[!] Operation aborted by user.{C.RESET}\n")
        sys.exit(0)
