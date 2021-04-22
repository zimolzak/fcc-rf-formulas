from fcc import pth

for f in [0.3, 0.45, 0.835]:
    for d in [0.5, 1, 1.5, 2]:
        print(round(pth(d,f), 1), end='\t')
    print()
