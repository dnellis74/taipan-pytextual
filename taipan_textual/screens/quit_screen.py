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
            Static("Comprador's Report\n\n", classes="title"),
            Static("Taipan, do you wish me to go to:\n1) Hong Kong, 2) Shanghai, 3) Nagasaki,\n4) Saigon, 5) Manila, 6) Singapore, or\n7) Batavia ?", classes="instructions"),
            Input(placeholder="Enter port number (1-7)", classes="input"),
            id="quit-container"
        )
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        # Check if ship is overloaded
        if self.game_state.hold > self.game_state.capacity:
            self.notify("Your ship is overloaded! You must lighten your cargo before traveling.", severity="error")
            self.app.pop_screen()
            return
            
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
                original_port = port
                while port == original_port:
                    port = random.randint(1, 7)
                self.notify(f"We've been blown off course\nto {LOCATIONS[port]}", severity="warning")
        
        # Advance date
        self.game_state.month += 1
        if self.game_state.month == 13:
            self.game_state.month = 1
            self.game_state.year += 1
            # TODO: Update enemy combat stats when we implement battles
            # self.game_state.enemy_health += 10
            # self.game_state.enemy_damage += 0.5
        
        # Update debt and bank balance
        self.game_state.debt = int(self.game_state.debt * 1.1)  # 10% increase
        self.game_state.bank = int(self.game_state.bank * 1.005)  # 0.5% increase
        
        # Update location
        self.game_state.port = port
        self.notify(f"Arriving at {LOCATIONS[port]}...", severity="information")
        
        # Update prices
        self.game_state.set_prices()
        
        # Return to port screen
        self.app.pop_screen()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "escape":
            self.app.pop_screen() 