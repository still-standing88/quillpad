import os

EXCLUDE_DIRS = {'node_modules', 'venv', '.git', '__pycache__', '.idea', '.vscode', 'dist', 'build'}
OUTPUT_FILE = 'project_snapshot.md'
ROOT_DIR = '.'  # Change this if needed

def should_exclude(path):
    return any(part in EXCLUDE_DIRS for part in path.split(os.sep))

def dump_project_structure(root):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not should_exclude(os.path.join(dirpath, d))]
            if should_exclude(dirpath):
                continue

            rel_dir = os.path.relpath(dirpath, root)
            out.write(f"\n\n## Directory: `{rel_dir}`\n")

            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if should_exclude(filepath):
                    continue

                out.write(f"\n### File: `{os.path.relpath(filepath, root)}`\n")
                out.write("```" + get_file_language(filename) + "\n")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"[Could not read file: {e}]")
                out.write("\n```\n")

def get_file_language(filename):
    ext = os.path.splitext(filename)[1]
    return {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.svelte': 'svelte',
        '.json': 'json',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.yml': 'yaml',
        '.yaml': 'yaml',
    }.get(ext, '')

if __name__ == "__main__":
    dump_project_structure(ROOT_DIR)
    print(f"\n✅ Project snapshot saved to `{OUTPUT_FILE}`.")
