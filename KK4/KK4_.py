
import pydot
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from collections import deque
import re

class Synthaxis_Tree():
    id_ = 0
    def __init__(self, name):
        self.name = f'[{Synthaxis_Tree.id_}]\n' + name
        Synthaxis_Tree.id_ += 1
        self.childs = {}

    def addNode(self, symbol, tree):
        self.childs[symbol] = tree

    def visualize(self, filename='D:/tree.png'):
        def add_nodes_edges(tree, graph):
            for symbol, child in tree.childs.items():
                edge = pydot.Edge(tree.name, child.name, label=symbol)
                graph.add_edge(edge)
                add_nodes_edges(child, graph)

        graph = pydot.Dot(graph_type='digraph')
        graph.add_node(pydot.Node(self.name))
        add_nodes_edges(self, graph)

        graph.write_png(filename)
        img = mpimg.imread(filename)
    
    
        fig, ax = plt.subplots()

   
        ax.imshow(img)
        ax.axis('off')  

    
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()  

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        plt.show()


class Scaner:
    def __init__(self, s):
        matches = re.findall(r'}', s)
        valid_matches = re.findall(r';}', s)
        if len(matches) != len(valid_matches):
            print('Error: wanted ;')
            self.correct = False
            return
        self.s = s.replace(' ', '').replace('\n', '').replace('\r', '').replace(';}','}')
        #print(self.s)
        self.pos = 0
        self.cur_tree = None
        #self.correct = self.P()
        self.correct = self.E()

    def draw(self):
        
        self.cur_tree.visualize()

    def ID(self):
        i = self.pos
        if self.pos >= len(self.s) or self.s[self.pos] not in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_':
            return False
        else:
            while self.pos < len(self.s) and self.s[self.pos] in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_1234567890':
                self.pos += 1
            self.cur_tree = Synthaxis_Tree(self.s[i:self.pos])
            return True

    def Const(self):
        i = self.pos
        if self.pos >= len(self.s) or self.s[self.pos] not in '+-0123456789':
            return False
        else:
            if self.pos - 1 >= len(self.s) or self.s[self.pos] in '+-' and self.s[self.pos + 1] not in '0123456789':
                return False
            self.pos += 1
            while self.pos < len(self.s) and self.s[self.pos] in '0123456789':
                self.pos += 1
            if self.pos < len(self.s) and self.s[self.pos] == '.':
                self.pos += 1
                while self.pos < len(self.s) and self.s[self.pos] in '0123456789':
                    self.pos += 1
            if self.pos < len(self.s) and (self.s[self.pos] == 'e' or self.s[self.pos] == 'E'):
                self.pos += 1
                if self.pos < len(self.s) and self.s[self.pos] not in '+-0123456789':
                    return False
                if self.pos - 1 >= len(self.s) or self.s[self.pos] in '+-' and self.s[self.pos + 1] not in '0123456789':
                    return False
                self.pos += 1
                while self.pos < len(self.s) and self.s[self.pos] in '0123456789':
                    self.pos += 1
            self.cur_tree = Synthaxis_Tree(self.s[i:self.pos])
            return True

    def P(self):
        if self.pos < len(self.s) and self.s[self.pos] == '{':
            self.pos += 1
            i = self.pos
            t = Synthaxis_Tree("{ L }")
            if self.L():
                if  self.pos < len(self.s) and self.s[self.pos] == '}':
                    t.addNode('L', self.cur_tree)
                    self.pos += 1
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {self.pos} wanted ' + '"}"')
                    return False
            else:
                print(f'Error: position = {i} Incorrect operator list')
                return False
        else:
            print(f'Error: position = {self.pos} wanted ' + '"{"')
            return False
    
    def L(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '{':
            self.pos += 1
            t = Synthaxis_Tree("{ L } T")
            if self.L():
                t.addNode('L', self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == '}':
                    self.pos += 1
                    i = self.pos
                    if self.T():
                        t.addNode('T')
                        self.cur_tree = t
                        return True
                    else:
                        print(f'Error: position = {i} Incorrect operator tail')
                        return False
                else:
                    print(f'Error: position = {self.pos} wanted ' + '"}"')
                    return False
            else:
                return False

        elif self.ID():
            t = Synthaxis_Tree("id = E T")
            t.addNode('id', self.cur_tree)
            if  self.pos < len(self.s) and self.s[self.pos] == '=':
                self.pos += 1
                i = self.pos
                if self.E():
                    t.addNode('E', self.cur_tree)
                    i = self.pos
                    if self.T():
                        t.addNode('T', self.cur_tree)
                        self.cur_tree = t
                        return True
                    else:
                        print(f'Error: position = {i} Incorrect operator tail')
                        return False
                else:
                    print(f'Error: position = {i} Incorrect expression')
                    return False
            else:
                print(f'Error: position = {self.pos} wanted ' + '"="')
                return False
        else:
            print(f'Error: position = {self.pos} wanted ' + '"{" or id')
            return False

    def T(self):
        if  self.pos < len(self.s) and self.s[self.pos] == ';':
            t = Synthaxis_Tree("; O T")
            self.pos += 1
            i = self.pos
            if self.O():
                t.addNode('O', self.cur_tree)
                i = self.pos
                if self.T():
                    t.addNode('T', self.cur_tree)
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {i} Incorrect tail')
                    return False
            else:
                print(f'Error: position = {i} Incorrect operator')
                return False
        else:
            t = Synthaxis_Tree(" ")
            self.cur_tree = t
            return True


    def O(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '{':
            t = Synthaxis_Tree("{ L }")
            self.pos += 1
            i = self.pos
            if self.L():
                 
                if  self.pos < len(self.s) and self.s[self.pos] == '}':
                    t.addNode('L', self.cur_tree)
                    self.pos += 1
                    self.cur_tree = t
                    return True  
                else:
                    print(f'Error: position = {self.pos} wanted ' + '"}"')
                    return False
            else:
                print(f'Error: position = {i} Incorrect operators list')
                return False

        elif self.ID():
            t = Synthaxis_Tree("id = E")
            t.addNode('id', self.cur_tree)
            if  self.pos < len(self.s) and self.s[self.pos] == '=':
                self.pos += 1
                i = self.pos
                if self.E():
                    t.addNode('E', self.cur_tree)
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {i} Incorrect expression')
                    return False
            else:
                print(f'Error: position = {self.pos} wanted ' + '"="')
                return False
        else:
            print(f'Error: position = {self.pos} wanted ' + '"{" or id')
            return False

    def E(self):
        i = self.pos
        if  self.pos < len(self.s) and self.s[self.pos] == '(':
            t = Synthaxis_Tree("( A ) TE1 A1 C")
            self.pos += 1
            i = self.pos
            if self.A():
                t.addNode('A', self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    i = self.pos
                    if self.TE1():
                        t.addNode('TE1', self.cur_tree)
                        i = self.pos
                        if self.A1(): 
                            t.addNode('A1', self.cur_tree)
                            i = self.pos
                            if self.C():
                                t.addNode('C', self.cur_tree)
                                self.cur_tree = t
                                return True  
                            else:
                                print(f'Error: position = {i} Incorrect comparasion expression')
                                return False
                        else:
                            print(f'Error: position = {i} Incorrect sum expression')
                            return False
                    else:
                        print(f'Error: position = {i} Incorrect multiplication expression')
                        return False
                else:
                    print(f'Error: position = {self.pos} wanted ' + '")"')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif self.ID():
            t = Synthaxis_Tree("id TE1 A1 C")
            t.addNode('id', self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1', self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1', self.cur_tree)
                    i = self.pos
                    if self.C():
                        t.addNode('C', self.cur_tree)
                        self.cur_tree = t
                        return True
                    else:
                        print(f'Error: position = {i} Incorrect comparasion expression')
                        return False
                else:
                    print(f'Error: position = {i} Incorrect sum expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect multiplication expression')
                return False

        elif self.Const():
            t = Synthaxis_Tree("const TE1 A1 C")
            t.addNode('const', self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1', self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1', self.cur_tree)
                    i = self.pos
                    if self.C():
                        t.addNode('C', self.cur_tree)
                        self.cur_tree = t 
                        return True
                    else:
                        print(f'Error: position = {i} Incorrect comparasion expression')
                        return False
                else:
                    print(f'Error: position = {i} Incorrect sum expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect multiplication expression')
                return False
        else:
            print(f'Error: position = {self.pos} wanted ' + '"(" or id or const')
            return False

    def C(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '<':
            self.pos += 1
            if  self.pos < len(self.s) and self.s[self.pos] == '=':
                 self.pos += 1
                 t = Synthaxis_Tree("<= A")
            elif  self.pos < len(self.s) and self.s[self.pos] == '>':
                 t = Synthaxis_Tree("<> A")
                 self.pos += 1
            else:
                 t = Synthaxis_Tree("< A")
                 self.pos += 0
            i = self.pos
            if self.A():
                t.addNode('A', self.cur_tree)
                self.cur_tree = t 
                return True
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif  self.pos < len(self.s) and self.s[self.pos] == '>':
            self.pos += 1
            if self.pos < len(self.s) and self.s[self.pos] == '=':
                 t = Synthaxis_Tree(">= A")
                 self.pos += 1
            else:
                t = Synthaxis_Tree("> A")
            i = self.pos
            if self.A():
                t.addNode('A', self.cur_tree)
                self.cur_tree = t 
                return True
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif  self.pos < len(self.s) and self.s[self.pos] == '=':
            self.pos += 1
            if  self.pos < len(self.s) and self.s[self.pos] == '=':
                t = Synthaxis_Tree("== A")
                self.pos += 1
                i = self.pos
                if self.A():
                    t.addNode('A', self.cur_tree)
                    self.cur_tree = t 
                    return True
                else:
                    print(f'Error: position = {i} Incorrect arifmetical expression')
                    return False
            else:
                print(f'Error: position = {i} wanted ' + '"==" but got "="')
                return False

        else:
            t = Synthaxis_Tree(" ")
            self.cur_tree = t 
            return True

    def A(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '(':
            t = Synthaxis_Tree("( A ) TE1 A1")
            self.pos += 1
            i = self.pos
            if self.A():
                t.addNode('A', self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    i = self.pos
                    if self.TE1():
                        t.addNode('TE1', self.cur_tree)
                        i = self.pos
                        if self.A1():
                            t.addNode('A1', self.cur_tree)
                            self.cur_tree = t 
                            return True
                        else:
                            print(f'Error: position = {i} Incorrect sum expression')
                            return False
                    else:
                        print(f'Error: position = {i} Incorrect multiplication expression')
                        return False
                else:
                    print(f'Error: position = {self.pos} wanted ' + '")"')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif self.ID():
            t = Synthaxis_Tree("id TE1 A1")
            t.addNode('id', self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1', self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1', self.cur_tree)
                    self.cur_tree = t 
                    return True
                else:
                    print(f'Error: position = {i} Incorrect sum expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect multiplication expression')
                return False
        elif self.Const():
            t = Synthaxis_Tree("const TE1 A1")
            t.addNode('const', self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1', self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1', self.cur_tree)
                    self.cur_tree = t 
                    return True
                else:
                    print(f'Error: position = {i} Incorrect sum expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect multiplication expression')
                return False
        else:
            print(f'Error: position = {self.pos} wanted ' + '"(" or id or const')
            return False

    def TE(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '(':
            t = Synthaxis_Tree("( A ) TE1")
            self.pos += 1
            i = self.pos
            if self.A():
                t.addNode('A', self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    i = self.pos
                    if self.TE1():
                        t.addNode('TE1', self.cur_tree)
                        self.cur_tree = t 
                        return True  
                    else:
                        print(f'Error: position = {i} Incorrect multiplication expression')
                        return False
                else:
                    print(f'Error: position = {self.pos} wanted ' + '")"')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif self.ID():
            t = Synthaxis_Tree("id TE1")
            t.addNode('id', self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1', self.cur_tree)
                self.cur_tree = t 
                return True
            else:
                print(f'Error: position = {i} Incorrect multiplication expression')
                return False
        elif self.Const():
            t = Synthaxis_Tree("const TE1")
            t.addNode('const', self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1', self.cur_tree)
                self.cur_tree = t 
                return True
            else:
                print(f'Error: position = {i} Incorrect multiplication expression')
                return False
        else:
            print(f'Error: position = {self.pos} wanted ' + '"(" or id or const')
            return False

    def F(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '(':
            t = Synthaxis_Tree("( A )")
            self.pos += 1
            i = self.pos
            if self.A():
                t.addNode('A', self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    self.cur_tree = t
                    return True 
                else:
                    print(f'Error: position = {self.pos} wanted ' + '")"')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif self.ID():
            t = Synthaxis_Tree("id")
            t.addNode('id', self.cur_tree)
            self.cur_tree = t
            return True
        elif self.Const():
            t = Synthaxis_Tree("const")
            t.addNode('const', self.cur_tree)
            self.cur_tree = t
            return True
        else:
            print(f'Error: position = {self.pos} wanted ' + '"(" or id or const')
            return False

    def A1(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '+':
            t = Synthaxis_Tree("+ TE A1")
            self.pos += 1
            i = self.pos
            if self.TE():
                t.addNode('TE', self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1', self.cur_tree)
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {i} Incorrect sum expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif  self.pos < len(self.s) and self.s[self.pos] == '-':
            t = Synthaxis_Tree("- TE A1")
            self.pos += 1
            i = self.pos
            if self.TE():
                t.addNode('TE', self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1', self.cur_tree)
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {i} Incorrect sum expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        else:
            t = Synthaxis_Tree(" ")
            self.cur_tree = t
            return True

    def TE1(self):
        if  self.pos < len(self.s) and self.s[self.pos] == '*':
            t = Synthaxis_Tree("* F TE1")
            self.pos += 1
            i = self.pos
            if self.F():
                t.addNode('F', self.cur_tree)
                i = self.pos
                if self.TE1():
                    t.addNode('TE1', self.cur_tree)
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {i} Incorrect multiplication expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        elif self.pos < len(self.s) and self.s[self.pos] == '/':
            t = Synthaxis_Tree("/ F TE1")
            self.pos += 1
            i = self.pos
            if self.F():
                t.addNode('F', self.cur_tree)
                i = self.pos
                if self.TE1():
                    t.addNode('TE1', self.cur_tree)
                    self.cur_tree = t
                    return True
                else:
                    print(f'Error: position = {i} Incorrect multiplication expression')
                    return False
            else:
                print(f'Error: position = {i} Incorrect arifmetical expression')
                return False

        else:
            t = Synthaxis_Tree(" ")
            self.cur_tree = t
            return True

arifmetic_symbols = ["+", "-", "*", "/", "==", "<", ">", "<>", "<=", ">="]
managment_symbols = [";", "{", "}", "="]
breakets = "(", ")"
var = ['id', 'const']
def to_polish_notation(tree):
    T = Synthaxis_Tree('')
    if len(tree.name.split('\n')[1].replace(" ", "")) == 0:
        return ('', T)
    res = ''
    exp = tree.name.split('\n')[1].split(' ')
    if exp[0] in arifmetic_symbols:
        buf = exp[0]
        exp[0] = exp[1]
        exp[1] = buf
    for e in exp:
        if e == '':
            continue
        if e in arifmetic_symbols or e in managment_symbols:
            res += e + ' '
        elif e in var:
            s = tree.childs[e].name.split('\n')[1].replace(" ", "")
            NT = Synthaxis_Tree(s)
            T.addNode(f'{e}', NT)
            res += s + ' '
        elif e not in breakets:
            s, NT = to_polish_notation(tree.childs[e])
            T.addNode(f'{e}', NT)
            res += s
    T.name += res
    return res, T

st = '1 + 12 + kk -12 *(jdi + 12 *3 - (17 + kk)) + 1'
while True: 
    st = input('Input string: ')
    s = Scaner(st)
    if s.correct:
        #s.draw()
        s, t = to_polish_notation(s.cur_tree)
        print(s)
        t.visualize()
    else:
        print("Error")