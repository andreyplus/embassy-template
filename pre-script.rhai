let chip = variable::get("chip");
let chip_upper = chip.to_upper();

variable::set("probe_chip", chip_upper);

let mappings = [
    ["thumbv6m-none-eabi", ["STM32C0", "STM32F0", "STM32G0", "STM32L0", "STM32U0", "STM32WB0"]],
    ["thumbv7m-none-eabi", ["STM32F1", "STM32F2", "STM32L1"]],
    ["thumbv7em-none-eabihf", ["STM32F3", "STM32F4", "STM32F7", "STM32G4", "STM32H7", "STM32L4", "STM32WB", "STM32WL"]],
    ["thumbv8m.main-none-eabihf", ["STM32H5", "STM32L5", "STM32U3", "STM32U5", "STM32WBA"]],
];

let rust_target = ();

for m in mappings {
    let target = m[0];
    let prefixes = m[1];

    for p in prefixes {
        if chip_upper.starts_with(p) {
            rust_target = target;
            break;
        }
    }

    if rust_target != () {
        break;
    }
}

if rust_target == () {
    throw `Unknown rust target: ${chip}`;
}

variable::set("rust_target", rust_target);
