---
name: travel-executor
description: Flight search and booking via MCP. ALWAYS read this skill first for flight operations.
---

# ⚠️ TRAVEL EXECUTOR - READ FIRST ⚠️

**When user asks about flights, ALWAYS read this skill file first**

## To Search Flights (DO NOT BOOK unless user explicitly asks)
```bash
/home/kiara/.nvm/versions/node/v22.22.0/bin/mcporter call travel-executor.search_flights origin=BOM destination=CDG date=2026-06-15 --config /home/kiara/.config/mcporter.json
```

**STOP HERE unless user asks to book!**

## To Book a Flight (ONLY if user explicitly requests booking)

### Step 1: Get ArmorIQ intent token
```bash
/home/kiara/.nvm/versions/node/v22.22.0/bin/mcporter call travel-executor.get_booking_intent_token item_id=FLIGHT_ID price=PRICE --config /home/kiara/.config/mcporter.json
```

### Step 2: Book with the token
```bash
/home/kiara/.nvm/versions/node/v22.22.0/bin/mcporter call travel-executor.book_travel item_id=FLIGHT_ID price=PRICE armor_token=TOKEN_FROM_STEP1 --config /home/kiara/.config/mcporter.json
```

## Important Rules:
- ONLY search if user asks to search
- ONLY book if user explicitly asks to book
- Get intent token BEFORE booking
- Use `exec` tool to run mcporter commands
- NEVER use web_search for flights

## IATA Codes:
BOM=Mumbai, CDG=Paris, LON=London, JFK=New York
