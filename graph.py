from functools import reduce
from math import ceil


class Vertex:

    def __init__(self, label: int):
        self.label = label
        self.ancestry_map = []

    def set_ancestry_dictionary_for_source_vertex(self, descendants):
        self.ancestry_map = dict([(x, {self.label}) for x in descendants])

    def set_ancestry_dictionary_given_parents(self, left_parent, right_parent, dictionary):
        map = dict(left_parent.ancestry_map)
        for key, value in right_parent.ancestry_map.items():
            if key in map:
                map[key] = set(map[key])
                map[key].update(value)
            else:
                map[key] = value
        if self.label in dictionary:
            for child in dictionary[self.label]:
                map[child].add(self.label)
        map[self.label].add(self.label)
        self.ancestry_map = map

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


def find_direct_descendants_of_vertex(graph, vertex, cache):
    if vertex in cache:
        return cache[vertex]
    descendants = {vertex}
    if vertex in graph:
        for child in graph[vertex]:
            descendants.update(find_direct_descendants_of_vertex(graph, child, cache))
    cache[vertex] = descendants
    return descendants


def find_source_vertices(graph):
    # Definitely not the most efficient way
    return [x for x in graph.keys() if x not in reduce(set.union, map(set, graph.values()))]


def calculate_all_descendants(graph):
    source_vertices = find_source_vertices(graph)
    cache = dict()
    for source_vertex in source_vertices:
        find_direct_descendants_of_vertex(graph, source_vertex, cache)
    return (source_vertices, cache)


def add_direct_descendant(dictionary, parent, child):
    if parent in dictionary:
        dictionary[parent].append(child)
    else:
        dictionary[parent] = list([child])


def get_graph_from_file(filename):
    file = open(filename, 'r')
    # Saving the list of direct descendants for every vertex
    dictionary = dict()
    reverse_dictionary = dict()
    for line in file.readlines():
        line = line.strip('\n')
        components = list(map(lambda name: int(str(name)), line.split(' ')))
        add_direct_descendant(dictionary, components[1], components[0])
        add_direct_descendant(dictionary, components[2], components[0])
        add_direct_descendant(reverse_dictionary, components[0], components[1])
        add_direct_descendant(reverse_dictionary, components[0], components[2])
    (source_vertices, result) = calculate_all_descendants(dictionary)
    vertices = dict()
    # Starting with the source vertices
    current_level_vertices = set(source_vertices)
    for source_vertex in current_level_vertices:
        vertex = Vertex(source_vertex)
        vertex.set_ancestry_dictionary_for_source_vertex(result[source_vertex])
        vertices[source_vertex] = vertex
    levels = []
    # Initializing all the other vertices
    while current_level_vertices:
        levels.append(current_level_vertices)
        next_level_vertices = set()
        for parent in current_level_vertices:
            if parent in dictionary:
                next_level_vertices.update(dictionary[parent])
                for child in dictionary[parent]:
                    vertex = Vertex(child)
                    [left_parent, right_parent] = reverse_dictionary[child]
                    vertex.set_ancestry_dictionary_given_parents(vertices[left_parent], vertices[right_parent], dictionary)
                    vertices[child] = vertex
        current_level_vertices = next_level_vertices
    for value in vertices.values():
        value.ancestry_map.pop(value.label)
    graph = Graph(vertices, levels, dictionary, reverse_dictionary)
    return graph
