# BrandIt - KRunner Plugin

A customizable KRunner plugin for Plasma 6 that provides a quick way to copy formatted text patterns to your clipboard.

Based on the great work of [Jim Cornmell](https://github.com/jimcornmell/scriptRunner).

## Features

When you type `!<keyword>` in KRunner, it will offer to copy predefined text patterns to your clipboard. The patterns are fully customizable through a YAML configuration file.

### Examples

| What you type | What gets copied (default) | What gets copied (customizable) |
|---------------|-----------------------------|----------------------------------|
| !slack        | :slack: Slack               | Can be customized               |
| !bug          | :bug: bug                   | 🐛 Bug:                          |
| !meeting      | :meeting: meeting           | 📅 Meeting Notes - meeting       |
| !github       | :github: GitHub             | Can be customized               |
| !anykeyword   | :anykeyword: anykeyword     | Uses default pattern             |

## Requirements

- KDE Plasma 6
- Python 3
- PyYAML (`python3-yaml` or `pip install pyyaml`)
- `wl-clipboard` (for clipboard functionality on Wayland)
- KRunner

## Installation

Run these commands to install:

```bash
cd ~/.local/share/kio
git clone git@github.com:margual56/krunner_brandit.git
cd krunner_brandit
./install.sh
```

The installation script will:
1. Install the plugin files to the appropriate locations
2. Check for and install dependencies if needed
3. Copy the configuration file to `~/.config/brandIt/config.yaml`
4. Register the D-Bus service
5. Restart KRunner to load the plugin

## Configuration

The plugin uses a YAML configuration file located at `~/.config/brandIt/config.yaml`.

### Configuration Structure

```yaml
# Default pattern for unknown keywords
# {brand} will be replaced with the typed keyword
default_pattern: ":{brand}: {brand}"

# Custom patterns for specific keywords
patterns:
  slack: ":slack: Slack"
  github: ":github: GitHub"
  bug: "🐛 Bug:"
  feature: "✨ Feature:"
  meeting: "📅 Meeting Notes - {brand}"
```

### Customizing Patterns

1. Edit the config file: `~/.config/brandIt/config.yaml`
2. Add your own patterns under the `patterns:` section
3. Use `{brand}` as a placeholder for the keyword itself
4. Save the file - changes take effect immediately

### Pattern Examples

```yaml
patterns:
  # Simple replacements
  python: ":python: Python"

  # Emoji shortcuts
  bug: "🐛"
  star: "⭐"
  fire: "🔥"

  # Text templates
  pr: "Pull Request #{brand}"
  issue: "Issue #{brand}:"
  todo: "TODO: {brand}"

  # Meeting notes
  standup: "📅 Daily Standup - {brand}"
  retro: "📋 Retrospective Notes - {brand}"

  # Commit message prefixes
  fix: "fix: {brand}"
  feat: "feat: {brand}"
  docs: "docs: {brand}"
```

## Usage

1. Open KRunner (usually `Alt+Space` or `Alt+F2`)
2. Type `!` followed by a keyword (e.g., `!slack`, `!bug`, `!meeting`)
3. Press Enter to copy the formatted text to your clipboard
4. Paste anywhere you need it

### Tips

- Keywords are case-insensitive (`!SLACK` and `!slack` both work)
- Custom patterns have higher priority in search results
- Unknown keywords use the default pattern
- A notification confirms when text is copied

## Debugging

If the plugin doesn't work:

1. Check the debug log: `tail -f /tmp/brandit_debug.log`
2. Verify dependencies are installed:
   ```bash
   python3 -c "import yaml"  # Should not error
   which wl-copy             # Should show path
   ```
3. Restart KRunner manually:
   ```bash
   kquitapp6 krunner
   kstart6 --windowclass krunner krunner
   ```

## Uninstallation

To remove the plugin:

```bash
cd ~/.local/share/kio/BrandIt
./uninstall.sh
```

This will remove the plugin files but preserve your configuration file at `~/.config/brandIt/config.yaml`.

## File Structure

- `main.py` - The main plugin code
- `config.yaml` - Default configuration template
- `BrandIt.desktop` - KRunner service definition
- `install.sh` - Installation script
- `uninstall.sh` - Uninstallation script
- `~/.config/brandIt/config.yaml` - Your personal configuration (created on install)

## Technical Details

- Uses D-Bus to communicate with KRunner
- Written in Python 3 with PyYAML for configuration
- Uses `wl-copy` from `wl-clipboard` for Wayland clipboard operations
- Falls back to KDE's Klipper if `wl-copy` is unavailable
- Shows desktop notifications when text is copied

## License

GNU General Public License v3.0

## Author

Jim Cornmell - brandIt@cornmell.com

## Contributing

Feel free to submit issues or pull requests at https://github.com/jimcornmell/BrandIt

### Ideas for Contributions

- Support for multiple configuration profiles
- Import/export configuration
- GUI configuration editor
- Integration with other clipboard managers
- Support for rich text/HTML
 copying
