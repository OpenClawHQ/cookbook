# OpenClaw Skills Cookbook

[![Skills](https://img.shields.io/badge/skills-5-E03E3E)](./skills) [![skill-lint](https://img.shields.io/badge/validated%20by-skill--lint-success)](https://github.com/OpenClawHQ/skill-lint) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

A collection of community-contributed OpenClaw skill recipes. Each skill is a ready-to-use workflow component for common tasks: Jira triage, database queries, Docker management, git operations, and more.

## What Are Skills?

Skills are reusable workflow automation components that extend OpenClaw with new capabilities. Each skill includes:

- A `SKILL.md` file with YAML frontmatter (metadata) and markdown documentation
- Clear command definitions and examples
- Setup instructions and prerequisites
- Real-world usage patterns and best practices

Skills are **not** Python plugins—they're self-contained, declarative workflow definitions that OpenClaw executes directly.

## Available Skills

| Skill | Description | Requires |
|-------|-------------|----------|
| **[notion-sync](./skills/notion-sync/)** | Create, read, search, and update Notion pages and databases | `NOTION_API_KEY` env var |
| **[docker-manager](./skills/docker-manager/)** | Control Docker containers: start, stop, logs, exec, stats | `docker` binary |
| **[git-worktree](./skills/git-worktree/)** | Advanced git worktree management for parallel development | `git` binary (v2.7+) |
| **[jira-triage](./skills/jira-triage/)** | Triage, search, transition, and comment on Jira issues | `JIRA_API_TOKEN` + `JIRA_BASE_URL` env vars |
| **[postgres-query](./skills/postgres-query/)** | Run read-only PostgreSQL queries and analyze databases | `psql` binary + `DATABASE_URL` env var |

## Quick Start

### Option 1: Install from Cookbook

Copy any skill to your OpenClaw workspace:

```bash
# Copy a single skill
cp -r skills/notion-sync ~/.openclaw/workspace/skills/

# Or copy all skills
cp -r skills/* ~/.openclaw/workspace/skills/
```

### Option 2: Use Claw Hub (Coming Soon)

```bash
clawhub install notion-sync
clawhub install docker-manager
clawhub install jira-triage
```

### Verify Installation

```bash
# List all skills
openclaw skills list

# Use a skill
openclaw notion-sync search "project status"
openclaw docker-manager list --running
```

## Skill Structure

Each skill is a directory with a single file:

```
skills/
├── notion-sync/
│   └── SKILL.md          # Frontmatter + documentation
├── docker-manager/
│   └── SKILL.md
├── git-worktree/
│   └── SKILL.md
├── jira-triage/
│   └── SKILL.md
└── postgres-query/
    └── SKILL.md
```

### SKILL.md Format

```yaml
---
name: skill-name
description: "Short description of what this skill does"
metadata:
  openclaw:
    emoji: 🎯
    requires:
      bins:
        - required-binary
      config:
        - REQUIRED_ENV_VAR
    install:
      - id: install-method
        kind: brew
        formula: package-name
---

# Markdown body with:
## Purpose
## When to Use
## Setup
## Commands
## Examples
## Notes
```

## Creating Your Own Skill

See the [Contributing Guide](./CONTRIBUTING.md) for step-by-step instructions to create and submit a new skill.

Quick summary:

1. Create a folder: `skills/my-skill/`
2. Write `SKILL.md` with frontmatter and documentation
3. Include realistic examples that actually work
4. Submit a PR with your skill recipe

## Our Principles

**Build First, Ship Loud, Open by Default**

- **Build First**: Real, functional skills with genuine examples—not stubs
- **Ship Loud**: Skills are polished, documented, and ready to inspire
- **Open by Default**: All code is MIT licensed and community-driven

## Using Skills in Your Workflow

### Basic Usage

```bash
# Run a skill command
openclaw <skill-name> <command> [arguments]

# Example: List Jira issues
openclaw jira-triage search "project = PROJ AND status = 'To Do'"

# Example: View Docker container logs
openclaw docker-manager logs my-app --tail 50 --follow

# Example: Query database
openclaw postgres-query execute "SELECT * FROM users LIMIT 10" --output json
```

### Chaining Skills

Combine multiple skills in workflows:

```bash
# Transition Jira issues based on Docker deployment status
if openclaw docker-manager inspect api-service; then
  openclaw jira-triage transition PROJ-123 "Deployed"
  openclaw jira-triage comment PROJ-123 "Service is live in production"
fi
```

### Environment Configuration

Each skill may require environment variables. Set them in your shell:

```bash
# Jira
export JIRA_API_TOKEN="your_token"
export JIRA_BASE_URL="https://org.atlassian.net"

# Notion
export NOTION_API_KEY="your_api_key"

# Postgres
export DATABASE_URL="postgresql://user:pass@host/db"
```

Or use OpenClaw's config management:

```bash
openclaw config set NOTION_API_KEY "your_key"
openclaw config set JIRA_API_TOKEN "your_token"
```

## Documentation Structure

Each skill includes:

- **Purpose**: When and why to use it
- **Setup**: Prerequisites, installation, configuration
- **Commands**: Available operations with syntax
- **Examples**: Real-world usage patterns
- **Notes**: Performance tips, security considerations

See any skill's `SKILL.md` for complete details.

## Resources

- [OpenClaw GitHub](https://github.com/openclaw/openclaw) - Main project
- [Skill Template](https://github.com/OpenClawHQ/skill-template) - Starter template
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute
- [OpenClaw Docs](https://docs.openclaw.dev) - Full documentation

## Contributing

We welcome new skills! See [CONTRIBUTING.md](./CONTRIBUTING.md) for:

- How to create a new skill
- Documentation standards
- Testing and review process
- License requirements

## License

MIT License. See [LICENSE](./LICENSE) for details.

All skills in this cookbook are MIT licensed and open source.

---

**Have an idea for a new skill?** Open an issue or submit a PR!

Questions? Start a discussion in the [OpenClaw repository](https://github.com/openclaw/openclaw).
