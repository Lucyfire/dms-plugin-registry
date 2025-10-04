# Dank Material Shell Plugins

This repository contains a collection of plugins for [Dank Material Shell](https://github.com/AvengeMedia/DankMaterialShell)

## Contributing

To add your Plugin to the list please read the [contribution guidelines](CONTRIBUTING.md) and create a pull request.

## Installing Plugins

To install a plugin clone the plugin repository into your `~/.config/DankMaterialShell/plugins/` folder and restart your dms session with `dms restart`. NOTE: Some plugins may have additional dependencies that need to be installed manually, please refer to the plugin documentation for more information, some plugins are part of a monorepo and need to be installed by copying the relvant path to the plugins folder.

## Plugins

{% for category in categories %}
### {{ category.name }}

{% for plugin in category.plugins %}
#### [{{ plugin.name }}]({{ plugin.repo }})

{{ plugin.description }}

- author: {{ plugin.author }}
- compositors: {{ plugin.compositors | join(", ") }}
- capabilities: {{ plugin.capabilities | join(", ") }}
- dependencies: {{ plugin.dependencies | join(", ") }}
- distro: {{ plugin.distro | join(", ") }}

{% if plugin.path %}

> [!NOTE]
> This plugin is part of a monorepo, please copy the contents of the [{{ plugin.path }}]({{ plugin.repo }}/tree/main/{{ plugin.path }}) folder to your `~/.config/DankMaterialShell/plugins/` folder.

{% endif %}

{% if plugin.screenshot %}

<details>
<summary>Screenshot</summary>

![screenshot]({{ plugin.screenshot }})

</details>

{% endif %}

{% endfor %}

----

{% endfor %}
