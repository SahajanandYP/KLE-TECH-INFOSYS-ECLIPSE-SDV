# ARM64 Portability & Jetson AGX Orin Hardware Profile

- **Validated CPU**: 12-core ARM Cortex-A78AE (up to 2.2 GHz)
- **Memory**: 29 GiB physical RAM
- **OS / Kernel**: Ubuntu 22.04 LTS / 5.15.148-tegra
- **Container Runtime**: Docker 29.7.2 with NVIDIA Container Runtime & cgroups v2
- **Portability**: All Python and container definitions are pure cross-platform and execute identically on `aarch64` and `x86_64` without hardware lock-in.
