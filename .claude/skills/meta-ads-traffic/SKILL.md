---
name: meta-ads-traffic
description: Create and publish a Meta (Facebook/Instagram) traffic ad campaign from a name, CSV row, and image. Handles the full pipeline — campaign, ad set, creative, and final ad.
argument-hint: [ad-name]
allowed-tools: Read, Edit, Bash, Glob
---

# Meta Traffic Ad Creator

Create a live Meta traffic ad (OUTCOME_TRAFFIC) by updating `src/main.py` and executing the pipeline.

## Inputs to extract from the user's message

| Input | Description | Default |
|---|---|---|
| **Ad name** | Name for the campaign and final ad | `$ARGUMENTS` (required) |
| **CSV row** | Which row from `creates/ad_copy.csv` to use (1-based, excluding header) | Row 1 |
| **Image** | Filename inside `Creatives/` folder | `image.png` |
| **Interest query** | Targeting interest keyword for Meta search | `"Mental health"` |
| **Daily budget** | Budget in cents (e.g. 1500 = $15/day) | `1500` |
| **Platforms** | List of platforms | `['facebook', 'instagram']` |

## Steps

1. **Read the CSV** at `creates/ad_copy.csv` to confirm the requested row exists.
2. **Confirm the image** exists in `Creatives/` using Glob.
3. **Read `src/main.py`** to get the current state.
4. **Edit `src/main.py`** with the user's inputs:
   - Set the campaign name on the `create_campaign()` call.
   - Set the final ad name on the `create_final_ad()` call.
   - If a non-default CSV row was requested, update the CSV reader logic to skip to the correct row.
   - If a different image was requested, update the `image_file` path.
   - If a different interest query was requested, update `target_query`.
   - If a different daily budget was requested, update `daily_budget`.
5. **Show the user a dry-run summary** with all the values that will be sent to Meta. Confirm the ad set status is `AdSet.Status.paused`.
6. **Execute the pipeline**:
   ```bash
   ./.venv/bin/python src/main.py
   ```
7. **Report the created entity IDs** (Campaign, Ad Set, Creative, Ad) back to the user.

## Safety rules

- The ad set status in `src/services/adset_service.py` MUST remain `AdSet.Status.paused`. Never change this.
- Do NOT modify any files in `src/services/` or `src/config/` — only edit `src/main.py`.
- If the `.env` is missing credentials, stop and tell the user instead of proceeding.
