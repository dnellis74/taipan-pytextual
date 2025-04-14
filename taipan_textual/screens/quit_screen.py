"""
Quit screen for Taipan.
"""

from typing import Union, Optional, cast
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events
from ..game_state import GameState, LOCATIONS
import random

class QuitScreen(Screen):
    """Screen for selecting a port to travel to."""
    
    def __init__(self, game_state: GameState, name: Union[str, None] = None, id: Union[str, None] = None, classes: Union[str, None] = None) -> None:
        super().__init__(name, id, classes)
        self.game_state = game_state
        self.input_widget: Optional[Input] = None
        self.instructions: Optional[Static] = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Static("TAIPAN!", classes="title"),
            Static("Select a port to travel to:", classes="instructions"),
            Input(placeholder="Enter port number (1-7)", classes="input"),
            id="quit-container"
        )
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        self.input_widget = cast(Input, self.query_one(Input))
        self.instructions = cast(Static, self.query_one(".instructions"))
        self.input_widget.focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        try:
            port = int(event.value)
            if 1 <= port <= 7:
                self._handle_travel(port)
            else:
                self.notify("Invalid port number. Please enter a number between 1 and 7.", severity="error")
        except ValueError:
            self.notify("Please enter a valid number.", severity="error")
        event.input.value = ""
    
    def _handle_travel(self, port: int) -> None:
        """Handle travel to a new port."""
        # Check for battle
        if self.game_state.battle_probability > 0 and random.random() < self.game_state.battle_probability / 100.0:
            self.notify("You have been attacked by pirates!", severity="warning")
            # TODO: Implement battle screen
            return
        
        # Update location
        self.game_state.port = port
        self.notify(f"Arrived at {LOCATIONS[port]}", severity="information")
        
        # Update prices
        self.game_state.set_prices()
        
        # Return to port screen
        self.app.pop_screen()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "escape":
            self.app.pop_screen() 