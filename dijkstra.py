# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 11:07:33 2022

@author: vishnu
"""

## Tracing path using Dijkstra's algorithm 

import networkx as nx
from generator import *

@timer
def runDijkstra(G, df, terminalNodes,terminalNodesConnect, weight='weight'):    
    alreadyIncludedNodes = []
    finalDijPathList = []
    pairs = []
    nConnectPaths = 0
    for connect in terminalNodesConnect:
        nConnectPaths += connect[2]
    i = 0
    for connect in terminalNodesConnect:
        for ci in range(connect[2]):
            i += 1
            print(f'Dijkstra-{weight} path... tracing {ci} path between {connect[0]}-{connect[1]} > path{i}/path{nConnectPaths}')
            subG = createSubGraph(G,alreadyIncludedNodes)
            dijPath = nx.dijkstra_path(subG, connect[0], connect[1], weight=weight)
            alreadyIncludedNodes = alreadyIncludedNodes + dijPath
            alreadyIncludedNodes = list(set(alreadyIncludedNodes) -set([connect[0]])-set([connect[1]]))
            finalDijPathList.append(dijPath)
    return finalDijPathList  

