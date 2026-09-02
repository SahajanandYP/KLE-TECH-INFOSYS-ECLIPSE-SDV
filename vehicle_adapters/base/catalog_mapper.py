"""
Generalized VSS Catalog Mapping Engine
Loads standard open-source automotive tables (OBD-II, J1939, EV CAN) and applies them dynamically.
"""

import json
import os
from typing import Dict, Any, Optional

class CatalogVssMapper:
    def __init__(self, catalog_path: str = "config/standard_vss_catalog.json"):
        self.catalog_path = catalog_path
        self.catalog: Dict[str, Any] = {}
        self.load_catalog()

    def load_catalog(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, "r") as f:
                self.catalog = json.load(f)

    def map_standard_signal(self, standard_key: str, raw_value: float) -> Optional[tuple]:
        """Returns (target_vss_path, normalized_value)"""
        rule = self.catalog.get("mappings", {}).get(standard_key)
        if not rule:
            return None
        target_vss = rule["target_vss"]
        scale = rule.get("scale", 1.0)
        offset = rule.get("offset", 0.0)
        normalized_val = round((raw_value * scale) + offset, 3)
        return target_vss, normalized_val
