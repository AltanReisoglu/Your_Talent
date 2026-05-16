# Final Handoff Native n8n Pack

Import these files into n8n.

## Import order

1. Run `00_POSTGRES_SCHEMA.sql` in Postgres / Supabase SQL editor.
2. Import `01_WF_01_LEAD_SALES_NATIVE.json`.
3. Import `02_WF_02_CLIENT_PRODUCTION_NATIVE.json`.
4. Import `03_WF_03_APPROVAL_DELIVERY_INVOICE_NATIVE.json`.
5. Import `04_MAIN_OPERATIONS_DASHBOARD_NATIVE.json`.
6. Copy each child workflow production webhook URL into n8n env:
   - `WF01_SALES_WEBHOOK_URL`
   - `WF02_PRODUCTION_WEBHOOK_URL`
   - `WF03_APPROVAL_WEBHOOK_URL`
   - `DASHBOARD_WEBHOOK_URL`
7. Import `00_TELEGRAM_COMMAND_ROUTER.json`.

## Credentials / env required

- Telegram credential on router Telegram nodes.
- Postgres credential on every Postgres node.
- Gmail credential on Gmail nodes.
- Google Drive credential on Drive nodes.
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `APIFY_TOKEN`
- `APIFY_GOOGLE_MAPS_ACTOR_URL`
- `GOOGLE_DRIVE_OUTPUT_FOLDER_ID`
- `DEFAULT_OUTREACH_EMAIL` for testing outreach if scraped lead has no email field
- `DEFAULT_INVOICE_EMAIL` for testing invoice send if client email is not available

## Why router + child workflows

Telegram Bot API has one active webhook per bot. For n8n, the safest build is:

- one Telegram Trigger router
- three main child workflows called by webhook
- one dashboard read-model workflow

This preserves the handoff idea of one Telegram bot plus three main workflows without making three workflows fight over the same Telegram bot webhook.

## Commands

```text
/sales find <niche> <location>
/sales review
/sales approve <lead_batch_id>
/sales send <lead_id>
/sales followup
/client start <client_name_or_lead_id>
/content create <client_id_or_name> <goal>
/content status <project_id>
/content select <project_id> <option refs>
/status <project_id>
/review submit <project_id>
/review queue
/review approve <approval_id>
/review reject <approval_id>
/review revise <project_id> <instruction>
/deliver <project_id>
/invoice send <project_id>
/summary today
/dashboard
```

`/review submit <project_id>` is intentionally added. The handoff requires creating an `approval_item` and moving the project to `Sent For Approval`, but the original Telegram command list did not include a clear command to initiate that step.
