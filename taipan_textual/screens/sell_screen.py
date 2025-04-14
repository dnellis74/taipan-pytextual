"""
Sell screen for selling items in Taipan.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Container
from textual import events
from rich.panel import Panel
from rich.text import Text
from typing import Literal, Optional, Union, cast

from ..game_state import GameState, ITEMS
from ..utils import get_one
from .port_screen import PortScreen

class SellScreen(Screen):
    """Screen for selling cargo."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
        self.amount_input = ""
        self.selected_cargo = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static(self.render_content())
    
    def render_content(self) -> str:
        """Render the sell screen content."""
        content = f"""
[bold]Sell Cargo[/bold]

Current Port: {self.game_state.get_current_location()}
Cash: ${self.game_state.format_money(self.game_state.cash)}
Hold Space: {self.game_state.hold}/{self.game_state.capacity}

[bold]Available Cargo:[/bold]
O) Opium: ${self.game_state.format_money(self.game_state.price[0])} per unit (Have: {self.game_state.hold_[0]})
S) Silk: ${self.game_state.format_money(self.game_state.price[1])} per unit (Have: {self.game_state.hold_[1]})
A) Arms: ${self.game_state.format_money(self.game_state.price[2])} per unit (Have: {self.game_state.hold_[2]})
G) General: ${self.game_state.format_money(self.game_state.price[3])} per unit (Have: {self.game_state.hold_[3]})

Select cargo type (O/S/A/G) or press Q to quit:
"""
        if self.selected_cargo:
            cargo_name = {"o": "Opium", "s": "Silk", "a": "Arms", "g": "General"}[self.selected_cargo]
            content += f"\nEnter amount of {cargo_name} to sell (or press Enter to sell all): {self.amount_input}"
        return content
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "q":
            self.app.pop_screen()
            return
        
        if self.selected_cargo is None:
            # First key press - select cargo type
            if event.key.lower() in ["o", "s", "a", "g"]:
                self.selected_cargo = event.key.lower()
                self.query_one(Static).update(self.render_content())
                return
        
        if self.selected_cargo is not None:
            # Second key press - enter amount
            if event.key.isdigit():
                self.amount_input += event.key
                self.query_one(Static).update(self.render_content())
                return
            
            if event.key == "enter":
                try:
                    cargo_index = {"o": 0, "s": 1, "a": 2, "g": 3}[self.selected_cargo]
                    
                    # If no amount entered, sell all
                    if not self.amount_input:
                        amount = self.game_state.hold_[cargo_index]
                    else:
                        amount = int(self.amount_input)
                    
                    if amount <= 0:
                        self.notify("Amount must be positive", severity="error")
                        return
                    
                    # Check if we have enough to sell
                    if self.game_state.hold_[cargo_index] < amount:
                        self.notify("Not enough cargo to sell", severity="error")
                        return
                    
                    # Make the sale
                    self.game_state.cash += amount * self.game_state.price[cargo_index]
                    self.game_state.hold_[cargo_index] -= amount
                    self.game_state.hold -= amount
                    
                    # Refresh port screen
                    self.app.pop_screen()
                    self.app.push_screen(PortScreen(self.game_state))
                    
                except ValueError:
                    self.notify("Invalid amount", severity="error")
                finally:
                    self.amount_input = ""
                    self.selected_cargo = None 