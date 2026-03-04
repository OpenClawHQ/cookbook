# Contributing to OpenClaw Skills Cookbook

Thank you for your interest in contributing skills to the OpenClaw cookbook! We welcome new recipes that solve real problems and help the community automate their workflows.

## What Makes a Good Skill

- **Real and Functional**: Solves an actual problem; examples actually work
- **Well Documented**: Clear setup, commands, and examples
- **Production Ready**: Can be used immediately without major changes
- **Self-Contained**: Works independently with clear requirements
- **Practical Examples**: Real-world use cases developers will recognize

## Adding a New Skill

### Step 1: Create the Skill Directory

```bash
mkdir -p skills/my-skill
touch skills/my-skill/SKILL.md
```

### Step 2: Write the SKILL.md File

Start with this template:

```yaml
---
name: my-skill
description: "Brief one-line description of what this skill does"
metadata:
  openclaw:
    emoji: 🎯
    requires:
      bins:
        - required-binary
      config:
        - REQUIRED_ENV_VAR
    install:
      - id: install-method-id
        kind: brew
        formula: package-name
        bins:
          - binary-name
        label: "User-friendly install description"
---

## Purpose

Explain what this skill does and why it matters.

## When to Use

List scenarios where this skill is valuable.

## When Not to Use

Be honest about limitations.

## Setup

### Prerequisites

List what users need before installing.

### Installation

Provide step-by-step setup instructions:

```bash
# Installation example
brew install my-tool
export MY_API_KEY="your_key"
```

### Verify

Include a quick verification command:

```bash
my-skill --version
my-skill test-command
```

## Commands

### Command Name

Brief description.

```bash
my-skill command arg1 arg2 --flag
my-skill command with-options "quoted string"
```

**Use case**: When and why to use this command

## Examples

### Example 1: Clear Use Case

Realistic example that actually works.

```bash
# Real command that accomplishes something
my-skill do-something important
```

Expected output and explanation.

### Example 2: Another Use Case

More examples for different scenarios.

## Notes

Performance tips, limitations, best practices.
```

### Step 3: Fill In Each Section

#### Purpose & When to Use

Be clear about what problem this skill solves:

```markdown
## Purpose

Use this skill to manage Docker containers without switching to the command line.
Start, stop, inspect, and monitor containers from OpenClaw workflows.

## When to Use

- Local development: Start/stop services quickly
- Debugging: View logs and inspect container state
- Monitoring: Check resource usage and health
- CI/CD: Control containers programmatically

## When Not to Use

- Production orchestration (use Kubernetes)
- Complex multi-container setups (use docker-compose)
```

#### Setup

Make setup foolproof:

```markdown
## Setup

### Prerequisites

- Docker Desktop or Docker Engine installed
- For Linux: Docker daemon running and user in docker group

### Installation

**macOS:**
```bash
brew install docker
```

**Linux:**
```bash
sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

**Verify:**
```bash
docker ps  # Should list containers
```

### Configuration (if needed)

```bash
export DOCKER_HOST="unix:///var/run/docker.sock"
```
```

#### Commands

List each command clearly:

```markdown
## Commands

### Start Container

Start a stopped container.

```bash
my-skill start <container-name>
my-skill start web-service
```

**Output**: Container starts and is ready to serve requests
**Use case**: Resume development after stopping services
```

#### Examples

Provide 3-5 realistic examples:

```markdown
### Example 1: Daily Database Backup

Schedule automatic backups:

```bash
#!/bin/bash
# Runs via cron: 0 2 * * * /path/to/backup.sh

my-skill backup-database \
  --database prod_db \
  --output s3://backups/$(date +%Y%m%d).sql
```

This backs up the production database daily at 2am.

### Example 2: Verify Data Integrity

```bash
# Check data after deployment
my-skill verify-tables --database prod_db

# Output shows any errors
# All 247 tables verified ✓
```
```

#### Notes

Include practical guidance:

```markdown
## Notes

- Rate limits: 100 requests/minute on free tier
- Backups are retained for 30 days
- Always test on staging first
- Monitor resource usage during large operations
- Credentials in `DATABASE_URL` should not be committed
```

### Step 4: Test Your Skill

Verify the examples actually work:

1. Follow your own setup instructions
2. Run each example command
3. Verify output matches what you documented
4. Test edge cases and error handling

### Step 5: Update the Root README.md

Add your skill to the "Available Skills" table:

```markdown
| **[my-skill](./skills/my-skill/)** | Description | `REQUIRED_VAR` |
```

Keep it alphabetical.

### Step 6: Submit a PR

Create a pull request with:

1. New skill directory with `SKILL.md`
2. Updated `README.md` with skill listed
3. Clear PR title: "Add my-skill recipe"
4. PR description:
   - What the skill does
   - Why it's useful
   - Any special setup needed
   - Example use case

## Documentation Guidelines

### Writing Style

- Clear and concise
- Use examples liberally
- Write for developers who may not know the tool
- Avoid jargon without explanation

### Markdown Format

- Use code blocks for commands: `my-skill command`
- Use tables for command reference
- Use headers for sections: `## Purpose`
- Use **bold** for important terms
- Include realistic output examples

### Command Reference

Show actual usage syntax:

```markdown
```bash
my-skill command arg1 [optional] --flag value
```

Good: Shows required args and optional parts
```

### Examples Quality

Good examples:

```markdown
### Example 1: Production Deployment Notification

When code merges to main, notify Slack:

```bash
# Extract deployed version
VERSION=$(my-skill deployed-version)

# Send notification
my-skill notify-slack \
  --channel #deployments \
  --message "Version $VERSION deployed to production"
```

Output: Message posted to Slack channel.
```

This example:
- ✓ Solves a real problem
- ✓ Shows input and expected output
- ✓ Is immediately usable
- ✓ Explains the use case

## Skill Template Structure

```
skills/
└── my-skill/
    └── SKILL.md              # Only file needed!
```

That's it. No Python, no dependencies, no build steps.

## Metadata Reference

### Required Fields

```yaml
---
name: my-skill                # Lowercase, hyphenated
description: "One-line description"
metadata:
  openclaw:
    emoji: 🎯
---
```

### Optional Requirements

```yaml
metadata:
  openclaw:
    requires:
      bins:                   # Required binaries
        - docker
      config:                 # Required env vars
        - DATABASE_URL
    install:                  # Installation methods
      - id: homebrew
        kind: brew            # Or: apt, manual, etc.
        formula: docker
        label: "Install Docker (brew)"
```

## Review Checklist

Before submitting, verify:

- [ ] SKILL.md file exists and is valid YAML
- [ ] All examples tested and working
- [ ] Setup instructions are clear and complete
- [ ] Purpose and use cases are explained
- [ ] At least 3 realistic examples included
- [ ] Notes section addresses common issues
- [ ] README.md updated with new skill
- [ ] No Python/code outside the skill definition
- [ ] MIT License header in SKILL.md (implicit)
- [ ] No hardcoded credentials or secrets

## Common Issues

### Example Doesn't Work

- Verify on your own system first
- Include all setup steps
- Show expected output
- Explain what might go wrong

### Missing Prerequisites

List all requirements:
- Tools to install
- Environment variables
- Accounts or API keys
- Permissions

### Unclear Commands

Use consistent format:
```bash
skill-name command arg1 arg2 --flag value
```

Not:
```
skill-name [command] {optional stuff here}
```

## Help & Questions

- **Design question?** Open an issue first to discuss
- **Need feedback?** Submit a draft PR with `[WIP]` tag
- **Technical help?** Check existing skills for patterns

## Principles

We follow these principles for all cookbook skills:

1. **Build First**: Real, functional solutions
2. **Ship Loud**: Polished and production-ready
3. **Open by Default**: MIT licensed, community-owned
4. **No Lock-in**: Portable, not vendor-specific
5. **Practical**: Solves actual developer problems

## License

All contributions are MIT licensed. By submitting a PR, you agree to license your skill under MIT.

See [LICENSE](./LICENSE) for details.

---

**Thank you for contributing!** Your skills help the community automate and collaborate better.

Questions? Open an issue or discussion in the [OpenClaw repository](https://github.com/openclaw/openclaw).
