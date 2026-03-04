# GitHub Connector Plugin

A plugin that connects to the GitHub API to fetch repository information, issues, and pull requests.

## What It Does

- Fetch repository details (stars, forks, description)
- List open issues with titles and URLs
- List pull requests with titles and states
- All data returned as structured dictionaries

## Requirements

- Python 3.8+
- GitHub personal access token (optional, for authenticated requests)

## Configuration

Create a `config.yaml` file in your plugin directory:

```yaml
github_token: "ghp_YOUR_TOKEN_HERE"
owner: "OpenClawHQ"
repo: "cookbook"
```

Or pass them as environment variables:
- `GITHUB_TOKEN`: Your GitHub personal access token
- `GITHUB_OWNER`: Repository owner
- `GITHUB_REPO`: Repository name

**Note**: Without a token, you're limited to 60 requests/hour. With a token, you get 5000 requests/hour.

## How to Run

```bash
# Install
pip install -e .

# Run
python -m plugin
```

## Example Usage

```python
from src.plugin import GitHubConnector

config = {
    "github_token": "ghp_YOUR_TOKEN",
    "owner": "OpenClawHQ",
    "repo": "cookbook"
}

plugin = GitHubConnector(config)

# Get repo info
repo_info = plugin.execute({
    "action": "get_repo"
})

# List issues
issues = plugin.execute({
    "action": "list_issues"
})

# List pull requests
prs = plugin.execute({
    "action": "list_prs"
})
```

## API Actions

### `get_repo`
Fetches repository metadata.

**Returns:**
```python
{
    "name": "cookbook",
    "description": "Example plugins for OpenClaw",
    "url": "https://github.com/OpenClawHQ/cookbook",
    "stars": 42,
    "forks": 10,
    "language": "Python"
}
```

### `list_issues`
Lists the 10 most recent open issues.

**Returns:**
```python
{
    "count": 5,
    "issues": [
        {
            "number": 1,
            "title": "Add more examples",
            "url": "https://github.com/OpenClawHQ/cookbook/issues/1",
            "created_at": "2026-03-01T12:00:00Z"
        }
    ]
}
```

### `list_prs`
Lists the 10 most recent pull requests.

**Returns:**
```python
{
    "count": 2,
    "pull_requests": [
        {
            "number": 5,
            "title": "Add webhook listener example",
            "url": "https://github.com/OpenClawHQ/cookbook/pull/5",
            "state": "open",
            "created_at": "2026-03-02T10:30:00Z"
        }
    ]
}
```

## Under the Hood

This plugin uses only Python's standard library (`urllib.request`, `json`) to communicate with GitHub's REST API. No external dependencies required.

## License

MIT License
