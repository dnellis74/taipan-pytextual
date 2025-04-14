"""
Main entry point for the Taipan game.
"""

from .game_ui import TaipanApp

def main():
    """Run the Taipan game."""
    app = TaipanApp()
    app.run()

if __name__ == "__main__":
    main() 