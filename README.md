# embassy-template

Simple template to generate a embassy project for a few common boards. Make sure you've run `cargo install cargo-generate` before using.

STM32 chip choices are automatically updated from [stm32-data-generated](https://github.com/embassy-rs/stm32-data-generated).

## Usage

```
cargo generate --git https://github.com/lulf/embassy-template.git
```

Then follow the instructions.

## Add new chip choices

If you want to add a new chip choice, you can add it to the `NON_STM32_CHIPS` list in `scripts/update-chip-choices.py`.

Then run the `update-chip-choices.py` script to update the `cargo-generate.toml` file or let the GitHub Actions workflow do it for you.
