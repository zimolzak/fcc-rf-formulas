from fcc import pth, erpth

print("\n# P_th (part of Table 1, FCC 19-126 p.23)\n")
for f in [0.3, 0.45, 0.835]:
    for d in [0.5, 1, 1.5, 2]:
        print(round(pth(d,f), 1), end='\t')
    print()

print("\n\n# ERP_th\n")

def test_erpth(d, f):
    erp = erpth(d, f)
    print("%.0f m, %.0f MHz:\t%.1f W" % (d, f, erp))

#erpth(0.01, 144)
#erpth(0.01, 239)
test_erpth(1, 239)
#erpth(3, 0.1)
#erpth(3, 1)
test_erpth(3, 20)
test_erpth(3, 50)
test_erpth(3, 100)
test_erpth(3, 10000)
#erpth(4, 1)
#erpth(5, 1)
#erpth(6, 1)
test_erpth(50, 1)
test_erpth(50, 100)
test_erpth(50, 420)
test_erpth(50, 2000)
#erpth(30000, 0.1)
test_erpth(30000, 10000)
#erpth(30000, 101000)
print()
