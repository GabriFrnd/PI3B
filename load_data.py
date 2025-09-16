import networkx as nx

def load_data(facebook_dir):
    G_nx = nx.read_edgelist(f"{facebook_dir}/0.edges", nodetype=int)

    featnames = [line.strip() for line in open(f"{facebook_dir}/0.featnames")]
    node_features = {}
    for line in open(f"{facebook_dir}/0.feat"):
        parts = line.strip().split()
        node = int(parts[0])
        features = list(map(int, parts[1:]))
        node_features[node] = dict(zip(featnames, features))

    circles = []
    with open(f"{facebook_dir}/0.circles") as f:
        for line in f:
            parts = line.strip().split()
            circles.append(set(map(int, parts[1:])))

    return G_nx, node_features, circles

