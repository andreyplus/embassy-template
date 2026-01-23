#!/usr/bin/env python3
"""
Script to auto-generate chip choices from stm32-data-generated.
Fetches the Cargo.toml directly from GitHub and updates cargo-generate.toml.
"""

import re
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError


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


def extract_stm32_chips(cargo_toml_content):
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

    # Method 2: Extract all stm32* patterns that look like chip names
    # Pattern: stm32 + family letter + number + variant letters/numbers
    # pattern = r"\bstm32[a-z][0-9][a-z0-9]{2,}\b"
    # matches = re.findall(pattern, cargo_toml_content)
    # for match in matches:
    #     if re.match(r"^stm32[a-z][0-9][a-z0-9]+$", match):
    #         chips.add(match)

    return sorted(chips)


def get_non_stm32_chips():
    """Return list of non-STM32 chips to preserve."""
    return [
        "esp32c3",
        "nrf9151",
        "nrf9160",
        "nrf54l15",
        "nrf52833",
        "nrf52840",
        "rp2040",
        "rp2350a",
        "rp2350b",
        "rp2354a",
        "rp2354b",
    ]


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

    # Extract STM32 chips
    print("Extracting STM32 chip names...")
    stm32_chips = extract_stm32_chips(cargo_toml_content)

    if not stm32_chips:
        print("Error: No STM32 chips found!", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(stm32_chips)} STM32 chips")

    # Get non-STM32 chips
    non_stm32_chips = get_non_stm32_chips()

    # Combine and sort all chips
    all_chips = sorted(non_stm32_chips + stm32_chips)

    print(f"Total chips (including non-STM32): {len(all_chips)}\n")

    # Update cargo-generate.toml
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    cargo_generate_toml = repo_dir / "cargo-generate.toml"

    print(f"Updating {cargo_generate_toml}...")
    update_cargo_generate_toml(cargo_generate_toml, all_chips)

    print("\n✓ Successfully updated chip choices in cargo-generate.toml\n")


if __name__ == "__main__":
    main()
