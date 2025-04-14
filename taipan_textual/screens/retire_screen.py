"""
Retire screen for Taipan game.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container
from rich.panel import Panel
from rich.text import Text

from ..game_state import GameState

class RetireScreen(Screen):
    """Screen for retiring from the game."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the retire screen."""
        yield Container(
            Static(self._create_retire_panel(), id="retire-status"),
            id="retire-container"
        )
    
    def _create_retire_panel(self) -> Panel:
        """Create the panel showing retirement status."""
        text = Text()
        text.append("You have retired from the game.\n")
        text.append("Thank you for playing!")
        
        return Panel(
            text,
            title="Retirement",
            border_style="yellow"
        ) 