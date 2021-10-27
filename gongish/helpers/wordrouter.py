ARG_MARK = 1
WILDCARD_MARK = 2
FN_MARK = 3


class WordRouter:
    delimiter = "/"
    arg_char = ":"
    wildcard_char = "*"

    def __init__(self):
        self.routes = dict()

    def add(self, route, fn):
        wchar = self.wildcard_char
        achar = self.arg_char
        parent = self.routes
        for word in route.split(self.delimiter):
            firstchar = word[:1]
            if firstchar == achar:
                word = ARG_MARK

            elif firstchar == wchar:
                word = WILDCARD_MARK

            if word not in parent.keys():
                parent[word] = dict()

            parent = parent[word]

        parent[FN_MARK] = fn

    def dispatch(self, route):
        words = route.split(self.delimiter)
        route = self.routes
        route_keys = route.keys()
        route_args = []
        steps = 0
        for word in words:
            if word in route_keys:
                route = route[word]
                route_keys = route.keys()
                steps += 1

            elif ARG_MARK in route_keys:
                # Extract arguments
                route = route[ARG_MARK]
                route_keys = route.keys()
                route_args.append(word)
                steps += 1

            elif WILDCARD_MARK in route_keys:
                if WILDCARD_MARK in route:
                    route = route[WILDCARD_MARK]
                route_keys = (WILDCARD_MARK,)
                route_args.append(word)
                steps += 1

        if steps != len(words):
            return None, route_args

        return route.get(FN_MARK), route_args

    def __call__(self, route):
        fn, args = self.dispatch(route)
        if not fn:
            return
        return fn(*args)
