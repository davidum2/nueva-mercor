import os
import sys

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

KB_DIR = r'c:\desarrollo\Curriculum Vitae y plataformas\knowel\knowledge_base'

def read_swe_ab():
    for fn in ['asha_resume_promotion_reproducibility_model_ab.md', 'exact_rank_matrix_market_migration_model_ab.md', 'packed_sequence_gradient_repair_model_ab.md']:
        path = os.path.join(KB_DIR, fn)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                print(f"=== {fn} ({len(content)} chars) ===")
                print(content[:3500])
                print("\n" + "="*60 + "\n")
                break

if __name__ == '__main__':
    read_swe_ab()
