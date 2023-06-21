class Pedigree:
    def __init__(self):
        self.children_map = dict()
        self.parents_map = dict()

    def add_child(self, parent, child):
        if parent in self.children_map:
            self.children_map[parent].append(child)
        else:
            self.children_map[parent] = list([child])

    def add_line_from_pedigree(self, line):
        (child, parent_left, parent_right) = list(map(lambda name: int(str(name)), line.strip('\n').split(' ')))
        self.add_child(parent_left, child)
        self.add_child(parent_right, child)
        # Every non-founder appears only once in the pedigree as a child
        assert child not in self.parents_map
        self.parents_map[child] = [parent_left, parent_right]

    @staticmethod
    def get_pedigree_from_file(filename):
        pedigree = Pedigree()
        file = open(filename, 'r')
        for line in file.readlines():
            pedigree.add_line_from_pedigree(line)
        file.close()
        return pedigree


class Vertex:

    def __init__(self, label: int):
        self.label = label
        self.ancestry_map = []

    def set_ancestry_dictionary_for_source_vertex(self, descendants):
        self.ancestry_map = dict([(x, {self.label}) for x in descendants])

    def update_ancestry_dictionary(self, parent):
        for key, value in parent.ancestry_map.items():
            if key in self.ancestry_map:
                self.ancestry_map[key].update(value)
            else:
                self.ancestry_map[key] = set(value)

    def set_ancestry_dictionary_given_parents(self, descendants, left_parent, right_parent):
        self.set_ancestry_dictionary_for_source_vertex(descendants)
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
    def get_graph_from_pedigree_and_probands(pedigree: Pedigree, probands: [int]):
        # Assigning the levels and calculating the descendants for every vertex
        levels = []
        dictionary = pedigree.parents_map
        current_level_vertices = set(probands)
        descendants_map = dict()
        for proband in probands:
            descendants_map[proband] = {proband}
        while current_level_vertices:
            levels.append(current_level_vertices)
            next_level_vertices = set()
            for child in current_level_vertices:
                if child in dictionary:
                    next_level_vertices.update(dictionary[child])
                    [left_parent, right_parent] = dictionary[child]
                    if left_parent not in descendants_map:
                        descendants_map[left_parent] = {left_parent}
                    descendants_map[left_parent].update(descendants_map[child])
                    if right_parent not in descendants_map:
                        descendants_map[right_parent] = {right_parent}
                    descendants_map[right_parent].update(descendants_map[child])
            current_level_vertices = next_level_vertices
        # Initializing the common-ancestor map for the founders
        vertices = dict()
        current_level_vertices = levels[len(levels) - 1]
        for source_vertex in current_level_vertices:
            vertex = Vertex(source_vertex)
            vertex.set_ancestry_dictionary_for_source_vertex(descendants_map[source_vertex])
            vertices[source_vertex] = vertex
        # Initializing the common-ancestor map for all the other levels
        for index in range(len(levels) - 1).__reversed__():
            for child in levels[index]:
                vertex = Vertex(child)
                [left_parent, right_parent] = dictionary[child]
                vertex.set_ancestry_dictionary_given_parents(descendants_map[child],
                                                             vertices[left_parent], vertices[right_parent])
                vertices[child] = vertex
        # Removing the diagonal from the common-ancestry matrix
        for value in vertices.values():
            value.ancestry_map.pop(value.label)
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
        if other in self.vertices[max_label].ancestry_map:
            return self.vertices[max_label].ancestry_map[other]
        return []
