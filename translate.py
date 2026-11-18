from pathlib import Path
PAGE_SIZE = 1024
PAGE_TABLE = {0: 5, 1: 2, 2: 7, 3: 0}

def translate(addr):
    page, offset = divmod(addr, PAGE_SIZE)
    if page not in PAGE_TABLE:
        raise ValueError(f'страница отсутствует: {page}')
    return PAGE_TABLE[page] * PAGE_SIZE + offset

def main():
    for addr in (1200, 3100, 5000):
        page, offset = divmod(addr, PAGE_SIZE)
        try:
            result = translate(addr)
        except ValueError as e:
            result = str(e)
        print(f'{addr}: page={page}, offset={offset}, physical={result}')
    refs = Path(__file__).with_name('refs.txt')
    print('\nrefs.txt:')
    for line in refs.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        addr = int(line)
        try: print(f'{addr} -> {translate(addr)}')
        except ValueError as e: print(f'{addr} -> {e}')

if __name__ == '__main__': main()
