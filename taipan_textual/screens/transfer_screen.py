"""
Transfer screen for moving cargo between ship and warehouse in Taipan.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container
from textual import events
from rich.panel import Panel
from rich.text import Text

from ..game_state import GameState, ITEMS

class TransferScreen(Screen):
    """Screen for transferring cargo between ship and warehouse."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the transfer screen."""
        yield Container(
            Static(self._create_status_panel(), id="transfer-status"),
            Static(self._create_items_panel(), id="transfer-items"),
            id="transfer-container"
        )
    
    def _create_status_panel(self) -> Panel:
        """Create the panel showing transfer status."""
        text = Text()
        text.append(f"Ship Cargo Space: {self.game_state.hold}/{self.game_state.capacity}\n")
        text.append(f"Warehouse Space: {self.game_state.total_warehouse}/10000\n")
        
        return Panel(
            text,
            title="Transfer Status",
            border_style="green"
        )
    
    def _create_items_panel(self) -> Panel:
        """Create the panel with available items to transfer."""
        text = Text()
        text.append("Items:\n\n")
        
        for i, item in enumerate(ITEMS):
            ship_qty = self.game_state.hold_[i]
            warehouse_qty = self.game_state.warehouse[i]
            text.append(f"{item}:\n")
            text.append(f"  Ship: {ship_qty} units\n")
            text.append(f"  Warehouse: {warehouse_qty} units\n")
            text.append(f"  Press {i+1} to transfer\n\n")
        
        return Panel(
            text,
            title="Items",
            border_style="yellow"
        )
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        try:
            item_index = int(event.key) - 1
            if 0 <= item_index < len(ITEMS):
                self.handle_transfer(item_index)
        except ValueError:
            pass
    
    def handle_transfer(self, item_index: int) -> None:
        """Handle transferring an item."""
        # TODO: Implement transfer logic
        self.app.pop_screen() 