"""
Transfer screen for moving cargo between ship and warehouse in Taipan.
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

class TransferScreen(Screen):
    """Screen for transferring cargo between ship and warehouse."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
        self.amount_input = ""
        self.current_cargo: int = 0
        self.direction: Optional[Literal["to_warehouse", "to_ship"]] = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static(self.render_content())
    
    def render_content(self) -> str:
        """Render the transfer screen content."""
        content = f"""
[bold]Comprador's Report[/bold]

Current Port: {self.game_state.get_current_location()}
Hold Space: {self.game_state.hold}/{self.game_state.capacity}
Warehouse Space: {sum(self.game_state.warehouse)}/10000

[bold]Current Cargo:[/bold]
"""
        for i, item in enumerate(ITEMS):
            content += f"{item}: {self.game_state.hold_[i]} in hold, {self.game_state.warehouse[i]} in warehouse\n"
        
        if self.direction is not None:
            cargo_name = ITEMS[self.current_cargo]
            if self.direction == "to_warehouse":
                content += f"\nHow much {cargo_name} shall I move to the warehouse, Taipan? {self.amount_input}"
            else:
                content += f"\nHow much {cargo_name} shall I move aboard ship, Taipan? {self.amount_input}"        
        return content
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        # First check if we have any cargo to transfer
        if not any(self.game_state.hold_) and not any(self.game_state.warehouse):
            self.notify("You have no cargo, Taipan.", severity="error")
            self.app.pop_screen()
            return
        
        # Start with first cargo type
        self.current_cargo = 0
        self._check_next_cargo()
    
    def _check_next_cargo(self) -> None:
        """Check the next cargo type for transfer."""
        if self.current_cargo >= len(ITEMS):
            # All cargo types processed, return to port
            self.app.pop_screen()
            self.app.push_screen(PortScreen(self.game_state))
            return
        
        # Check hold for this cargo type
        if self.game_state.hold_[self.current_cargo] > 0:
            self.direction = "to_warehouse"
            self.query_one(Static).update(self.render_content())
            return
        
        # Check warehouse for this cargo type
        if self.game_state.warehouse[self.current_cargo] > 0:
            self.direction = "to_ship"
            self.query_one(Static).update(self.render_content())
            return
        
        # Move to next cargo type
        self.current_cargo += 1
        self._check_next_cargo()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key.isdigit():
            self.amount_input += event.key
            self.query_one(Static).update(self.render_content())
            return
        
        if event.key == "enter":
            try:
                if self.direction is None:
                    return
                    
                if self.direction == "to_warehouse":
                    # Moving to warehouse
                    if not self.amount_input:
                        amount = self.game_state.hold_[self.current_cargo]
                    else:
                        amount = int(self.amount_input)
                    
                    if amount < 0:
                        self.notify("Amount must be positive", severity="error")
                        return
                    
                    if amount > self.game_state.hold_[self.current_cargo]:
                        self.notify(f"You have only {self.game_state.hold_[self.current_cargo]}, Taipan.", severity="error")
                        return
                    
                    in_use = sum(self.game_state.warehouse)
                    if in_use + amount > 10000:
                        if in_use == 10000:
                            self.notify("Your warehouse is full, Taipan!", severity="error")
                        else:
                            self.notify(f"Your warehouse will only hold an additional {10000 - in_use}, Taipan!", severity="error")
                        return
                    
                    self.game_state.hold_[self.current_cargo] -= amount
                    self.game_state.warehouse[self.current_cargo] += amount
                    self.game_state.hold -= amount  # Decrease hold space when moving to warehouse
                    
                    # After moving to warehouse, check if we can move from warehouse
                    if self.game_state.warehouse[self.current_cargo] > 0:
                        self.direction = "to_ship"
                        self.amount_input = ""
                        self.query_one(Static).update(self.render_content())
                        return
                    
                else:
                    # Moving to ship
                    if not self.amount_input:
                        amount = self.game_state.warehouse[self.current_cargo]
                    else:
                        amount = int(self.amount_input)
                    
                    if amount < 0:
                        self.notify("Amount must be positive", severity="error")
                        return
                    
                    if amount > self.game_state.warehouse[self.current_cargo]:
                        self.notify(f"You have only {self.game_state.warehouse[self.current_cargo]}, Taipan.", severity="error")
                        return
                    
                    if self.game_state.hold + amount > self.game_state.capacity:
                        self.notify("Not enough hold space", severity="error")
                        return
                    
                    self.game_state.warehouse[self.current_cargo] -= amount
                    self.game_state.hold_[self.current_cargo] += amount
                    self.game_state.hold += amount  # Increase hold space when moving to ship
                
                # Move to next cargo type
                self.amount_input = ""
                self.current_cargo += 1
                self.direction = None
                self._check_next_cargo()
                    
            except ValueError:
                self.notify("Invalid amount", severity="error")
            finally:
                self.amount_input = ""
