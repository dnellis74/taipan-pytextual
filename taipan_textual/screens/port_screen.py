"""
Port screen for Taipan game.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group
import random
from typing import cast
from textual import events

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
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        # Check for random events when arriving at port
        self._check_random_events()
    
    def _check_random_events(self) -> None:
        """Check for random events that can occur when arriving at a port."""
        # Li Yuen extortion (only in Hong Kong, if not already paid, and have cash)
        if (self.game_state.port == 1 and 
            self.game_state.li_yuen_relation == 0 and 
            self.game_state.cash > 0):
            self._li_yuen_extortion()
        
        # TODO: Implement mchenry (ship repair in Hong Kong)
        if self.game_state.port == 1 and self.game_state.damage > 0:
            pass  # TODO: Implement mchenry
        
        # TODO: Implement Elder Brother Wu warning
        if (self.game_state.port == 1 and 
            self.game_state.debt >= 10000 and 
            self.game_state.wu_warn == 0):
            pass  # TODO: Implement Wu warning
        
        # TODO: Implement Elder Brother Wu visit
        if self.game_state.port == 1:
            pass  # TODO: Implement Elder Brother Wu
        
        # TODO: Implement new ship/gun offers
        if random.randint(1, 4) == 1:
            pass  # TODO: Implement new ship/gun offers
        
        # TODO: Implement opium seizure
        if (self.game_state.port != 1 and 
            random.randint(1, 18) == 1 and 
            self.game_state.hold_[0] > 0):
            pass  # TODO: Implement opium seizure
        
        # TODO: Implement warehouse theft
        if (random.randint(1, 50) == 1 and 
            sum(self.game_state.warehouse) > 0):
            pass  # TODO: Implement warehouse theft
        
        # TODO: Implement Li Yuen relation decay
        if random.randint(1, 20) == 1:
            pass  # TODO: Implement Li Yuen relation decay
        
        # TODO: Implement Li Yuen summons
        if (self.game_state.port != 1 and 
            self.game_state.li_yuen_relation == 0 and 
            random.randint(1, 4) != 1):
            pass  # TODO: Implement Li Yuen summons
        
        # TODO: Implement good prices
        if random.randint(1, 9) == 1:
            pass  # TODO: Implement good prices
        
        # TODO: Implement robbery
        if (self.game_state.cash > 25000 and 
            random.randint(1, 20) == 1):
            pass  # TODO: Implement robbery
    
    def _li_yuen_extortion(self) -> None:
        """Handle Li Yuen's extortion attempt."""
        time = ((self.game_state.year - 1860) * 12) + self.game_state.month
        i = 1.8
        j = 0
        
        if time > 12:
            j = random.randint(1000 * time, 2000 * time)
            i = 1
        
        amount = int((self.game_state.cash / i) * random.random() + j)
        
        self.notify(f"Comprador's Report\n\nLi Yuen asks ${self.game_state.format_money(amount)} in donation\nto the temple of Tin Hau, the Sea\nGoddess.  Will you pay? (Y/N)", severity="warning")
        
        # Store the amount for the key handler
        self._li_yuen_amount = amount 

    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "escape":
            self.app.exit()
        elif hasattr(self, '_li_yuen_amount'):
            # Handle Li Yuen extortion choice
            if event.key.lower() == 'y':
                if self._li_yuen_amount <= self.game_state.cash:
                    self.game_state.cash -= self._li_yuen_amount
                    self.game_state.li_yuen_relation = 1
                    self.notify("Thank you, Taipan.", severity="information")
                else:
                    # TODO: Implement Elder Brother Wu loan option
                    self.game_state.cash = 0
                    self.notify("You don't have enough cash!", severity="error")
            elif event.key.lower() == 'n':
                self.notify("Very well, Taipan.", severity="information")
            else:
                return  # Ignore other keys
            
            # Clear the stored amount
            del self._li_yuen_amount 