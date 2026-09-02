"""
Native Digital Instrument Cluster Dashboard (NO Browser / NO HTML)
Hardware-accelerated native embedded automotive cluster running directly on display (HDMI/eDP).
Subscribes to local KUKSA VSS Databroker and renders gauges at 60 FPS.
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

# Initialize Pygame
os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
pygame.init()

# Visual Theme (Automotive Dark Cockpit)
BG_COLOR = (12, 16, 24)
PANEL_COLOR = (20, 26, 38)
ACCENT_BLUE = (0, 180, 255)
ACCENT_GREEN = (0, 230, 118)
ACCENT_RED = (255, 46, 76)
ACCENT_AMBER = (255, 171, 0)
TEXT_WHITE = (240, 244, 248)
TEXT_MUTED = (120, 134, 150)

class NativeDigitalCluster:
    def __init__(self, vehicle_api_url: str = "http://localhost:5000/api/telemetry", width: int = 1024, height: int = 600):
        self.vehicle_api_url = vehicle_api_url
        self.width = width
        self.height = height
        
        # Display setup
        flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("Eclipse SDV Native Instrument Cluster")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 64, bold=True)
        self.font_medium = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 28, bold=True)
        self.font_small = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 18)
        self.font_tiny = pygame.font.SysFont("DejaVu Sans, Arial, Helvetica", 14)

        # Vehicle State Cache
        self.speed_kmh = 0.0
        self.battery_soc = 85.0
        self.gear = 1 # 1: D, 0: N, -1: R
        self.steering_angle = 0.0
        self.dbw_active = True
        self.estop_active = False
        self.is_running = True

        # Start telemetry polling thread
        self.poll_thread = threading.Thread(target=self._telemetry_poll_loop, daemon=True)
        self.poll_thread.start()

    def _telemetry_poll_loop(self):
        """Polls local vehicle stack telemetry API at 20 Hz."""
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

    def draw_speedometer(self, center_x: int, center_y: int, radius: int):
        """Draws circular arc gauge and digital readout."""
        # Outer Ring
        pygame.draw.circle(self.screen, PANEL_COLOR, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (40, 50, 70), (center_x, center_y), radius, 4)

        # Speed Arc (from 135 deg to 405 deg)
        max_speed = 60.0
        clamped_speed = min(max_speed, max(0.0, self.speed_kmh))
        fraction = clamped_speed / max_speed

        start_angle = math.radians(135)
        sweep = math.radians(270 * fraction)
        end_angle = start_angle + sweep

        # Arc segments
        arc_points = []
        for a in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 3):
            rad = math.radians(a)
            px = center_x + int((radius - 12) * math.cos(rad))
            py = center_y + int((radius - 12) * math.sin(rad))
            arc_points.append((px, py))

        if len(arc_points) > 1:
            pygame.draw.lines(self.screen, ACCENT_BLUE, False, arc_points, 8)

        # Digital Speed Value
        speed_surf = self.font_large.render(f"{int(round(self.speed_kmh))}", True, TEXT_WHITE)
        unit_surf = self.font_small.render("km/h", True, ACCENT_BLUE)
        self.screen.blit(speed_surf, (center_x - speed_surf.get_width() // 2, center_y - 45))
        self.screen.blit(unit_surf, (center_x - unit_surf.get_width() // 2, center_y + 25))

    def draw_battery_gauge(self, x: int, y: int, w: int, h: int):
        """Draws battery state of charge bar."""
        # Background Panel
        pygame.draw.rect(self.screen, PANEL_COLOR, (x, y, w, h), border_radius=12)
        pygame.draw.rect(self.screen, (40, 50, 70), (x, y, w, h), 2, border_radius=12)

        # Title
        title_surf = self.font_small.render("TRACTION BATTERY", True, TEXT_MUTED)
        self.screen.blit(title_surf, (x + 20, y + 15))

        # Battery % Value
        val_color = ACCENT_GREEN if self.battery_soc > 20 else ACCENT_RED
        val_surf = self.font_medium.render(f"{self.battery_soc:.1f}%", True, val_color)
        self.screen.blit(val_surf, (x + w - val_surf.get_width() - 20, y + 15))

        # Fill Bar
        bar_x, bar_y, bar_w, bar_h = x + 20, y + 55, w - 40, 22
        pygame.draw.rect(self.screen, (30, 38, 54), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int((self.battery_soc / 100.0) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(self.screen, val_color, (bar_x, bar_y, fill_w, bar_h), border_radius=6)

    def draw_gear_indicator(self, center_x: int, y: int):
        """Draws PRND gear selector."""
        gears = [("R", -1), ("N", 0), ("D", 1)]
        total_w = len(gears) * 60
        start_x = center_x - total_w // 2

        for i, (label, val) in enumerate(gears):
            gx = start_x + i * 60
            active = (self.gear == val)
            color = ACCENT_GREEN if active else TEXT_MUTED
            box_color = (0, 100, 60) if active else PANEL_COLOR

            pygame.draw.rect(self.screen, box_color, (gx, y, 48, 48), border_radius=8)
            pygame.draw.rect(self.screen, color, (gx, y, 48, 48), 2 if active else 1, border_radius=8)

            txt_surf = self.font_medium.render(label, True, color if active else TEXT_MUTED)
            self.screen.blit(txt_surf, (gx + 24 - txt_surf.get_width() // 2, y + 24 - txt_surf.get_height() // 2))

    def draw_header_badges(self):
        """Draws top status badges (Autonomous DBW, E-Stop, Time)."""
        # DBW Badge
        dbw_color = ACCENT_GREEN if self.dbw_active else TEXT_MUTED
        dbw_text = "● DBW AUTO ACTIVE" if self.dbw_active else "○ MANUAL MODE"
        dbw_surf = self.font_small.render(dbw_text, True, dbw_color)
        self.screen.blit(dbw_surf, (30, 20))

        # Center Title
        title_surf = self.font_small.render("ECLIPSE SDV DIGITAL COCKPIT", True, TEXT_MUTED)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 20))

        # E-Stop Warning Banner if active
        if self.estop_active:
            banner_rect = pygame.Rect(0, self.height - 50, self.width, 50)
            pygame.draw.rect(self.screen, ACCENT_RED, banner_rect)
            warn_surf = self.font_medium.render("⚠ EMERGENCY STOP SWITCH ENGAGED - DRIVE INHIBITED ⚠", True, TEXT_WHITE)
            self.screen.blit(warn_surf, (self.width // 2 - warn_surf.get_width() // 2, self.height - 40))

    def run(self):
        """Main rendering loop at 60 FPS."""
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.is_running = False

            # Clear Frame
            self.screen.fill(BG_COLOR)

            # Draw Components
            self.draw_header_badges()
            self.draw_speedometer(self.width // 2, self.height // 2 - 20, 160)
            self.draw_gear_indicator(self.width // 2, self.height // 2 + 160)
            self.draw_battery_gauge(50, self.height // 2 - 60, 240, 100)

            # Refresh display at 60 FPS
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/api/telemetry"
    cluster = NativeDigitalCluster(vehicle_api_url=url)
    cluster.run()
