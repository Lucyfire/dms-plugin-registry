#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""
Validate plugin links and paths.

This script validates:
- Screenshot URLs are valid and reachable
- Repository URLs are valid and reachable
- Plugin paths exist in the repository (for monorepo plugins)
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def validate_url(url: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Validate that a URL is reachable.

    Returns:
        (is_valid, error_message)
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 405:  # HEAD not allowed, try GET
            response = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)

        if response.status_code >= 200 and response.status_code < 400:
            return True, ""
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def validate_repo_path(repo_url: str, path: str) -> tuple[bool, str]:
    """
    Validate that a path exists in a git repository.
    Supports GitHub, GitLab, Codeberg, and other common git hosting services.

    Returns:
        (is_valid, error_message)
    """
    parsed = urlparse(repo_url)

    # Extract owner/repo from path like /owner/repo or /owner/repo.git
    path_parts = parsed.path.strip("/").rstrip(".git").split("/")
    if len(path_parts) < 2:
        return False, "Invalid repository URL format"

    owner, repo = path_parts[0], path_parts[1]

    # Determine hosting service and construct API URL
    api_url = None
    service_name = None

    if parsed.netloc == "github.com":
        # GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        service_name = "GitHub"
    elif parsed.netloc == "gitlab.com" or "gitlab" in parsed.netloc:
        # GitLab API (gitlab.com or self-hosted)
        # URL encode the project path (owner/repo)
        project_path = f"{owner}%2F{repo}"
        base_url = f"https://{parsed.netloc}"
        api_url = f"{base_url}/api/v4/projects/{project_path}/repository/tree?path={path}"
        service_name = "GitLab"
    elif parsed.netloc == "codeberg.org" or "gitea" in parsed.netloc or "forgejo" in parsed.netloc:
        # Codeberg/Gitea/Forgejo API
        base_url = f"https://{parsed.netloc}"
        api_url = f"{base_url}/api/v1/repos/{owner}/{repo}/contents/{path}"
        service_name = "Gitea/Forgejo"
    else:
        # Unknown hosting service - skip path validation with warning
        return True, f"Warning: Path validation skipped for {parsed.netloc} (unsupported hosting service)"

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            # For GitLab, check if the response is an empty array (path not found)
            if service_name == "GitLab":
                data = response.json()
                if isinstance(data, list) and len(data) == 0:
                    return False, f"Path '{path}' not found in repository"
            return True, ""
        elif response.status_code == 404:
            return False, f"Path '{path}' not found in repository"
        else:
            return False, f"{service_name} API returned HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Failed to check path: {str(e)}"


def validate_plugin(plugin_file: Path) -> list[str]:
    """
    Validate a single plugin file.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    try:
        with open(plugin_file, "r") as f:
            plugin = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Failed to read file: {e}"]

    plugin_name = plugin.get("name", plugin_file.stem)

    # Validate screenshot
    if "screenshot" not in plugin:
        errors.append("Missing required 'screenshot' property")
    else:
        screenshot_url = plugin["screenshot"]
        if not screenshot_url:
            errors.append("Screenshot URL is empty")
        else:
            is_valid, error_msg = validate_url(screenshot_url)
            if not is_valid:
                errors.append(f"Screenshot URL unreachable: {error_msg}")

    # Validate repo
    if "repo" not in plugin:
        errors.append("Missing required 'repo' property")
    else:
        repo_url = plugin["repo"]
        if not repo_url:
            errors.append("Repository URL is empty")
        else:
            is_valid, error_msg = validate_url(repo_url)
            if not is_valid:
                errors.append(f"Repository URL unreachable: {error_msg}")

            # Validate path if present
            if "path" in plugin and plugin["path"]:
                path = plugin["path"]
                is_valid, error_msg = validate_repo_path(repo_url, path)
                if not is_valid:
                    errors.append(f"Path validation failed: {error_msg}")
                elif error_msg:  # Warning message (unsupported service)
                    print(f" {YELLOW}({error_msg}){RESET}", end="")

    return errors


def main():
    """Main validation entry point."""
    plugins_dir = Path(__file__).parent.parent / "plugins"

    if not plugins_dir.exists():
        print(f"{RED}Error: plugins/ directory not found{RESET}")
        sys.exit(1)

    plugin_files = list(plugins_dir.glob("*.json"))

    if not plugin_files:
        print(f"{YELLOW}Warning: No plugin files found in plugins/{RESET}")
        sys.exit(0)

    print(f"Validating {len(plugin_files)} plugin(s)...\n")

    all_errors = {}

    for plugin_file in sorted(plugin_files):
        print(f"Checking {plugin_file.name}...", end=" ")
        errors = validate_plugin(plugin_file)

        if errors:
            print(f"{RED}FAILED{RESET}")
            all_errors[plugin_file.name] = errors
        else:
            print(f"{GREEN}OK{RESET}")

    # Print summary
    print()
    if all_errors:
        print(f"{RED}Validation failed for {len(all_errors)} plugin(s):{RESET}\n")
        for filename, errors in all_errors.items():
            print(f"{RED}✗ {filename}{RESET}")
            for error in errors:
                print(f"  - {error}")
            print()
        sys.exit(1)
    else:
        print(f"{GREEN}✓ All plugins validated successfully!{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
