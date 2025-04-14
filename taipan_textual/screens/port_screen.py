"""
Port screen for Taipan game.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from ..game_state import GameState, ITEMS, LOCATIONS

class PortScreen(Screen):
    """Screen showing the current port status and available actions."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the port screen."""
        yield Header()
        yield Container(
            Static(self._create_status_panel(), id="status"),
            Static(self._create_prices_panel(), id="prices"),
            Static(self._create_actions_panel(), id="actions"),
            id="port-container"
        )
        yield Footer()
    
    def refresh(self, *args, **kwargs) -> None:
        """Refresh the port screen display."""
        # Only try to update widgets if they exist
        try:
            if status_widget := self.query_one("#status", Static):
                status_widget.update(self._create_status_panel())
            if prices_widget := self.query_one("#prices", Static):
                prices_widget.update(self._create_prices_panel())
            if actions_widget := self.query_one("#actions", Static):
                actions_widget.update(self._create_actions_panel())
        except Exception:
            # If widgets don't exist yet, just pass
            pass
        super().refresh(*args, **kwargs)
    
    def _create_status_panel(self) -> Panel:
        """Create the panel showing current status."""
        text = Text()
        text.append(f"Date: {self.game_state.month}/{self.game_state.year}\n")
        text.append(f"Location: {self.game_state.get_current_location()}\n")
        text.append(f"Cash: ${self.game_state.format_money(self.game_state.cash)}\n")
        text.append(f"Bank: ${self.game_state.format_money(self.game_state.bank)}\n")
        text.append(f"Debt: ${self.game_state.format_money(self.game_state.debt)}\n")
        text.append(f"Ship Status: {self.game_state.get_ship_status_text()}\n")
        text.append(f"Guns: {self.game_state.guns}\n")
        text.append(f"Hold Space: {self.game_state.hold}/{self.game_state.capacity}\n")
        
        # Create a table for cargo
        table = Table(show_header=False, box=None)
        table.add_column("Warehouse", style="cyan")
        table.add_column("Hold", style="green")
        
        for i, item in enumerate(ITEMS):
            table.add_row(
                f"{item}: {self.game_state.warehouse[i]}",
                f"{item}: {self.game_state.hold_[i]}"
            )
        
        content = Group(text, table)
        
        return Panel(
            content,
            title="Status",
            border_style="blue"
        )
    
    def _create_prices_panel(self) -> Panel:
        """Create the panel showing current prices."""
        text = Text()
        text.append("Current Prices:\n\n", style="bold")
        
        for i, item in enumerate(ITEMS):
            text.append(f"{item}: ${self.game_state.format_money(self.game_state.price[i])}\n")
        
        return Panel(
            text,
            title="Prices",
            border_style="yellow"
        )
    
    def _create_actions_panel(self) -> Panel:
        """Create the panel with available actions."""
        actions = [
            ("Buy", "b"),
            ("Sell", "s"),
            ("Visit Bank", "v"),
            ("Transfer Cargo", "t"),
            ("Quit Trading", "q")
        ]
        
        if self.game_state.port == 1:  # Hong Kong
            actions.extend([
                ("Wheedle Wu", "w"),
                ("Retire", "r")
            ])
        
        # Create a simple string representation of the actions
        action_text = "\n".join(f"{action} ({key})" for action, key in actions)
        
        return Panel(
            action_text,
            title="Actions",
            border_style="yellow"
        ) 