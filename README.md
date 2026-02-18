# 🔮 RedTeamOracle

> *A totally agentic red team framework.*

---

## What is this?

RedTeamOracle is a **professional-grade** agentic penetration testing framework with:

- 🔍 **Recon** — Subdomain enumeration, passive DNS, cert transparency
- 🔌 **Scanner** — TCP/UDP port scanning with service detection
- 💣 **Exploit** — CVE-based automated exploitation (educational only)
- 🕵️  **OSINT** — Open-source intelligence gathering and correlation

And most importantly:

- 🔮 **The Oracle** — Rolls the dice every time you run the tool. If it's not your day, it will tell you, display the answer, and lock you out for **24 hours** if you are not eligible to continue.

## Installation

```bash
pipx install git+https://github.com/kvsec/redteamoracle
```

Or from source:
```bash
git clone https://github.com/kvsec/redteamoracle
cd redteamoracle
pipx install .
```

## Usage

```bash
# Check if the oracle approves of your existence today
redteamoracle oracle

# Run a module (oracle will be consulted first)
redteamoracle run recon --target example.com
redteamoracle run scan  --target 192.168.1.1
redteamoracle run osint --target example.com
redteamoracle run exploit --target example.com

# Check your lockout status
redteamoracle status

# List all modules
redteamoracle modules
```

## AI Providers

The oracle uses an AI backend to ask its important questions. Configure with `--provider`:

| Provider | Flag | Notes |
|---|---|---|
| Ollama | `--provider ollama` | Local, free, runs on your GPU |
| LM Studio | `--provider lmstudio` | Local, GUI, also free |
| ChatGPT | `--provider openai` | Set `OPENAI_API_KEY` env var |
| Claude | `--provider claude` | Set `ANTHROPIC_API_KEY` env var |
| Offline | `--provider offline` | Canned responses, always available |

### Examples

```bash
# Use Ollama with a specific model
redteamoracle --provider ollama --model mistral run recon --target example.com

# Use LM Studio on a custom port
redteamoracle --provider lmstudio --base-url http://localhost:5678 run scan --target 10.0.0.1

# Use ChatGPT
OPENAI_API_KEY=sk-... redteamoracle --provider openai run osint --target example.com

# Use Claude
ANTHROPIC_API_KEY=sk-ant-... redteamoracle --provider claude run exploit --target example.com
```

## Disclaimer

This tool is for **educational and authorized testing purposes only**. Real exploitation may occur. The oracle's decisions are final and binding in all parallel universes.

---

*"The oracle has spoken. You shall not pass. Come back tomorrow."*
