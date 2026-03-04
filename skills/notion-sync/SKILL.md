---
name: notion-sync
description: Sync and manage Notion pages via the Notion API. Search pages, read content, create pages, update properties, and manage workspace organization.
metadata:
  openclaw:
    emoji: 📝
    requires:
      config:
        - NOTION_API_KEY
    install:
      - id: notion-api-key
        kind: config
        label: "Set NOTION_API_KEY environment variable"
        docs: "https://developers.notion.com/docs/getting-started/setup"
---

## Purpose

Automate your Notion workspace by syncing pages, reading content, creating structured pages, and updating properties. Use this skill to bridge Notion with your OpenClaw workflows.

## When to Use

- Sync documentation from external sources into Notion
- Search and retrieve page content programmatically
- Create pages with specific properties (databases, templates)
- Update page status, assignees, tags across your workspace
- Automate organization of research, notes, or project tracking

## When Not to Use

- Avoid direct database modifications without proper structure
- Don't bulk delete without confirmation

## Setup

### Prerequisites

- Notion account and workspace
- Notion API key (integration token)

### Installation

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Generate an API key and note it
3. Set the environment variable:
   ```bash
   export NOTION_API_KEY="your_integration_token_here"
   ```
4. Share pages/databases with your integration in Notion
5. Copy this skill to `~/.openclaw/workspace/skills/notion-sync/`

## Commands

### Search Pages

Find pages by title or content:

```bash
notion-sync search "project status"
notion-sync search "Q1 Planning" --database-id <db-id>
```

**Use case**: Locate existing pages before syncing or updating

### Read Page

Retrieve full page content and metadata:

```bash
notion-sync read <page-id>
notion-sync read <page-id> --properties only  # Just metadata
```

**Use case**: Get current content before updating or syncing

### Create Page

Create a new page in a database or as a child page:

```bash
notion-sync create \
  --title "New Project" \
  --database-id <db-id> \
  --properties '{"Status":"Planned","Owner":"Alice"}'

notion-sync create \
  --title "Meeting Notes" \
  --parent-id <page-id> \
  --content "- Item 1\n- Item 2"
```

**Use case**: Automatically add entries to project tracking, meeting notes, etc.

### Update Page

Modify page properties:

```bash
notion-sync update <page-id> \
  --properties '{"Status":"In Progress","Due":"2026-03-15"}'

notion-sync update <page-id> \
  --append-content "- New item added by automation"
```

**Use case**: Update status, deadlines, or assign tasks

### List Database Items

Retrieve all items in a database with filtering:

```bash
notion-sync list <database-id>
notion-sync list <database-id> --filter '{"property":"Status","select":{"equals":"Pending"}}'
notion-sync list <database-id> --sort-by "Created time" --limit 50
```

**Use case**: Generate reports, find items needing action

## Examples

### Example 1: Sync External Issues to Notion

```bash
# Create a page for each GitHub issue in a Notion database
notion-sync create \
  --title "Issue: Fix login bug" \
  --database-id "abc123..." \
  --properties '{
    "Status": "To Do",
    "Priority": "High",
    "GitHub URL": "https://github.com/org/repo/issues/42",
    "Assignee": "dev-team"
  }' \
  --content "## Description\nUsers report login failures on mobile.\n\n## Steps\n1. Open app on iOS\n2. Try to login"
```

### Example 2: Update Project Status Weekly

```bash
# Update all "In Progress" items to include this week's date
notion-sync list <database-id> --filter '{"property":"Status","select":{"equals":"In Progress"}}' | while read page_id; do
  notion-sync update "$page_id" \
    --properties '{"Last Updated":"2026-03-04"}'
done
```

### Example 3: Archive Completed Items

```bash
# Find and archive old completed items
notion-sync list <database-id> \
  --filter '{"property":"Status","select":{"equals":"Done"}}' \
  --filter '{"property":"Completed","date":{"before":"2026-01-01"}}' | \
  xargs -I {} notion-sync update {} --properties '{"Status":"Archived"}'
```

### Example 4: Generate Team Workload Report

```bash
# Get all "In Progress" items grouped by assignee
notion-sync list <database-id> \
  --filter '{"property":"Status","select":{"equals":"In Progress"}}' | \
  xargs -I {} notion-sync read {} --properties-only | \
  jq '.properties.Assignee' | sort | uniq -c
```

## API Reference

### Required Headers

All requests to the Notion API include:
```
Authorization: Bearer ${NOTION_API_KEY}
Notion-Version: 2022-06-28
```

### Common Properties Format

```json
{
  "title": [{"text": {"content": "Page Title"}}],
  "status": {"select": {"name": "In Progress"}},
  "assignee": {"people": [{"id": "person-id"}]},
  "due_date": {"date": {"start": "2026-03-15"}},
  "tags": {"multi_select": [{"name": "urgent"}, {"name": "review"}]}
}
```

## Environment Variables

- `NOTION_API_KEY` - Your Notion integration token (required)
- `NOTION_WORKSPACE_ID` - Optional: Default workspace to use

## Notes

- Notion API has rate limits: 3 requests/second for regular operations
- Page IDs are UUIDs formatted as `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Always get database IDs and parent page IDs from Notion URLs or previous queries
- Archive instead of delete to preserve history
- Test with a secondary Notion workspace first
