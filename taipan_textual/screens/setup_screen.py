"""
Setup screen for Taipan.
"""

from typing import Union, Optional, cast
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events
from ..game_state import GameState
from ..utils import get_one
from ..screens.port_screen import PortScreen

class SetupScreen(Screen):
    """Screen for initial game setup."""
    
    def __init__(self, game_state: GameState, name: Union[str, None] = None, id: Union[str, None] = None, classes: Union[str, None] = None) -> None:
        super().__init__(name, id, classes)
        self.game_state = game_state
        self.input_widget: Optional[Input] = None
        self.instructions_widget: Optional[Static] = None
        self.stage: str = "name"  # name, cash_guns
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Static("TAIPAN!", classes="title"),
            Static("What will you name your firm, Taipan?", classes="instructions"),
            Input(placeholder="Enter firm name", classes="input"),
            id="setup-container"
        )
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        self.input_widget = cast(Input, self.query_one(Input))
        self.instructions_widget = cast(Static, self.query_one(".instructions"))
        self.input_widget.focus()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if self.stage == "cash_guns":
            choice = get_one(event)
            if choice is None:  # Escape key
                self.app.pop_screen()
                return
            
            if choice in ['1', '2']:
                if choice == '1':
                    # Start with cash and debt
                    self.game_state.cash = 400
                    self.game_state.debt = 5000
                    self.game_state.capacity = 60  # Set capacity to 60
                    self.game_state.hold = 0  # Start with empty hold
                    self.game_state.guns = 0
                    self.game_state.li_yuen_relation = 0
                    self.game_state.battle_probability = 10
                else:
                    # Start with guns and no cash
                    self.game_state.cash = 0
                    self.game_state.debt = 0
                    self.game_state.capacity = 10  # Set capacity to 10
                    self.game_state.hold = 0  # Start with empty hold
                    self.game_state.guns = 5
                    self.game_state.li_yuen_relation = 1
                    self.game_state.battle_probability = 7
                
                # Pop the setup screen and push the port screen
                self.app.pop_screen()
                self.app.push_screen(PortScreen(self.game_state))
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if self.stage == "name":
            # Handle firm name input
            if event.value.strip():
                self.game_state.firm_name = event.value.strip()
                self.stage = "cash_guns"
                # Clear the input widget and update instructions
                event.input.value = ""
                self._update_instructions()
                # Remove the input widget since we don't need it for the cash/guns choice
                event.input.remove()
            else:
                self.notify("Please enter a firm name", severity="error")
                event.input.value = ""
    
    def _update_instructions(self) -> None:
        """Update instructions based on current stage."""
        if self.instructions_widget is not None:
            if self.stage == "name":
                self.instructions_widget.update("What will you name your firm, Taipan?")
            elif self.stage == "cash_guns":
                self.instructions_widget.update(
                    "Do you want to start . . .\n\n"
                    "  1) With cash (and a debt)\n\n"
                    "                >> or <<\n\n"
                    "  2) With five guns and no cash\n"
                    "                (But no debt!)"
                ) 