import sys
sys.path.insert(0, r'd:\project\math-visualization\dictionary')
from build_vocab_json import generate_word_family

for base in ['review', 'finish', 'like', 'know']:
    fams = generate_word_family(base)
    print(f"\n=== {base} ===")
    for f in fams:
        print(f"  {f}")
