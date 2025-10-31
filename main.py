#!/usr/bin/python3

import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import subprocess
import sys
import yaml
from pathlib import Path

# Enable debug output
DEBUG = True

def debug_log(msg):
    if DEBUG:
        with open("/tmp/brandit_debug.log", "a") as f:
            f.write(f"{msg}\n")

DBusGMainLoop(set_as_default=True)

objpath = "/runner"  # Default value for X-Plasma-DBusRunner-Path metadata property
iface = "org.kde.krunner1"


class Runner(dbus.service.Object):
    def __init__(self):
        debug_log("Initializing Runner...")
        dbus.service.Object.__init__(self, dbus.service.BusName("org.kde.BrandIt", dbus.SessionBus()), objpath)

        # Load configuration
        self.config = self.load_config()
        debug_log(f"Config loaded: {self.config is not None}")
        debug_log("Runner initialized successfully")

    def load_config(self):
        """Load configuration from YAML file"""
        config_path = Path.home() / ".config" / "brandIt" / "config.yaml"

        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    debug_log(f"Loaded config from {config_path}")
                    return config
            else:
                debug_log(f"Config file not found at {config_path}")
                # Return default config if file doesn't exist
                return {
                    'default_pattern': ':{brand}: {brand}',
                    'patterns': {}
                }
        except Exception as e:
            debug_log(f"Error loading config: {e}")
            # Return default config on error
            return {
                'default_pattern': ':{brand}: {brand}',
                'patterns': {}
            }

    def get_text_for_brand(self, brand):
        """Get the text pattern for a given brand/keyword"""
        if not self.config:
            return f":{brand}: {brand}"

        # Check if there's a specific pattern for this keyword
        patterns = self.config.get('patterns', {})
        if brand.lower() in patterns:
            pattern = patterns[brand.lower()]
            # Replace {brand} placeholder with actual brand name
            return pattern.replace('{brand}', brand)

        # Use default pattern
        default_pattern = self.config.get('default_pattern', ':{brand}: {brand}')
        return default_pattern.replace('{brand}', brand)

    @dbus.service.method(iface, in_signature='s', out_signature='a(sssida{sv})')
    def Match(self, query: str):
        """This method is used to get the matches and it returns a list of tuples"""
        debug_log(f"Match called with query: '{query}'")
        matches = []

        # Check if query starts with ! followed by a brand name
        if query.startswith('!') and len(query) > 1:
            brand = query[1:].strip()
            debug_log(f"Brand detected: '{brand}'")

            # Only show match if there's actual text after !
            if brand:
                if not self.config:
                    debug_log("Config wasn't loaded, loading now...")
                    self.config = self.load_config()
                    debug_log("Config loaded successfully")
                else:
                    debug_log(self.config)

                # Get the text pattern for this brand
                copy_text = self.get_text_for_brand(brand)
                display_text = f'Copy "{copy_text}"'

                # Check if this is a known pattern
                patterns = self.config.get('patterns', {})
                is_custom = brand.lower() in patterns

                # Create match tuple
                # (data, text, icon, type, relevance, properties)
                match = (
                    copy_text,  # data - this is what gets passed to Run
                    display_text,  # display text
                    "edit-copy",  # icon
                    100,  # type (100 = ExactMatch)
                    1.0 if is_custom else 0.9,  # higher relevance for custom patterns
                    {
                        'subtext': f'{brand}' if is_custom else 'Default pattern',
                        'category': 'Brand'
                    }
                )
                matches.append(match)
                debug_log(f"Match added: {match}")

        debug_log(f"Returning {len(matches)} matches")
        return matches

    @dbus.service.method(iface, out_signature='a(sss)')
    def Actions(self):
        debug_log("Actions called")
        # id, text, icon
        return [("copy", "Copy to clipboard", "edit-copy")]

    @dbus.service.method(iface, in_signature='ss')
    def Run(self, data: str, action_id: str):
        """Copy the formatted brand text to clipboard"""
        debug_log(f"Run called with data: '{data}', action_id: '{action_id}'")

        try:
            # Use wl-copy for Wayland
            subprocess.run(['wl-copy', data],
                                  capture_output=True,
                                  text=True,
                                  check=True)
            debug_log("wl-copy successful")

            # Optional: Send notification
            try:
                subprocess.run([
                    'notify-send',
                    'Brand Text Copied',
                    f'Copied "{data}" to clipboard',
                    '--icon=edit-copy',
                    '--expire-time=2000'
                ], check=False)
                debug_log("Notification sent")
            except Exception as e:
                debug_log(f"Notification failed: {e}")

        except subprocess.CalledProcessError as e:
            debug_log(f"wl-copy failed: {e}")
            # Fallback: try using qdbus to copy
            try:
                subprocess.run([
                    'qdbus',
                    'org.kde.klipper',
                    '/klipper',
                    'setClipboardContents',
                    data
                ], check=True)
                debug_log("Fallback to klipper successful")
            except Exception as e2:
                debug_log(f"Klipper fallback also failed: {e2}")

        except FileNotFoundError:
            debug_log("wl-copy not found")
            # Try fallback
            try:
                subprocess.run([
                    'qdbus',
                    'org.kde.klipper',
                    '/klipper',
                    'setClipboardContents',
                    data
                ], check=True)
                debug_log("Fallback to klipper successful")
            except Exception as e:
                debug_log(f"All clipboard methods failed: {e}")

    @dbus.service.method(iface)
    def Teardown(self):
        """Called when the runner should free resources"""
        debug_log("Teardown called")
        pass

    @dbus.service.method(iface)
    def ReloadConfig(self):
        """Reload the configuration file"""
        debug_log("Reloading configuration...")
        self.config = self.load_config()
        debug_log("Configuration reloaded")


if __name__ == "__main__":
    debug_log("Starting BrandIt...")
    try:
        runner = Runner()
        debug_log("Runner created, starting main loop...")
        loop = GLib.MainLoop()
        loop.run()
    except Exception as e:
        debug_log(f"Error in main: {e}")
        sys.exit(1)
