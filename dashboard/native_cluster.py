#!/usr/bin/env python3
import pygame
import urllib.request
import json
import time
import os
import sys

# --- CONFIGURATION ---
API_URL = "http://localhost:5000"
# os.environ["DISPLAY"] = ":0"  # Removed to support Wayland/:1

# --- COLORS (Cyberpunk / Next-Gen EV Theme) ---
BG_COLOR = (11, 15, 25)
NEON_CYAN = (0, 240, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 65)
ALERT_RED = (255, 0, 60)
HUD_GREY = (40, 50, 65)
TEXT_WHITE = (240, 240, 255)

pygame.init()
infoObject = pygame.display.Info()
# Fallback if no display detected
w = infoObject.current_w if infoObject.current_w > 0 else 1280
h = infoObject.current_h if infoObject.current_h > 0 else 720
screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.DOUBLEBUF)
pygame.mouse.set_visible(False)

font_huge = pygame.font.SysFont("trebuchetms", 180, bold=True)
font_large = pygame.font.SysFont("trebuchetms", 80, bold=True)
font_med = pygame.font.SysFont("trebuchetms", 40, bold=True)
font_small = pygame.font.SysFont("trebuchetms", 24)
font_mono = pygame.font.SysFont("courier", 20, bold=True)

class CyberDashboard:
    def __init__(self):
        self.speed = 0.0
        self.battery = 0.0
        self.gear = 0
        self.online = False
        self.show_ota_banner = False
        self.pending_reboot = False
        self.last_api_time = 0
        
        self.boot_sequence()

    def boot_sequence(self):
        # Sci-Fi Boot Animation
        for i in range(0, 100, 5):
            screen.fill(BG_COLOR)
            text = font_large.render("SYSTEM INITIALIZING...", True, NEON_CYAN)
            screen.blit(text, (w//2 - text.get_width()//2, h//2 - 50))
            
            # Progress bar
            pygame.draw.rect(screen, HUD_GREY, (w//4, h//2 + 50, w//2, 10))
            pygame.draw.rect(screen, NEON_CYAN, (w//4, h//2 + 50, (w//2) * (i/100.0), 10))
            
            pygame.display.flip()
            time.sleep(0.05)

    def fetch_data(self):
        now = time.time()
        if now - self.last_api_time > 0.5: # 2 Hz
            self.last_api_time = now
            try:
                req = urllib.request.Request(f"{API_URL}/api/telemetry")
                with urllib.request.urlopen(req, timeout=0.3) as res:
                    data = json.loads(res.read().decode())
                    self.speed = float(data.get("speed_kmh", 0))
                    self.battery = float(data.get("battery_soc_percent", 0))
                    self.gear = int(data.get("current_gear", 0))
                    self.online = True
            except:
                self.online = False
                
            try:
                req2 = urllib.request.Request(f"{API_URL}/api/ota/status")
                with urllib.request.urlopen(req2, timeout=0.3) as res2:
                    ota_data = json.loads(res2.read().decode())
                    self.show_ota_banner = ota_data.get("update_available", False)
            except:
                pass

    def draw_hud_brackets(self):
        # Draw sci-fi corners
        thickness = 4
        length = 60
        margin = 30
        c = NEON_CYAN
        # Top Left
        pygame.draw.line(screen, c, (margin, margin), (margin+length, margin), thickness)
        pygame.draw.line(screen, c, (margin, margin), (margin, margin+length), thickness)
        # Top Right
        pygame.draw.line(screen, c, (w-margin, margin), (w-margin-length, margin), thickness)
        pygame.draw.line(screen, c, (w-margin, margin), (w-margin, margin+length), thickness)
        # Bottom Left
        pygame.draw.line(screen, c, (margin, h-margin), (margin+length, h-margin), thickness)
        pygame.draw.line(screen, c, (margin, h-margin), (margin, h-margin-length), thickness)
        # Bottom Right
        pygame.draw.line(screen, c, (w-margin, h-margin), (w-margin-length, h-margin), thickness)
        pygame.draw.line(screen, c, (w-margin, h-margin), (w-margin, h-margin-length), thickness)

    def draw_battery(self):
        # Battery outline
        bx, by = 80, h//2 - 100
        bw, bh = 80, 200
        pygame.draw.rect(screen, HUD_GREY, (bx, by, bw, bh), 4, border_radius=10)
        pygame.draw.rect(screen, HUD_GREY, (bx+20, by-15, 40, 15), border_radius=5)
        
        # Fill
        fill_color = NEON_GREEN if self.battery > 20 else ALERT_RED
        fill_h = int((self.battery / 100.0) * (bh - 10))
        pygame.draw.rect(screen, fill_color, (bx+5, by + bh - 5 - fill_h, bw-10, fill_h), border_radius=5)
        
        # Text
        bat_txt = font_med.render(f"{int(self.battery)}%", True, TEXT_WHITE)
        screen.blit(bat_txt, (bx + bw//2 - bat_txt.get_width()//2, by + bh + 20))
        lbl = font_small.render("ENERGY", True, NEON_CYAN)
        screen.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by + bh + 60))

    def draw_speed(self):
        cx, cy = w//2, h//2
        # Speed Number
        spd_txt = font_huge.render(f"{int(self.speed)}", True, TEXT_WHITE)
        screen.blit(spd_txt, (cx - spd_txt.get_width()//2, cy - spd_txt.get_height()//2 - 20))
        
        # KM/H label
        lbl = font_med.render("KM/H", True, NEON_CYAN)
        screen.blit(lbl, (cx - lbl.get_width()//2, cy + spd_txt.get_height()//2 - 30))
        
        # Power Band (Speed bar)
        bar_w = 600
        pygame.draw.rect(screen, HUD_GREY, (cx - bar_w//2, cy + 100, bar_w, 8))
        spd_ratio = min(self.speed / 60.0, 1.0)
        fill_w = int(bar_w * spd_ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, NEON_CYAN, (cx - bar_w//2, cy + 100, fill_w, 8))
            # Glowing dot at the end
            pygame.draw.circle(screen, TEXT_WHITE, (cx - bar_w//2 + fill_w, cy + 104), 10)

    def draw_gear(self):
        gx, gy = w - 180, h//2 - 100
        gears = [("P", 0), ("R", -1), ("N", 2), ("D", 1)]
        
        for i, (g_txt, g_val) in enumerate(gears):
            active = (self.gear == g_val)
            color = NEON_CYAN if active else HUD_GREY
            
            # Box
            rect = pygame.Rect(gx, gy + (i * 60), 60, 50)
            pygame.draw.rect(screen, color, rect, width=2 if not active else 0, border_radius=8)
            
            # Text
            txt = font_med.render(g_txt, True, BG_COLOR if active else color)
            screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            
    def draw_console(self):
        # Matrix style console log at bottom left
        txt1 = font_mono.render(f"SYS.STATE   : {'ONLINE' if self.online else 'OFFLINE'}", True, NEON_GREEN if self.online else ALERT_RED)
        txt2 = font_mono.render(f"NET.UPLINK  : SECURE (ZENOH/HTTP)", True, NEON_CYAN)
        txt3 = font_mono.render(f"SDV.CORE    : v2.0-CYBER", True, TEXT_WHITE)
        
        screen.blit(txt1, (50, h - 120))
        screen.blit(txt2, (50, h - 90))
        screen.blit(txt3, (50, h - 60))

    def draw_ota_banner(self):
        if not self.show_ota_banner: return
        
        bw, bh = 800, 100
        bx, by = w//2 - bw//2, 50
        
        pygame.draw.rect(screen, NEON_PINK, (bx, by, bw, bh), border_radius=15)
        pygame.draw.rect(screen, TEXT_WHITE, (bx, by, bw, bh), 3, border_radius=15)
        
        txt = font_med.render("CRITICAL OTA UPDATE READY", True, TEXT_WHITE)
        sub = font_small.render("Press [ENTER] to Install  |  Press [ESC] to Dismiss", True, TEXT_WHITE)
        
        screen.blit(txt, (bx + bw//2 - txt.get_width()//2, by + 15))
        screen.blit(sub, (bx + bw//2 - sub.get_width()//2, by + 60))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_RETURN and self.show_ota_banner:
                        self.trigger_ota_reboot()
                    elif event.key == pygame.K_ESCAPE and self.show_ota_banner:
                        self.show_ota_banner = False
            
            self.fetch_data()
            
            screen.fill(BG_COLOR)
            self.draw_hud_brackets()
            self.draw_battery()
            self.draw_speed()
            self.draw_gear()
            self.draw_console()
            self.draw_ota_banner()
            
            pygame.display.flip()
            clock.tick(30)
            
        pygame.quit()

    def trigger_ota_reboot(self):
        # Cinematic reboot sequence
        for i in range(0, 255, 10):
            s = pygame.Surface((w,h))
            s.set_alpha(i)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
            pygame.display.flip()
            time.sleep(0.05)
            
        try:
            req = urllib.request.Request(f"{API_URL}/api/ota/approve", method="POST")
            urllib.request.urlopen(req, timeout=1.0)
        except:
            pass
            
        # Hot reload the dashboard
        pygame.quit()
        os.execv(sys.executable, ['python3'] + sys.argv)

if __name__ == "__main__":
    CyberDashboard().run()
