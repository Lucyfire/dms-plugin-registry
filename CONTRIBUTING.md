# Contributing a Plugin

Thank you for contributing to the Dank Material Shell Plugins registry!

## How to Add Your Plugin

1. **Fork this repository**

2. **Create a new JSON file** in the `plugins/` directory following this naming convention:
   ```
   plugins/{github-username}-{plugin-name}.json
   ```
   - Use lowercase letters
   - Separate words with hyphens
   - Examples: `daniel-42-z-powerusage.json`, `rochacbruno-worldclock.json`

3. **Fill in your plugin information** using the schema below:

```json
{
    "name": "PluginName",
    "capabilities": ["dankbar-widget"],
    "category": "monitoring",
    "repo": "https://github.com/yourusername/your-plugin-repo",
    "path": "optional/path/in/monorepo",
    "author": "Your Name",
    "description": "Brief description of what your plugin does",
    "dependencies": ["dependency1", "dependency2"],
    "compositors": ["niri", "hyprland"],
    "distro": ["any"],
    "screenshot": "https://url/to/screenshot.png"
}
```

### Field Descriptions

- **name** (required): Display name of your plugin
- **capabilities** (required): Array of capabilities, e.g., `["dankbar-widget"]`
- **category** (required): One of: `monitoring`, `utilities`, `appearance`, `system`, etc.
- **repo** (required): Full GitHub URL to your plugin repository
- **path** (optional): If your plugin is in a monorepo, specify the subdirectory path
- **author** (required): Your name or GitHub username
- **description** (required): Clear, concise description of the plugin's purpose
- **dependencies** (required): Array of dependencies, use `[]` if none
- **compositors** (required): Supported Wayland compositors: `["niri", "hyprland"]`, etc.
- **distro** (required): Supported distributions: `["any"]`, `["fedora"]`, `["arch"]`, etc.
- **screenshot** (optional): Direct URL to a screenshot image

4. **Validate your JSON** - Ensure:
   - Valid JSON syntax (no trailing commas)
   - All required fields are present
   - Arrays use proper formatting
   - URLs are complete and correct

5. **Submit a Pull Request**
   - Commit your JSON file
   - Push to your fork
   - Create a PR to this repository
   - Include a brief description of your plugin in the PR

## Guidelines

- Keep descriptions concise and informative
- Ensure your repository has proper documentation
- Test that your plugin works with the specified compositors and distros
- Include a screenshot when possible to showcase your plugin

## Questions?

If you have questions about the contribution process, please open an issue in this repository.
