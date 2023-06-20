import time

from graph import get_graph_from_file

if __name__ == '__main__':
    filename = input("Specify the name of the pedigree file\n")
    start = time.time()
    graph = get_graph_from_file(filename)
    end = time.time()
    print(f"The execution time: {end - start}")
    while True:
        [first, second] = input("Specify the vertices\n").split(' ')
        first = int(first)
        second = int(second)
        common_ancestors = graph.get_common_ancestors(first, second)
        print(common_ancestors)
