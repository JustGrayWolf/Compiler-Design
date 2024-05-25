import re
from collections import defaultdict

def parse_grammar(file_content):
    lines = file_content.strip().split('\n')
    non_terminals = lines[1].strip().split()
    terminals = lines[3].strip().split()
    
    prod_quantity = int(lines[4])

    productions = defaultdict(list)
    
    for line in lines[5:5 + prod_quantity]:
        if '→' in line:
            lhs, rhs = line.split('→')
            lhs = lhs.strip()
            rhs = rhs.strip().split('|')
            rhs = [s.split() for s in rhs]
            if lhs in productions:
                productions[lhs] += rhs
            else:
                productions[lhs] = rhs

    start_symbol =  lines[5 + prod_quantity].strip()
    
    return non_terminals, terminals, productions, start_symbol

def GenerateNewNotTerminal(non_terminals, non_terminal, terminals):
    c = 1;
    new_term = non_terminal + str(c)
    while new_term in non_terminals or new_term in terminals:
        c += 1
        new_term = non_terminal + str(c)
    non_terminals.append(new_term)

    return new_term

def eliminate_left_recursion(non_terminals, terminals, productions):
    non_termin_order = list(productions.keys())
    newprod = {}
    for s in productions:
        has_left_rec = False
        ready = False
        while not ready:
            ready = True
            for p in productions[s]:
                if len(p) > 0 and  p[0] == s:
                    has_left_rec = True
                elif len(p) > 0 and p[0] in non_termin_order and  non_termin_order.index(p[0]) < non_termin_order.index(s):
                    prods = productions[p[0]][:]
                    for i in range(len(prods)):
                        prods[i] = list(prods[i])
                    for prod in prods:
                        prod += p[1:]
                    productions[s].remove(p)
                    productions[s] += prods
                    ready = False
        if has_left_rec:
            new_term = GenerateNewNotTerminal(non_terminals, s, terminals)
            new_p1 = []
            new_p2 = []
            for p in productions[s]:
                if len(p) > 0 and  p[0] == s:
                    new_p2.append(p[1:] + [new_term])
                else:
                    new_p1.append(p[:] + [new_term])
            new_p2.append(['ε'])
            productions[s] = new_p1
            newprod[new_term] = new_p2
        
    for i in newprod:
        productions[i] = newprod[i]

    return non_terminals, productions

def get_order(productions, T, order):
    m = 0
    for p in productions[T]:
        if len(p) > 0 and p[0] in productions:
            if p[0] not in order:
                m = max(m, get_order(productions, p[0], order))
            else:
                m = max(m, order[p[0]])

    m += 1
    order[T] = m
    return m

def to_greibach_normal_form(non_terminals, terminals, productions, start_symbol):
    new_productions = defaultdict(list)
    non_termin_order = list(productions.keys())
    order = {}
    for i in non_termin_order:
        if i not in order:
            get_order(productions, i, order)

    for i in range(len(non_termin_order)):
        for j in range(i + 1, len(non_termin_order)):
            if order[non_termin_order[i]] > order[non_termin_order[j]]:
                buf = non_termin_order[i]
                non_termin_order[i] = non_termin_order[j]
                non_termin_order[j] = buf

    for s in non_termin_order:
        if s in productions:
            ready = False
            while not ready:
                ready = True
                for p in productions[s]:
                    if len(p) > 0 and p[0] in non_termin_order:
                        prods = productions[p[0]][:]
                        for i in range(len(prods)):
                            prods[i] = list(prods[i])
                        for prod in prods:
                            prod += p[1:]
                        productions[s].remove(p)
                        productions[s] += prods
                        ready = False
    
    change = {}
    new_productions = {}

    for s in productions:
        new_productions[s] = productions[s]
        for r in productions[s]:
            for i in range(1, len(r)):
                if r[i] in terminals:
                    if r[i] in change:
                        r[i] = change[r[i]]
                    else:
                        b = GenerateNewNotTerminal(non_terminals, r[i], terminals)
                        change[r[i]] = b
                        new_productions[b] = [list([str(r[i])])]
                        r[i] = b

    return non_terminals, terminals, new_productions, start_symbol

def read_grammar(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def write_grammar(file_path, non_terminals, terminals, productions, start_symbol):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f'{len(non_terminals)}\n')
        print('{')
        print(f'{terminals}')
        print(f'{non_terminals}')
        print('[')
        for lhs in productions:
            s = ''
            for rhs in productions[lhs]:
                s += ' '.join(rhs) + '|'
            s = s[0:len(s) - 1]
            print(f"{lhs} → {s}")
        print(']')
        print(f'{start_symbol}')
        print('}')
        file.write(' '.join(non_terminals) + '\n')
        file.write(f'{len(terminals)}\n')
        file.write(' '.join(terminals) + '\n')
        l = 0
        for lhs in productions:
            l += len(productions[lhs])
        file.write(f'{l}\n')
        for lhs in productions:
            for rhs in productions[lhs]:
                    file.write(f"{lhs} → {' '.join(rhs)}\n")
        file.write(f"{start_symbol}\n")

def main(input_file, output_file):
    input_file = ''
    menu = '\n\n\n0 - exit\n1 - Input grammar file\n'
    dfa = None
    choose = int(input(menu + ('2 - Eliminate left recursion\n3 - To Greibach form\n\n' if not input_file == '' else '\n') + 'Input your choice: '))
    while choose > 0:
        if choose == 1:
            input_file = input('Input file name:')
        elif choose == 2 and not input_file == '':
            file_content = read_grammar(input_file)
            non_terminals, terminals, productions, start_symbol = parse_grammar(file_content)
            non_terminals, productions = eliminate_left_recursion(non_terminals, terminals, productions)
            write_grammar(output_file, non_terminals, terminals, productions, start_symbol)
        elif choose == 3 and not input_file == '':
            file_content = read_grammar(input_file)
            non_terminals, terminals, productions, start_symbol = parse_grammar(file_content)
            non_terminals, terminals, productions, start_symbol = to_greibach_normal_form(non_terminals, terminals, productions, start_symbol)
            write_grammar(output_file, non_terminals, terminals, productions, start_symbol)
        choose = int(input(menu + ('2 - Eliminate left recursion\n3 - To Greibach form\n\n' if not input_file == '' else '\n') + 'Input your choice: '))    

if __name__ == "__main__":
    input_file = r"D:/input_grammar.txt"
    output_file = "D:/output_grammar.txt"
    main(input_file, output_file)

