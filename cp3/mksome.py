for ascii in range(ord('a'), ord('z')):
    lhs = chr(ascii); rhs = chr(ascii + 1)
    print(f'Succ[{lhs}] -> {rhs}')
