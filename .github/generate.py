#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jinja2",
# ]
# ///
"""Generate README.md from plugins/*.json files using README_TEMPLATE.md."""

import json
import sys
from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def load_plugins(plugins_dir: Path) -> dict[str, list[dict]]:
    """Load all plugin JSON files and group them by category."""
    categories = defaultdict(list)

    for json_file in plugins_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                plugin_data = json.load(f)
                category = plugin_data.get("category", "uncategorized")
                categories[category].append(plugin_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing {json_file}: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {json_file}: {e}", file=sys.stderr)
            sys.exit(1)

    return categories


def validate_plugin(plugin: dict, filename: str) -> bool:
    """Validate required fields in plugin data."""
    required_fields = ["name", "capabilities", "category", "repo", "author",
                      "description", "dependencies", "compositors", "distro"]

    missing_fields = [field for field in required_fields if field not in plugin]

    if missing_fields:
        print(f"Validation error in {filename}: Missing required fields: {', '.join(missing_fields)}",
              file=sys.stderr)
        return False

    return True


def validate_all_plugins(plugins_dir: Path) -> bool:
    """Validate all plugin JSON files."""
    all_valid = True
    seen_ids = {}
    seen_names = {}

    for json_file in plugins_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                plugin_data = json.load(f)
                if not validate_plugin(plugin_data, json_file.name):
                    all_valid = False

                # Check for duplicate IDs
                plugin_id = plugin_data.get("id")
                if plugin_id:
                    if plugin_id in seen_ids:
                        print(f"Duplicate ID '{plugin_id}' found in {json_file.name} "
                              f"(previously in {seen_ids[plugin_id]})", file=sys.stderr)
                        all_valid = False
                    else:
                        seen_ids[plugin_id] = json_file.name

                # Check for duplicate names
                plugin_name = plugin_data.get("name")
                if plugin_name:
                    if plugin_name in seen_names:
                        print(f"Duplicate name '{plugin_name}' found in {json_file.name} "
                              f"(previously in {seen_names[plugin_name]})", file=sys.stderr)
                        all_valid = False
                    else:
                        seen_names[plugin_name] = json_file.name

        except json.JSONDecodeError as e:
            print(f"JSON parse error in {json_file}: {e}", file=sys.stderr)
            all_valid = False
        except Exception as e:
            print(f"Error reading {json_file}: {e}", file=sys.stderr)
            all_valid = False

    return all_valid


def generate_readme(validate_only: bool = False) -> int:
    """Generate README.md from template and plugin data."""
    repo_root = Path(__file__).parent.parent
    plugins_dir = repo_root / "plugins"
    template_file = repo_root / "README_TEMPLATE.md"
    output_file = repo_root / "README.md"

    # Validate all plugins
    if not validate_all_plugins(plugins_dir):
        return 1

    if validate_only:
        print("Validation successful!")
        return 0

    # Load plugins and group by category
    categories_dict = load_plugins(plugins_dir)

    # Sort categories by name and plugins within each category by name
    sorted_categories = sorted(categories_dict.keys())

    categories = []
    for category_name in sorted_categories:
        plugins = sorted(categories_dict[category_name], key=lambda p: p.get("name", ""))
        categories.append({
            "name": category_name.title(),
            "plugins": plugins
        })

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(repo_root))
    template = env.get_template("README_TEMPLATE.md")

    # Render template
    try:
        rendered = template.render(categories=categories)
    except Exception as e:
        print(f"Error rendering template: {e}", file=sys.stderr)
        return 1

    # Write output
    try:
        with open(output_file, "w") as f:
            f.write(rendered)
        print(f"Successfully generated {output_file}")
        return 0
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    validate_only = "--validate" in sys.argv
    sys.exit(generate_readme(validate_only))
