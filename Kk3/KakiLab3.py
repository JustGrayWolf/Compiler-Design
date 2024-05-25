import pydot
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from collections import deque

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
        plt.imshow(img)
        plt.axis('off')
        plt.show()


class Scaner:
    def __init__(self, s):
        self.s = s.replace(' ', '').replace('\n', '').replace('\r', '')
        print(self.s)
        self.pos = 0
        self.cur_tree = None
        self.correct = self.P()

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
            if self.pos < len(self.s) and self.s[self.pos] == 'e' or self.s[self.pos] == 'E':
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
                    t.addNode('L' + ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('L'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == '}':
                    self.pos += 1
                    i = self.pos
                    if self.T():
                        t.addNode('T'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                    t.addNode('E'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                    i = self.pos
                    if self.T():
                        t.addNode('T'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('O'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.T():
                    t.addNode('T'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                    t.addNode('L'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                    t.addNode('E'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    i = self.pos
                    if self.TE1():
                        t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                        i = self.pos
                        if self.A1(): 
                            t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                            i = self.pos
                            if self.C():
                                t.addNode('C'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                    i = self.pos
                    if self.C():
                        t.addNode('C'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
            t.addNode('const'+ ' = ' + self.s[i:self.pos], self.cur_tree)
            i = self.pos
            if self.TE1():
                t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                    i = self.pos
                    if self.C():
                        t.addNode('C'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                    t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    i = self.pos
                    if self.TE1():
                        t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                        i = self.pos
                        if self.A1():
                            t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                if  self.pos < len(self.s) and self.s[self.pos] == ')':
                    self.pos += 1
                    i = self.pos
                    if self.TE1():
                        t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('A'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('TE'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.A1():
                    t.addNode('A1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('F'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.TE1():
                    t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
                t.addNode('F'+ ' = ' + self.s[i:self.pos], self.cur_tree)
                i = self.pos
                if self.TE1():
                    t.addNode('TE1'+ ' = ' + self.s[i:self.pos], self.cur_tree)
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
st = '{b = b + 11;\n {s = g * g + b * b; hi <= -99.99}; calculate = 13 * s / b / s + 123 * 10 * (0.181 + 2 * (b + 1) - s )}'
while True: 
    st = input('Введите строку для анализа: ')
    s = Scaner(st)
    if s.correct:
        s.draw()
    else:
        print("Синтаксическое дерево не построено так как переданная строка не соответствует граматике")
#P → { L }
#L → { L } T|id = E T
#T → ; O T| 
#O → { L }|id = E

#E → ( A ) TE1 A1 C|id TE1 A1 C|const TE1 A1 C
#C → < A|<= A|== A|<> A|> A|>= A |  

#A → ( A ) TE1 A1|id TE1 A1|const TE1 A1
#TE → ( A ) TE1|id TE1|const TE1
#F → ( A )|id|const

#A1 →  |+ TE A1|- TE A1
#TE1 →  |* F TE1|/ F TE1