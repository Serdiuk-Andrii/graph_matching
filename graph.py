class Pedigree:
    def __init__(self):
        self.children_map = dict()
        self.parents_map = dict()
        self.source_vertices: [Vertex] = []
        self.sink_vertices = []

    def add_child(self, parent, child):
        if parent in self.children_map:
            self.children_map[parent].append(child)
        else:
            self.children_map[parent] = list([child])

    def add_line_from_pedigree(self, line):
        (child, mother, father) = list(map(lambda name: int(str(name)), line.strip('\n').split(' ')))
        child_maternal = 2 * child - 1
        child_paternal = child_maternal + 1
        if mother == -1 or father == -1:
            self.source_vertices.append(child)
            return
        self.add_child(2 * mother - 1, child_maternal)
        self.add_child(2 * mother, child_maternal)
        self.add_child(2 * father - 1, child_paternal)
        self.add_child(2 * father, child_paternal)
        # Every non-founder appears only once in the pedigree as a child
        assert child_maternal not in self.parents_map
        assert child_paternal not in self.parents_map
        self.parents_map[child_maternal] = [2 * mother - 1, 2 * mother]
        self.parents_map[child_paternal] = [2 * father - 1, 2 * father]

    @staticmethod
    def get_pedigree_from_file(filename):
        pedigree = Pedigree()
        file = open(filename, 'r')
        for line in file.readlines():
            pedigree.add_line_from_pedigree(line)
        file.close()
        return pedigree

    def get_sink_vertices(self):
        if self.sink_vertices:
            return self.sink_vertices
        self.sink_vertices = [x for x in self.parents_map.keys() if x not in self.children_map.keys()]
        return self.sink_vertices


class Vertex:

    def __init__(self, label: int):
        self.label: int = label
        self.common_ancestry_map = dict()
        self.descendants: {int} = {self.label}
        self.children = []
        self.parents = []

    def set_common_ancestry_map_self(self):
        self.common_ancestry_map = dict([(x, {self.label}) for x in self.descendants])

    def update_ancestry_dictionary(self, parent):
        excluded_descendants = parent.get_excluded_descendants(self)
        for key, value in parent.common_ancestry_map.items():
            if key in self.descendants:
                if key in excluded_descendants:
                    self.common_ancestry_map[key].update(value)
                else:
                    continue
            elif key in self.common_ancestry_map:
                self.common_ancestry_map[key].update(value)
            else:
                self.common_ancestry_map[key] = set(value)

    def get_excluded_descendants(self, excluded_vertex):
        result = set()
        for child in self.children:
            if child != excluded_vertex:
                result.update(child.descendants)
        return result

    def set_common_ancestry_map_given_parents(self, left_parent, right_parent):
        self.set_common_ancestry_map_self()
        self.update_ancestry_dictionary(left_parent)
        self.update_ancestry_dictionary(right_parent)

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return self.label


class Graph:

    def __init__(self, vertices, levels, adjacency_list, reverse_adjacency_list):
        self.vertices = vertices
        self.levels = levels
        self.adjacency_list = adjacency_list
        self.reverse_adjacency_list = reverse_adjacency_list

    @staticmethod
    def process_level_vertex(vertices, parent_label: int, child: Vertex):
        if parent_label not in vertices:
            parent = Vertex(parent_label)
            vertices[parent_label] = parent
            # next_level_vertices.add(left_parent)
        else:
            parent = vertices[parent_label]
        parent.descendants.update(child.descendants)
        child.parents.append(parent)
        parent.children.append(child)
        return parent

    @staticmethod
    def get_graph_from_pedigree_and_probands(pedigree: Pedigree, probands: [int]):
        # Assigning the levels and calculating the descendants for every vertex
        levels: [{Vertex}] = []
        dictionary = pedigree.parents_map
        current_level_vertices = {Vertex(x) for x in probands}
        vertices: {Vertex} = dict()
        for vertex in current_level_vertices:
            vertices[vertex.label] = vertex
        while current_level_vertices:
            levels.append(current_level_vertices)
            next_level_vertices = set()
            for child in current_level_vertices:
                if child.label in dictionary:
                    (left_parent_label, right_parent_label) = dictionary[child.label]
                    next_level_vertices.add(Graph.process_level_vertex(vertices, left_parent_label, child))
                    next_level_vertices.add(Graph.process_level_vertex(vertices, right_parent_label, child))
            current_level_vertices = next_level_vertices
        # Initializing the common-ancestor map for the founders
        current_level_vertices = levels[len(levels) - 1]
        for founder_vertex in current_level_vertices:
            founder_vertex.set_common_ancestry_map_self()
        # Initializing the common-ancestor map for all the other levels
        for index in range(len(levels) - 1).__reversed__():
            for vertex in levels[index]:
                [left_parent, right_parent] = dictionary[vertex.label]
                vertex.set_common_ancestry_map_given_parents(vertices[left_parent], vertices[right_parent])
        return Graph(vertices, levels, pedigree.children_map, pedigree.parents_map)

    def get_vertices_for_given_level(self, level):
        return self.levels[level]

    def get_children_of_given_vertex(self, vertex):
        return self.adjacency_list[vertex]

    def get_parents_of_given_vertex(self, vertex):
        return self.reverse_adjacency_list(vertex)

    def get_common_ancestors(self, first, second):
        max_label = max(first, second)
        other = first + second - max_label
        if other in self.vertices[max_label].common_ancestry_map:
            return self.vertices[max_label].common_ancestry_map[other]
        return []
