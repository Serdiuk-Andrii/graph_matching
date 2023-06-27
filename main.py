import time

from graph import Graph, Pedigree


def read_option(number_of_options):
    while True:
        option = input()
        try:
            option = int(option)
        except TypeError:
            print("Specify an integer")
            continue
        if option > number_of_options or option < 1:
            print("Specify a correct option")
            continue
        return option


def read_probands(pedigree):
    while True:
        try:
            print("Choose the option:\n"
                  "1) Read the probands from the input stream\n"
                  "2) Take all the sink vertices from the pedigree\n")
            option = read_option(2)
            if option == 1:
                probands = input("Specify the probands:\n")
                return list(map(lambda name: int(str(name)), probands.strip('\n').split(' ')))
            probands = pedigree.get_sink_vertices()
            print(f"The probands are: {probands}")
            return probands
        except EOFError:
            print("An error occurred, try again")


if __name__ == '__main__':
    filename = input("Specify the name of the pedigree file\n")
    start_pedigree = time.time()
    pedigree = Pedigree.get_pedigree_from_file(filename)
    end_pedigree = time.time()
    print(f"The execution time for reading the pedigree: {end_pedigree - start_pedigree}")
    probands = read_probands(pedigree)
    start_graph = time.time()
    graph = Graph.get_graph_from_pedigree_and_probands(pedigree, probands)
    end_graph = time.time()
    print(f"The execution time for preprocessing: {end_graph - start_graph}")
    while True:
        [first, second] = input("Specify the vertices\n").split(' ')
        first = int(first)
        second = int(second)
        common_ancestors = graph.get_common_ancestors(first, second)
        print(common_ancestors)
