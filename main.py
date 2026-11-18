from collections import OrderedDict
from pathlib import Path
import csv
import random

PAGE_SIZE = 1024
PAGE_TABLE = {0: 5, 1: 2, 2: 7, 3: 0}
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)

class TLB:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = OrderedDict()
        self.hits = self.misses = 0
    def lookup(self, page):
        if page in self.entries:
            self.hits += 1
            self.entries.move_to_end(page)
            return True
        self.misses += 1
        if self.capacity:
            if len(self.entries) >= self.capacity:
                self.entries.popitem(last=False)
            self.entries[page] = True
        return False

def eat(hit_rate, levels=1):
    # TLB hit: 10ns lookup + 100ns data. Miss: lookup + page table levels * 100ns + data.
    return 10 + 100 + (1 - hit_rate) * levels * 100

def main():
    refs = [int(s) for s in (ROOT / 'variant_a' / 'refs.txt').read_text().splitlines() if s.strip() and not s.startswith('#')]
    tlb = TLB(2)
    print('TLB LRU, K=2; page_size=1024')
    with (OUT / 'tlb_trace.csv').open('w', newline='') as f:
        writer = csv.writer(f); writer.writerow(['address','page','result','translation'])
        for addr in refs:
            page = addr // PAGE_SIZE
            if page not in PAGE_TABLE:
                status = 'PAGE_FAULT'; phys = ''
            else:
                status = 'HIT' if tlb.lookup(page) else 'MISS'
                phys = PAGE_TABLE[page] * PAGE_SIZE + addr % PAGE_SIZE
            writer.writerow([addr,page,status,phys])
            print(f'{addr:5} page={page} {status:10} physical={phys}')
    total = tlb.hits + tlb.misses
    measured = tlb.hits / total if total else 0
    print(f'Hit rate: {tlb.hits}/{total} = {measured:.3f} (unmapped pages excluded)')
    print('Effective access time (single-level table, ns):')
    for h in (0, .25, .5, .75, .9, .99, measured):
        print(f'  hit rate={h:.3f}, EAT={eat(h):.2f} ns')
    print('Two-level page table: 2 memory reads for page tables + 1 for data = 3 (without TLB)')
    print('With TLB: hit 110ns, miss 310ns for two-level model')
    rng = random.Random(42)
    # 90% accesses within a small working set; remaining accesses across 64 pages.
    pages = [rng.randrange(8) if rng.random() < .9 else rng.randrange(64) for _ in range(20000)]
    rows = []
    for k in (1,2,4,8,12,16,24,32,48,64):
        model = TLB(k)
        for p in pages: model.lookup(p)
        rate = model.hits / len(pages)
        rows.append((k,rate))
        print(f'TLB size={k:2}, hit rate={rate:.4f}')
    with (OUT / 'tlb_sizes.csv').open('w', newline='') as f:
        w=csv.writer(f);w.writerow(['tlb_size','hit_rate']);w.writerows(rows)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8,4.5))
        ax.plot([x for x,_ in rows],[y for _,y in rows],marker='o')
        ax.set(xlabel='TLB entries',ylabel='Hit rate',title='TLB LRU: size vs hit rate',ylim=(0,1.02))
        ax.grid(alpha=.3); fig.tight_layout();fig.savefig(OUT / 'tlb_hit_rate.png',dpi=160);plt.close(fig)
        print('Saved results/tlb_hit_rate.png')
    except ImportError:
        print('Install python3-matplotlib to generate PNG graph')

if __name__ == '__main__': main()
