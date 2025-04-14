"""
Battle screen for sea battles in Taipan.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container
from textual import events
from rich.panel import Panel
from rich.text import Text

from ..game_state import GameState, BATTLE_NOT_FINISHED, BATTLE_WON, BATTLE_INTERRUPTED, BATTLE_FLED, BATTLE_LOST

class BattleScreen(Screen):
    """Screen for handling sea battles."""
    
    def __init__(self, game_state: GameState, enemy_type: int, num_ships: int):
        super().__init__()
        self.game_state = game_state
        self.enemy_type = enemy_type
        self.num_ships = num_ships
        self.ships_on_screen = [0] * 10
        self.num_on_screen = 0
        self.orders = 0
        self.ok = 0
        self.ik = 1
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the battle screen."""
        yield Container(
            Static(self._create_battle_panel(), id="battle-status"),
            Static(self._create_orders_panel(), id="battle-orders"),
            id="battle-container"
        )
    
    def _create_battle_panel(self) -> Panel:
        """Create the panel showing battle status."""
        text = Text()
        text.append(f"{self.num_ships} ships attacking, Taipan!\n")
        text.append(f"Your orders are to: {self._get_orders_text()}\n")
        text.append(f"We have {self.game_state.guns} guns\n")
        text.append(f"Current seaworthiness: {self.game_state.get_ship_status_text()}\n")
        
        # Draw ships
        for i in range(10):
            if i == 5:
                text.append("\n")
            if self.ships_on_screen[i] > 0:
                text.append(self._draw_lorcha(i))
            else:
                text.append("        ")
            text.append(" ")
        
        return Panel(
            text,
            title="Battle Status",
            border_style="red"
        )
    
    def _create_orders_panel(self) -> Panel:
        """Create the panel with battle orders."""
        text = Text()
        text.append("Available Orders:\n\n")
        text.append("Fight (F)\n")
        text.append("Run (R)\n")
        text.append("Throw Cargo (T)")
        
        return Panel(
            text,
            title="Orders",
            border_style="yellow"
        )
    
    def _get_orders_text(self) -> str:
        """Get text description of current orders."""
        if self.orders == 0:
            return ""
        elif self.orders == 1:
            return "Fight"
        elif self.orders == 2:
            return "Run"
        else:
            return "Throw Cargo"
    
    def _draw_lorcha(self, index: int) -> str:
        """Draw a lorcha (ship) at the given index."""
        x = (index % 5 + 1) * 10
        y = 6 if index < 5 else 12
        
        # TODO: Implement proper ASCII art for ships
        return "-|-_|_  "
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        key = event.key.lower()
        
        if key == 'f':
            self.handle_fight()
        elif key == 'r':
            self.handle_run()
        elif key == 't':
            self.handle_throw_cargo()
    
    def handle_fight(self) -> None:
        """Handle fight orders."""
        if self.game_state.guns == 0:
            # TODO: Show message about having no guns
            return
        
        self.orders = 1
        # TODO: Implement fighting logic
        self.refresh_battle_display()
    
    def handle_run(self) -> None:
        """Handle run orders."""
        self.orders = 2
        # TODO: Implement running logic
        self.refresh_battle_display()
    
    def handle_throw_cargo(self) -> None:
        """Handle throwing cargo orders."""
        self.orders = 3
        # TODO: Implement cargo throwing logic
        self.refresh_battle_display()
    
    def refresh_battle_display(self) -> None:
        """Refresh the battle display after orders change."""
        if battle_status := self.query_one("#battle-status", Static):
            battle_status.update(self._create_battle_panel()) 