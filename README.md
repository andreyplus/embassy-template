# embassy-template

Simple template to generate a embassy project for a few common boards. Make sure you've run `cargo install cargo-generate` before using.

## Usage

```
cargo generate --git gh:andreyplus/embassy-template
```

Then follow the instructions.

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
