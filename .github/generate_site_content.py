#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
# ]
# ///
"""Generate site content from plugins/*.json files."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests


def fetch_readme(repo_url: str, path: Optional[str] = None) -> str:
    """Fetch README.md from a GitHub repository.

    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/author/repo)
        path: Optional subdirectory path for monorepos

    Returns:
        README content as string, or error message if not found
    """
    # Extract owner and repo name from URL
    # https://github.com/author/repo -> author/repo
    parts = repo_url.rstrip('/').split('github.com/')
    if len(parts) != 2:
        return f"<!-- Could not parse repository URL: {repo_url} -->"

    owner_repo = parts[1]

    # Build raw.githubusercontent.com URL
    # Try both main and master branches
    for branch in ['main', 'master']:
        if path:
            # Monorepo: https://raw.githubusercontent.com/author/repo/main/path/README.md
            raw_url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/{path}/README.md"
        else:
            # Regular repo: https://raw.githubusercontent.com/author/repo/main/README.md
            raw_url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/README.md"

        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.RequestException as e:
            print(f"Warning: Failed to fetch {raw_url}: {e}", file=sys.stderr)
            continue

    return f"<!-- README not found for {repo_url} -->"


def generate_markdown(plugin: dict, plugin_filename: str, current_date: str) -> str:
    """Generate markdown content for a plugin.

    Args:
        plugin: Plugin data dictionary
        plugin_filename: Original JSON filename (without .json extension)
        current_date: Current date in YYYY-MM-DD format

    Returns:
        Markdown content with frontmatter
    """
    # Fetch README from repository
    readme_content = fetch_readme(
        plugin.get('repo', ''),
        plugin.get('path')
    )

    # If inside readme_content there is a relative image link, we might want to adjust it
    # and add the repo raw URL prefix.
    # so ![image](image.png) becomes ![image](https://raw.githubusercontent.com/author/repo/main/image.png)
    # use regex to match ![alt](url.{png,jpg,jpeg,gif,webp})
    import re 
    def replace_relative_image(match):
        alt_text = match.group(1)
        img_url = match.group(2)
        if img_url.startswith('http://') or img_url.startswith('https://'):
            return match.group(0)  # leave unchanged
        # Build raw URL
        parts = plugin.get('repo', '').rstrip('/').split('github.com/')
        if len(parts) != 2:
            return match.group(0)  # leave unchanged
        owner_repo = parts[1]
        branch = 'main'  # default to main
        if plugin.get('path'):
            raw_img_url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/{plugin['path']}/{img_url}"
        else:
            raw_img_url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/{img_url}"
        return f"![{alt_text}]({raw_img_url})"

    readme_content = re.sub(r'!\[([^\]]*)\]\(([^)]+\.(png|jpg|jpeg|gif|webp))\)', replace_relative_image, readme_content)


    # Build tags list: capabilities + category + compositors + distro
    tags = []
    tags.extend(plugin.get('capabilities', []))
    if 'category' in plugin:
        tags.append(plugin['category'])
    tags.extend(plugin.get('compositors', []))
    tags.extend(plugin.get('distro', []))

    # Format tags as comma-separated string
    tags_str = ', '.join(tags)

    # Build screenshot section
    screenshot = plugin.get("screenshot", "null")
    no_image_on_readme = '![' not in readme_content
    screenshot_section = ""
    if 'screenshot' in plugin and plugin['screenshot'] and no_image_on_readme:
        screenshot_section = f"\n![{plugin['name']} Screenshot]({plugin['screenshot']})\n"

    # Build requires_dms section
    requires_section = ""
    if 'requires_dms' in plugin and plugin['requires_dms']:
        requires_section = f"\n**Requires DMS version:** `{plugin['requires_dms']}`\n"

    is_official = plugin.get("author") == "Avenge Media"

    # Build markdown content
    markdown = f"""---
date: {current_date}
title: {plugin.get('name', 'Unknown Plugin')}
author: {plugin.get('author', 'Unknown Author')}
tags: {tags_str}
card_image: {screenshot}
pinned: {"true" if is_official else "false"}
---

{plugin.get('description', 'No description available.')}


> [!NOTE] installation
> Run `dms plugins install "{plugin.get('name')}"`

---

| Plugin Information                 | Value                                         |
| ---------------------------------- | --------------------------------------------- |
| name                               | {plugin.get('name')}                          |
| author                             | {plugin.get('author', 'Unknown Author')}      |
| repo                               | [Link]({plugin.get('repo', '#')})             |
| capabilities                       | {', '.join(plugin.get('capabilities', []))}   |
| category                           | {plugin.get('category', 'Uncategorized')}     |
| compositors                        | {', '.join(plugin.get('compositors', []))}    |
| distro                             | {', '.join(plugin.get('distro', []))}         |
| dependencies                       | {', '.join(plugin.get('dependencies', []))}   |
| requires DMS                       | {plugin.get('requires_dms', 'N/A')}           |

{screenshot_section}
{readme_content}

"""

    return markdown


def generate_site_content() -> int:
    """Generate site content for all plugins."""
    repo_root = Path(__file__).parent.parent
    plugins_dir = repo_root / "plugins"
    content_dir = repo_root / "site" / "content"

    # Ensure content directory exists
    content_dir.mkdir(parents=True, exist_ok=True)


    # Process each plugin JSON file
    processed_count = 0
    error_count = 0

    for json_file in plugins_dir.glob("*.json"):
        
        # current date must be the date the json file was last edited
        # 
        # current_date = datetime.now().strftime('%Y-%m-%d')
        current_date = datetime.fromtimestamp(json_file.stat().st_mtime).strftime('%Y-%m-%d')
        
        try:
            # Load plugin data
            with open(json_file) as f:
                plugin_data = json.load(f)

            # Generate output filename based on JSON filename
            # e.g., rochacbruno-calculator.json -> rochacbruno-calculator.md
            output_filename = json_file.stem + ".md"
            output_path = content_dir / output_filename

            # Generate markdown content
            markdown_content = generate_markdown(
                plugin_data,
                json_file.stem,
                current_date
            )

            # Write to file
            with open(output_path, 'w') as f:
                f.write(markdown_content)

            print(f"Generated: {output_filename}")
            processed_count += 1

        except json.JSONDecodeError as e:
            print(f"Error parsing {json_file}: {e}", file=sys.stderr)
            error_count += 1
        except Exception as e:
            print(f"Error processing {json_file}: {e}", file=sys.stderr)
            error_count += 1

    print(f"\nProcessed {processed_count} plugins")
    if error_count > 0:
        print(f"Encountered {error_count} errors", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(generate_site_content())
