"""
Game state for Taipan.
"""

from dataclasses import dataclass, field
from typing import List
import random

# Game constants
BATTLE_NOT_FINISHED = 0
BATTLE_WON = 1
BATTLE_INTERRUPTED = 2
BATTLE_FLED = 3
BATTLE_LOST = 4

# Constants from the C code
ITEMS = ["Opium", "Silk", "Arms", "General Cargo"]
LOCATIONS = [
    "At sea",
    "Hong Kong",
    "Shanghai",
    "Nagasaki",
    "Saigon",
    "Manila",
    "Singapore",
    "Batavia"
]

# Base prices from the C code
BASE_PRICES = [
    [1000, 11, 16, 15, 14, 12, 10, 13],  # Opium
    [100,  11, 14, 15, 16, 10, 13, 12],  # Silk
    [10,   12, 16, 10, 11, 13, 14, 15],  # Arms
    [1,    10, 11, 12, 13, 14, 15, 16]   # General Cargo
]

@dataclass
class GameState:
    """Game state for Taipan."""
    
    # Basic information
    firm_name: str = "Your Firm"
    cash: int = 0
    bank: int = 0
    debt: int = 0
    booty: int = 0
    
    # Combat stats
    enemy_health: float = 20.0  # ec in C code
    enemy_damage: float = 0.5   # ed in C code
    battle_probability: int = 0  # bp in C code
    
    # Cargo and ship stats
    warehouse: List[int] = field(default_factory=lambda: [0] * 4)  # hkw_ in C code
    hold_: List[int] = field(default_factory=lambda: [0] * 4)      # hold_ in C code
    hold: int = 0                                                 # hold in C code
    capacity: int = 60
    guns: int = 0
    damage: int = 0
    
    # Time and location
    month: int = 1
    year: int = 1860
    port: int = 1  # 1 = Hong Kong
    
    # Special flags
    li_yuen_relation: int = 0  # li in C code
    wu_warned: bool = False    # wu_warn in C code
    wu_bailouts: int = 0       # wu_bailout in C code
    wu_warn: int = 0           # Track if Elder Brother Wu has warned about debt
    
    # Current prices
    price: List[int] = field(default_factory=lambda: [0] * 4)  # price in C code
    
    def __post_init__(self):
        """Initialize prices after object creation."""
        self.set_prices()
    
    def set_prices(self) -> None:
        """Set current prices based on port and base prices."""
        for i in range(4):
            base_price = BASE_PRICES[i][self.port]
            multiplier = random.randint(1, 3)  # Random multiplier between 1 and 3
            self.price[i] = (base_price // 2) * multiplier * BASE_PRICES[i][0]
    
    @property
    def total_warehouse(self) -> int:
        """Calculate total warehouse space used."""
        return sum(self.warehouse)
    
    def get_current_location(self) -> str:
        """Get the current location name."""
        return LOCATIONS[self.port]
    
    def get_current_date(self) -> str:
        """Get the current date as a string."""
        return f"{self.month}/{self.year}"
    
    def get_ship_status_text(self) -> str:
        """Get the ship status as text."""
        status = 100 - ((self.damage / self.capacity) * 100)
        if status >= 100:
            return "Perfect"
        elif status >= 80:
            return "Prime"
        elif status >= 60:
            return "Good"
        elif status >= 40:
            return "Fair"
        elif status >= 20:
            return "Poor"
        else:
            return "Critical"
    
    def calculate_ship_status(self) -> int:
        """Calculate ship status percentage."""
        return int(100 - ((self.damage / self.capacity) * 100))
    
    def format_money(self, amount: int) -> str:
        """Format money amount with commas."""
        return f"{amount:,}" 