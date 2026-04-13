let chip = variable::get("chip");

let mappings = [
    ["STM32C0", "thumbv6m-none-eabi"],
    ["STM32F0", "thumbv6m-none-eabi"],
    ["STM32G0", "thumbv6m-none-eabi"],
    ["STM32L0", "thumbv6m-none-eabi"],
    ["STM32U0", "thumbv6m-none-eabi"],
    ["STM32WB0", "thumbv6m-none-eabi"],

    ["STM32F1", "thumbv7m-none-eabi"],
    ["STM32F2", "thumbv7m-none-eabi"],
    ["STM32L1", "thumbv7m-none-eabi"],

    ["STM32F3", "thumbv7em-none-eabihf"],
    ["STM32F4", "thumbv7em-none-eabihf"],
    ["STM32F7", "thumbv7em-none-eabihf"],
    ["STM32G4", "thumbv7em-none-eabihf"],
    ["STM32H7", "thumbv7em-none-eabihf"],
    ["STM32L4", "thumbv7em-none-eabihf"],
    ["STM32WB", "thumbv7em-none-eabihf"],
    ["STM32WL", "thumbv7em-none-eabihf"],

    ["STM32H5", "thumbv8m.main-none-eabihf"],
    ["STM32L5", "thumbv8m.main-none-eabihf"],
    ["STM32U3", "thumbv8m.main-none-eabihf"],
    ["STM32U5", "thumbv8m.main-none-eabihf"],
    ["STM32WBA", "thumbv8m.main-none-eabihf"],
];

let rust_target = ();

for m in mappings {
    let prefix = m[0];
    let target = m[1];

    if chip.starts_with(prefix) {
        rust_target = target;
        break;
    }
}

if rust_target == () {
    throw `Unknown rust target: ${chip}`;
}

variable::set("rust_target", rust_target);
