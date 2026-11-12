# Connect Four AI

## How to play

Run these commands in PowerShell from the project folder.

Terminal game (choose Easy, Medium or Hard and who goes first; type `q` to quit):

```powershell
.venv\Scripts\python.exe play_cli.py
```

Graphical game (click a column to drop a disc; pick the settings and press New Game):

```powershell
.venv\Scripts\python.exe gui.py
```

Run the tests:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

The Medium level needs the trained model in `models/medium_model.joblib`. If it is missing, run:

```powershell
.venv\Scripts\python.exe train_models.py
```
