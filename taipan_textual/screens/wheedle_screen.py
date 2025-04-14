"""
Wheedle screen for Taipan game.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container
from rich.panel import Panel
from rich.text import Text

from ..game_state import GameState

class WheedleScreen(Screen):
    """Screen for wheedling Elder Brother Wu."""
    
    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the wheedle screen."""
        yield Container(
            Static(self._create_wheedle_panel(), id="wheedle-status"),
            id="wheedle-container"
        )
    
    def _create_wheedle_panel(self) -> Panel:
        """Create the panel showing wheedle status."""
        text = Text()
        text.append("Elder Brother Wu is not available right now.\n")
        text.append("Please try again later.")
        
        return Panel(
            text,
            title="Wheedle Wu",
            border_style="yellow"
        ) 