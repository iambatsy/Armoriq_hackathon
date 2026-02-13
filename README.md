
# ClaudiusMaximus - ArmorIQ Travel MCP Server

AI-powered travel booking with cryptographic intent verification via ArmorIQ.

## Architecture

- **MCP Server**: `executor/server.py` - FastMCP server for flight/hotel booking
- **ArmorIQ Integration**: Real-time intent token generation and verification
- **Amadeus API**: Live flight and hotel data
- **OpenClaw Agent**: AI orchestration via Telegram

## Setup

### 1. Install Dependencies
```bash
pip install fastmcp amadeus requests python-dotenv --break-system-packages
```

### 2. Configure Environment

Create `executor/.env`:
```env
AMADEUS_CLIENT_ID=your_amadeus_key
AMADEUS_CLIENT_SECRET=your_amadeus_secret
ARMORIQ_API_KEY=your_armoriq_key
```

### 3. Run MCP Server
update mcp.json accordingly
```bash
cd executor
python3 server.py
```


### 4. Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:
the example file that ive sent to you

Add skill file at `~/.openclaw/skills/travel-executor/SKILL.md` (see repo)

## ArmorIQ Integration

- **Endpoint**: `https://customer-iap.armoriq.ai/intent`
- **Dashboard**: `https://platform.armoriq.ai/dashboard`
- Generates cryptographic intent tokens before high-stakes actions
- Policy enforcement: $100k spending limit

## Demo

Message the Telegram bot:
```
search for flights from Mumbai to Paris on June 15 2026, then book the cheapest one
```

The system will:
1. Search Amadeus for real flights
2. Get ArmorIQ intent token (cryptographic approval)
3. Book with verified token
4. Enforce policy limits

## Links

- MCP Server: `executor/server.py`
- OpenClaw Config: `aiq-openclaw/` directory
- Live Demo: Telegram bot @YourBotName

