#!/usr/bin/env python3

import networkx as nx
import argparse as ap
import glob
import os
import re

import matplotlib.pyplot as plt

exclude_list = []

def build_cxx_dependency_graph(root):
    """
    Builds a dependency graph of the files in the project

    Returns:
        graph (nx.graph): a dependency graph of the files in the project, as promised.
        Edges are directed from the file that depends, to the file it depends on, 
        i.e. sinks in the graph represent files that are very depended on, and 
        sources are probably just main.
    """
    # compule a regex pattern to match includes
    #re.compile(r'^\s*#include [<"]([^>"]+)[>"]') # including standard libraried
    pattern = re.compile(r'^\s*#include "([^"]+)"')

    # create a new graph object
    graph = nx.DiGraph()

    # get all the files we need
    files = glob.glob(os.path.join(root,"**/*.h"), recursive=True) #+ glob.glob("**/*.cpp", recursive=True) + glob.glob("**/*.c", recursive=True)

    # for each file that we find
    for fl in files:
        # begin reading the file
        with open(fl, 'r') as f:
            # for each line
            for line in f:
                # for each thing that the file imports add a directed edge from this file to the imported file
                # TODO we might need to resolve some paths here
                graph.add_edges_from([(fl,dependent) for dependent in re.findall(pattern, line)])
    for ex in exclude_list:
        graph.remove_node(ex)
    return graph

def build_py_dependency_graph(root):
    """
    builds a dependency grapn of the files in the project

    Returns:
        graph (nx.graph): a dependency graph of the files in the project, as promised.
        Edges are directed from the file that depends, to the file it depends on, 
        i.e. sinks in the graph represent files that are very depended on, and 
        sources are probably just main.
    """
    # compule a regex pattern to match imports
    pattern = re.compile(r'^(\s*import\s+(\S+))|^(\s*from\s+(\S+)\s+import\s+(\S+))')

    # create a new graph object
    graph = nx.DiGraph()

    # get all the files we need
    files = glob.glob(os.path.join(root,"**/*.py"), recursive=True)
    # print(files)

    # for each of the files we find
    for fl in files:
        edges = []
        # begin reading the file
        with open(fl, 'r') as f:
            # print('\n',fl)
            # for each line:
            for line in f:
                # find import matches
                matches = re.findall(pattern, line)
                # for each match we found
                for match in matches:
                    edge = None
                    # get the groups
                    groups = match
                    # print(match[0] if match[0] else match [2])
                    # if this is import <package>
                    if groups[0]:
                        # do path resolution to find out if this file is in here or a system library
                        the_path = os.path.join(*fl.split(os.sep)[:-1],groups[1].replace('.',os.sep))+'.py'
                        # print(f"trying import {the_path}")
                        # if this path is there, then save it as that path
                        if the_path in files:
                            edge = (fl,the_path)
                            # print(f'0) using import {the_path}')
                        else:
                            # imports of the form import <builtin-pkg>
                            # print(f'1) using import {groups[1]}')
                            edge = (fl,groups[1])
                    else:
                        # then this is a from <pkg> import <pkg or name>
                        if groups[3].startswith('.'):
                            # if the base package is a relative import
                            the_path = os.path.join(*fl.split(os.sep)[:-1],'.'+groups[3][1:].replace('.',os.sep))
                        else:
                            # the package is not a relative import
                            the_path = os.path.join(*fl.split(os.sep)[:-1],groups[3].replace('.',os.sep))
                        # print(f"trying from {groups[3]} import {groups[4]}")
                        if groups[3].startswith('.') and os.path.join(*fl.split(os.sep)[:-1],groups[3][1:].replace('.', os.sep), groups[4]+'.py') in files:
                            # import of the form: from .<pkg> import <sub>
                            pth = os.path.join(*fl.split(os.sep)[:-1],groups[3][1:].replace('.', os.sep), groups[4]+'.py')
                            # print(f"2) using import {pth}")
                            edge = (fl,pth)
                        elif groups[3].startswith('.') and os.path.join(*fl.split(os.sep)[:-1],groups[3][1:].replace('.',os.sep)+'.py') in files:
                            # import of the form: from .<pkg>.<sub> import <name>
                            pth = os.path.join(*fl.split(os.sep)[:-1],groups[3][1:].replace('.',os.sep)+'.py')
                            # print(f"3) using import {pth}")
                            edge = (fl,pth)
                        elif groups[3].startswith('.') and os.path.join(*fl.split(os.sep)[:-1],groups[3][1:]+'.py') in files:
                            # import of the form: from .<pkg> import <name>
                            pth = os.path.join(*fl.split(os.sep)[:-1],groups[3][1:]+'.py')
                            # print(f"4) using import {pth}")
                            edge = (fl,pth)
                        elif groups[3] == '.' and os.path.join(*fl.split(os.sep)[:-1],groups[4]+'.py') in files:
                            # imports of the form: from . import <pkg>
                            pth = os.path.join(*fl.split(os.sep)[:-1],groups[4]+'.py')
                            # print(f"5) using import {pth}")
                            edge = (fl,pth)
                        elif groups[3] == '.':
                            # then it has the form: from . import <name>
                            # not interesting
                            # pth = os.path.join(*fl.split(os.sep)[:-1],'__init__.py')
                            # print(f"6) usint import {pth}")
                            # edge = (fl,pth)
                            continue
                        else:
                            # imports of the form "from <pkg>.<sub> import <name>"
                            # print(f"6) using import {groups[3].split('.')[0]}")
                            edge = (fl,groups[3].split('.')[0])
                    if edge and not edge[0] in exclude_list and not edge[1] in exclude_list:
                        edges.append(edge)
        # print(edges)
        graph.add_edges_from(edges)

    return graph

def visualize(graph, path):
    options = {
        'node_color': 'blue',
        'node_size': 100,
        'width': 2,
        'font_size': 8
    }
    from networkx.drawing.nx_pylab import draw_planar
    try:
        draw_planar(graph)
        plt.savefig(path+'.png')
    except:
        print('planar print failed')
    #   print("Bruh, this is one h*** of a dependency graph. Thes should be trees, not flipping K_12!!")
    #   plt.draw()
    # plt.subplot(111)
        # nx.draw(graph, with_labels=True, font_weight='bold')
        write_gv(graph, path+'gv')

def write_gv(graph, path):
    """writes the given graph to a graphviz file with the specified name
    """
    with open(path, 'w+') as f:
        f.write('digraph dependency_graph {\n')
        f.write('    graph [nodesep="1", ranksep="2"];\n')
        f.write('    splines="false";')
        f.write('    node [shape = circle];\n')
        edges = list(graph.edges())
        for edge in edges:
            f.write(f'    "{edge[0]}" -> "{edge[1]}";\n')
        f.write('}')

def statistics(graph, reduce=True, verb=True):
    stats = dict()

    # perform transitive reduction
    if reduce:
        from networkx.algorithms.dag import transitive_reduction
        reduced = transitive_reduction(graph)
        stats['reduced'] = reduced

        # git the extra edges that we honestly don't need
        superfluous_edges = graph.edges() - reduced.edges()
        stats['superfluous_edges'] = superfluous_edges
        # if verb:
            # print(superfluous_edges)
    else:
        stats['reduced'] = graph

    # find any cycles
    from networkx.algorithms.cycles import simple_cycles
    cycles = list(simple_cycles(stats['reduced']))
    if verb and len(cycles) > 0:
        print("Found {0} cycles".format(len(cycles)))
    elif verb:
        print("Graph is cycle-free")
    stats['cycles'] = cycles

    # calculate connected components
    # from networkx.algorithms.components import connected_components
    components = list(nx.weakly_connected_components(stats['reduced']))
    if verb:
        print("{0} connected component{1}".format(len(components), "" if len(components) == 1 else "s"))
    stats['components'] = components

    # return all the stats we calclulated
    return stats

if __name__ == "__main__":
    parser = ap.ArgumentParser('graph_deps',description="""graph_deps analyzes a
            project and builds the dependency graph of the project by language""")
    
    parser.add_argument('-l', '--lang', action='store', dest='lang', default="python",
            type=str, help="the language of the project to analyze")
    parser.add_argument('root', action='store', nargs='?', type=str,
            default='.', help='the root of the directory to analyze')

    args = parser.parse_args()

    print('analyzing...')
    global pattern
    if args.lang in {'c++', 'C++'}:
        G = build_cxx_dependency_graph(args.root)
        reduce=True
    elif args.lang in {'python', 'py'}:
        exclude_list = {'os','sys','pickle','json','socket',
        'functools','cvxopt','signal','PIL','traceback','pandas',
        'numpy','_thread','threading','inspect','io','flask',
        'flask_cas','matplotlib','Cryptodome','pytest','psutil',
        'docker','git','argparse','subprocess','random','time',
        'glob','importlib','shutil','collections','logging', 'requests',
        'matplotlib.pyplot','builtins','uuid', 'sqlalchemy', 'flask_login',
        'queue','socketserver','select','struct','urllib','webbrowser'}
        G = build_py_dependency_graph(args.root)
        reduce=True
    
    reduced = statistics(G, reduce=reduce)['reduced']
    # visualize(reduced)
    out = 'dependencies.gv'
    write_gv(reduced, out)
    print(f"Graphviz file written to {out}")
