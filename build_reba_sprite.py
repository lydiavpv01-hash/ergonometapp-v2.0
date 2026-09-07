from pathlib import Path
from PIL import Image


def build_reba_sprite(force=False):
    root = Path(__file__).resolve().parent
    source_dir = root / 'static' / 'img' / 'reba'
    output = root / 'static' / 'img' / 'reba-references-sprite.webp'

    sources = [source_dir / f'{i}.png' for i in range(1, 25)]
    if not all(p.exists() for p in sources):
        return False

    newest_source = max(p.stat().st_mtime for p in sources)
    if output.exists() and not force and output.stat().st_mtime >= newest_source:
        return True

    tile = 700
    cols, rows = 4, 6
    canvas = Image.new('RGB', (cols * tile, rows * tile), 'white')

    for i, path in enumerate(sources, start=1):
        with Image.open(path) as src:
            img = src.convert('RGB')
            img.thumbnail((tile, tile), Image.Resampling.LANCZOS)
            col = (i - 1) % cols
            row = (i - 1) // cols
            x = col * tile + (tile - img.width) // 2
            y = row * tile + (tile - img.height) // 2
            canvas.paste(img, (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, 'WEBP', quality=95, method=6)
    return True


if __name__ == '__main__':
    build_reba_sprite(force=True)
