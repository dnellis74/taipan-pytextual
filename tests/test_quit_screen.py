"""Tests for the QuitScreen functionality."""

from taipan_textual.game_state import GameState
from taipan_textual.screens.quit_screen import QuitScreen
from textual.app import App

class TestApp(App):
    """Test app for Li Yuen extortion."""
    
    def on_mount(self) -> None:
        """Set up the test."""
        # Create game state with different cash amounts
        self.game_state = GameState()
        self.game_state.port = 1  # Hong Kong
        self.game_state.li_yuen_relation = 0  # Not paid yet
        
        # Test case 1: Enough cash
        self.game_state.cash = 10000
        self.push_screen(QuitScreen(self.game_state))
        
        # After first test completes, test case 2: Not enough cash
        self.game_state.cash = 100
        self.push_screen(QuitScreen(self.game_state))

if __name__ == "__main__":
    app = TestApp()
    app.run() 