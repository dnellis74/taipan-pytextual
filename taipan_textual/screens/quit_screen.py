"""
Quit screen for Taipan.
"""

from typing import Union, Optional, cast
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events
import random
import time

from ..game_state import GameState, BATTLE_NOT_FINISHED, BATTLE_WON, BATTLE_INTERRUPTED, BATTLE_FLED, BATTLE_LOST
from .battle_screen import BattleScreen, LI_YUEN
from .complete_travel_screen import CompleteTravelScreen

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

class QuitScreen(Screen):
    """Screen for handling travel and quitting."""
    
    def __init__(
        self, 
        game_state: GameState,
        name: Union[str, None] = None, 
        id: Union[str, None] = None, 
        classes: Union[str, None] = None
    ) -> None:
        super().__init__(name, id, classes)
        self.game_state = game_state
        self.port = 0
        self.time = ((self.game_state.year - 1860) * 12) + self.game_state.month
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Static("", id="quit-status"),
            Static("", id="quit-message"),
            Static("", id="quit-options"),
            id="quit-container"
        )
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        # Check if ship is overloaded
        if self.game_state.hold > self.game_state.capacity:
            self.notify("Your ship is overloaded! You must lighten your cargo before traveling.", severity="error")
            self.app.pop_screen()
            return
        
        self._update_quit_status()
        self._update_quit_message("Where to, Taipan?")
        self._update_quit_options(
            "1) Hong Kong    2) Shanghai    3) Nagasaki    4) Saigon\n"
            "5) Manila      6) Singapore   7) Batavia     q) Quit"
        )
    
    def _update_quit_status(self) -> None:
        """Update the quit status display."""
        self.query_one("#quit-status", Static).update(
            f"Current location: {LOCATIONS[self.game_state.port]}\n"
            f"Hold: {self.game_state.hold}/{self.game_state.capacity}\n"
            f"Guns: {self.game_state.guns}\n"
            f"Damage: {self.game_state.damage}"
        )
    
    def _update_quit_message(self, message: str) -> None:
        """Update the quit message display."""
        self.query_one("#quit-message", Static).update(message)
    
    def _update_quit_options(self, options: str) -> None:
        """Update the quit options display."""
        self.query_one("#quit-options", Static).update(options)
    
    def _handle_travel(self, port: int) -> None:
        """Handle travel to a new port."""
        # Check for battle
        if self.game_state.battle_probability > 0 and random.randint(0, self.game_state.battle_probability - 1) == 0:
            # Calculate number of ships
            num_ships = random.randint(1, (self.game_state.capacity // 10) + self.game_state.guns)
            if num_ships > 9999:
                num_ships = 9999
                        
            # Start battle
            battle_screen = BattleScreen(self.game_state, num_ships=num_ships)
            self.app.push_screen(battle_screen)
        else:
            # If no battle, just complete the travel
            self.app.push_screen(CompleteTravelScreen(self.game_state, port))
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == 'q':
            self.app.exit()
        elif event.key in ['1', '2', '3', '4', '5', '6', '7']:
            port = int(event.key)
            if port != self.game_state.port:
                self._handle_travel(port)
            else:
                self.notify("You are already at that port!", severity="warning") 