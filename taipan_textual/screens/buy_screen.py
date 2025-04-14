"""
Buy screen for Taipan.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container
from textual import events
from rich.panel import Panel
from rich.text import Text
from typing import Literal, Optional, Union, cast

from ..game_state import GameState, ITEMS
from ..utils import get_one
from .port_screen import PortScreen

class BuyScreen(Screen):
    """Screen for buying cargo."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
        self.amount_input = ""
        self.selected_cargo = None
        self.amount_dialog = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static(self.render_content())
    
    def render_content(self) -> str:
        """Render the buy screen content."""
        content = f"""
[bold]Buy Cargo[/bold]

Current Port: {self.game_state.get_current_location()}
Cash: ${self.game_state.format_money(self.game_state.cash)}
Hold Space: {self.game_state.hold}/{self.game_state.capacity}

[bold]Available Cargo:[/bold]
O) Opium: ${self.game_state.format_money(self.game_state.price[0])} per unit
S) Silk: ${self.game_state.format_money(self.game_state.price[1])} per unit
A) Arms: ${self.game_state.format_money(self.game_state.price[2])} per unit
G) General: ${self.game_state.format_money(self.game_state.price[3])} per unit

Select cargo type (O/S/A/G) or press Q to quit:
"""
        if self.selected_cargo:
            cargo_name = {"o": "Opium", "s": "Silk", "a": "Arms", "g": "General"}[self.selected_cargo]
            content += f"\nEnter amount of {cargo_name} to buy: {self.amount_input}"
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
                    amount = int(self.amount_input)
                    if amount <= 0:
                        self.notify("Amount must be positive", severity="error")
                        return
                    
                    # Calculate total cost
                    cargo_index = {"o": 0, "s": 1, "a": 2, "g": 3}[self.selected_cargo]
                    total_cost = amount * self.game_state.price[cargo_index]
                    
                    # Check if player can afford it
                    if total_cost > self.game_state.cash:
                        self.notify("Not enough cash", severity="error")
                        return
                    
                    # Check if there's enough hold space
                    if self.game_state.hold + amount > self.game_state.capacity:
                        self.notify("Not enough hold space", severity="error")
                        return
                    
                    # Make the purchase
                    self.game_state.cash -= total_cost
                    self.game_state.hold_[cargo_index] += amount
                    self.game_state.hold += amount
                    
                    # Refresh port screen
                    self.app.pop_screen()
                    self.app.push_screen(PortScreen(self.game_state))
                    
                except ValueError:
                    self.notify("Invalid amount", severity="error")
                finally:
                    self.amount_input = ""
                    self.selected_cargo = None 