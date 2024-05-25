from inspect import trace
from lib2to3.pgen2 import token
from itertools import groupby
from lib2to3.pgen2.pgen import DFAState
from sqlite3 import adapt
from graphviz import Digraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import networkx as nx
from collections import deque

class State:
    def __init__(self, label):
        self.name = label

    def set(self, name):
        self.name = name
        
    def get(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, State) and str(self.name) == str(other.name)

    def __repr__(self):
        return f'state {self.name}'

class Transaction:
    def __init__(self, label, src, dst):
        self.name = label
        self.src = src
        self.dst = dst

    def get(self):
        return self.name, self.src, self.dst
    
class tree:

     global_index = 1

     def __init__(self, node):
         self.node = node
         self.nullable = True
         self.firstpos = []
         self.lastpos = []
         if (not node == '|') and (not node == '*') and (not node == '.') and (not node == ''):
            self.pos = tree.global_index
            tree.global_index += 1
         else:
             self.pos = 0
         self.childs = []

     def AddChild(self, child):
        self.childs.append(child)
    
class DFA:
    def __init__(self, regex):
        self.states = [State(0)]
        self.final_states = [self.states[0]]
        self.start_states = [self.states[0]]
        self.transactions = {}
        self.regex_direct_to_dfa(regex)

    def create_tree(self, symbols):
        while len(symbols) == 1 and isinstance(symbols[0], list):
            symbols = symbols[0] 


        if len(symbols) == 0:
             return tree('')
        elif len(symbols) == 1 and not symbols[0] == '*' and not symbols[0] == '|':
            return tree(symbols[0])
        elif len(symbols) == 1  and symbols[0] == '*':
            T = tree('*')
            T.AddChild('')
            return T
        elif len(symbols) == 2 and symbols[1] == '*':
            T = tree('*')
            T.AddChild(self.create_tree(symbols[0]))
        else:
            ready = False;
            for i, symbol in enumerate(symbols[::-1]):
                if symbol == '|':
                    T = tree('|')
                    ready = True
                    T.AddChild(self.create_tree(symbols[:len(symbols) - i - 1]))
                    T.AddChild(self.create_tree(symbols[len(symbols) - i:]))
            if not ready:
                if symbols[len(symbols) - 1] == '*':
                    T = tree('.')
                    T.AddChild(self.create_tree(symbols[:len(symbols) - 2]))
                    T.AddChild(self.create_tree(symbols[len(symbols) - 2:]))
                else:
                    T = tree('.')
                    T.AddChild(self.create_tree(symbols[:len(symbols) - 1]))
                    T.AddChild(self.create_tree(symbols[len(symbols) - 1]))

        return T

    def nullable(self, T):
        if T.node == '':
            T.nullable = True
            return True
        elif T.pos > 0:
            T.nullable = False
            return False
        elif T.node == '*':
            self.nullable(T.childs[0])
            T.nullable = True
            return True
        elif T.node == '|':
            T.nullable = self.nullable(T.childs[0]) or self.nullable(T.childs[1])
            return T.childs[0].nullable or T.childs[1].nullable
        elif T.node == '.':
            T.nullable = self.nullable(T.childs[0]) and self.nullable(T.childs[1])
            return T.childs[0].nullable and T.childs[1].nullable
        else:
            T.nullable = True
            return True

    def firstpos(self, T):
        if T.node == '':
            T.firstpos = []
            return []
        elif T.pos > 0:
            T.firstpos = [T.pos]
            return [T.pos]
        elif T.node == '*':
            T.firstpos = self.firstpos(T.childs[0])
            return T.firstpos
        elif T.node == '|':
            T.firstpos = self.firstpos(T.childs[0]) + self.firstpos(T.childs[1])
            return T.firstpos
        elif T.node == '.':
            if self.nullable(T.childs[0]):
                T.firstpos = self.firstpos(T.childs[0]) + self.firstpos(T.childs[1])
            else:
                T.firstpos = self.firstpos(T.childs[0])
            return T.firstpos
        else:
            T.firstpos = []
            return []

    def lastpos(self, T):
        if T.node == '':
            T.lastpos = []
            return []
        elif T.pos > 0:
            T.lastpos = [T.pos]
            return [T.pos]
        elif T.node == '*':
            T.lastpos = self.lastpos(T.childs[0])
            return T.lastpos
        elif T.node == '|':
            T.lastpos = self.lastpos(T.childs[0]) + self.lastpos(T.childs[1])
            return T.lastpos
        elif T.node == '.':
            if self.nullable(T.childs[1]):
                T.lastpos = self.lastpos(T.childs[0]) + self.lastpos(T.childs[1])
            else:
                T.lastpos = self.lastpos(T.childs[1])
            return T.lastpos
        else:
            T.lastpos = []
            return []

    def followpos(self, T, res):
        for i in T.childs:
            self.followpos(i, res)
        if T.node == '*':
            n = self.lastpos(T)
            m = self.firstpos(T)
            for i in n:
                if i in res:
                    for k in m:
                         if m not in res[i]:
                            res[i].append(k)
                else:
                    res[i] = list(set(m))
            return res
        elif T.node == '.':
            n = self.lastpos(T.childs[0])
            m = self.firstpos(T.childs[1]) 
            for i in n:
                if i in res:
                    for k in m:
                        if m not in res[i]:
                            res[i].append(k)
                else:
                    res[i] = list(set(m))
        
    def create_state(self):
        new_state = State(len(self.states))
        self.states.append(new_state)
        return new_state

    def draw(self):
        fig, ax = plt.subplots(frameon=False)
        G = nx.DiGraph()

        for state in self.states:
            if state in self.final_states:
                G.add_node(state.get(), shape='doublecircle', color='orange')
            else:
                G.add_node(state.get(), shape='circle', color='lightblue')

        G.add_node("Start", shape='point')
        G.add_node("Finish", shape='point')

        for state in self.final_states:
            G.add_edge(state.get(), "Finish", arrowstyle='->', arrowsize=20)
        for state in self.start_states:
            G.add_edge("Start", state.get(), arrowstyle='->', arrowsize=20)

        for src, edges in self.transactions.items():
            for tr in edges:
                nm, src, dst = tr.get() 
                G.add_edge(src.get(), dst.get(), label=nm)

        pos = nx.spring_layout(G, k = 1) 
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_nodes(G, pos, node_size=1500,  alpha=0.7)

        nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

        nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True, width=2, alpha=0.7, connectionstyle='arc3, rad = 0.2', arrowsize = 20)
       
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12, font_color='red', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5))
        #for (src, dst), labels in edge_labels.items():
            #x = pos[src][0] + pos[dst][0] / 2
            #y = pos[src][1] + pos[dst][1] / 2
            #plt.text(x, y, f"{' '.join(labels)}", fontsize=12, ha='center', va='center')

        
        plt.show()

    def console_print(self):
        for state in self.start_states:
            print(f'start->{state.get()}')

        for val in self.transactions:
            for tr in self.transactions[val]:
                name, src, dst = tr.get()
                print(f'{src.get()}->{name}->{dst.get()}');
        for state in self.final_states:
            print(f'{state.get()}->finish')

    def regex_to_symbols(self, regex, i):
        symbols = []
        
        while i < len(regex):
            if regex[i] == '(':
                i, ex = self.regex_to_symbols(regex, i + 1)
                symbols.append(ex)
            elif regex[i] == ')':
                i += 1
                return i, symbols
            else:
                symbols.append(regex[i])
                i += 1
        
        return i, symbols

    def simplify_transactions(self, transaction):
        symbols, src_state, dst_state = transaction.get()
        if len(symbols) < 2:
            while isinstance(symbols, list) and 2 > len(symbols) > 0:
                symbols = symbols[0]
                transaction.name = symbols
            if len(symbols) < 2:
                return
        self.delete_transaction(transaction)
        adding_transactions = []
        subarrays = [list(group) for k, group in groupby(symbols, lambda x: x != '|') if k]
        if len(subarrays) > 1:
            for array in subarrays:
                 adding_transactions.append(self.add_transaction(src_state, dst_state, array))
        elif len(symbols) == 2 and symbols[1] == '*':
            if self.edge_quantity(src_state) == 1:
                adding_transactions.append(self.add_transaction(src_state, src_state, symbols[0]))
                self.add_transaction(src_state, dst_state, '')
            elif self.edge_quantity_between_states(src_state, dst_state) == 1: 
                adding_transactions.append(self.add_transaction(dst_state, dst_state, symbols[0]))
                self.add_transaction(src_state, dst_state, '')
            else:
                additional_state = self.create_state();
                adding_transactions.append(self.add_transaction(additional_state, additional_state, symbols[0]))
                self.add_transaction(src_state, additional_state, '')
                self.add_transaction(additional_state, dst_state, '')
           
        else:
            additional_state = self.create_state();
            if  (symbols[1] == '*'):
                adding_transactions.append(self.add_transaction(src_state, additional_state, symbols[:2]))
                adding_transactions.append(self.add_transaction(additional_state, dst_state, symbols[2:]))
            else:
                adding_transactions.append(self.add_transaction(src_state, additional_state, symbols[0]))
                adding_transactions.append(self.add_transaction(additional_state, dst_state, symbols[1:]))

        for tr in adding_transactions:
            self.simplify_transactions(tr)

    def dict_by_tree(self, T, res):
        if T.pos > 0:
            res[T.pos] = T
        for i in T.childs:
            self.dict_by_tree(i, res)

    def regex_direct_to_dfa(self, regex):
        regex = '(' + regex + ')#'
        i, symbols = self.regex_to_symbols(regex, 0)
        if i < len(regex):
            raise(Exception(f"Error invalid regex pos {i}"))
        T = self.create_tree(symbols)
        
        dt = {}
        self.dict_by_tree(T, dt)

        
        fpos = {}
        self.followpos(T, fpos)


        
        start_st = self.firstpos(T)
        S = self.start_states[0]
        self.final_states.remove(S)

        new_nodes = {}
        nodes = {S:start_st}
        rev_nodes = {tuple(set(start_st)): S}

        Dstates = [S]
        
        while len(Dstates) > 0:
            S = Dstates.pop()
            new_nodes = {}
            for node in nodes[S]:
                symb = dt[node].node
                if symb == '#':
                    if S not in self.final_states:
                        self.final_states.append(S)
                    continue
                if node in fpos:
                    if symb not in new_nodes:
                        new_nodes[symb] = []  
                    
                    for f in fpos[node]:
                        if f not in new_nodes[symb]:
                            new_nodes[symb].append(f)
             
            for sy in new_nodes:
                if not sy == '#':
                    if tuple(set(new_nodes[sy])) not in rev_nodes:
                        nn = self.create_state()
                        rev_nodes[tuple(set(new_nodes[sy]))] = nn
                        nodes[nn] = new_nodes[sy]
                        Dstates.append(nn)
                    else:
                        nn = rev_nodes[tuple(set(new_nodes[sy]))]
                    self.add_transaction(S, nn, sy)
                    
                else:
                    if S not in self.final_states:
                        self.final_states.append(S)

        return T

    def regex_to_dfa(self, regex):
        i, symbols = self.regex_to_symbols(regex, 0)
        if i < len(regex):
            raise(Exception(f"Error invalid regex pos {i}"))


        src_state = self.start_states[0];
        
        if len(symbols) == 0:
            return 

        if len(symbols) == 2 and symbols[1] == '*':
            transaction = self.add_transaction(src_state, src_state, symbols[0])
        else:
            dst = self.create_state();
            transaction = self.add_transaction(src_state, dst, symbols)
            self.final_states.remove(src_state)
            self.final_states.append(dst)
        
        self.simplify_transactions(transaction)
        self.tompsoning()

    def edge_quantity(self, src):
        return len(self.transactions[src])

    def edge_quantity_between_states(self, src, dst):
        res = 0
        for i in self.transactions[src]:
            nm, s, d = i.get()
            if d == dst:
               res += 1
        return res

    def add_transaction(self, src, dst, nm):
        new = Transaction(nm, src, dst)
        if src not in self.transactions:
            edges = []
        else: 
            edges = self.transactions[src]

        edges.append(new)
        self.transactions[src] = edges

        return new
           
    def delete_transaction(self, transaction):
        nm, src, dst = transaction.get()
        if transaction in self.transactions[src]:
            self.transactions[src].remove(transaction)

    def check_edge(self, src, nm):
        edges = self.transactions[src]
        for edge in edges:
            name, src, dst = edge.get()
            if name == nm:
                return dst, edge
        return None, None

    def union(self, states, new_final_states, new_states):
        if len(states) == 0:
            return None
        new_state = State(len(new_states))
        new_states.append(new_state)
        for state in states:
            if state in self.final_states:
                new_final_states.append(new_state)
                break

        return new_state

    def minimise(self):
        self.reverse()
        self.tompsoning()
        self.reverse()
        self.tompsoning()

    def reverse(self):
        new_transactions = {}
        for state in self.transactions:
            for tr in self.transactions[state]:
                nm, src, dst = tr.get()
                tr.src = dst
                tr.dst = src
                if dst not in new_transactions:
                    new_transactions[dst] = [tr]
                else:
                    new_transactions[dst].append(tr)
        buf = self.start_states
        self.start_states = self.final_states
        self.final_states = buf
        self.transactions = new_transactions
                

    def tompsoning(self):
        start = self.epsilon_closure(set(self.start_states))
        queue = deque([start])
        new_final_states = []
        new_transactions = {}
        new_states = []
        new_start_state = [self.union(start, new_final_states, new_states)]
        new_srtates_dict = {tuple(start): new_start_state[0]}
   

        while queue:
            alphabet_tr = {}
            states = queue.popleft()
            for state in states:
                if state in self.transactions:
                    for tr in self.transactions[state]:
                        nm, src, dst = tr.get()
                        if not nm == '':
                            if nm not in alphabet_tr:
                                alphabet_tr[nm] = set()
                            alphabet_tr[nm].add(dst)

            src_state = new_srtates_dict[tuple(states)]

            for s in alphabet_tr:
                alphabet_tr[s] = self.epsilon_closure(alphabet_tr[s])

                state_set = alphabet_tr[s]

                if tuple(state_set) not in new_srtates_dict:
                    new_st = self.union(state_set, new_final_states, new_states)
                    new_srtates_dict[tuple(state_set)] = new_st
                    queue.append(state_set)

                st_dst = new_srtates_dict[tuple(state_set)]
                if src_state not in new_transactions:
                    new_transactions[src_state] = [Transaction(s, src_state, st_dst)]
                else:
                    new_transactions[src_state].append(Transaction(s, src_state, st_dst))

        
        self.transactions = new_transactions
        self.final_states = new_final_states
        self.start_states = new_start_state
        self.states = new_states
                



    def modeling(self, string):
        cur_state = self.start_states[0]
        for symbol in string:
            symbol_pass = False
            if cur_state in self.transactions:
                for tr in self.transactions[cur_state]:
                    nm, src, dst = tr.get()
                    if nm == symbol:
                        symbol_pass = True
                        cur_state = dst

            if not symbol_pass:
                return False

        if cur_state in self.final_states:
            return True
        else:
            return False


    def epsilon_closure(self, states):
        closure = set()
        stack = deque(states)
        while stack:
            current_state = stack.pop()
            if current_state in closure:
                continue
            closure.add(current_state)
            if current_state in self.transactions:
                for transaction in self.transactions[current_state]:
                    name, src, dst = transaction.get()
                    if name == '':
                        stack.append(dst)
        return closure
                   
                        


def main():
    menu = '\n\n\n0 - exit\n1 - Create DFA from regular expression\n'
    dfa = None
    choose = int(input(menu + ('2 - Minimize DFA\n3 - Modeling DFA\n\n' if not dfa is None else '\n') + 'Input your choice: '))
    while choose > 0:
        if choose == 1:
            regex = input("Input regular expression: ").replace(" ", "")
            dfa = DFA(regex)
            print('\n\n\nDFA from regular expression:\n\n')
            dfa.console_print()
            dfa.draw()
        elif choose == 2 and not dfa is None:
            dfa.minimise()
            print('\n\n\nMinimized DFA:\n\n')
            dfa.console_print()
            dfa.draw()
        elif choose == 3 and not dfa is None:
            string = input("Input string: ").replace(" ", "")
            if dfa.modeling(string):
                print("This string belong to regular expresion's language")
            else:
                print("This string not belong to regular expresion's language")
        choose = int(input(menu + ('2 - Minimize DFA\n3 - Modeling DFA\n\n' if not dfa is None else '\n') + 'Input your choice: '))
    
    


if __name__ == "__main__":
    main()

