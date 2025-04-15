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

### Debugging

To run the project in the debugger:

1. Make sure you have the Python debugger extension installed in your IDE (e.g., VS Code Python extension)

2. Create a debug configuration in your IDE. For VS Code, create a `.vscode/launch.json` file with:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Taipan",
               "type": "python",
               "request": "launch",
               "module": "taipan_textual",
               "justMyCode": false,
               "env": {
                   "PYTHONPATH": "${workspaceFolder}"
               },
               "python": "${command:python.interpreterPath}",
               "console": "integratedTerminal"
           }
       ]
   }
   ```

3. Make sure you're using the correct Python interpreter:
   - In VS Code, press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the Poetry environment (it should be in `.venv` or similar)

4. Set breakpoints in your code by clicking in the left margin of the editor

5. Start debugging by:
   - VS Code: Press F5 or click the "Run and Debug" button
   - PyCharm: Right-click the project and select "Debug 'taipan_textual'"
   - Command line: `poetry run python -m pdb -m taipan_textual`

6. When debugging:
   - Use the debug toolbar to step through code (F10), step into functions (F11), or continue execution (F5)
   - Inspect variables in the debug panel
   - Use the debug console to evaluate expressions
   - Set conditional breakpoints by right-clicking a breakpoint and adding a condition

## License

This project is licensed under the terms of the MIT license. 