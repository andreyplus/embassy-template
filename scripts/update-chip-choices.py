#!/usr/bin/env python3
"""
Script to auto-generate chip choices from stm32-data-generated.
Fetches the Cargo.toml directly from GitHub and update cargo-generate.toml.
"""

import re
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from typing import Dict, List, Optional

def fetch_cargo_toml():
    """Fetch stm32-metapac/Cargo.toml from GitHub."""
    url = "https://raw.githubusercontent.com/embassy-rs/stm32-data-generated/main/stm32-metapac/Cargo.toml"

    print("Fetching Cargo.toml from GitHub...")
    try:
        with urlopen(url) as response:
            return response.read().decode("utf-8")
    except URLError as e:
        print(f"Error fetching Cargo.toml: {e}", file=sys.stderr)
        sys.exit(1)


def extract_chips(cargo_toml_content):
    """Extract STM32 chip names from Cargo.toml content."""
    chips = set()

    # Method 1: Extract from [features] section
    in_features = False
    for line in cargo_toml_content.split("\n"):
        line = line.strip()
        if line.startswith("[features]"):
            in_features = True
            continue
        if line.startswith("[") and in_features:
            break
        if in_features:
            # Match feature names like: stm32f401re = []
            match = re.match(r"^\s*(stm32[a-z0-9]+)\s*=", line)
            if match:
                chip = match.group(1)
                # Validate chip name pattern: stm32 + family letter + number + variant
                if re.match(r"^stm32[a-z][0-9][a-z0-9]+$", chip):
                    chips.add(chip)

    return sorted(chips)


def update_cargo_generate_toml(file_path, all_chips):
    """Update the choices array in cargo-generate.toml."""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"Error: {file_path} not found", file=sys.stderr)
        sys.exit(1)

    # Read the file
    content = file_path.read_text()

    # Find and replace the choices line
    # Match: choices = ["chip1", "chip2", ...] (may span multiple lines)
    pattern = r"choices\s*=\s*\[[^\]]*\]"

    # Build the new choices string
    choices_str = "choices = [" + ", ".join(f'"{chip}"' for chip in all_chips) + "]"

    # Replace
    new_content = re.sub(pattern, choices_str, content, flags=re.MULTILINE)

    # Write back
    file_path.write_text(new_content)

    print(f"✓ Updated {file_path} with {len(all_chips)} chips")


def main():
    """Main function."""
    print("=== Updating chip choices from stm32-data-generated ===\n")

    # Fetch Cargo.toml from GitHub
    cargo_toml_content = fetch_cargo_toml()

    print("Extracting chip names...")
    chips = extract_chips(cargo_toml_content)

    if not chips:
        print("Error: No chips found!", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(chips)} chips")

    # Update cargo-generate.toml
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    cargo_generate_toml = repo_dir / "cargo-generate.toml"

    print(f"Updating {cargo_generate_toml}...")
    update_cargo_generate_toml(cargo_generate_toml, chips)

    print("\n✓ Successfully updated chip choices and configurations\n")


if __name__ == "__main__":
    main()
