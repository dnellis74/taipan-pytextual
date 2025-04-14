"""
Main game UI for Taipan using Textual.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Input, Label
from textual.screen import Screen
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

from .game_state import GameState, ITEMS, LOCATIONS
from .screens import (
    BuyScreen,
    SellScreen,
    BankScreen,
    TransferScreen,
    WheedleScreen,
    RetireScreen,
    PortScreen,
    SetupScreen
)

class TaipanApp(App):
    """Main Taipan application."""
    
    CSS = """
    #port-container {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 1fr;
        grid-rows: 1fr;
        padding: 1;
    }
    
    #status {
        width: 100%;
        height: 100%;
    }
    
    #prices {
        width: 100%;
        height: 100%;
    }
    
    #actions {
        width: 100%;
        height: 100%;
    }

    .panel {
        border: solid yellow;
        padding: 1;
    }

    .panel-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
    
    def on_mount(self) -> None:
        """Set up the application when it starts."""
        self.push_screen(SetupScreen(self.game_state))
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        key = event.key.lower()
        
        # Map keys to actions
        action_map = {
            'b': 'buy',
            's': 'sell',
            'v': 'visit_bank',
            't': 'transfer',
            'q': 'quit',
            'w': 'wheedle',
            'r': 'retire'
        }
        
        if key in action_map:
            action = action_map[key]
            self.handle_action(action)
    
    def handle_action(self, action: str) -> None:
        """Handle the selected action."""
        if action == "buy":
            self.app.push_screen(BuyScreen(self.game_state))
        elif action == "sell":
            self.app.push_screen(SellScreen(self.game_state))
        elif action == "visit_bank":
            self.app.push_screen(BankScreen(self.game_state))
        elif action == "transfer":
            self.app.push_screen(TransferScreen(self.game_state))
        elif action == "quit":
            self.app.exit()
        elif action == "wheedle" and self.game_state.port == 1:
            self.app.push_screen(WheedleScreen(self.game_state))
        elif action == "retire" and self.game_state.port == 1:
            self.app.push_screen(RetireScreen(self.game_state))
    
    def _update_status(self) -> None:
        """Update the status display."""
        status_text = (
            f"Location: {self.game_state.get_current_location()}\n"
            f"Cash: ${self.game_state.format_money(self.game_state.cash)}\n"
            f"Bank: ${self.game_state.format_money(self.game_state.bank)}\n"
            f"Ship Status: {self.game_state.calculate_ship_status()}%\n"
            f"Cargo Space: {self.game_state.hold}/{self.game_state.capacity}"
        )
        if status_panel := self.query_one("#status", Static):
            status_panel.update(status_text) 