#!/bin/bash
set -e

prefix="${XDG_DATA_HOME:-$HOME/.local/share}"
krunner_dbusdir="$prefix/krunner/dbusplugins"
services_dir="$prefix/dbus-1/services/"
config_dir="$HOME/.config/brandIt"

echo "Installing BrandIt plugin..."

# Kill any existing instances of the plugin
echo "Stopping any running instances..."
pkill -f "main.py" 2>/dev/null || true
pkill -f "org.kde.BrandIt" 2>/dev/null || true

# Stop KRunner
echo "Stopping KRunner..."
kquitapp6 krunner 2>&1 | grep -v "Message recipient disconnected from message bus without replying" || true
sleep 1

# Clean up old installations
echo "Cleaning up old installations..."
rm -f "$services_dir/org.kde.BrandIt.service"
rm -f "$krunner_dbusdir/BrandIt.desktop"

# Clear KRunner cache
echo "Clearing KRunner cache..."
rm -rf ~/.cache/krunnerplugins 2>/dev/null || true
rm -rf ~/.cache/krunner 2>/dev/null || true

# Create necessary directories
mkdir -p $krunner_dbusdir
mkdir -p $services_dir
mkdir -p $config_dir

# Check if PyYAML is installed
echo "Checking dependencies..."
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "Warning: PyYAML is not installed. Installing it..."

    # Try pip first (user install)
    if command -v pip3 &> /dev/null; then
        pip3 install --user pyyaml
    elif command -v pip &> /dev/null; then
        pip install --user pyyaml
    else
        echo "Error: pip is not installed. Please install PyYAML manually:"
        echo "  - Ubuntu/Debian: sudo apt-get install python3-yaml"
        echo "  - Fedora: sudo dnf install python3-pyyaml"
        echo "  - Arch: sudo pacman -S python-yaml"
        echo "  - Or use pip: pip3 install pyyaml"
        exit 1
    fi
fi

# Check if wl-clipboard is installed
if ! command -v wl-copy &> /dev/null; then
    echo "Warning: wl-copy is not installed. Installing it is recommended for clipboard functionality."
    echo "You can install it with:"
    echo "  - Ubuntu/Debian: sudo apt-get install wl-clipboard"
    echo "  - Fedora: sudo dnf install wl-clipboard"
    echo "  - Arch: sudo pacman -S wl-clipboard"
fi

# Install plugin files
echo "Installing plugin files..."
cp BrandIt.desktop $krunner_dbusdir/

# Create service file with absolute path to main.py
echo "Creating service file..."
cat > "$services_dir/org.kde.BrandIt.service" << EOF
[D-BUS Service]
Name=org.kde.BrandIt
Exec=$PWD/main.py
EOF

# Make main.py executable
chmod +x main.py

# Copy config file to user's config directory
if [[ -f "$config_dir/config.yaml" ]]; then
    echo "Config file already exists at $config_dir/config.yaml"
    echo "Creating backup at $config_dir/config.yaml.backup"
    cp "$config_dir/config.yaml" "$config_dir/config.yaml.backup"
    echo "NOTE: Your existing config is preserved. Delete it if you want the new default patterns."
else
    echo "Installing config file to $config_dir/config.yaml"
    cp config.yaml "$config_dir/config.yaml"
fi

# Clear debug log
echo "Clearing debug log..."
rm -f /tmp/brandit_debug.log

# Update KRunner's database
echo "Updating KRunner database..."
kbuildsycoca6 --noincremental 2>/dev/null || true

# Start KRunner
echo "Starting KRunner..."
kstart6 --windowclass krunner krunner > /dev/null 2>&1 &
sleep 2

# Test if the plugin is registered
echo "Verifying installation..."
if qdbus org.kde.krunner /App org.kde.krunner.App.loadedRunnerIds 2>/dev/null | grep -q BrandIt; then
    echo "✓ Plugin successfully registered with KRunner"
else
    echo "⚠ Plugin may not be registered yet. Try opening KRunner and typing '!test'"
fi

echo ""
echo "========================================="
echo "BrandIt plugin installed successfully!"
echo "========================================="
echo ""
echo "Configuration file: $config_dir/config.yaml"
echo "Debug log: /tmp/brandit_debug.log"
echo ""
echo "Usage: Open KRunner (Alt+Space) and type !<keyword>"
echo ""
echo "Examples:"
echo "  !slack    → copies ':slack: Slack'"
echo "  !bug      → copies '🐛 Bug:'"
echo "  !meeting  → copies '📅 Meeting Notes - meeting'"
echo ""
echo "To customize patterns, edit: $config_dir/config.yaml"
echo ""
echo "If the plugin doesn't work:"
echo "  1. Try logging out and back in"
echo "  2. Check the debug log: tail -f /tmp/brandit_debug.log"
echo "  3. Manually restart KRunner: kquitapp6 krunner && kstart6 krunner"
