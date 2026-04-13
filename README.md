# embassy-template

Simple template to generate a embassy project for a few common boards. Make sure you've run `cargo install cargo-generate` before using.

STM32 chip choices and configurations are automatically updated from [stm32-data-generated](https://github.com/embassy-rs/stm32-data-generated) via `scripts/update-chip-choices.py`.

## Usage

```
cargo generate --git https://github.com/lulf/embassy-template.git -d chip=<chip-name>
```

Then follow the instructions.

## Add new chip choices

If you want to add a new chip choice, you can add it to the `NON_STM32_CHIPS` and `NON_STM32_CONFIGS` dictionaries in `scripts/update-chip-choices.py`.

Then run `scripts/update-chip-choices.py` to update `cargo-generate.toml` and `pre-script.rhai`, or let the GitHub Actions workflow do it automatically.

Read more about the auto-generation process in [scripts/README.md](scripts/README.md).

### Targets
```
target = "thumbv6m-none-eabi"        # Cortex-M0 and Cortex-M0+
target = "thumbv7m-none-eabi"        # Cortex-M3
target = "thumbv7em-none-eabi"       # Cortex-M4 and Cortex-M7 (no FPU)
target = "thumbv7em-none-eabihf"     # Cortex-M4F and Cortex-M7F (with FPU)
target = "thumbv8m.base-none-eabi"   # Cortex-M23
target = "thumbv8m.main-none-eabi"   # Cortex-M33 (no FPU)
target = "thumbv8m.main-none-eabihf" # Cortex-M33 (with FPU)
```
