"""
Complete travel screen for Taipan.
"""

from typing import Union
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container
import random

from ..game_state import GameState
from .port_screen import PortScreen

# Port locations
LOCATIONS = {
    1: "Hong Kong",
    2: "Shanghai",
    3: "Nagasaki",
    4: "Saigon",
    5: "Manila",
    6: "Singapore",
    7: "Batavia"
}

class CompleteTravelScreen(Screen):
    """Screen for completing travel to a new port."""
    
    def __init__(
        self, 
        game_state: GameState,
        name: Union[str, None] = None, 
        id: Union[str, None] = None, 
        classes: Union[str, None] = None
    ) -> None:
        super().__init__(name, id, classes)
        self.game_state = game_state
        self.time = ((self.game_state.year - 1860) * 12) + self.game_state.month
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Static("", id="travel-status"),
            Static("", id="travel-message"),
            id="travel-container"
        )
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        self._update_travel_status()
        self._update_travel_message("Traveling...")
        
        self.game_state.port = self.game_state.destination_port
        # Check for storm
        if random.randint(1, 10) == 1:  # 1 in 10 chance of storm
            self.notify("Storm, Taipan!!", severity="warning")
            
            # Check for sinking
            if random.randint(1, 30) == 1:  # 1 in 30 chance of sinking
                self.notify("   I think we're going down!!", severity="warning")
                
                # Check if we actually sink
                if ((self.game_state.damage / self.game_state.capacity * 3) * random.random()) >= 1:
                    self.notify("We're going down, Taipan!!", severity="error")
                    # TODO: Implement final_stats
                    return
            
            self.notify("    We made it!!", severity="information")
            
            # Check for being blown off course
            if random.randint(1, 3) == 1:  # 1 in 3 chance of being blown off course                
                while self.game_state.port == self.game_state.destination_port:
                    self.game_state.port = random.randint(1, 7)
                self.notify(f"We've been blown off course\nto {LOCATIONS[self.game_state.port]}", severity="warning")
            
        
        # Advance date
        self.game_state.month += 1
        if self.game_state.month == 13:
            self.game_state.month = 1
            self.game_state.year += 1
            self.game_state.enemy_health += 10
            self.game_state.enemy_damage += 0.5
        
        # Update debt and bank balance
        self.game_state.debt = int(self.game_state.debt * 1.1)  # 10% increase
        self.game_state.bank = int(self.game_state.bank * 1.005)  # 0.5% increase
        
        # Update location
        self.notify(f"Arriving at {LOCATIONS[self.game_state.port]}...", severity="information")
        
        
        # Update prices
        self.game_state.set_prices()
        
        # Return to port screen
        self.app.pop_screen()
        self.app.push_screen(PortScreen(self.game_state))
    
    def _update_travel_status(self) -> None:
        """Update the travel status display."""
        self.query_one("#travel-status", Static).update(
            f"Current location: {LOCATIONS[self.game_state.port]}\n"
            f"Destination: {LOCATIONS[self.game_state.destination_port]}\n"
            f"Hold: {self.game_state.hold}/{self.game_state.capacity}\n"
            f"Guns: {self.game_state.guns}\n"
            f"Damage: {self.game_state.damage}"
        )
    
    def _update_travel_message(self, message: str) -> None:
        """Update the travel message display."""
        self.query_one("#travel-message", Static).update(message) 