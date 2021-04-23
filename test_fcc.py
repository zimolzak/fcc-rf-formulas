from fcc import exempt_milliwatts_sar, exempt_watts_mpe

def fcc_round(x):
    """Round as in FCC 19-126 Table 1, p. 23."""
    if x < 10:
        return(round(x, 1))
    else:
        return(int(round(x)))

def test_fcc_round():
    assert fcc_round(39.1234) == 39
    assert fcc_round(22) == 22
    assert fcc_round(22.0) == 22
    assert fcc_round(2.1234) == 2.1
    assert fcc_round(9.0) == 9.0
    assert fcc_round(9.01234) == 9.0
    assert fcc_round(3060.1234) == 3060

def test_all_sar():
    result_list = []
    reference = [39, 65, 88, 110, 22, 44, 67, 89, 9.2, 25, 44, 66]
    # reference is derived directly from FCC 19-126, Table 1.
    for f in [0.3, 0.45, 0.835]: # First 3 rows of Table 1
        for d in [0.5, 1, 1.5, 2]: # First 4 columns
            result = exempt_milliwatts_sar(d, f)
            printme = round(result, 1)
            compare = fcc_round(result)
            print(printme, end='\t')
            result_list.append(compare)
        print()
    print(result_list)
    assert result_list == reference

def t_erpth(d, f):
    erp = exempt_watts_mpe(d, f)
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
