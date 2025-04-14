"""
Bank screen for managing money in Taipan.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container
from textual import events
from rich.panel import Panel
from rich.text import Text

from ..game_state import GameState

class BankScreen(Screen):
    """Screen for bank transactions."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the bank screen."""
        yield Container(
            Static(self._create_bank_panel(), id="bank-status"),
            Static(self._create_actions_panel(), id="bank-actions"),
            id="bank-container"
        )
    
    def _create_bank_panel(self) -> Panel:
        """Create the panel showing bank status."""
        text = Text()
        text.append(f"Cash: ${self.game_state.format_money(self.game_state.cash)}\n")
        text.append(f"Bank: ${self.game_state.format_money(self.game_state.bank)}\n")
        text.append(f"Debt: ${self.game_state.format_money(self.game_state.debt)}\n")
        
        return Panel(
            text,
            title="Bank Status",
            border_style="green"
        )
    
    def _create_actions_panel(self) -> Panel:
        """Create the panel with available bank actions."""
        text = Text()
        text.append("Available Actions:\n\n")
        text.append("D: Deposit money\n")
        text.append("W: Withdraw money\n")
        text.append("P: Pay debt\n")
        text.append("B: Borrow money\n")
        
        return Panel(
            text,
            title="Actions",
            border_style="yellow"
        )
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        key = event.key.lower()
        
        if key == 'd':
            self.handle_deposit()
        elif key == 'w':
            self.handle_withdraw()
        elif key == 'p':
            self.handle_pay_debt()
        elif key == 'b':
            self.handle_borrow()
    
    def handle_deposit(self) -> None:
        """Handle depositing money."""
        # TODO: Implement deposit logic
        self.app.pop_screen()
    
    def handle_withdraw(self) -> None:
        """Handle withdrawing money."""
        # TODO: Implement withdraw logic
        self.app.pop_screen()
    
    def handle_pay_debt(self) -> None:
        """Handle paying debt."""
        # TODO: Implement pay debt logic
        self.app.pop_screen()
    
    def handle_borrow(self) -> None:
        """Handle borrowing money."""
        # TODO: Implement borrow logic
        self.app.pop_screen() 