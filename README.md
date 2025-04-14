# Taipan Textual

A Textual-based implementation of the classic Taipan trading game.

## Setup

This project uses Poetry for dependency management. To get started:

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry env activate
   ```

## Running the Game

To start the game, run:
```bash
poetry run python -m taipan_textual
```

### Game Controls

#### Port Screen
- B: Buy items
- S: Sell items
- V: Visit bank
- T: Transfer cargo
- Q: Quit trading
- W: Wheedle Wu (in Hong Kong)
- R: Retire (in Hong Kong)

#### Battle Screen
- F: Fight
- R: Run
- T: Throw cargo

## Development

The project requires Python 3.9.20. Make sure you have this version installed before proceeding.

## License

This project is licensed under the terms of the MIT license. 