

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

# Path for the 24h lockout state
STATE_FILE = Path.home() / ".redteamoracle" / "oracle_state.json"

# Probability of the oracle deciding it's not your day (0.0 - 1.0)
DOOM_PROBABILITY = 0.42  # Carefully chosen by the oracle

DOOM_MESSAGES = [
    "It's not your day.",
    "The stars are misaligned. Try again tomorrow.",
    "Mercury is in retrograde. Obviously.",
    "The oracle has consulted the ancient logs. You shall not pass.",
    "Today is a good day to touch some grass instead.",
    "The dice have spoken. They said no.",
    "Error 403: Destiny Forbidden.",
    "The oracle rolled a 1. Critical failure.",
    "Nope. Just… nope.",
    "The vibes are off. Come back tomorrow.",
]

NOT_PENTEST_DAY_MESSAGES = [
    "And frankly, it's not the best day for a pentest either.",
    "Your target is also having a bad day, so it evens out.",
    "The SOC team is probably awake today anyway.",
    "Your shells would reverse into the wrong IP anyway.",
    "The CVEs you need were patched this morning. Trust.",
    "Your Burp Suite would have crashed in 3 minutes. You're welcome.",
    "Even your wordlists feel uninspired today.",
]

LAZY_QUESTIONS = [
    "What is the color of the sky?",
    "How many legs does a dog have?",
    "What sound does a cow make?",
    "Is water wet?",
    "What comes after the number 2?",
    "If you have 1 apple and eat it, how many apples do you have?",
    "What is 1 + 1?",
    "Does the sun rise in the morning or at night?",
    "What shape is a circle?",
    "How many days are in a week?",
    "If it's raining outside, is it wet or dry?",
    "What do you call a male chicken?",
    "What color is a red traffic light?",
    "In which direction does the Earth spin? (Don't overthink it.)",
    "What do you put in a toaster to make toast?",
]


def _load_state() -> dict:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _is_locked_out() -> Optional[datetime]:
    """Returns the lockout expiry time if the user is locked out, else None."""
    state = _load_state()
    if "locked_until" in state:
        locked_until = datetime.fromisoformat(state["locked_until"])
        if datetime.now() < locked_until:
            return locked_until
        else:
            # Lockout expired, clean it up
            del state["locked_until"]
            _save_state(state)
    return None


def _set_lockout() -> datetime:
    """Sets a 24-hour lockout and returns the expiry time."""
    state = _load_state()
    locked_until = datetime.now() + timedelta(hours=24)
    state["locked_until"] = locked_until.isoformat()
    _save_state(state)
    return locked_until


def _clear_lockout() -> None:
    """Dev escape hatch — clears lockout."""
    state = _load_state()
    state.pop("locked_until", None)
    _save_state(state)


def _roll_dice() -> bool:
    """Returns True if the oracle decides it's NOT your day."""
    return random.random() < DOOM_PROBABILITY


def _animate_roll() -> None:
    """Visual dice roll animation."""
    import time

    dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    console.print("\n[dim]The Oracle prepares to roll...[/dim]")
    time.sleep(0.6)

    for i in range(10):
        face = random.choice(dice_faces)
        console.print(f"\r[bold yellow]  {face}  Rolling...  {face}[/bold yellow]", end="")
        time.sleep(0.08 + i * 0.015)

    console.print()  # newline after animation


def _display_doom(ai_answer: str) -> None:
    doom_msg = random.choice(DOOM_MESSAGES)
    pentest_msg = random.choice(NOT_PENTEST_DAY_MESSAGES)

    console.print()
    console.print(
        Panel.fit(
            f"[bold red]⚠  THE ORACLE HAS SPOKEN  ⚠[/bold red]\n\n"
            f"[red]{doom_msg}[/red]\n"
            f"[dim red]{pentest_msg}[/dim red]",
            box=box.DOUBLE,
            border_style="red",
            padding=(1, 4),
        )
    )


def _display_ai_question(question: str, answer: str) -> None:
    console.print()
    console.print(
        Panel(
            f"[bold yellow]📜  The Oracle's Final Inquiry[/bold yellow]\n\n"
            f"[italic white]{question}[/italic white]\n\n"
            f"[dim]The AI has pondered this deeply and responded:[/dim]\n"
            f"[green]{answer}[/green]",
            box=box.ROUNDED,
            border_style="yellow",
            padding=(1, 3),
        )
    )


def _display_lockout(locked_until: datetime) -> None:
    remaining = locked_until - datetime.now()
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes = remainder // 60

    console.print()
    console.print(
        Panel.fit(
            f"[bold red]🔒  ACCESS DENIED  🔒[/bold red]\n\n"
            f"[red]The Oracle has already judged you.\n"
            f"You are locked out for[/red] [bold white]{hours}h {minutes}m[/bold white] [red]more.[/red]\n\n"
            f"[dim]Lockout expires: {locked_until.strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n\n"
            f"[dim italic]Use this time to read a book. Maybe not a hacking one.[/dim italic]",
            box=box.HEAVY,
            border_style="red",
            padding=(1, 4),
        )
    )


def consult_oracle(ai_provider) -> bool:
    """
    The main oracle ritual.

    Returns True if the user may proceed, False if they are doomed.
    Also enforces existing lockouts from previous doom rolls.
    """
    # Check if already locked out from a previous session
    locked_until = _is_locked_out()
    if locked_until:
        _display_lockout(locked_until)
        return False

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]🔮  Consulting the Oracle...[/bold cyan]\n"
            "[dim]The Oracle will now determine if today is worthy of your l33t skills.[/dim]",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    _animate_roll()

    doomed = _roll_dice()

    if not doomed:
        # Lucky day
        console.print()
        lucky_face = "⚅"
        console.print(
            Panel.fit(
                f"[bold green]{lucky_face}  THE ORACLE SMILES UPON YOU  {lucky_face}[/bold green]\n\n"
                "[green]Today is your day. The stars align.\n"
                "Go forth and enumerate things.[/green]\n\n"
                "[dim](Don't mess it up)[/dim]",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 3),
            )
        )
        return True

    # DOOM PATH
    question = random.choice(LAZY_QUESTIONS)

    console.print(f"\n[dim yellow]The Oracle is consulting the AI about something very important...[/dim yellow]")

    try:
        answer = ai_provider.ask(question)
    except Exception as e:
        answer = f"[The AI was also having a bad day: {e}]"

    _display_doom(answer)
    _display_ai_question(question, answer)

    # Lock them out
    locked_until = _set_lockout()

    console.print()
    console.print(
        Panel.fit(
            f"[bold red]You are now locked out for 24 hours.[/bold red]\n"
            f"[dim]Lockout expires: {locked_until.strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="red",
            padding=(0, 2),
        )
    )

    return False
