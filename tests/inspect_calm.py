from pathlib import Path
path = Path(__file__).resolve().parent.parent / 'views/calm_mode_view.py'
text = path.read_text(encoding='utf-8')
for idx, line in enumerate(text.splitlines(), 1):
    if idx <= 260:
        print(idx, line)
