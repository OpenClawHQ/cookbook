"""
GitHub Connector Plugin

A working example plugin that demonstrates API integration with GitHub.
Uses only Python standard library (urllib.request, json).
"""

import json
import urllib.request
import urllib.error
import base64
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PluginConfig(dict):
    """Configuration container for plugins."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class PluginBase(ABC):
    """Abstract base class for all plugins."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin with configuration.

        Args:
            config: Dictionary of configuration parameters
        """
        self.config = PluginConfig(config or {})
        self.setup()

    @abstractmethod
    def setup(self):
        """Called once during initialization. Store or validate configuration."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin with the given context.

        Args:
            context: Dictionary containing action and parameters

        Returns:
            Result of the plugin execution
        """
        pass


class GitHubConnector(PluginBase):
    """
    A plugin that connects to the GitHub API to fetch repository information,
    issues, and pull requests.
    """

    BASE_URL = "https://api.github.com"

    def setup(self):
        """Initialize GitHub API credentials from config or environment variables."""
        self.token = self.config.get("github_token") or os.getenv("GITHUB_TOKEN")
        self.owner = self.config.get("owner") or os.getenv("GITHUB_OWNER")
        self.repo = self.config.get("repo") or os.getenv("GITHUB_REPO")

        if not self.owner or not self.repo:
            raise ValueError(
                "GitHub owner and repo must be set in config or environment variables"
            )

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action based on context["action"].

        Supported actions:
        - get_repo: Fetch repository metadata
        - list_issues: List open issues
        - list_prs: List pull requests
        """
        action = context.get("action")

        if action == "get_repo":
            return self._get_repo()
        elif action == "list_issues":
            return self._list_issues()
        elif action == "list_prs":
            return self._list_prs()
        else:
            return {"error": f"Unknown action: {action}"}

    def _get_repo(self) -> Dict[str, Any]:
        """Fetch repository metadata from GitHub API."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}"
        response = self._make_request(url)

        if "message" in response:
            return {"error": response.get("message")}

        return {
            "name": response.get("name"),
            "description": response.get("description"),
            "url": response.get("html_url"),
            "stars": response.get("stargazers_count"),
            "forks": response.get("forks_count"),
            "language": response.get("language"),
            "created_at": response.get("created_at"),
            "updated_at": response.get("updated_at"),
        }

    def _list_issues(self) -> Dict[str, Any]:
        """List open issues for the repository."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/issues"
        params = "?state=open&sort=created&direction=desc&per_page=10"
        response = self._make_request(url + params)

        if isinstance(response, dict) and "message" in response:
            return {"error": response.get("message")}

        if not isinstance(response, list):
            return {"error": "Unexpected response format"}

        issues = [
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "url": issue.get("html_url"),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "state": issue.get("state"),
            }
            for issue in response
        ]

        return {"count": len(issues), "issues": issues}

    def _list_prs(self) -> Dict[str, Any]:
        """List pull requests for the repository."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/pulls"
        params = "?state=all&sort=created&direction=desc&per_page=10"
        response = self._make_request(url + params)

        if isinstance(response, dict) and "message" in response:
            return {"error": response.get("message")}

        if not isinstance(response, list):
            return {"error": "Unexpected response format"}

        prs = [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "url": pr.get("html_url"),
                "state": pr.get("state"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
            }
            for pr in response
        ]

        return {"count": len(prs), "pull_requests": prs}

    def _make_request(self, url: str) -> Any:
        """
        Make an authenticated HTTP request to the GitHub API.

        Args:
            url: Full URL to request

        Returns:
            Parsed JSON response
        """
        try:
            req = urllib.request.Request(url)

            # Add authentication if token is available
            if self.token:
                auth_string = base64.b64encode(f":{self.token}".encode()).decode()
                req.add_header("Authorization", f"Basic {auth_string}")

            # Add user-agent header
            req.add_header("User-Agent", "OpenClaw-GitHub-Connector")

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("utf-8")
                return json.loads(data)

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_data = json.loads(error_body)
                return {"error": error_data.get("message", str(e))}
            except json.JSONDecodeError:
                return {"error": f"HTTP {e.code}: {str(e)}"}

        except urllib.error.URLError as e:
            return {"error": f"Network error: {str(e)}"}

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    config = {
        "owner": "OpenClawHQ",
        "repo": "cookbook",
    }

    plugin = GitHubConnector(config)

    print("Fetching repository info...")
    repo = plugin.execute({"action": "get_repo"})
    print(json.dumps(repo, indent=2))

    print("\nFetching open issues...")
    issues = plugin.execute({"action": "list_issues"})
    print(json.dumps(issues, indent=2))

    print("\nFetching pull requests...")
    prs = plugin.execute({"action": "list_prs"})
    print(json.dumps(prs, indent=2))
