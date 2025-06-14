#!/usr/bin/env python3

import requests
import os
import time
import json
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
from urllib.parse import urlparse

console = Console()

def banner():
    ascii_art = Text("""\
███╗   ██╗███████╗ ██████╗ ██████╗ ██╗  ██╗
████╗  ██║██╔════╝██╔════╝██╔═══██╗██║ ██╔╝
██╔██╗ ██║█████╗  ██║     ██║   ██║█████╔╝ 
██║╚██╗██║██╔══╝  ██║     ██║   ██║██╔═██╗ 
██║ ╚████║███████╗╚██████╗╚██████╔╝██║  ██╗
╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝

[bold cyan]Made in MD Abdullah[/bold cyan]
""", style="bold green")
    console.print(Panel(ascii_art, title="[bold yellow]My Custom Banner[/bold yellow]", expand=False))


def tor_status():
    proxies = {'http': 'socks5h://127.0.0.1:9050',
               'https': 'socks5h://127.0.0.1:9050'}
    try:
        r = requests.get("http://check.torproject.org", proxies=proxies, timeout=10)
        return "Congratulations" in r.text
    except requests.exceptions.RequestException:
        return False


def scan_onion(url, keywords):
    url = url if url.startswith("http") else f"http://{url}"
    proxies = {'http': 'socks5h://127.0.0.1:9050',
               'https': 'socks5h://127.0.0.1:9050'}
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        res = requests.get(url, proxies=proxies, headers=headers, timeout=25)
        content = res.text
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No Title"
        links = [a['href'] for a in soup.find_all('a', href=True) if ".onion" in a['href']]
        found_keywords = [k for k in keywords if k.lower() in content.lower()]

        level = "LOW"
        if len(found_keywords) >= 6:
            level = "CRITICAL"
        elif len(found_keywords) >= 3:
            level = "HIGH"
        elif found_keywords:
            level = "MEDIUM"

        table = Table(title=f"Scan Result: {urlparse(url).netloc}")
        table.add_column("Status", style="green")
        table.add_column("Title", style="cyan")
        table.add_column("Size", style="magenta")
        table.add_column("Keywords", style="red")
        table.add_column("Danger", style="yellow")

        table.add_row(
            str(res.status_code),
            title,
            f"{len(content)//1024} KB",
            ", ".join(found_keywords) or "None",
            level
        )
        console.print(table)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"scan_logs/scan_{timestamp}.json"
        os.makedirs("scan_logs", exist_ok=True)
        with open(log_path, "w") as f:
            json.dump({"url": url, "title": title, "danger": level, "keywords": found_keywords}, f, indent=2)
        console.print(f"[bold blue]✓ Log saved:[/bold blue] {log_path}")

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ Failed to scan {url} - {e}[/bold red]")


def menu():
    banner()  # ব্যানার দেখাবে মেনু শুরুতেই
    if not tor_status():
        console.print("[yellow]⚠ Tor not active. Starting...[/yellow]")
        os.system("tor &")
        time.sleep(7)
        if not tor_status():
            console.print("[bold red]❌ Tor could not be started.[/bold red]")
            return

    default_keywords = ["admin", "login", "bitcoin", "dark", "market", "hack", "illegal"]

    while True:
        console.print("""
[bold cyan]--- MENU ---[/bold cyan]
[green]1.[/green] Scan 1 .onion URL
[green]2.[/green] Scan Multiple from File
[green]3.[/green] Exit
        """)
        ch = input("Select: ").strip()
        if ch == "1":
            url = input(".onion URL: ").strip()
            scan_onion(url, default_keywords)
        elif ch == "2":
            file = input("Path to .txt file: ").strip()
            if not os.path.exists(file):
                console.print("[red]File not found[/red]")
                continue
            with open(file) as f:
                for line in f:
                    if line.strip():
                        scan_onion(line.strip(), default_keywords)
                        time.sleep(2)
        elif ch == "3":
            console.print("[green]Exiting...[/green]")
            break
        else:
            console.print("[yellow]Invalid choice[/yellow]")


if __name__ == "__main__":
    menu()
