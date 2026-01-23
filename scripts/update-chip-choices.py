#!/usr/bin/env python3
"""
Script to auto-generate chip choices from stm32-data-generated.
Fetches the Cargo.toml directly from GitHub and updates cargo-generate.toml and pre-script.rhai.
"""

import re
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from typing import Dict, List, Optional

NON_STM32_CHIPS = [
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

# Non-STM32 chip configurations for pre-script.rhai
NON_STM32_CONFIGS = {
    "rp2040": {
        "arch": "arm",
        "rust_target": "thumbv6m-none-eabi",
        "flash_start": "0x10000100",
        "flash_size": "2048K - 0x100",
        "ram_start": "0x20000000",
        "ram_size": "264K",
        "probe_chip": "RP2040",
    },
    "nrf52833": {
        "arch": "arm",
        "rust_target": "thumbv7em-none-eabihf",
        "probe_chip": "nRF52833_xxAA",
        "flash_start": "0x00000000",
        "flash_size": "512K",
        "ram_start": "0x20000000",
        "ram_size": "128K",
    },
    "nrf52840": {
        "arch": "arm",
        "rust_target": "thumbv7em-none-eabihf",
        "probe_chip": "nRF52840_xxAA",
        "flash_start": "0x00000000",
        "flash_size": "1024K",
        "ram_start": "0x20000000",
        "ram_size": "256K",
    },
    "nrf54l15": {
        "arch": "arm",
        "rust_target": "thumbv8m.main-none-eabihf",
        "probe_chip": "nRF54L15",
        "flash_start": "0x00000000",
        "flash_size": "1524K",
        "ram_start": "0x20000000",
        "ram_size": "256K",
    },
    "nrf9160": {
        "arch": "arm",
        "rust_target": "thumbv8m.main-none-eabihf",
        "probe_chip": "nRF9160_xxAA",
        "flash_start": "0x00000000",
        "flash_size": "1024K",
        "ram_start": "0x20010000",
        "ram_size": "192K",
    },
    "nrf9151": {
        "arch": "arm",
        "rust_target": "thumbv8m.main-none-eabihf",
        "probe_chip": "nRF9160_xxAA",
        "flash_start": "0x00000000",
        "flash_size": "1024K",
        "ram_start": "0x20010000",
        "ram_size": "192K",
    },
    "rp2350": {
        "arch": "arm",
        "rust_target": "thumbv8m.main-none-eabihf",
        "flash_start": "0x10000000",
        "flash_size": "4096K",
        "ram_start": "0x20000000",
        "ram_size": "512K",
        "probe_chip": "RP235x",
    },
    "rp2354": {
        "arch": "arm",
        "rust_target": "thumbv8m.main-none-eabihf",
        "flash_start": "0x10000000",
        "flash_size": "2048K",
        "ram_start": "0x20000000",
        "ram_size": "512K",
        "probe_chip": "RP235x",
    },
    "esp32c3": {
        "arch": "riscv",
        "rust_target": "riscv32imc-unknown-none-elf",
        "probe_chip": "esp32c3",
    },
}


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
    return NON_STM32_CHIPS


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


def fetch_metadata(chip: str, commit: str = "main") -> Optional[Dict]:
    """Fetch metadata.rs for a specific STM32 chip."""
    url = f"https://raw.githubusercontent.com/embassy-rs/stm32-data-generated/{commit}/stm32-metapac/src/chips/{chip}/metadata.rs"

    try:
        with urlopen(url) as response:
            content = response.read().decode("utf-8")
            return parse_metadata(content, chip)
    except URLError:
        return None


def parse_metadata(content: str, chip: str) -> Dict:
    """Parse metadata.rs content to extract chip configuration."""
    config = {
        "arch": "arm",
        "rust_target": None,
        "flash_start": None,
        "flash_size": None,
        "ram_start": None,
        "ram_size": None,
        "probe_chip": None,
    }

    # Extract chip name for probe_chip
    name_match = re.search(r'name:\s*"([^"]+)"', content)
    if name_match:
        config["probe_chip"] = name_match.group(1)

    # Determine rust target based on chip family
    chip_upper = chip.upper()
    if (
        chip_upper.startswith("STM32F0")
        or chip_upper.startswith("STM32G0")
        or chip_upper.startswith("STM32C0")
        or chip_upper.startswith("STM32L0")
    ):
        config["rust_target"] = "thumbv6m-none-eabi"
    elif (
        chip_upper.startswith("STM32F1")
        or chip_upper.startswith("STM32F2")
        or chip_upper.startswith("STM32L1")
    ):
        config["rust_target"] = "thumbv7m-none-eabi"
    else:
        config["rust_target"] = "thumbv7em-none-eabihf"

    # Find flash memory region (BANK_1 or FLASH)
    flash_match = re.search(
        r'name:\s*"(?:BANK_1|FLASH)".*?kind:\s*MemoryRegionKind::Flash.*?address:\s*(0x[0-9a-fA-F]+).*?size:\s*(\d+)',
        content,
        re.DOTALL,
    )
    if flash_match:
        flash_addr = int(flash_match.group(1), 16)
        flash_size = int(flash_match.group(2))
        config["flash_start"] = f"0x{flash_addr:08X}"
        config["flash_size"] = format_size(flash_size)

        # Check for BANK_2 and add to total flash size
        bank2_match = re.search(
            r'name:\s*"BANK_2".*?kind:\s*MemoryRegionKind::Flash.*?address:\s*0x[0-9a-fA-F]+.*?size:\s*(\d+)',
            content,
            re.DOTALL,
        )
        if bank2_match:
            bank2_size = int(bank2_match.group(1))
            total_flash = flash_size + bank2_size
            config["flash_size"] = format_size(total_flash)

    # Find RAM memory region (DTCM, SRAM, or RAM)
    # Priority: DTCM > SRAM1 > SRAM > RAM
    ram_patterns = [
        (
            r'name:\s*"DTCM".*?kind:\s*MemoryRegionKind::Ram.*?address:\s*(0x[0-9a-fA-F]+).*?size:\s*(\d+)',
            "DTCM",
        ),
        (
            r'name:\s*"SRAM1".*?kind:\s*MemoryRegionKind::Ram.*?address:\s*(0x[0-9a-fA-F]+).*?size:\s*(\d+)',
            "SRAM1",
        ),
        (
            r'name:\s*"SRAM".*?kind:\s*MemoryRegionKind::Ram.*?address:\s*(0x[0-9a-fA-F]+).*?size:\s*(\d+)',
            "SRAM",
        ),
        (
            r'name:\s*"RAM".*?kind:\s*MemoryRegionKind::Ram.*?address:\s*(0x[0-9a-fA-F]+).*?size:\s*(\d+)',
            "RAM",
        ),
    ]

    for pattern, name in ram_patterns:
        ram_match = re.search(pattern, content, re.DOTALL)
        if ram_match:
            ram_addr = int(ram_match.group(1), 16)
            ram_size = int(ram_match.group(2))
            config["ram_start"] = f"0x{ram_addr:08X}"
            config["ram_size"] = format_size(ram_size)
            break

    return config


def format_size(size_bytes: int) -> str:
    """Format size in bytes to KB."""
    size_kb = size_bytes // 1024
    return f"{size_kb}K"


def fetch_stm32_configs(chips: List[str], sample_size: int = 10) -> Dict[str, Dict]:
    """Fetch metadata for a sample of STM32 chips to generate configurations."""
    print("\nFetching metadata for sample STM32 chips (this may take a moment)...")

    configs = {}

    # Sample chips from different families
    families = {}
    for chip in chips:
        family = chip[:7]  # e.g., "stm32f1", "stm32h7"
        if family not in families:
            families[family] = []
        families[family].append(chip)

    # Take first chip from each family, up to sample_size
    sampled = []
    for family, family_chips in sorted(families.items()):
        if len(sampled) < sample_size:
            sampled.append(family_chips[0])

    # If we don't have enough, add more
    if len(sampled) < sample_size:
        for chip in chips:
            if chip not in sampled and len(sampled) < sample_size:
                sampled.append(chip)

    for i, chip in enumerate(sampled, 1):
        print(f"  [{i}/{len(sampled)}] Fetching {chip}...", end=" ")
        config = fetch_metadata(chip)
        if config:
            configs[chip] = config
            print("✓")
        else:
            print("✗ (skipped)")

    return configs


def generate_rhai_config(configs: Dict[str, Dict]) -> str:
    """Generate Rhai configuration for targets."""
    lines = ["let targets = #{"]

    # Add non-STM32 configs first
    for chip, config in NON_STM32_CONFIGS.items():
        lines.append(f"    {chip}: #{{{format_rhai_map(config)}}},")
        lines.append("")

    # Add STM32 configs
    for chip, config in sorted(configs.items()):
        lines.append(f"    {chip}: #{{{format_rhai_map(config)}}},")
        lines.append("")

    lines.append("};")
    lines.append("")
    lines.append('let target = variable::get("chip");')
    lines.append("")
    lines.append("// Collapse RP235x `chip` variants to either:")
    lines.append('//     "rp2350" (typically Pico 2 (w/4MB external flash)) or')
    lines.append('//     "rp2354" (w/2MB on-die flash)')
    lines.append('let valid_rp2350_variants = ["rp2350a", "rp2350b"];')
    lines.append('let valid_rp2354_variants = ["rp2354a", "rp2354b"];')
    lines.append("")
    lines.append("if valid_rp2350_variants.contains(target) {")
    lines.append('    target = "rp2350";')
    lines.append("} else if valid_rp2354_variants.contains(target) {")
    lines.append('    target = "rp2354";')
    lines.append("}")
    lines.append("")
    lines.append("// Get target properties, or use default STM32 config if not found")
    lines.append("let target_properties = if targets.contains(target) {")
    lines.append("    targets.get(target)")
    lines.append('} else if target.starts_with("stm32") {')
    lines.append(
        "    // Default STM32 config - memory layout will be overridden by stm32-metapac at build time"
    )
    lines.append("    let chip_upper = target.to_upper();")
    lines.append(
        '    let rust_target = if chip_upper.starts_with("STM32F0") || chip_upper.starts_with("STM32G0") || chip_upper.starts_with("STM32C0") || chip_upper.starts_with("STM32L0") {'
    )
    lines.append('        "thumbv6m-none-eabi"')
    lines.append(
        '    } else if chip_upper.starts_with("STM32F1") || chip_upper.starts_with("STM32F2") || chip_upper.starts_with("STM32L1") {'
    )
    lines.append('        "thumbv7m-none-eabi"')
    lines.append("    } else {")
    lines.append('        "thumbv7em-none-eabihf"')
    lines.append("    };")
    lines.append("    ")
    lines.append("    #{")
    lines.append('        arch: "arm",')
    lines.append("        rust_target: rust_target,")
    lines.append('        flash_start: "0x08000000",')
    lines.append('        flash_size: "1024K",')
    lines.append('        ram_start: "0x20000000",')
    lines.append('        ram_size: "128K",')
    lines.append("        probe_chip: chip_upper")
    lines.append("    }")
    lines.append("} else {")
    lines.append("    throw `Unknown chip: ${target}`;")
    lines.append("};")
    lines.append("")
    lines.append("for key in target_properties.keys() {")
    lines.append("    variable::set(key, target_properties.get(key));")
    lines.append("}")

    return "\n".join(lines)


def format_rhai_map(config: Dict) -> str:
    """Format a config dict as Rhai map entries."""
    entries = []
    for key, value in config.items():
        if value is not None:
            entries.append(f'\n        {key}: "{value}"')
    return ",".join(entries) + "\n    "


def update_pre_script_rhai(file_path: Path, configs: Dict[str, Dict]):
    """Update pre-script.rhai with new target configurations."""
    rhai_content = generate_rhai_config(configs)
    file_path.write_text(rhai_content)
    print(f"✓ Updated {file_path}")


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

    # Fetch metadata for sample STM32 chips
    stm32_configs = fetch_stm32_configs(stm32_chips, sample_size=20)

    # Update pre-script.rhai
    pre_script_rhai = repo_dir / "pre-script.rhai"
    print(f"\nUpdating {pre_script_rhai}...")
    update_pre_script_rhai(pre_script_rhai, stm32_configs)

    print("\n✓ Successfully updated chip choices and configurations\n")
    print(
        f"Note: Generated configurations for {len(stm32_configs)} sample STM32 chips."
    )
    print(
        "Other STM32 chips will use the configuration from their matching sample chip."
    )


if __name__ == "__main__":
    main()
