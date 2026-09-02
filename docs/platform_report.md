# Jetson AGX Orin Platform Discovery Report

**Target Node**: NVIDIA Jetson AGX Orin Developer Kit  
**Role**: Reusable SDV Platform Server / Edge Compute Host  

## System Summary
- **CPU**: 12-core ARM Cortex-A78AE (ARM64)
- **RAM**: 29 GiB physical RAM (20 GiB available)
- **OS / BSP**: Ubuntu 22.04 LTS / Kernel 5.15.148-tegra / JetPack 6.2 (L4T R36.4.7)
- **Container Engine**: Docker 29.7.2 with NVIDIA Container Runtime & cgroups v2
- **CAN**: 2x Bosch M_TTCAN controllers (`can0`, `can1`) on-chip
- **ROS 2**: ROS 2 Humble installed
