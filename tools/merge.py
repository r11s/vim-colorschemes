# Fügt <sprache>.meta.tsv und <sprache>.vim.tsv zu <sprache>.groups.tsv zusammen
import csv, os, sys, glob
src, dst = sys.argv[1], sys.argv[2]
for mf in sorted(glob.glob(f'{src}/*.meta.tsv')):
    l = os.path.basename(mf)[:-9]
    meta = {int(r[0]): r for r in csv.reader(open(mf), delimiter='\t')}
    act = {}
    vf = f'{src}/{l}.vim.tsv'
    if os.path.exists(vf):
        for r in csv.reader(open(vf), delimiter='\t'):
            act[int(r[0])] = (r[1] if len(r) > 1 else '', r[2] if len(r) > 2 else '')
    with open(f'{dst}/{l}.groups.tsv', 'w') as fh:
        fh.write('line\tword\tdeclared_group\tflags\tvim_group\tvim_effective_group\n')
        for i, r in sorted(meta.items()):
            a = act.get(i, ('', ''))
            fh.write(f'{i}\t{r[1]}\t{r[2]}\t{r[3]}\t{a[0]}\t{a[1]}\n')
