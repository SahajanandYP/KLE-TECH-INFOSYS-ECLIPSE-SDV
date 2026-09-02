"""
Generic Declarative Signal Mapping Engine
Translates arbitrary vehicle bus telemetry into COVESA VSS paths using declarative rules.
"""

from typing import Dict, Any, List, Callable, Optional

class SignalMappingRule:
    def __init__(
        self,
        source_key: str,
        target_vss_path: str,
        scale: float = 1.0,
        offset: float = 0.0,
        value_map: Optional[Dict[Any, Any]] = None,
        transform_fn: Optional[Callable[[Any], Any]] = None
    ):
        self.source_key = source_key
        self.target_vss_path = target_vss_path
        self.scale = scale
        self.offset = offset
        self.value_map = value_map
        self.transform_fn = transform_fn

    def apply(self, raw_value: Any) -> Any:
        if raw_value is None:
            return None
        if self.transform_fn:
            return self.transform_fn(raw_value)
        if self.value_map and raw_value in self.value_map:
            return self.value_map[raw_value]
        if isinstance(raw_value, (int, float)):
            return round((raw_value * self.scale) + self.offset, 3)
        return raw_value

class GenericSignalMapper:
    """
    Executes mapping rules against raw telemetry dictionaries.
    """
    def __init__(self, rules: Optional[List[SignalMappingRule]] = None):
        self.rules: List[SignalMappingRule] = rules or []

    def add_rule(self, rule: SignalMappingRule):
        self.rules.append(rule)

    def map_to_vss(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        vss_output: Dict[str, Any] = {}
        for rule in self.rules:
            if rule.source_key in raw_data:
                transformed = rule.apply(raw_data[rule.source_key])
                if transformed is not None:
                    vss_output[rule.target_vss_path] = transformed
        return vss_output
