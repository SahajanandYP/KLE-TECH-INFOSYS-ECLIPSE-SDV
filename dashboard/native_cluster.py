
"""
Native Digital Instrument Cluster Dashboard - Sleek Vercel Minimalist Design
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

# Vercel / Tesla Minimalist Palette
BG_COLOR = (0, 0, 0)
PANEL_COLOR = (10, 10, 10)
ACCENT_BLUE = (0, 112, 243)  # Vercel Blue
ACCENT_CYAN = (50, 205, 255)
ACCENT_GREEN = (0, 204, 102)
ACCENT_RED = (255, 51, 102)
TEXT_WHITE = (237, 237, 237)
TEXT_MUTED = (136, 136, 136)

class NativeDigitalCluster:
    def __init__(self, vehicle_api_url: str = "http://localhost:5000/api/telemetry", width: int = 1024, height: int = 600):
        self.vehicle_api_url = vehicle_api_url
        self.width = width
        self.height = height
        
        flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("Eclipse SDV Minimalist Cluster")
        self.clock = pygame.time.Clock()

        # Fonts (Sleek sans-serif)
        self.font_huge = pygame.font.SysFont("sans-serif", 140, bold=False)
        self.font_large = pygame.font.SysFont("sans-serif", 48, bold=False)
        self.font_medium = pygame.font.SysFont("sans-serif", 24, bold=False)
        self.font_small = pygame.font.SysFont("sans-serif", 18, bold=False)
        self.font_tiny = pygame.font.SysFont("sans-serif", 12, bold=False)

        # Load Logos for Splash Screen
        self.logos = {}
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            img_eclipse = pygame.image.load(os.path.join(base_dir, "assets", "eclipse_sdv_logo.png")).convert_alpha()
            img_infosys = pygame.image.load(os.path.join(base_dir, "assets", "infosys_logo.png")).convert_alpha()
            img_kle = pygame.image.load(os.path.join(base_dir, "assets", "kle_logo.png")).convert_alpha()
            
            def scale_logo(img, target_width):
                ratio = img.get_height() / img.get_width()
                return pygame.transform.smoothscale(img, (target_width, int(target_width * ratio)))
            
            self.logos["eclipse"] = scale_logo(img_eclipse, 250)
            self.logos["infosys"] = scale_logo(img_infosys, 140)
            self.logos["kle"] = scale_logo(img_kle, 160)
        except Exception as e:
            pass

        self.speed_kmh = 0.0
        self.battery_soc = 85.0
        self.gear = 1
        self.steering_angle = 0.0
        self.dbw_active = False
        self.estop_active = False
        self.ota_available = False
        self.ota_installing = False
        
        self.boot_start_time = time.time()
        self.is_running = True
        self.sweep_speed = 0.0

        threading.Thread(target=self.fetch_telemetry, daemon=True).start()

    def fetch_telemetry(self):
        while self.is_running:
            try:
                req = urllib.request.Request(self.vehicle_api_url)
                with urllib.request.urlopen(req, timeout=0.5) as response:
                    data = {}
                    try:
                        data = json.loads(response.read().decode())
                    except:
                        pass
                    
                    try:
                        req2 = urllib.request.Request(self.vehicle_api_url.replace("/telemetry", "/ota/status"))
                        with urllib.request.urlopen(req2, timeout=0.5) as r2:
                            d2 = json.loads(r2.read().decode())
                            self.ota_available = bool(d2.get("update_available", False))
                    except:
                        pass

                    if isinstance(data, dict):
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
        self.screen.fill((255, 255, 255))
        center_x, center_y = self.width // 2, self.height // 2

        if "eclipse" in self.logos:
            ec_surf = self.logos["eclipse"]
            self.screen.blit(ec_surf, (center_x - ec_surf.get_width() // 2, center_y - 120))
        
        pygame.draw.line(self.screen, (220, 220, 220), (center_x - 150, center_y), (center_x + 150, center_y), 1)

        if "infosys" in self.logos:
            inf_surf = self.logos["infosys"]
            self.screen.blit(inf_surf, (center_x - inf_surf.get_width() - 20, center_y + 20))
            
        if "kle" in self.logos:
            kle_surf = self.logos["kle"]
            self.screen.blit(kle_surf, (center_x + 20, center_y + 20))

        foot_surf = self.font_small.render("Initializing System...", True, (150, 150, 150))
        self.screen.blit(foot_surf, (center_x - foot_surf.get_width() // 2, self.height - 80))

        bar_w = int(min(200, (elapsed / 2.5) * 200))
        pygame.draw.rect(self.screen, (240, 240, 240), (center_x - 100, self.height - 50, 200, 2))
        pygame.draw.rect(self.screen, ACCENT_BLUE, (center_x - 100, self.height - 50, bar_w, 2))

    def draw_needle_sweep(self, elapsed: float):
        t = (elapsed - 2.5) / 1.5
        if t < 0.5:
            self.sweep_speed = (t / 0.5) * 60.0
        else:
            self.sweep_speed = (1.0 - (t - 0.5) / 0.5) * 60.0
        self.draw_cluster_view(display_speed=max(0.0, min(60.0, self.sweep_speed)), sweep_mode=True)

    def draw_cluster_view(self, display_speed: float, sweep_mode: bool = False):
        self.screen.fill(BG_COLOR)
        center_x, center_y = self.width // 2, self.height // 2

        # Ultra-Minimalist Speed Arc
        radius = 180
        start_angle = math.radians(140)
        max_speed = 60.0
        fraction = min(1.0, display_speed / max_speed)
        sweep = math.radians(260 * fraction)
        end_angle = start_angle + sweep

        # Background track
        pygame.draw.arc(self.screen, (30, 30, 30), (center_x - radius, center_y - radius, radius*2, radius*2), -math.radians(400), -math.radians(140), 2)
        
        # Active speed track
        if fraction > 0:
            arc_points = []
            for a in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 2):
                rad = math.radians(a)
                px = center_x + int(radius * math.cos(rad))
                py = center_y + int(radius * math.sin(rad))
                arc_points.append((px, py))
            if len(arc_points) > 1:
                pygame.draw.lines(self.screen, ACCENT_BLUE, False, arc_points, 4)
                # Glow dot
                pygame.draw.circle(self.screen, ACCENT_CYAN, arc_points[-1], 6)

        # Huge Sleek Speed Text
        val_surf = self.font_huge.render(f"{int(round(display_speed))}", True, TEXT_WHITE)
        unit_surf = self.font_medium.render("km/h", True, TEXT_MUTED)
        self.screen.blit(val_surf, (center_x - val_surf.get_width() // 2, center_y - 60))
        self.screen.blit(unit_surf, (center_x - unit_surf.get_width() // 2, center_y + 60))

        # Minimalist Battery Bar (Bottom Center)
        bat_w = 120
        bat_h = 4
        bat_x = center_x - bat_w // 2
        bat_y = center_y + 110
        pygame.draw.rect(self.screen, (30, 30, 30), (bat_x, bat_y, bat_w, bat_h), border_radius=2)
        fill_w = int((self.battery_soc / 100.0) * bat_w)
        bat_color = ACCENT_GREEN if self.battery_soc > 20 else ACCENT_RED
        if fill_w > 0:
            pygame.draw.rect(self.screen, bat_color, (bat_x, bat_y, fill_w, bat_h), border_radius=2)
        
        bat_text = self.font_small.render(f"{self.battery_soc:.0f}%", True, TEXT_MUTED)
        self.screen.blit(bat_text, (center_x - bat_text.get_width() // 2, bat_y + 10))

        # Sleek Gear Selector (Left)
        gears = [("R", -1), ("N", 0), ("D", 1)]
        for i, (lbl, val) in enumerate(gears):
            gy = center_y - 40 + (i * 40)
            active = (self.gear == val)
            color = TEXT_WHITE if active else (50, 50, 50)
            txt = self.font_medium.render(lbl, True, color)
            self.screen.blit(txt, (center_x - 260, gy))
            if active:
                pygame.draw.circle(self.screen, ACCENT_BLUE, (center_x - 280, gy + 12), 4)

        # Brand / Mode (Right)
        brand_surf = self.font_small.render("ECLIPSE SDV", True, (80, 80, 80))
        self.screen.blit(brand_surf, (center_x + 220, center_y - 40))
        
        dbw_color = ACCENT_CYAN if (self.dbw_active or sweep_mode) else TEXT_MUTED
        dbw_text = "AUTO" if (self.dbw_active or sweep_mode) else "MANUAL"
        dbw_surf = self.font_small.render(dbw_text, True, dbw_color)
        self.screen.blit(dbw_surf, (center_x + 220, center_y))

        # Warnings & OTA (Bottom)
        if self.estop_active and not sweep_mode:
            pygame.draw.rect(self.screen, ACCENT_RED, (0, self.height - 40, self.width, 40))
            warn = self.font_small.render("EMERGENCY STOP ENGAGED", True, (0,0,0))
            self.screen.blit(warn, (center_x - warn.get_width() // 2, self.height - 30))
        elif self.ota_installing:
            pygame.draw.rect(self.screen, ACCENT_BLUE, (0, self.height - 40, self.width, 40))
            warn = self.font_small.render("INSTALLING UPDATE...", True, (0,0,0))
            self.screen.blit(warn, (center_x - warn.get_width() // 2, self.height - 30))
        elif self.ota_available and not sweep_mode:
            pygame.draw.rect(self.screen, TEXT_WHITE, (0, self.height - 40, self.width, 40))
            warn = self.font_small.render("UPDATE AVAILABLE • PRESS [ENTER]", True, (0,0,0))
            self.screen.blit(warn, (center_x - warn.get_width() // 2, self.height - 30))

    def run(self):
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.is_running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.ota_available and not self.ota_installing:
                        self.ota_installing = True
                        try:
                            req = urllib.request.Request(self.vehicle_api_url.replace("/telemetry", "/ota/approve"), method="POST")
                            req.add_header('Content-Type', 'application/json')
                            urllib.request.urlopen(req, data=b'{}', timeout=1.0)
                        except:
                            pass

            elapsed = time.time() - self.boot_start_time
            if elapsed < 2.5:
                self.draw_startup_splash(elapsed)
            elif elapsed < 4.0:
                self.draw_needle_sweep(elapsed)
            else:
                self.draw_cluster_view(display_speed=self.speed_kmh, sweep_mode=False)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/api/telemetry"
    cluster = NativeDigitalCluster(vehicle_api_url=url)
    cluster.run()
