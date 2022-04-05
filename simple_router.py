class Router:
    def __init__(self):
        self.route = "root"
        self.status = True
        self.data = ""

    def moveTo(self, path):
        p = self.route.split("/")
        p.append(path)
        self.route = "/".join(p)

        return self.route

    def back(self):
        p = self.route.split("/")
        p.pop()
        self.route = "/".join(p)

        return self.route

    def whereAmI(self):
        p = self.route.split("/")

        return p[-1]

    def lock(self, data):
        self.data = data
        self.status = False

    def unlock(self):
        self.status = True
        self.data = ""