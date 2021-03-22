import csv
import tkinter as tk
import math
import random

# A Label that thinks its a Node

class Node(tk.Label):
    def __init__(self, root, i, j):
        super().__init__(root)
        self.root = root
        self.i = i
        self.j = j
        self.unselected_color = "teal"
        self.selected_color = "blue"
        self.target_color = "orange"
        self.visited_color = "red"
        
        self.bind("<Button-1>", lambda e, s=self: s.clicked())
        
        self.unselect()
        self.grid(row=i, column=j, sticky="news")
        
        root.rowconfigure(i, weight=1)
        root.columnconfigure(j, weight=1)

        self.visited = False
        self.target = False

# Pretty output

    def __str__(self):
        return f'({self.i}, {self.j})'

    def clicked(self):
        print(f'I am {self} and my neighbours are: {self.root.get_neighbours(self)}')
        self.root.clicked(self)
        
    def select(self):
        self.configure(bg=self.selected_color, borderwidth=2, relief="sunken")
        self.selected = True

    def targetted(self):
        self.configure(bg=self.target_color, borderwidth=2, relief="sunken")
        self.target = True

    def unselect(self):
        self.configure(bg=self.unselected_color, borderwidth=2, relief="raised")
        self.selected = False
        self.target = False

    def visit(self):
        if not(self.target or self.selected):
            self.configure(bg=self.visited_color, borderwidth=2, relief="raised")
        self.visited = True
        
    def unvisit(self):
        if not(self.target or self.selected):
            self.configure(bg=self.unselected_color, borderwidth=2, relief="raised")
        self.visited = False

# A Frame that thinks it's an Adjacency List

class AdjGrid(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.adj_list = {}
        self.selected_node = None
        self.target_node = None
        self.traversal = None

    def add_edge(self, n , m):
        if n in self.adj_list:
            self.adj_list[n].append(m)
        else:
            self.adj_list[n] = [m]

    def get_neighbours(self, n):
        return [str(m) for m in self.adj_list[n]]

# What to do if a node is clicked

    def clicked(self, n):
        if not self.traversal:

# This is totally mad, but it gets there eventually

            if self.selected_node:
                if self.selected_node == n:
                    self.selected_node.unselect()
                    self.selected_node = None
                    if self.target_node:
                        self.target_node.unselect()
                        self.target_node = None
                elif self.target_node == n:
                    self.target_node.unselect()
                    self.target_node = None
                elif self.target_node:
                    self.target_node.unselect()
                    self.target_node = n
                    self.target_node.targetted()                  
                else:
                    self.target_node = n
                    self.target_node.targetted()
            else:
                self.selected_node = n
                self.selected_node.select()

# Unvisit all nodes

    def reset(self):
        for n in self.adj_list:
            n.unvisit()
        self.traversal = None

# Start a traversal

    def start(self, traversal_type):
        if not self.selected_node and self.target_node:
            print("Selection?")
            return
        self.reset()
        self.traversal = traversal_type(self, self.selected_node, self.target_node)
        self.tick()

# Iterate after given time period

    def tick(self):
        if self.traversal:
            self.traversal.tick()
            if self.traversal.done():
                self.traversal = None
            else:
                self.after(50, self.tick)

# Traversals: first a wrapper class

class Traversal:
    def __init__(self, adj_grid, root_node, target_node):
        self.adj_grid = adj_grid
        self.root_node = root_node
        self.target_node = target_node
        self.queue = [root_node]

    def tick(self):
        pass

    def done(self):
        return self.queue == [] or self.target_node in self.queue

# A BFS that steps each time tick is called

class BFS(Traversal):
    def __init__(self, adj_grid, root_node, target_node):
        super().__init__(adj_grid, root_node, target_node)

    def tick(self):
        if self.queue:
            node = self.queue.pop(0)
            node.visit()
            for n in self.adj_grid.adj_list[node]:
                if not(n.visited or n in self.queue):
                    self.queue.append(n)


# A DFS that steps each time tick is called

class DFS(Traversal):
    def __init__(self, adj_grid, root_node, target_node):
        self.adj_grid = adj_grid
        self.root_node = root_node
        self.target_node = target_node
        self.stack = [root_node]        

    def tick(self):
        if self.stack:
            node = self.stack.pop()
            node.visit()
            for n in self.adj_grid.adj_list[node]:
                if not n.visited:
                    self.stack.append(n)

    def done(self):
        return self.stack == [] or self.target_node in self.stack

# A Dijkstra that steps each time tick is called

class Dijkstra(Traversal):
    def __init__(self, adj_grid, root_node, target_node):
        super().__init__(adj_grid, root_node, target_node)
        self.distances = {n : math.inf for n in adj_grid.adj_list}
        self.distances[root_node] = 0        

    def tick(self):
        if self.queue:
            node = min(self.queue, key = lambda n: self.distances[n])
            self.queue.remove(node)
            node.visit()
            for n in self.adj_grid.adj_list[node]:
                if self.distances[node]+1 < self.distances[n]:
                    self.distances[n] = self.distances[node]+1
                    self.queue.append(n)

# An AStar that steps each time tick is called

class AStar(Traversal):
    def __init__(self, adj_grid, root_node, target_node):
        super().__init__(adj_grid, root_node, target_node)
        
        self.distances = {n : math.inf for n in adj_grid.adj_list}
        self.distances[root_node] = 0
        self.heuristic = lambda node: self.distances[node] + abs(node.i - self.target_node.i) + abs(node.j - self.target_node.j)

    

    def tick(self):
        if self.queue:
            node = min(self.queue, key = self.heuristic)
            self.queue.remove(node)
            node.visit()
            for n in self.adj_grid.adj_list[node]:
                if self.distances[node] + 1 < self.distances[n]:
                    self.distances[n] = self.distances[node] + 1
                    self.queue.append(n)

# An AStar that steps each time tick is called

class BrokenAStar(AStar):
    def __init__(self, adj_grid, root_node, target_node):
        super().__init__(adj_grid, root_node, target_node)
        
        self.heuristic = lambda node:  abs(node.j - self.target_node.j) + abs(node.i - self.target_node.i)


# Somewhere for our control buttons to live

class ControlFrame(tk.Frame):
    def __init__(self, root, grid_frame):
        super().__init__(root)
        self.root = root
        self.grid_frame = grid_frame
        
        bfs_button = tk.Button(self, text="BFS", command=lambda:grid_frame.start(BFS))
        dfs_button = tk.Button(self, text="DFS", command=lambda:grid_frame.start(DFS))
        dijkstra_button = tk.Button(self, text="Dijkstra", command=lambda:grid_frame.start(Dijkstra))
        AStar_button = tk.Button(self, text="A*", command=lambda:grid_frame.start(AStar))
        BrokenAStar_button = tk.Button(self, text="Broken A*", command=lambda:grid_frame.start(BrokenAStar))
        reset_button = tk.Button(self, text="Reset", command=grid_frame.reset)

        bfs_button.grid(row=0, column=0)
        dfs_button.grid(row=0, column=1)
        dijkstra_button.grid(row=0, column=2)
        AStar_button.grid(row=0, column=3)
        BrokenAStar_button.grid(row=0, column=4)
        reset_button.grid(row=0, column=5)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)

# The usual tkInter nonsense - this creates the Adjacency list/Frame and the controls

root = tk.Tk()
root.geometry("800x600")

grid_frame = AdjGrid(root)
grid_frame.grid(sticky="news")

control_frame = ControlFrame(root, grid_frame)
control_frame.grid(sticky="news")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
root.columnconfigure(0, weight=1)

# Read the csv file and create nodes where the entry is "0"

nodes = []

with open('maze.csv', encoding='utf-8-sig') as csvfile:
    csvreader = csv.reader(csvfile, dialect='excel')
    i = 0
    for row in csvreader:
        j = 0
        for cell in row:
            if cell == '0':
                nodes.append(Node(grid_frame, i, j))
            j += 1
        i += 1

# This needs improving: double iterate the nodes and create an edge wherever there is adjacency

for n in nodes:
    for m in nodes:
        if not(m == n):
            if m.i == n.i:
                if m.j == n.j - 1 or m.j == n.j + 1:
                    grid_frame.add_edge(n, m)
            if m.j == n.j:
                if m.i == n.i - 1 or m.i == n.i + 1:
                    grid_frame.add_edge(n, m)

# Handover

root.mainloop()  
