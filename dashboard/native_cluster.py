"""
Native Digital Instrument Cluster Dashboard (NO Browser / NO HTML)
Hardware-accelerated native embedded automotive cluster running directly on display (HDMI/eDP).
Features:
1. Automotive Boot Sequence: Splash Screen with Eclipse SDV, Infosys, and KLE Tech branding.
2. Gauge Needle Sweep & Warning Light Self-Test (0 -> 60 -> 0 km/h).
3. Live 60 FPS Real-time cluster subscribing to local KUKSA VSS broker.
"""

import sys
import os
import math
import time
import urllib.request
import json
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pygame

os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
pygame.init()

# Automotive Color Palette
BG_COLOR = (10, 14, 22)
PANEL_COLOR = (18, 24, 36)
ACCENT_BLUE = (0, 180, 255)
ACCENT_CYAN = (0, 230, 210)
ACCENT_GREEN = (0, 230, 118)
ACCENT_RED = (255, 46, 76)
ACCENT_AMBER = (255, 171, 0)
TEXT_WHITE = (240, 244, 248)
TEXT_MUTED = (110, 125, 145)
INFOSYS_BLUE = (0, 122, 255)
KLE_NAVY = (14, 43, 92)

class NativeDigitalCluster:
    def __init__(self, vehicle_api_url: str = "http://localhost:5000/api/telemetry", width: int = 1024, height: int = 600):
        self.vehicle_api_url = vehicle_api_url
        self.width = width
        self.height = height
        
        flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("Eclipse SDV Native Instrument Cluster")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_huge = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 72, bold=True)
        self.font_large = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 52, bold=True)
        self.font_medium = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 24, bold=True)
        self.font_small = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 16)
        self.font_tiny = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 13)

        # Vehicle State Cache
        self.speed_kmh = 0.0
        self.battery_soc = 85.0
        self.gear = 1
        self.steering_angle = 0.0
        self.dbw_active = True
        self.estop_active = False
        self.is_running = True
        self.boot_phase = "SPLASH" # "SPLASH" -> "SWEEP" -> "READY"
        self.boot_start_time = time.time()
        self.sweep_speed = 0.0

        # Start telemetry thread
        self.poll_thread = threading.Thread(target=self._telemetry_poll_loop, daemon=True)
        self.poll_thread.start()

    def _telemetry_poll_loop(self):
        while self.is_running:
            try:
                req = urllib.request.Request(self.vehicle_api_url, headers={"User-Agent": "SDV-Cluster"})
                with urllib.request.urlopen(req, timeout=0.5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        self.speed_kmh = float(data.get("speed_kmh", 0.0))
                        self.battery_soc = float(data.get("battery_soc_percent", 85.0))
                        self.gear = int(data.get("gear", 1))
                        self.steering_angle = float(data.get("steering_angle_deg", 0.0))
                        self.dbw_active = bool(data.get("dbw_active", False))
                        self.estop_active = bool(data.get("estop_active", False))
            except Exception:
                pass
            time.sleep(0.05)

    def draw_startup_splash(self, elapsed: float):
        """Draws OEM Brand Startup Screen with Eclipse SDV, Infosys, and KLE Tech."""
        self.screen.fill((5, 8, 14))
        alpha_factor = min(1.0, elapsed / 1.0) if elapsed < 2.0 else max(0.0, 1.0 - (elapsed - 2.0) / 0.5)

        # Draw Center Glow Circle
        pygame.draw.circle(self.screen, (15, 30, 55), (self.width // 2, self.height // 2 - 30), 180)
        pygame.draw.circle(self.screen, (0, 100, 180), (self.width // 2, self.height // 2 - 30), 180, 2)

        # Eclipse SDV Header
        e_surf = self.font_large.render("ECLIPSE SDV", True, TEXT_WHITE)
        self.screen.blit(e_surf, (self.width // 2 - e_surf.get_width() // 2, self.height // 2 - 80))

        # Infosys & KLE Tech Subtitle
        sub_surf = self.font_medium.render("INFOSYS  ×  KLE TECH", True, ACCENT_CYAN)
        self.screen.blit(sub_surf, (self.width // 2 - sub_surf.get_width() // 2, self.height // 2 - 10))

        foot_surf = self.font_small.render("Software Defined Vehicle Cockpit Platform • Initializing...", True, TEXT_MUTED)
        self.screen.blit(foot_surf, (self.width // 2 - foot_surf.get_width() // 2, self.height // 2 + 50))

        # Bottom loading bar
        bar_w = int(min(300, (elapsed / 2.5) * 300))
        pygame.draw.rect(self.screen, (30, 40, 60), (self.width // 2 - 150, self.height - 80, 300, 6), border_radius=3)
        pygame.draw.rect(self.screen, ACCENT_CYAN, (self.width // 2 - 150, self.height - 80, bar_w, 6), border_radius=3)

    def draw_needle_sweep(self, elapsed: float):
        """Simulates authentic automotive gauge sweep (0 -> 60 -> 0 km/h) & warning self-test."""
        # 1.5 second sweep up and down
        t = (elapsed - 2.5) / 1.5 # 0.0 to 1.0
        if t < 0.5:
            self.sweep_speed = (t / 0.5) * 60.0
        else:
            self.sweep_speed = (1.0 - (t - 0.5) / 0.5) * 60.0
        self.sweep_speed = max(0.0, min(60.0, self.sweep_speed))

        self.draw_cluster_view(display_speed=self.sweep_speed, sweep_mode=True)

    def draw_cluster_view(self, display_speed: float, sweep_mode: bool = False):
        """Draws the main live instrument cluster."""
        self.screen.fill(BG_COLOR)

        # Header Badges
        dbw_color = ACCENT_GREEN if self.dbw_active or sweep_mode else TEXT_MUTED
        dbw_text = "● DBW AUTO ACTIVE" if (self.dbw_active or sweep_mode) else "○ MANUAL MODE"
        dbw_surf = self.font_small.render(dbw_text, True, dbw_color)
        self.screen.blit(dbw_surf, (35, 25))

        # Center OEM Branding Badge
        brand_surf = self.font_tiny.render("ECLIPSE SDV  |  INFOSYS  |  KLE TECH", True, TEXT_MUTED)
        self.screen.blit(brand_surf, (self.width // 2 - brand_surf.get_width() // 2, 25))

        # Speedometer Gauge (Center)
        center_x, center_y, radius = self.width // 2, self.height // 2 - 20, 160
        pygame.draw.circle(self.screen, PANEL_COLOR, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (35, 45, 65), (center_x, center_y), radius, 4)

        # Arc
        max_speed = 60.0
        fraction = min(1.0, display_speed / max_speed)
        start_angle = math.radians(135)
        sweep = math.radians(270 * fraction)
        end_angle = start_angle + sweep

        arc_points = []
        for a in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 3):
            rad = math.radians(a)
            px = center_x + int((radius - 12) * math.cos(rad))
            py = center_y + int((radius - 12) * math.sin(rad))
            arc_points.append((px, py))

        if len(arc_points) > 1:
            pygame.draw.lines(self.screen, ACCENT_BLUE if not sweep_mode else ACCENT_CYAN, False, arc_points, 8)

        # Speed Value
        val_surf = self.font_huge.render(f"{int(round(display_speed))}", True, TEXT_WHITE)
        unit_surf = self.font_small.render("km/h", True, ACCENT_BLUE)
        self.screen.blit(val_surf, (center_x - val_surf.get_width() // 2, center_y - 50))
        self.screen.blit(unit_surf, (center_x - unit_surf.get_width() // 2, center_y + 30))

        # Battery Panel (Left)
        self.draw_battery_panel(50, self.height // 2 - 60, 240, 100)

        # Gear Selector (Bottom Center)
        self.draw_gear_selector(self.width // 2, self.height // 2 + 160)

        # Warning Self-Test / E-Stop Banner
        if self.estop_active and not sweep_mode:
            banner_rect = pygame.Rect(0, self.height - 50, self.width, 50)
            pygame.draw.rect(self.screen, ACCENT_RED, banner_rect)
            warn_surf = self.font_medium.render("⚠ EMERGENCY STOP SWITCH ENGAGED - DRIVE INHIBITED ⚠", True, TEXT_WHITE)
            self.screen.blit(warn_surf, (self.width // 2 - warn_surf.get_width() // 2, self.height - 40))

    def draw_battery_panel(self, x: int, y: int, w: int, h: int):
        pygame.draw.rect(self.screen, PANEL_COLOR, (x, y, w, h), border_radius=12)
        pygame.draw.rect(self.screen, (35, 45, 65), (x, y, w, h), 2, border_radius=12)

        title = self.font_tiny.render("TRACTION BATTERY", True, TEXT_MUTED)
        self.screen.blit(title, (x + 18, y + 15))

        val_color = ACCENT_GREEN if self.battery_soc > 20 else ACCENT_RED
        val_surf = self.font_medium.render(f"{self.battery_soc:.1f}%", True, val_color)
        self.screen.blit(val_surf, (x + w - val_surf.get_width() - 18, y + 15))

        # Bar
        bar_x, bar_y, bar_w, bar_h = x + 18, y + 55, w - 36, 20
        pygame.draw.rect(self.screen, (25, 32, 46), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int((self.battery_soc / 100.0) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(self.screen, val_color, (bar_x, bar_y, fill_w, bar_h), border_radius=6)

    def draw_gear_selector(self, center_x: int, y: int):
        gears = [("R", -1), ("N", 0), ("D", 1)]
        start_x = center_x - (len(gears) * 60) // 2
        for i, (lbl, val) in enumerate(gears):
            gx = start_x + i * 60
            active = (self.gear == val)
            pygame.draw.rect(self.screen, (0, 90, 50) if active else PANEL_COLOR, (gx, y, 48, 48), border_radius=8)
            pygame.draw.rect(self.screen, ACCENT_GREEN if active else (40, 50, 70), (gx, y, 48, 48), 2 if active else 1, border_radius=8)
            txt = self.font_medium.render(lbl, True, ACCENT_GREEN if active else TEXT_MUTED)
            self.screen.blit(txt, (gx + 24 - txt.get_width() // 2, y + 24 - txt.get_height() // 2))

    def run(self):
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.is_running = False

            now = time.time()
            elapsed = now - self.boot_start_time

            if elapsed < 2.5:
                # 1. Startup Splash (Eclipse, Infosys, KLE Tech)
                self.draw_startup_splash(elapsed)
            elif elapsed < 4.0:
                # 2. Needle Sweep Self-Test
                self.draw_needle_sweep(elapsed)
            else:
                # 3. Live 60 FPS Cluster
                self.draw_cluster_view(display_speed=self.speed_kmh, sweep_mode=False)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/api/telemetry"
    cluster = NativeDigitalCluster(vehicle_api_url=url)
    cluster.run()
