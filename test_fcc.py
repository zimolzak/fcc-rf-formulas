from fcc import pth, erpth

def test_all_sar():
    for f in [0.3, 0.45, 0.835]:
        for d in [0.5, 1, 1.5, 2]:
            print(round(pth(d,f), 1), end='\t')
        print()

def t_erpth(d, f):
    erp = erpth(d, f)
    print("%.0f m, %.0f MHz:\t%.1f W" % (d, f, erp))

def test_all_erp():
    #erpth(0.01, 144)
    #erpth(0.01, 239)
    t_erpth(1, 239)
    #erpth(3, 0.1)
    #erpth(3, 1)
    t_erpth(3, 20)
    t_erpth(3, 50)
    t_erpth(3, 100)
    t_erpth(3, 10000)
    #erpth(4, 1)
    #erpth(5, 1)
    #erpth(6, 1)
    t_erpth(50, 1)
    t_erpth(50, 100)
    t_erpth(50, 420)
    t_erpth(50, 2000)
    #erpth(30000, 0.1)
    t_erpth(30000, 10000)
    #erpth(30000, 101000)
    print()

if __name__ == '__main__':
    print("\n# P_th (part of Table 1, FCC 19-126 p.23)\n")
    test_all_sar()
    print("\n\n# ERP_th\n")
    test_all_erp()
