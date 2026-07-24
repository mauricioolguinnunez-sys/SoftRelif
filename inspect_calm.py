from pathlib import Path
path = Path('views/calm_mode_view.py')
text = path.read_text(encoding='utf-8')
for idx, line in enumerate(text.splitlines(), 1):
    if idx <= 260:
        print(idx, line)
