# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 11:07:33 2022

@author: vishnu
"""

## Mixed Integer Linear Programming using Gurobi

from gurobipy import *
from generator import timer
import numpy as np

@timer
def buildArcs(G,weight):
    res = {}
    for edge in G.edges(data=True):
        
        k1 = (edge[0],edge[1])
        v1 = edge[2][weight]
        
        k2 = (edge[1],edge[0])
        v2 = edge[2][weight]
        
        res[k1] = v1
        res[k2] = v2
        # v = (edge[2]['resistance'],edge[2]['cost'],edge[2]['resistDist'])
    return res

@timer
def buildGurobiModel(G,startNode,endNode,excludeNodes,res):
    
    source_nodes = np.array([startNode])
    destination_nodes = np.array([endNode])
    exclude_nodes = np.array(excludeNodes) 
    interim_nodes = np.array(list(set(G.nodes)-set([startNode]) - set([endNode]) -set(excludeNodes)))
    
    m = Model()
    
    x = m.addVars(res.keys(), vtype = GRB.BINARY, name='x', obj = res)
    
    # Flow Constraints
    # at source outflow = 1, inflow = 0
    m.addConstr(x.sum(startNode,"*") == 1)
    m.addConstr(x.sum("*",startNode) == 0)
    
    ## at destination inflow = 1, outflow = 0
    m.addConstr(x.sum("*",endNode) == 1)
    m.addConstr(x.sum(endNode,"*") == 0)
    
    ## interim nodes inflow=outflow
    m.addConstrs(x.sum('*',interim_node) == x.sum(interim_node,'*') for interim_node in interim_nodes)
    m.addConstrs(x.sum('*',interim_node) + x.sum(interim_node,'*') <= 2 for interim_node in interim_nodes)
    
    ## exlcude nodes
    m.addConstrs(x.sum("*",exclude_node) + x.sum(exclude_node,"*") == 0 for exclude_node in exclude_nodes)
    
    return m

@timer
def optimizeModel(gurobiModel):
    gurobiModel.modelSense = GRB.MINIMIZE
    gurobiModel.setParam('OutputFlag', 0)
    gurobiModel.optimize()
    return gurobiModel

@timer
def returnOptPairs(gurobiModel):
    pairs = []
    for var in gurobiModel.getVars():
        if var.X >= 0.5:
            pairs.append(tuple(eval(var.VarName[1:])))
    milpNodes = []
    for pair in pairs:
        milpNodes.append(pair[0])
    return milpNodes,pairs


@timer
def runGurobiModel(G, df, terminalNodes,terminalNodesConnect, weight = 'weight'):
    '''MILP model'''
    res = buildArcs(G,weight)
    alreadyIncludedNodes = []
    finalMilpNodePathList = []
    pairs = []
    nConnectPaths = 0
    for connect in terminalNodesConnect:
        nConnectPaths += connect[2]
    
    i = 0
    for connect in terminalNodesConnect:
        for ci in range(connect[2]):
            i += 1
            print(f'\n\n Gurobi... tracing {ci} path between {connect[0]}-{connect[1]} > path{i}/path{nConnectPaths}')
            model = buildGurobiModel(G, connect[0], connect[1], alreadyIncludedNodes, res)
            optModel = optimizeModel(model)
            milpNodePathList,pairs = returnOptPairs(optModel)
            alreadyIncludedNodes = alreadyIncludedNodes + milpNodePathList
            alreadyIncludedNodes = list(set(alreadyIncludedNodes) -set([connect[0]])-set([connect[1]]))
            finalMilpNodePathList.append(milpNodePathList)
    return finalMilpNodePathList  
    
