import urllib.request
import urllib.error
import concurrent.futures
import re
import base64
import json
import csv
import time
import sys
import os
import socket
import glob
from datetime import datetime, timedelta

# --- TERMINAL COLORS ---
class C:
    NEON = '\033[92m'    # Light Green
    DARK = '\033[32m'    # Dark Green
    CYAN = '\033[96m'    # Cyan
    RED = '\033[91m'     # Red
    YELLOW = '\033[93m'  # Yellow
    MAGENTA = '\033[95m' # Magenta
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
        'https://fastly.jsdelivr.net/gh/Leon406/Sub@master/sub/share/mtp'
    ],
    'v2ray': [
        'https://fastly.jsdelivr.net/gh/barry-jelly/Free_Proxy_Daily@master/V2Ray/v2ray.txt',
        'https://fastly.jsdelivr.net/gh/Pawdroid/Free-servers@main/sub',
        'https://fastly.jsdelivr.net/gh/mahdibland/ShadowsocksAggregator@master/Eternity',
        'https://fastly.jsdelivr.net/gh/Leon406/Sub@master/sub/share/v2',
        'https://fastly.jsdelivr.net/gh/mfuu/v2ray@master/v2ray',
        'https://fastly.jsdelivr.net/gh/MatinGhanbari/v2ray-configs@main/subscriptions/v2ray/all_sub.txt'
    ]
}

# --- ENGINE V10.0 CORE ---
class ProxyEngineV10:
    def __init__(self):
        self.master_set = set()
        self.counts = {k: 0 for k in SOURCES.keys()}
        self.ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}\b')
        self.v2_regex = re.compile(r'(?:vmess|vless|trojan|ss)://[a-zA-Z0-9._~:/?#@!$&\'()*+,;=%-]+')
        self.mtp_regex = re.compile(r'(?:https://t\.me/proxy\?|tg://proxy\?)?server=([a-zA-Z0-9.-]+)&port=(\d+)&secret=([a-zA-Z0-9_\-%=]+)', re.IGNORECASE)

    @staticmethod
    def is_public_ip(ip):
        try:
            parts = [int(p) for p in ip.split('.')]
            if len(parts) != 4 or not all(0 <= p <= 255 for p in parts): return False
            if parts[0] in (0, 10, 127): return False
            if parts[0] == 172 and 16 <= parts[1] <= 31: return False
            if parts[0] == 192 and parts[1] == 168: return False
            if parts[0] == 169 and parts[1] == 254: return False
            return True
        except ValueError:
            return False

    @staticmethod
    def safe_b64decode(data):
        data = data.strip().replace(r'\s', '')
        padding = len(data) % 4
        if padding: 
            data += '=' * (4 - padding)
        try:
            return base64.b64decode(data).decode('utf-8', errors='ignore')
        except Exception:
            return ""

    def fetch_url(self, url, category, retries=2):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=8) as response:
                    return response.read().decode('utf-8', errors='ignore'), category
            except Exception:
                if attempt < retries - 1:
                    time.sleep(1)
        return "", category

    def process_text(self, text, category):
        matches = []
        if category == 'mtproto':
            for match in self.mtp_regex.finditer(text):
                server, port, secret = match.groups()
                if 32 <= len(secret) <= 34 and not secret.lower().startswith('ee'):
                    matches.append(f"tg://proxy?server={server}&port={port}&secret={secret}")
        
        elif category == 'v2ray':
            decoded_text = text
            if re.match(r'^[a-zA-Z0-9+/=\s\n\r]+$', text.strip()) and len(text.strip()) > 50:
                decoded = self.safe_b64decode(text)
                if decoded: decoded_text = decoded
            matches = self.v2_regex.findall(decoded_text)
            
        else:
            raw_matches = self.ip_regex.findall(text)
            for ip_str in raw_matches:
                ip, port = ip_str.split(':')
                if int(port) <= 65535 and self.is_public_ip(ip):
                    matches.append(ip_str)
                    
        return matches

# --- V10.0 LIVE CHECKER MODULE ---
def check_proxy_tcp(proxy):
    """Sends a fast TCP ping to see if the proxy port is open and alive."""
    try:
        if "://" not in proxy:
            ip, port = proxy.split(':')
            socket.create_connection((ip, int(port)), timeout=3.0)
            return proxy, True
            
        elif "tg://proxy" in proxy:
            server = re.search(r'server=([^&]+)', proxy).group(1)
            port = re.search(r'port=(\d+)', proxy).group(1)
            socket.create_connection((server, int(port)), timeout=3.0)
            return proxy, True
            
        else:
            return proxy, True 
            
    except Exception:
        return proxy, False

# --- V10.0 AUTO CLEANUP MODULE ---
def cleanup_old_files(days=3):
    """Deletes proxy files older than specified days to prevent directory bloat."""
    cutoff = datetime.now() - timedelta(days=days)
    deleted_count = 0
    patterns = ['Silverbullet_Proxies_*.txt', 'Silverbullet_Proxies_*.json', 'Silverbullet_Proxies_*.csv']
    
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            try:
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if file_time < cutoff:
                    os.remove(filepath)
                    deleted_count += 1
            except Exception:
                pass
    return deleted_count

# --- UI & EXECUTION ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = fr"""{C.NEON}{C.BOLD}
 ███████╗██╗██╗     ██╗   ██╗███████╗██████╗ 
 ██╔════╝██║██║     ██║   ██║██╔════╝██╔══██╗
 ███████╗██║██║     ██║   ██║█████╗  ██████╔╝
 ╚════██║██║██║     ╚██╗ ██╔╝██╔══╝  ██╔══██╗
 ███████║██║███████╗ ╚████╔╝ ███████╗██║  ██║
 ╚══════╝╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
 ██████╗ ██╗   ██╗██╗     ██╗     ███████╗████████╗
 ██╔══██╗██║   ██║██║     ██║     ██╔════╝╚══██╔══╝
 ██████╔╝██║   ██║██║     ██║     █████╗     ██║  
 ██╔══██╗██║   ██║██║     ██║     ██╔══╝     ██║  
 ██████╔╝╚██████╔╝███████╗███████╗███████╗   ██║  
 ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝
                                                                            
{C.MAGENTA} :: PROXY ENGINE v10.0 :: {C.CYAN}THE MILESTONE RELEASE{C.RESET}
 {C.YELLOW}Developed by:{C.RESET} @Silverbullets_bot
 {C.YELLOW}Telegram:{C.RESET}     https://t.me/Silverbullets_bot
"""
    print(banner)

def draw_progress_bar(completed, total, bar_length=40):
    percent = float(completed) / total
    arrow = '█' * int(round(percent * bar_length))
    spaces = '░' * (bar_length - len(arrow))
    sys.stdout.write(f"\r {C.BOLD}{C.MAGENTA}[{C.NEON}{arrow}{C.DARK}{spaces}{C.MAGENTA}]{C.RESET} {int(percent * 100)}%  {C.YELLOW}({completed}/{total} clusters){C.RESET}")
    sys.stdout.flush()

def draw_checker_bar(completed, total, alive, bar_length=35):
    percent = float(completed) / total
    arrow = '█' * int(round(percent * bar_length))
    spaces = '░' * (bar_length - len(arrow))
    sys.stdout.write(f"\r {C.BOLD}{C.YELLOW}[{C.NEON}{arrow}{C.DARK}{spaces}{C.YELLOW}]{C.RESET} {int(percent * 100)}% {C.CYAN}(Tested: {completed} | Alive: {C.NEON}{alive}{C.CYAN}){C.RESET}")
    sys.stdout.flush()

def sort_key(item):
    ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', item)
    if ip_match:
        return (0, tuple(int(x) for x in ip_match.group(0).split('.')), item)
    return (1, (), item)

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
    
    choice = input(f" {C.MAGENTA}>{C.RESET} Enter your choice (1-6): ").strip()
    
    print()
    check_choice = input(f" {C.MAGENTA}>{C.RESET} Run Live TCP Ping to drop dead proxies? (y/n): ").strip().lower()
    run_checker = check_choice == 'y'
    
    clean_choice = input(f" {C.MAGENTA}>{C.RESET} Auto-delete proxy files older than 3 days? (y/n): ").strip().lower()
    if clean_choice == 'y':
        removed = cleanup_old_files(days=3)
        if removed > 0:
            print(f" {C.NEON}[✓] Cleaned up {removed} old file(s).{C.RESET}")
        else:
            print(f" {C.DARK}[i] No old files needed cleaning.{C.RESET}")

    options = {
        '1': list(SOURCES.keys()), '2': ['http'], '3': ['socks4'],
        '4': ['socks5'], '5': ['mtproto'], '6': ['v2ray']
    }
    
    targets = options.get(choice, list(SOURCES.keys()))
    tasks = [(url, cat) for cat in targets for url in SOURCES[cat]]
    
    engine = ProxyEngineV10()
    max_threads = min(32, (os.cpu_count() or 1) * 4 + 10)
    
    print(f"\n{C.BOLD}{C.NEON}[+]{C.RESET} Phase 1: Handshaking with {len(tasks)} target nodes...\n")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(engine.fetch_url, url, cat): (url, cat) for url, cat in tasks}
        
        completed = 0
        draw_progress_bar(0, len(tasks))
        for future in concurrent.futures.as_completed(future_to_url):
            text, cat = future.result()
            if text:
                proxies = engine.process_text(text, cat)
                for p in proxies:
                    if p not in engine.master_set:
                        engine.master_set.add(p)
                        engine.counts[cat] += 1
            completed += 1
            draw_progress_bar(completed, len(tasks))

    scrape_time = round(time.time() - start_time, 2)
    print(f"\n\n{C.BOLD}{C.NEON}[+]{C.RESET} Target scraping complete in {scrape_time}s. ({len(engine.master_set)} Found)")

    if not engine.master_set:
        print(f"\n{C.RED}[!] NO PROXIES FOUND. Target lists completely unreachable.{C.RESET}")
        return

    # --- PHASE 2: CHECKER ---
    if run_checker:
        print(f"\n{C.BOLD}{C.NEON}[+]{C.RESET} Phase 2: TCP Ping testing {len(engine.master_set)} nodes...\n")
        working_proxies = set()
        alive_count = 0
        total_to_check = len(engine.master_set)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=300) as checker_executor:
            future_to_proxy = {checker_executor.submit(check_proxy_tcp, p): p for p in engine.master_set}
            
            checked = 0
            draw_checker_bar(0, total_to_check, 0)
            
            for future in concurrent.futures.as_completed(future_to_proxy):
                p, is_alive = future.result()
                if is_alive:
                    working_proxies.add(p)
                    alive_count += 1
                checked += 1
                draw_checker_bar(checked, total_to_check, alive_count)
        
        engine.master_set = working_proxies
        print(f"\n\n{C.BOLD}{C.NEON}[+]{C.RESET} Filtering complete. {len(working_proxies)} proxies are alive.")

    sorted_proxies = sorted(list(engine.master_set), key=sort_key)
    
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    txt_filename = f"Silverbullet_Proxies_{timestamp}.txt"
    json_filename = f"Silverbullet_Proxies_{timestamp}.json"
    csv_filename = f"Silverbullet_Proxies_{timestamp}.csv"

    # TXT Export
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_proxies))
    
    # JSON Export (v10: Rich Metadata Format)
    json_export_data = {
        "metadata": {
            "engine_version": "10.0",
            "scraped_at": timestamp,
            "live_checked": run_checker,
            "total_proxies": len(sorted_proxies)
        },
        "proxies": sorted_proxies
    }
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_export_data, f, indent=2)
        
    # CSV Export
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Proxy", "Estimated_Protocol"])
        for p in sorted_proxies:
            protocol_guess = "v2ray/mtproto" if "://" in p else "http/socks"
            writer.writerow([p, protocol_guess])

    print(f"\n{C.MAGENTA} ┌──────────────────────────────────────────┐{C.RESET}")
    print(f"{C.MAGENTA} │ {C.BOLD}{C.NEON}V10.0 FINAL STATISTICS{C.RESET}{C.MAGENTA}                   │{C.RESET}")
    print(f"{C.MAGENTA} ├──────────────────────────────────────────┤{C.RESET}")
    print(f"{C.MAGENTA} │ {C.BOLD}TOTAL RETAINED{C.RESET} : {C.NEON}{len(engine.master_set):<23}{C.MAGENTA} │{C.RESET}")
    print(f"{C.MAGENTA} └──────────────────────────────────────────┘{C.RESET}")

    print(f"\n{C.BOLD}{C.NEON}[ SUCCESS ]{C.RESET} Output saved securely to local directory:")
    print(f"  {C.CYAN}→{C.RESET} {txt_filename}")
    print(f"  {C.CYAN}→{C.RESET} {json_filename}")
    print(f"  {C.CYAN}→{C.RESET} {csv_filename}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C.RED}[!] Operation aborted by user.{C.RESET}\n")
        sys.exit(0)
