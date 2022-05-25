import json
from local_modules.vars.project_config import MAP_FILE, MAP_LEGEND

class pathSearcher:
    def __init__(self, matrix=None, graph=None, file=None, titles=False, legend=None):
        self.matrix = []
        self.graph = {}
        self.paths = {}
        self.legend = legend

        self.entry = 0
        self.dest = 0

        file = MAP_FILE # DEV
        self.legendFromFile(MAP_LEGEND) # DEV
        titles=True # DEV
        
        if file is not None:
            try:
                with open(file, mode="r", encoding="utf-8-sig") as f:
                    data = f.read()
            except Exception as ex:
                print(ex)
                exit()
            
            self.__fileToMatrix(data, titles)
            self.__matrixToDict()
        elif matrix is not None:
            self.matrix = matrix
            self.__matrixToDict()
        elif graph is not None:
            self.graph = graph

    def calc(self):
        path = self.minPath(self.entry, self.dest)

        return self.getPathLegend(path)

    def __fileToMatrix(self, data, titles):
        s = 1 if titles else 0
        self.matrix = []

        for i, _row in enumerate(data.split("\n")[s:]):
            row = []
            for j, cell in enumerate(_row.split(";")[s:]):
                app = 0
                if str(cell).isdigit():
                    if int(cell) == 1:
                        app = 1
                
                row.append(app)

            self.matrix.append(row)

    def __matrixToDict(self):
        self.graph = {}

        for i, _row in enumerate(self.matrix):
            row = []
            for j, cell in enumerate(_row):
                if cell == 1:
                    row.append(j)
            self.graph[i] = row

    def allPaths(self, _from, _to):
        key = "%d->%d" % (_from, _to)
        if key not in self.paths:
            self.paths[key] = list(self.__DFS(_from, _to))

        return self.paths[key]
    
    def minPath(self, _from, _to):
        key = "%d->%d" % (_from, _to)
        if key not in self.paths: self.allPaths(_from, _to)

        _minLen = len(self.graph) * 2
        _minPath = None
        for p in self.paths[key]:
            l = len(p)

            if l < _minLen:
                _minLen = l
                _minPath = p

        return _minPath

    def legendFromFile(self, file):
        try:
            with open(file, "r") as f:
                self.legend = json.load(f)
        except Exception as ex:
            print(ex)
            self.legend = None
            return ex

    def getPathLegend(self, path, separator=" ->\n"):
        if self.legend is None:
            return "Legend is not uploaded"

        message = []
    
        i = 0
        while i < len(path):
            p = path[i]

            if "e" in self.legend[str(p)]:
                r = self.__parseE(self.legend[str(p)])
                for key in r:
                    if r[key] == str(path[i+1]):
                        message.append(key)
                        i += 1
                i += 1
            else:
                message.append(self.legend[str(p)])
                i += 1

        return separator.join(message)

    def __parseE(self, data):
        keyval = data.split("?")[1]
        out = {}

        for kv in keyval.split("&"):
            k, v = kv.split("=")
            out[k] = v

        return out

    def __DFS(self, start, goal):
        stack = [(start, [start])]
        while stack:
            (vertex, path) = stack.pop()
            for next in set(self.graph[vertex]) - set(path):
                if next == goal:
                    yield path + [next]
                else:
                    stack.append((next, path + [next]))


