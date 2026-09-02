# Jetson AGX Orin Platform Discovery Report (Phase 0)

**Date**: 2026-09-01  
**Target Node**: NVIDIA Jetson AGX Orin Developer Kit  
**Role**: Reusable SDV Platform Server / Edge Compute Host  

---

## 1. Hardware Specification

- **Compute Board**: NVIDIA Jetson AGX Orin Developer Kit (Generic Board, aarch64 / ARM64)
- **CPU**: 12-core ARM Cortex-A78AE
  - Cores 0-7 online (Clusters 0 & 1), Cores 8-11 offline (Cluster 2 power profile)
  - Max Frequency: ~2201.6 MHz
  - Architecture Features: FP, ASIMD, AES, PMULL, SHA1, SHA2, CRC32, ATOMICS, PACA, PACG
- **System Memory**: 29 GiB physical RAM (approx. 20 GiB free, 4.9 GiB buffer/cache)
- **Swap**: 14 GiB Swap active
- **Primary Storage**: 57 GiB root filesystem (`/dev/mmcblk0p1`), 21 GiB available (63% utilized)
- **GPU / Accelerator**: NVIDIA Ampere Architecture GPU with Tensor Cores
- **CUDA Environment**: CUDA 12.6 (V12.6.68) installed at `/usr/local/cuda-12.6`

---

## 2. Operating System & BSP

- **Linux Distribution**: Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- **Kernel**: `Linux 5.15.148-tegra #1 SMP PREEMPT Fri Jul 11 02:33:45 UTC 2025 aarch64`
- **L4T (Linux for Tegra) Version**: R36.4.7 (Release 36, Revision 4.7, Date: 2025-09-18)
- **JetPack Version**: JetPack 6.2.1 / 6.2 (Compatible with L4T 36.4.x)
- **Cgroups Hierarchy**: Cgroups v2 (`cgroup2fs` at `/sys/fs/cgroup`)

---

## 3. Container Runtime Environment

- **Docker Engine**: Community Edition 29.7.2
- **Docker Buildx**: v0.36.1
- **Docker Compose**: v5.4.0
- **NVIDIA Container Runtime**: `/usr/bin/nvidia-container-runtime` & `/usr/bin/nvidia-container-cli` present and registered in `/etc/docker/daemon.json`
- **Runtime Socket**: `/var/run/docker.sock` active

---

## 4. Middleware & Runtimes

- **ROS 2**: ROS 2 Humble (`ros-humble-*` debian packages installed, `ROS_DISTRO=humble`)
- **Python**: Python 3.10.12 (Standard system runtime)
- **C/C++ Toolchain**: GCC 11.4.0, G++ 11.4.0
- **Git**: Git 2.34.1
- **Eclipse SDV ARM64 Assessment**:
  - **Eclipse KUKSA**: Full ARM64 multi-arch OCI image support (`ghcr.io/eclipse-kuksa/kuksa-databroker:main`).
  - **Eclipse Velocitas**: Python & C++ SDKs execute natively on `aarch64`.
  - **Eclipse Zenoh**: Pre-compiled `aarch64` binaries and Docker containers available.
  - **Eclipse Kanto & Ankaios**: Native ARM64 binary and container releases available.
  - **Eclipse OpenSOVD**: Python / C++ based diagnostic server runs natively.

---

## 5. Network & CAN Bus Interfaces

- **Ethernet**: `eno1` (GbE interface, down/unplugged)
- **Wi-Fi**: `wlP1p1s0` (Realtek RTL8822CE 802.11ac PCIe Wireless)
- **Native On-SoC CAN**:
  - `can0`: Bosch M_TTCAN at `c310000.mttcan`, MTU 16, Clock 50MHz, State: STOPPED/DOWN.
  - `can1`: Bosch M_TTCAN at `c320000.mttcan`, MTU 16, Clock 50MHz, State: STOPPED/DOWN.
  - Kernel modules: `mttcan`, `can_dev`, `nvpps` loaded.
- **USB Devices**: Primax Keyboard/Mouse, Realtek USB 3.0/2.0 Hubs, Bluetooth radio. No USB-CAN adapter plugged in.
- **Virtual CAN**: `vcan` kernel module available for simulation and offline testing.

---

## 6. Physical Hardware & Safety Notes

1. **CAN Transceiver Requirement**: The Jetson 40-pin header provides logic-level (3.3V) CAN TX/RX signals. Direct physical connection to the VIRYA skateboard CAN bus requires either an external 3.3V CAN transceiver board (SN65HVD230) on header pins (29/31 or 37/39) or a USB-CAN dongle (PCAN-USB, CANable).
2. **Read-Only Telemetry First**: Initial bring-up must strictly use SocketCAN in passive / listen-only mode at **500 kbps** to ingest `0x1291` General Status without transmitting actuation frames.
3. **Multi-Platform Portability**: All software modules must strictly separate the reusable platform from the VIRYA vehicle profile and adapter, ensuring seamless porting to x86_64 edge compute (Lenovo ThinkEdge SE50) or other ARM64 systems.
