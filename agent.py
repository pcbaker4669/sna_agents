import random


class Agent:
    def __init__(self, name, interactions):
        self.name = name
        self.interactions = interactions

    def set_interactions(self, in_degree):
        self.interactions = in_degree

    def get_interactions(self):
        return self.interactions

    def increment_interaction(self):
        self.interactions += 1

    def get_name(self):
        return self.name

    def __str__(self):
        return "N: {}, I: {}".format(self.name, self.interactions)


class CC_Model:

    def __init__(self):
        self.count = 0
        self.nodes = {}
        self.tot_interactions = 0

    def update_graph_totals(self):
        tot = 0
        keys = list(self.nodes.keys())
        for n in keys:
            tot += self.nodes[n].get_interactions()
        self.tot_interactions = tot

    def get_count(self):
        return self.count

    def get_nodes(self):
        return self.nodes

    def get_node_att_prob(self, node):
        d = node.get_interactions()
        return node.get_interactions()/self.tot_interactions

    # get a parent, this choice will be from similarity, right now
    # it is random
    def get_parent_for_new_node(self, node):
        keys = list(self.nodes.keys())
        keys.remove(node.get_name())
        k = random.choice(keys)
        return self.nodes[k]

    # this is for the recommended nodes, the new node has interaction
    # zero and won't get picked.  Implement random activation, this
    # might prove to be too slow.
    def get_popular_match(self):
        keys = list(self.nodes.keys())
        # picks nodes randomly and get attachment prob to test for selection
        # using the interactions score
        cnt = 0
        while True or cnt > 100000:
            k = random.choice(keys)
            prob = int(self.get_node_att_prob(self.nodes[k]) * 100)
            roll = random.randint(0, 100)
            #print("> {}, node: {}, prob: {}, roll: {}".format(cnt, k, prob, roll))
            if prob >= roll:
                print(f"get_popular_match ran {cnt} attempts before finds a match")
                return self.nodes[k]
            cnt += 1


    def create_rnd_node(self):
        name = self.count
        interactions = 0
        node = Agent(name, interactions)
        keys = self.nodes.keys()
        if name not in keys:
            self.nodes[name] = node
        else:
            print("error: node already exits {}".format(name))
        self.count += 1
        return node

    def __str__(self):
        s = ''
        keys = self.nodes.keys()
        for i in keys:
            s += "(" + str(self.nodes[i].get_name()) + ":" + str(self.nodes[i].get_interactions()) + ")"
        return s
