"""
Bank screen for managing money in Taipan.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Container
from textual import events
from rich.panel import Panel
from rich.text import Text

from ..game_state import GameState
from ..screens.port_screen import PortScreen

class BankScreen(Screen):
    """Screen for visiting the bank."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
        self.amount_input = ""
        self.stage = "deposit"  # or "withdraw"
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static(self.render_content())
    
    def render_content(self) -> str:
        """Render the bank screen content."""
        content = f"""
[bold]Comprador's Report[/bold]

Current Port: {self.game_state.get_current_location()}
Cash: ${self.game_state.format_money(self.game_state.cash)}
Bank: ${self.game_state.format_money(self.game_state.bank)}

"""
        if self.stage == "deposit":
            content += f"How much will you deposit? (Press Enter to deposit all) {self.amount_input}"
        else:
            content += f"How much will you withdraw? (Press Enter to withdraw all) {self.amount_input}"
        
        return content
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "q":
            self.app.pop_screen()
            return
        
        if event.key.isdigit():
            self.amount_input += event.key
            self.query_one(Static).update(self.render_content())
            return
        
        if event.key == "enter":
            try:
                if self.stage == "deposit":
                    # Handle deposit
                    if not self.amount_input:
                        amount = self.game_state.cash
                    else:
                        amount = int(self.amount_input)
                    
                    if amount <= 0:
                        self.notify("Amount must be positive", severity="error")
                        return
                    
                    if amount > self.game_state.cash:
                        self.notify(f"Taipan, you only have ${self.game_state.format_money(self.game_state.cash)} in cash.", severity="error")
                        return
                    
                    self.game_state.cash -= amount
                    self.game_state.bank += amount
                    
                    # Move to withdrawal stage
                    self.stage = "withdraw"
                    self.amount_input = ""
                    self.query_one(Static).update(self.render_content())
                    
                else:
                    # Handle withdrawal
                    if not self.amount_input:
                        amount = self.game_state.bank
                    else:
                        amount = int(self.amount_input)
                    
                    if amount <= 0:
                        self.notify("Amount must be positive", severity="error")
                        return
                    
                    if amount > self.game_state.bank:
                        self.notify(f"Taipan, you only have ${self.game_state.format_money(self.game_state.bank)} in the bank.", severity="error")
                        return
                    
                    self.game_state.cash += amount
                    self.game_state.bank -= amount
                    
                    # Return to port screen
                    self.app.pop_screen()
                    self.app.push_screen(PortScreen(self.game_state))
                    
            except ValueError:
                self.notify("Invalid amount", severity="error")
            finally:
                if self.stage == "deposit":
                    self.amount_input = "" 