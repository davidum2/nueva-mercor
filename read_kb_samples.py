import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

KB_DIR = r'c:\desarrollo\Curriculum Vitae y plataformas\knowel\knowledge_base'

def read_samples():
    # 1. Read INDEX.md if it exists
    index_path = os.path.join(KB_DIR, 'INDEX.md')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
            print("=== INDEX.MD ===")
            print(f.read()[:2000])

    # 2. Read electerm_electerm_3875.md
    el_path = os.path.join(KB_DIR, 'electerm_electerm_3875.md')
    if os.path.exists(el_path):
        with open(el_path, 'r', encoding='utf-8', errors='ignore') as f:
            print("\n=== ELECTERM_ELECTERM_3875.MD ===")
            print(f.read()[:3000])

if __name__ == '__main__':
    read_samples()
