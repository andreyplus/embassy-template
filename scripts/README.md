# STM32 Chip Auto-Generation Scripts

This directory contains scripts to automatically generate chip choices and configurations from the [stm32-data-generated](https://github.com/embassy-rs/stm32-data-generated) repository.

## Overview

The `update-chip-choices.py` script performs the following tasks:

1. **Fetches STM32 chip list**: Downloads the `Cargo.toml` from stm32-data-generated and extracts all STM32 chip names
2. **Updates cargo-generate.toml**: Updates the `choices` array with all available chips (STM32 + non-STM32)
3. **Fetches chip metadata**: Downloads metadata for a representative sample of STM32 chips
4. **Generates pre-script.rhai**: Creates Rhai configuration with chip-specific settings (flash/RAM layout, Rust target, etc.)

## Usage

Run the script from the repository root:

```bash
python3 scripts/update-chip-choices.py
```

The script will:
- Fetch data from GitHub (no authentication required)
- Update `cargo-generate.toml` with ~1300+ chip choices
- Update `pre-script.rhai` with configurations for 20 sample STM32 chips from different families
- Take approximately 15-45 seconds to complete

## How It Works

### 1. Chip List Generation

The script extracts STM32 chip names from the `[features]` section of stm32-metapac's Cargo.toml:

```toml
[features]
stm32f401re = []
stm32h743zi = []
# ... etc
```

### 2. Metadata Parsing

For each sample chip, the script:
- Downloads `metadata.rs` from `stm32-metapac/src/chips/{chip}/metadata.rs`
- Extracts memory regions (Flash, RAM addresses and sizes)
- Determines the correct Rust target triple based on chip family
- Extracts the official chip name for probe-rs

Example metadata structure:
```rust
MemoryRegion {
    name: "BANK_1",
    kind: MemoryRegionKind::Flash,
    address: 0x8000000,
    size: 1048576,
    settings: Some(FlashSettings { ... }),
}
```

### 3. Fallback Configuration

The generated `pre-script.rhai` includes intelligent fallback logic:

- **Explicitly configured chips**: Use fetched metadata (20 sample chips)
- **Other STM32 chips**: Use family-based defaults (correct Rust target, generic memory layout)
- **Unknown chips**: Throw an error

The actual memory layout is determined by stm32-metapac at build time, so the defaults are just for initial configuration.

## Configuration

### Non-STM32 Chips

Non-STM32 chip configurations (RP2040, nRF, ESP32) are hardcoded in the script's `NON_STM32_CONFIGS` dictionary. To add a new non-STM32 chip:

1. Add the chip name to `NON_STM32_CHIPS` list
2. Add the configuration to `NON_STM32_CONFIGS` dictionary
3. Run the script to regenerate

### Sample Size

By default, the script fetches metadata for 20 STM32 chips (one from each major family). To change this, modify the `sample_size` parameter in the `main()` function:

```python
stm32_configs = fetch_stm32_configs(stm32_chips, sample_size=20)
```

**Note**: Fetching all chips would take hours and isn't necessary since stm32-metapac provides the actual memory layouts at build time.

## Memory Region Priority

When parsing metadata, the script uses this priority for RAM regions:

1. **DTCM** (Tightly-Coupled Memory on Cortex-M7)
2. **SRAM1** (Primary SRAM on multi-bank chips)
3. **SRAM** (Generic SRAM)
4. **RAM** (Fallback)

For Flash, it looks for:
1. **BANK_1** (primary flash bank)
2. **BANK_2** (if present, adds to total size)
3. **FLASH** (generic flash region)

## Rust Target Mapping

The script determines the Rust target triple based on chip family:

| Chip Family | Rust Target | Architecture |
|-------------|-------------|--------------|
| STM32F0, G0, C0, L0 | `thumbv6m-none-eabi` | Cortex-M0/M0+ |
| STM32F1, F2, L1 | `thumbv7m-none-eabi` | Cortex-M3 |
| All others | `thumbv7em-none-eabihf` | Cortex-M4/M7 with FPU |

## Files Modified

- `cargo-generate.toml`: Chip choices array
- `pre-script.rhai`: Target configurations

## Dependencies

The script requires only Python 3 standard library modules:
- `re` - Regular expressions
- `urllib` - HTTP requests
- `pathlib` - Path manipulation

No external dependencies needed!

## Maintenance

Run this script periodically (e.g., monthly) or when Embassy/stm32-data-generated adds new chips:

```bash
cd /path/to/embassy-template
python3 scripts/update-chip-choices.py
git diff  # Review changes
git commit -am "Update STM32 chip list"
```

## Troubleshooting

### Script fails to fetch data

Check your internet connection and verify the stm32-data-generated repository is accessible:
```bash
curl -I https://raw.githubusercontent.com/embassy-rs/stm32-data-generated/main/stm32-metapac/Cargo.toml
```

### Parsing errors

If the metadata format changes in stm32-data-generated, the regex patterns may need updating. Check the `parse_metadata()` function.

### Missing chips

If specific chips are missing, they may not be in the latest stm32-data-generated release. The repository is updated regularly by the Embassy team.
