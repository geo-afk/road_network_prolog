import osmium


class OSMHandler(osmium.SimpleHandler):

    def __init__(self) -> None:
         super().__init__()
         self.nodes = 0
         self.ways = 0
         self.relations = 0

    def node(self, n):
        self.nodes += 1

    def way(self, n):
        self.ways +=1

    def relation(self, n):
        self.relations += 1


class OSMPrinter(osmium.SimpleHandler):
    def node(self, n):
        print(f"Node {n.id} at ({n.location.lat}, {n.location.lon}) with tags {n.tags}")

    def way(self, w):
        print(f"Way {w.id} has {len(w.nodes)} nodes and tags {w.tags}")

    def relation(self, r):
        print(f"Relation {r.id} with members {len(r.members)} and tags {r.tags}")

printer = OSMPrinter()
printer.apply_file("jamaica-latest.osm.pbf", locations=True, idx='flex_mem')


objects = {
    'n': [],
    'w': [],
    'r': []
}


if __name__ == "__main__":
    # handler = OSMHandler()
    # handler.apply_file("./map_data/jamaica-251022.osm.pbf", locations=False)
    # print(f"Nodes: {handler.nodes}")
    # print(f"Ways: {handler.ways}")
    # print(f"Relations: {handler.relations}")
