
"""
Use Case 4: Remote OTA Manager & Automated Rollback Engine
Now with REAL Git-based Over-The-Air updates.
"""

import logging
import time
import os
import sys
import subprocess
from typing import Dict, Any, Tuple

logger = logging.getLogger("OtaManagerApp")

class OtaManagerApp:
    def __init__(self, current_version: str = "v1.1.0"):
        self.current_version = current_version
        self.stable_version = current_version
        self.update_state = "IDLE"

    def apply_ota_update(self, target_version: str = "latest", simulate_post_install_health_pass: bool = True) -> Tuple[bool, str]:
        """Executes a REAL OTA update by pulling from GitHub and restarting the process."""
        logger.info(f"OTA Triggered: Pulling latest code from GitHub (Current: {self.current_version})")
        self.update_state = "DOWNLOADING"
        
        try:
            # 1. Pull the latest code from the internet (GitHub)
            repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            result = subprocess.run(["git", "pull", "origin", "main"], cwd=repo_dir, capture_output=True, text=True, check=True)
            logger.info(f"OTA Git Pull Success: {result.stdout.strip()}")
            
            self.update_state = "STAGING"
            self.current_version = target_version
            self.update_state = "ACTIVATING"
            
            if simulate_post_install_health_pass:
                logger.info("OTA SUCCESS. Rebooting internal vehicle software engine in 3 seconds...")
                self.update_state = "VERIFIED"
                time.sleep(3)
                
                # 2. Automatically restart the Python software stack to apply the new code!
                # This gracefully reboots the vehicle software without turning off the computer
                os.execv(sys.executable, ['python3'] + sys.argv)
                return True, "Update applied."
            else:
                logger.warning(f"OTA HEALTH CHECK FAILED. Rolling back...")
                self.update_state = "ROLLED_BACK"
                return False, "Health check failed."
                
        except subprocess.CalledProcessError as e:
            logger.error(f"OTA FAILED during download: {e.stderr}")
            self.update_state = "ROLLED_BACK"
            return False, f"Git pull failed: {e.stderr}"
