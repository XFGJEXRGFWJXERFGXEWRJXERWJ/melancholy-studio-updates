"""Build the single replaceable melancholy_studio.zip + update.json."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

REPO = 'XFGJEXRGFWJXERFGXEWRJXERWJ/melancholy-studio-updates'


def build(source, output, notes):
    source = Path(source).resolve()
    output = Path(output).resolve()
    tree = ast.parse((source / '__init__.py').read_text(encoding='utf8'))
    meta = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in n.targets))
    version = meta['version']
    name = 'melancholy_studio.zip'
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output / name, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(source.rglob('*')):
            if not file.is_file() or any(p.startswith('.') or p == '__pycache__' for p in file.relative_to(source).parts):
                continue
            if file.suffix in ('.py', '.md') or file.name == 'LICENSE':
                archive.write(file, Path('melancholy_studio') / file.relative_to(source))
    manifest = dict(schema=1, addon='melancholy_studio', version=list(version), blender_min=list(meta['blender']), url='https://raw.githubusercontent.com/' + REPO + '/main/' + name, sha256=hashlib.sha256((output / name).read_bytes()).hexdigest(), notes=notes)
    (output / 'update.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('Upload together:', output / name, output / 'update.json')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='Path to the melancholy_studio addon folder')
    parser.add_argument('--output', default='update_dist')
    parser.add_argument('--notes', default='melancholy Studio update')
    args = parser.parse_args()
    build(args.source, args.output, args.notes)
