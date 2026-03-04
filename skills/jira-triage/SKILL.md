---
name: jira-triage
description: Triage and manage Jira issues. List, search, transition, comment on, and assign issues directly from OpenClaw workflows.
metadata:
  openclaw:
    emoji: 🎯
    requires:
      config:
        - JIRA_API_TOKEN
        - JIRA_BASE_URL
    install:
      - id: jira-credentials
        kind: config
        label: "Set JIRA_API_TOKEN and JIRA_BASE_URL"
        docs: "https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/"
---

## Purpose

Manage Jira issues programmatically: search, filter, transition states, assign, comment, and update fields without opening the Jira UI.

## When to Use

- Automate issue triage based on criteria
- Bulk transition issues (e.g., move all "In Review" to "Done")
- Post automated comments with test results or deployment status
- Assign issues to team members based on rules
- Generate status reports and metrics
- Link OpenClaw workflows to Jira updates

## When Not to Use

- Complex project configuration changes
- Bulk deletion without careful verification
- Without understanding your team's Jira workflow

## Setup

### Prerequisites

- Jira Cloud or Jira Server instance
- API token or password
- Your Jira username/email

### Installation

1. Get your Jira API token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create API token
   - Note the token (you won't see it again)

2. Get your Jira base URL (e.g., `https://your-org.atlassian.net`)

3. Set environment variables:
   ```bash
   export JIRA_API_TOKEN="your_api_token_here"
   export JIRA_BASE_URL="https://your-org.atlassian.net"
   ```

4. Copy this skill to `~/.openclaw/workspace/skills/jira-triage/`

5. Verify connection:
   ```bash
   jira-triage search "project = YOUR_PROJECT" --limit 1
   ```

## Commands

### List Issues

Find issues in a project with optional filtering:

```bash
jira-triage list <project-key>
jira-triage list PROJECT --assignee me              # My issues
jira-triage list PROJECT --status "To Do"           # By status
jira-triage list PROJECT --assignee unassigned      # Unassigned
jira-triage list PROJECT --priority high            # By priority
jira-triage list PROJECT --limit 20                 # Limit results
```

**Use case**: See work items, find what needs action

### Search Issues

Advanced search with JQL (Jira Query Language):

```bash
jira-triage search "project = PROJECT AND assignee = CURRENTUSER()"
jira-triage search "project = PROJECT AND status = 'In Review'" --limit 50
jira-triage search "type = Bug AND priority = Highest AND status != Done"
jira-triage search "component = backend AND created >= -7d"  # Last week
jira-triage search "assignee = EMPTY AND status = 'To Do'"   # Unassigned work
```

**Use case**: Complex filtering beyond simple list

### Get Issue Details

Retrieve full issue information:

```bash
jira-triage get PROJ-123
jira-triage get PROJ-123 --fields key,summary,status,assignee,priority
```

**Use case**: Check current state, metadata before acting

### Transition Issue

Move an issue to a different status:

```bash
jira-triage transition PROJ-123 "In Progress"       # By status name
jira-triage transition PROJ-123 "Done" --comment "Shipped to production"
jira-triage transition PROJ-456 "Review Needed" --comment "Tests passing, ready for review"
```

**Use case**: Update workflow status automatically

### Assign Issue

Assign or reassign an issue:

```bash
jira-triage assign PROJ-123 alice@company.com
jira-triage assign PROJ-456 unassigned             # Remove assignment
jira-triage assign PROJ-789 currentUser            # Assign to self
```

**Use case**: Route work to correct owner

### Add Comment

Post a comment on an issue:

```bash
jira-triage comment PROJ-123 "Fixed in commit abc123def"
jira-triage comment PROJ-456 "Waiting for design review from @alice"
jira-triage comment PROJ-789 "{{ environment }} deployment successful"
```

**Use case**: Provide status updates, link external actions

### Update Field

Change any issue field:

```bash
jira-triage update PROJ-123 --field priority --value "Highest"
jira-triage update PROJ-456 --field labels --value "urgent,blocking"
jira-triage update PROJ-789 --field customfield_10001 --value "Some value"
```

**Use case**: Bulk field updates, custom field management

### Link Issues

Create links between issues:

```bash
jira-triage link PROJ-123 blocks PROJ-456
jira-triage link PROJ-123 "is related to" PROJ-789
jira-triage link PROJ-111 duplicates PROJ-222
```

**Use case**: Establish relationships and dependencies

## Examples

### Example 1: Daily Triage Automation

```bash
#!/bin/bash
# Find unassigned issues, comment, and assign to first available person

PROJECT="PROJ"
TEAM=("alice@company.com" "bob@company.com" "charlie@company.com")
ASSIGNEE_INDEX=0

# Get unassigned high-priority issues
jira-triage search "project = $PROJECT AND assignee = EMPTY AND priority = High" | while read issue; do
  # Add comment
  jira-triage comment "$issue" "Auto-triaged. Assigning to team member."

  # Assign to next person (round-robin)
  jira-triage assign "$issue" "${TEAM[$ASSIGNEE_INDEX]}"
  ASSIGNEE_INDEX=$(( ($ASSIGNEE_INDEX + 1) % ${#TEAM[@]} ))
done
```

### Example 2: Auto-Update Status with Deployment

```bash
#!/bin/bash
# When deployment succeeds, update linked issues

DEPLOYMENT_ENV="production"
DEPLOYMENT_BUILD="123"

# Find issues linked to this deployment
jira-triage search "labels = deployed-${DEPLOYMENT_BUILD}" | while read issue; do
  jira-triage transition "$issue" "Done"
  jira-triage comment "$issue" "Deployed to $DEPLOYMENT_ENV (build ${DEPLOYMENT_BUILD})"
done
```

### Example 3: Review Status Report

```bash
# Get all issues in review, count by assignee
jira-triage search "project = PROJ AND status = 'In Review'" | while read issue; do
  jira-triage get "$issue" --fields assignee,priority
done | jq '.assignee.name' | sort | uniq -c
```

Output:
```
  3 alice@company.com
  2 bob@company.com
  1 unassigned
```

### Example 4: Bulk Transition After Testing

```bash
#!/bin/bash
# Move all tested bugs to "Ready for Release"

jira-triage search "project = BUG AND status = 'Testing' AND created <= -1w" | while read issue; do
  # Check if it has recent test comments
  if jira-triage get "$issue" --fields comment | grep -q "Test passed"; then
    jira-triage transition "$issue" "Ready for Release"
    echo "Transitioned $issue"
  fi
done
```

### Example 5: Create Issue and Link to Epic

```bash
#!/bin/bash
# Create subtasks for an epic

EPIC="PROJ-100"
TASKS=("Design API schema" "Implement backend" "Write tests" "Deploy")

for task in "${TASKS[@]}"; do
  NEW_ISSUE=$(jira-triage create \
    --project PROJ \
    --type "Sub-task" \
    --summary "$task" \
    --parent "$EPIC" \
    --assignee "alice@company.com")

  echo "Created $NEW_ISSUE for task: $task"
done
```

### Example 6: Monitor Blocked Issues

```bash
# Find all issues blocked and notify team

BLOCKED=$(jira-triage search "project = PROJ AND issueFunction in blockedBy()")

if [ -z "$BLOCKED" ]; then
  echo "No blocked issues. All clear!"
  exit 0
fi

# For each blocked issue
jira-triage search "project = PROJ AND issueFunction in blockedBy()" | while read issue; do
  BLOCKER=$(jira-triage get "$issue" --fields linked-issue)

  jira-triage comment "$issue" \
    "Reminder: This is blocked by $BLOCKER. Check if you can help unblock."
done
```

## JQL (Jira Query Language) Reference

### Common Operators

```jql
project = KEY                          # Specific project
status = "To Do"                       # Exact status
status in ("To Do", "In Progress")    # Multiple statuses
priority >= High                       # Priority comparison
created >= -7d                        # Created in last 7 days
assignee = CURRENTUSER()              # Current user
assignee = EMPTY                      # Unassigned
component = "Backend"                 # Component filter
labels in (urgent, blocking)          # Label filter
issueType = Bug                       # Issue type
summary ~ "payment"                   # Text search
```

### Combinations

```jql
project = PROJ AND status = "In Review" AND priority = Highest
project = PROJ OR project = OTHER
project = PROJ AND assignee = EMPTY AND priority >= High
created >= -1w AND status != Done
component = Backend AND type in (Bug, Task)
```

## API Reference

### Authentication

All requests use Basic Auth:
```
Authorization: Basic base64(email:api_token)
Content-Type: application/json
```

### Issue Structure

```json
{
  "key": "PROJ-123",
  "fields": {
    "summary": "Issue title",
    "status": {
      "name": "To Do"
    },
    "assignee": {
      "emailAddress": "user@company.com"
    },
    "priority": {
      "name": "High"
    },
    "created": "2026-03-01T10:30:00Z",
    "updated": "2026-03-04T15:45:00Z"
  }
}
```

## Environment Variables

- `JIRA_API_TOKEN` - Your API token (required)
- `JIRA_BASE_URL` - Your Jira instance URL, e.g., `https://org.atlassian.net` (required)
- `JIRA_USER_EMAIL` - Your email (usually auto-detected)

## Best Practices

1. **Use JQL filters**: More powerful than simple list commands
2. **Test before bulk operations**: Always verify with `--limit 1` first
3. **Add comments**: Keep audit trail when automating changes
4. **Respect workflows**: Don't transition to invalid states
5. **Batch operations**: Use `| while read` for bulk actions
6. **Link related issues**: Maintain relationships in Jira

## Common Workflows

### PR → Jira Transition

When PR merges, auto-transition linked Jira:
```bash
# Extract issue key from branch name: feature/PROJ-123-description
ISSUE_KEY=$(git branch | grep "*" | sed -E 's/.*\b([A-Z]+-[0-9]+).*/\1/')
jira-triage transition "$ISSUE_KEY" "Done"
jira-triage comment "$ISSUE_KEY" "Merged to main: $(git log -1 --oneline)"
```

### Status Dashboard

```bash
# Count issues by status
for status in "To Do" "In Progress" "In Review" "Done"; do
  count=$(jira-triage search "project = PROJ AND status = '$status'" | wc -l)
  echo "$status: $count"
done
```

## Limitations & Notes

- Jira Cloud API rate limit: 300 requests per minute
- Custom fields require `customfield_XXXXX` format in updates
- Bulk operations require care; test with `--limit 1` first
- Some transitions require specific conditions/fields
- Assignee must have access to the project
