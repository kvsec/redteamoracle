"""
redteamoracle Pentest Modules
Sample modules that look very professional until the oracle decides otherwise.
"""

from __future__ import annotations

import random
import time
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

console = Console()


# ---------------------------------------------------------------------------
# Base Module
# ---------------------------------------------------------------------------

class BaseModule:
    """Every module inherits this. Every module is equally at mercy of the oracle."""

    name: str = "base"
    description: str = "Base module"
    author: str = "The Oracle"

    def run(self, target: str, **kwargs) -> None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Recon Module
# ---------------------------------------------------------------------------

class ReconModule(BaseModule):
    """
    Advanced Reconnaissance Module™
    Totally real recon. Not fake at all.
    """

    name = "recon"
    description = "Passive and active reconnaissance against a target"
    author = "The Oracle"

    FAKE_SUBDOMAINS = [
        "dev", "staging", "admin", "api", "mail", "vpn", "remote",
        "test", "old", "backup", "portal", "internal", "db", "jenkins",
        "gitlab", "jira", "confluence", "legacy", "beta", "support",
    ]

    FAKE_TECH = [
        "Apache/2.4.51", "nginx/1.18.0", "Microsoft-IIS/10.0",
        "Express/4.18.2", "Werkzeug/2.3.0", "Tomcat/9.0.65",
    ]

    def run(self, target: str, **kwargs) -> None:
        console.print(f"\n[bold cyan]🔍 Recon Module[/bold cyan] → target: [yellow]{target}[/yellow]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Enumerating subdomains...", total=None)
            time.sleep(random.uniform(1.5, 2.5))
            progress.update(task, description="[cyan]Querying passive DNS...")
            time.sleep(random.uniform(0.8, 1.5))
            progress.update(task, description="[cyan]Checking certificate transparency logs...")
            time.sleep(random.uniform(0.5, 1.2))
            progress.update(task, description="[cyan]Fingerprinting web technologies...")
            time.sleep(random.uniform(0.6, 1.0))
            progress.remove_task(task)

        # Fake results
        found = random.sample(self.FAKE_SUBDOMAINS, random.randint(4, 8))
        tech = random.choice(self.FAKE_TECH)

        table = Table(title=f"Recon Results — {target}", box=box.ROUNDED, border_style="cyan")
        table.add_column("Subdomain", style="green")
        table.add_column("IP", style="yellow")
        table.add_column("Status", style="white")

        for sub in found:
            ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            status = random.choice(["🟢 Online", "🟡 Filtered", "🔴 Offline"])
            table.add_row(f"{sub}.{target}", ip, status)

        console.print(table)
        console.print(f"\n[dim]Detected server: {tech}[/dim]")
        console.print(f"[dim]Found {len(found)} subdomains. Some of them might even be real.[/dim]\n")


# ---------------------------------------------------------------------------
# Port Scanner Module
# ---------------------------------------------------------------------------

class ScannerModule(BaseModule):
    """
    Advanced Port Scanner™
    Like nmap, but slower and with worse accuracy.
    """

    name = "scan"
    description = "TCP/UDP port scanner with service detection"
    author = "The Oracle"

    COMMON_PORTS = {
        21: ("FTP", "vsftpd 3.0.3"),
        22: ("SSH", "OpenSSH 8.2p1"),
        23: ("Telnet", "Linux telnetd"),
        25: ("SMTP", "Postfix smtpd"),
        53: ("DNS", "ISC BIND 9.16"),
        80: ("HTTP", "Apache httpd 2.4.51"),
        443: ("HTTPS", "Apache httpd 2.4.51"),
        445: ("SMB", "Samba 4.13.2"),
        3306: ("MySQL", "MySQL 8.0.27"),
        3389: ("RDP", "xrdp 0.9.17"),
        5432: ("PostgreSQL", "PostgreSQL 13.4"),
        6379: ("Redis", "Redis 6.2.6"),
        8080: ("HTTP-alt", "Jetty 9.4.43"),
        8443: ("HTTPS-alt", "nginx 1.18.0"),
        27017: ("MongoDB", "MongoDB 5.0.3"),
    }

    def run(self, target: str, ports: str = "top-100", **kwargs) -> None:
        console.print(f"\n[bold cyan]🔌 Port Scanner Module[/bold cyan] → target: [yellow]{target}[/yellow]\n")

        port_list = list(self.COMMON_PORTS.keys())
        to_scan = random.sample(port_list, min(len(port_list), 10))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Scanning ports...", total=len(to_scan))
            for port in to_scan:
                time.sleep(random.uniform(0.15, 0.4))
                progress.advance(task)

        # Show results
        open_ports = random.sample(to_scan, random.randint(2, 5))

        table = Table(title=f"Scan Results — {target}", box=box.ROUNDED, border_style="cyan")
        table.add_column("Port", style="bold white", justify="right")
        table.add_column("State", style="white")
        table.add_column("Service", style="cyan")
        table.add_column("Version", style="dim")

        for port in sorted(to_scan):
            state = "[green]open[/green]" if port in open_ports else "[red]closed[/red]"
            service, version = self.COMMON_PORTS[port]
            version_str = version if port in open_ports else ""
            table.add_row(str(port), state, service, version_str)

        console.print(table)
        console.print(
            f"\n[dim]Scanned {len(to_scan)} ports. Found {len(open_ports)} open. "
            f"Real nmap would be faster. Just saying.[/dim]\n"
        )


# ---------------------------------------------------------------------------
# Exploit Module
# ---------------------------------------------------------------------------

class ExploitModule(BaseModule):
    """
    Advanced Exploit Framework™
    Warning: Exploits are purely theoretical and entirely made up.
    """

    name = "exploit"
    description = "Automated vulnerability exploitation (educational purposes only)"
    author = "The Oracle"

    FAKE_CVES = [
        ("CVE-2021-44228", "Log4Shell", "Critical", 10.0),
        ("CVE-2021-34527", "PrintNightmare", "Critical", 8.8),
        ("CVE-2022-26134", "Confluence RCE", "Critical", 9.8),
        ("CVE-2022-22965", "Spring4Shell", "Critical", 9.8),
        ("CVE-2023-23397", "Outlook 0-click", "Critical", 9.8),
        ("CVE-2023-44487", "HTTP/2 Rapid Reset", "High", 7.5),
        ("CVE-2024-3400", "PAN-OS RCE", "Critical", 10.0),
    ]

    FAKE_OUTCOMES = [
        "⚡ Exploit launched successfully... or did it?",
        "🎯 Session opened. Probably.",
        "💥 Target responded with something. Unclear what.",
        "🔓 Authentication bypassed. Server confused.",
        "📦 Payload delivered. Target is thinking about it.",
    ]

    def run(self, target: str, cve: Optional[str] = None, **kwargs) -> None:
        console.print(f"\n[bold red]💣 Exploit Module[/bold red] → target: [yellow]{target}[/yellow]\n")
        console.print("[dim yellow]⚠  EDUCATIONAL/AUTHORIZED USE ONLY ⚠[/dim yellow]\n")

        # Vuln scan phase
        console.print("[cyan]Phase 1: Vulnerability Assessment[/cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Scanning for vulnerabilities...", total=None)
            time.sleep(random.uniform(2.0, 3.5))
            progress.update(task, description="[cyan]Correlating CVE database...")
            time.sleep(random.uniform(0.8, 1.5))
            progress.remove_task(task)

        # Show fake vulns
        found_vulns = random.sample(self.FAKE_CVES, random.randint(1, 3))

        vuln_table = Table(title="Potential Vulnerabilities", box=box.SIMPLE_HEAVY, border_style="yellow")
        vuln_table.add_column("CVE", style="bold red")
        vuln_table.add_column("Name", style="white")
        vuln_table.add_column("Severity", style="bold")
        vuln_table.add_column("CVSS", justify="right")

        for cve_id, name, severity, cvss in found_vulns:
            color = "red" if cvss >= 9.0 else "yellow"
            vuln_table.add_row(cve_id, name, f"[{color}]{severity}[/{color}]", f"[{color}]{cvss}[/{color}]")

        console.print(vuln_table)

        # Pick one to "exploit"
        target_cve, target_name, _, _ = random.choice(found_vulns)
        console.print(f"\n[cyan]Phase 2: Exploitation → [bold]{target_cve} ({target_name})[/bold][/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[red]Preparing exploit...", total=None)
            time.sleep(random.uniform(1.0, 2.0))
            progress.update(task, description="[red]Sending payload...")
            time.sleep(random.uniform(0.8, 1.5))
            progress.update(task, description="[red]Awaiting response...")
            time.sleep(random.uniform(1.0, 2.0))
            progress.remove_task(task)

        outcome = random.choice(self.FAKE_OUTCOMES)
        console.print(f"\n[bold green]{outcome}[/bold green]")
        console.print(
            "[dim]Note: This module is entirely fictional. "
            "No systems were harmed in the making of this output.[/dim]\n"
        )


# ---------------------------------------------------------------------------
# OSINT Module
# ---------------------------------------------------------------------------

class OSINTModule(BaseModule):
    """
    OSINT Module™
    Open Source Intelligence gathering. Very open. Very source.
    """

    name = "osint"
    description = "Open-source intelligence gathering and correlation"
    author = "The Oracle"

    def run(self, target: str, **kwargs) -> None:
        console.print(f"\n[bold cyan]🕵️  OSINT Module[/bold cyan] → target: [yellow]{target}[/yellow]\n")

        sources = [
            "Shodan",
            "Censys",
            "Hunter.io",
            "WHOIS records",
            "LinkedIn (lurking)",
            "GitHub (searching for secrets)",
            "Pastebin (classic)",
            "Google Dorks",
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Querying sources...", total=len(sources))
            for source in sources:
                progress.update(task, description=f"[cyan]Querying {source}...")
                time.sleep(random.uniform(0.3, 0.8))
                progress.advance(task)

        findings = [
            f"📧  {random.randint(3, 47)} email addresses exposed",
            f"🔑  {random.randint(1, 5)} potential API keys found in public repos",
            f"📁  {random.randint(2, 12)} documents with metadata",
            f"👤  {random.randint(5, 30)} employee LinkedIn profiles",
            f"🌐  {random.randint(1, 6)} IP ranges identified",
            f"🔓  {random.randint(0, 3)} credentials in paste sites",
        ]

        console.print("\n[bold]OSINT Findings:[/bold]")
        for finding in random.sample(findings, random.randint(3, 5)):
            console.print(f"  {finding}")
        console.print(
            f"\n[dim]Report generated. Correlation confidence: {random.randint(42, 97)}%[/dim]\n"
        )


# ---------------------------------------------------------------------------
# Module Registry
# ---------------------------------------------------------------------------

ALL_MODULES: dict[str, type[BaseModule]] = {
    "recon": ReconModule,
    "scan": ScannerModule,
    "exploit": ExploitModule,
    "osint": OSINTModule,
}


def get_module(name: str) -> Optional[BaseModule]:
    cls = ALL_MODULES.get(name.lower())
    if cls:
        return cls()
    return None


def list_modules() -> list[BaseModule]:
    return [cls() for cls in ALL_MODULES.values()]
