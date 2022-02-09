"""Models."""
import dataclasses
from typing import Dict, List


@dataclasses.dataclass(frozen=True)
class DiscoveredBulb:
    """Representation of discovered bulb."""

    ip_address: str
    mac_address: str


@dataclasses.dataclass
class BulbRegistry:
    """Representation of the bulb registry."""

    bulbs_by_mac: Dict[str, DiscoveredBulb] = dataclasses.field(default_factory=dict)

    def register(self, bulb: DiscoveredBulb) -> None:
        """Register a new bulb."""
        self.bulbs_by_mac[bulb.mac_address] = bulb

    def bulbs(self) -> List[DiscoveredBulb]:
        """Get all present bulbs."""
        return list(self.bulbs_by_mac.values())
