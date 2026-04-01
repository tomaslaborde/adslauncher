# Meta Ads Project Context for AI Agents (Claude Code)

This document provides system instructions for any AI coding assistant (e.g., Claude Code, Cursor) interacting with this repository. Read this context before modifying any logic or executing campaigns.

## 1. Project Architecture

This project is a modular Python CLI dedicated to automating Meta Graph API interactions. It creates Live Ads (Campaigns -> Ad Sets -> Creatives -> Ads).

- `/src/config/settings.py` - Manages `.env` loading and secure SDK initialization.
- `/src/services/` - Contains decoupled logic for different Meta entity creations (campaigns, ad sets, search queries, creatives).
- `/src/main.py` - The central orchestrator file.
- `/creates/ad_copy.csv` - The "Database" containing variations of Headlines, Descriptions, and Call To Actions.
- `/Creatives/` - The directory holding raw visual assets (images/videos) to be uploaded to Meta.

## 2. Environment Setup Commands

If the user asks you to initialize or fix the environment, run:

```bash
/usr/local/bin/python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Automation Execution Guidelines

When the user asks you to "Run an Ad", "Publish Content", or "Start a Campaign", follow these exact steps:

1. **Parse the User's Intent**: Identify which row from `creates/ad_copy.csv` the user wants to use based on their conversational prompt (or default to the first row).
2. **Find the Asset**: Identify the requested image inside the `Creatives/` folder.
3. **Modify the Orchestrator**: Update `src/main.py` to point to the correct CSV row variables and the correct `image_hash` upload path. Do NOT modify the core service files unless requested to change complex targeting logic.
4. **Execute**: Do a dry run review, then execute the live publisher natively via:
`./.venv/bin/python src/main.py`

## 5. Campaign Brief via Chat

The user sends campaign details directly in the chat. When the user provides a brief, extract the following and update `src/main.py` accordingly before executing:

- **Creative**: Download or reference the image from the provided Google Drive / URL link. Place it in `/Creatives/` and update the `image_file` path in `main.py`.
- **Copy**: Headline and description provided in chat → update `creates/ad_copy.csv` with these values (or hardcode directly in `main.py` if only one variation).
- **Campaign name**: Update the `campaign_name` variable or reuse existing campaign if one is active.
- **Budget**: Daily budget in ARS → convert to centavos (× 100) for the API.
- **Audience / Targeting**: Gender, age range, interests, platforms (FB/IG) → update `create_adset()` call in `main.py`.
- **Status**: Default to `PAUSED` unless user explicitly says to activate.

Always confirm what you understood from the brief before executing.

## 4. Coding Conventions

- **Strict Modularity**: Maintain the "One File, One Responsibility" architectural rule. Never bloat `main.py` with Meta SDK specific API definitions. All endpoints go into `src/services/`.
- Ensure Ad Set `status` remains `AdSet.Status.paused` during testing to prevent accidental ad spend for the user.
