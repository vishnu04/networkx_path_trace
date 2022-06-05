# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 18:38:28 2022

@author: vishnu
"""

import networkx as nx
from itertools import *
from generator import *


''' creating Path with least distance '''
def distBtnNodes(node1,node2,df):
    dist =  ((df.iloc[node1,]['y']-df.iloc[node2,]['y'])**2 + \
                (df.iloc[node1,]['x']-df.iloc[node2,]['x'])**2)**0.5
    return dist

@timer
def findLeastDistancePath(G,originalDF,neighbors,terminalNodes,terminalNodesConnect):
    alreadyIncludedNodes = []
    finalPathList = []
    pairs = []
    nConnectPaths = 0
    routePathTotalResistance = 0
    for connect in terminalNodesConnect:
        nConnectPaths += connect[2]
    i = 0
    for connect in terminalNodesConnect:
        for ci in range(connect[2]):
            i += 1
            print(f'Least Distance Path... tracing {ci} path between {connect[0]}-{connect[1]} > path{i}/path{nConnectPaths}')
            route = connect
            routeStart = route[0]
            routeEnd = route[1]
            routeDist = distBtnNodes(routeStart,routeEnd, originalDF)
            routePath = [routeStart]
            alreadyConsideredNodes = []
            while routeEnd not in routePath:
                lastNode = routePath[-1]
                neighborsLastNode = list(set(neighbors[lastNode]) - set(alreadyIncludedNodes))
                distToRouteEnd = [distBtnNodes(neighNode,routeEnd, originalDF) for neighNode in neighborsLastNode]
                routePath.append(neighborsLastNode[distToRouteEnd.index(min(distToRouteEnd))])
            routePathTotalResistance += sum([G.nodes[node]['resistance'] for node in routePath])
            alreadyIncludedNodes = alreadyIncludedNodes + routePath
            alreadyIncludedNodes = list(set(alreadyIncludedNodes) -set([connect[0]])-set([connect[1]]))
            finalPathList.append(routePath)
    return finalPathList  

def getNeighbors(node,neigbors):
    return list(neigbors[node])

def getNNeighbors(node,neighbors, n = 500):
    i = 0
    neighNodes = [node]
    lvl = len(getNeighbors(node,neighbors))+n
    for node in neighNodes:
        if lvl > 0 :
            neighNode_l = list(set(getNeighbors(node,neighbors)))
            neighNodes += neighNode_l
        lvl -= 1
        if lvl == 0:
            break
    return neighNodes

@timer
def runSteiner(subG, terminal_nodes, weight='weight'):
    steinerPath = nx.algorithms.approximation.steinertree.steiner_tree(subG, terminal_nodes=terminal_nodes, weight=weight)
    return steinerPath

@timer
def findSteinerPath(G, minSpanPaths, df, neighbors, terminalNodes, terminalNodesConnect, step = 10, weight='weight'):
    cAlreadyIncludedNodes = []
    finalSteinerPathList = []
    pairs = []
    nConnectPaths = 0
    for connect in terminalNodesConnect:
        nConnectPaths += connect[2]
    i = 0
    for connect in terminalNodesConnect:
        for ci in range(connect[2]):
            i += 1
            print(f'Steiner-{weight} path... tracing {ci} path between {connect[0]}-{connect[1]} > path{i}/path{nConnectPaths}')
            routeStart = connect[0]
            routeEnd = connect[1]
            newRoute = []
            minSpanPath = minSpanPaths[i-1]
            for j in range(0,len(minSpanPath),step):
                k = min(j+step,len(minSpanPath)-1)
                node1 = minSpanPath[j]
                node2 = minSpanPath[k]
                subgraphNodes = []
                for n in range(j,k+1):
                    subgraphNodes = subgraphNodes + getNNeighbors(minSpanPath[n], neighbors, n = 1000)
                subgraphNodes = list(set(subgraphNodes))
                alreadyIncludedNodes = set(list(G.nodes - subgraphNodes) + cAlreadyIncludedNodes)
                subG = createSubGraph(G,alreadyIncludedNodes)
                if nx.is_connected(subG) == False:
                    alreadyIncludedNodes = set(list(G.nodes - subgraphNodes))
                    subG = createSubGraph(G,alreadyIncludedNodes)
                steinerPath = runSteiner(subG, terminal_nodes=[node1,node2], weight=weight)
                newRoute += steinerPath
                newRoute = list(set(newRoute))
            cAlreadyIncludedNodes = cAlreadyIncludedNodes + list(newRoute)
            cAlreadyIncludedNodes = list(set(cAlreadyIncludedNodes) -set([connect[0]])-set([connect[1]]))
            finalSteinerPathList.append(newRoute)
    return finalSteinerPathList  
    



# def metric_closure(G, weight='weight'):
#     """  Return the metric closure of a graph.

#     The metric closure of a graph *G* is the complete graph in which each edge
#     is weighted by the shortest path distance between the nodes in *G* .

#     Parameters
#     ----------
#     G : NetworkX graph

#     Returns
#     -------
#     NetworkX graph
#         Metric closure of the graph `G`.

#     """
#     M = nx.Graph()

#     Gnodes = set(G)

#     # check for connected graph while processing first node
#     all_paths_iter = nx.all_pairs_dijkstra(G, weight=weight)
#     u, (distance, path) = next(all_paths_iter)
#     if Gnodes - set(distance):
#         msg = "G is not a connected graph. metric_closure is not defined."
#         raise nx.NetworkXError(msg)
#     Gnodes.remove(u)
#     for v in Gnodes:
#         M.add_edge(u, v, distance=distance[v], path=path[v])

#     # first node done -- now process the rest
#     for u, (distance, path) in all_paths_iter:
#         Gnodes.remove(u)
#         for v in Gnodes:
#             M.add_edge(u, v, distance=distance[v], path=path[v])

#     return M



# def steiner_tree(G, terminal_nodes, weight='weight'):
#     """ Return an approximation to the minimum Steiner tree of a graph.

#     Parameters
#     ----------
#     G : NetworkX graph

#     terminal_nodes : list
#          A list of terminal nodes for which minimum steiner tree is
#          to be found.

#     Returns
#     -------
#     NetworkX graph
#         Approximation to the minimum steiner tree of `G` induced by
#         `terminal_nodes` .

#     Notes
#     -----
#     Steiner tree can be approximated by computing the minimum spanning
#     tree of the subgraph of the metric closure of the graph induced by the
#     terminal nodes, where the metric closure of *G* is the complete graph in
#     which each edge is weighted by the shortest path distance between the
#     nodes in *G* .
#     This algorithm produces a tree whose weight is within a (2 - (2 / t))
#     factor of the weight of the optimal Steiner tree where *t* is number of
#     terminal nodes.

#     """
#     # M is the subgraph of the metric closure induced by the terminal nodes of
#     # G.
#     M = metric_closure(G, weight=weight)
#     # Use the 'distance' attribute of each edge provided by the metric closure
#     # graph.
#     H = M.subgraph(terminal_nodes)
#     mst_edges = nx.minimum_spanning_edges(H, weight='distance', data=True)
#     # Create an iterator over each edge in each shortest path; repeats are okay
#     edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)
#     T = G.edge_subgraph(edges)
#     return T


