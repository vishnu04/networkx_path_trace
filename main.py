# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 17:54:58 2022

@author: vishnu
"""
import pandas as pd
import networkx as nx
from dijkstra import * 
from milp import *
from generator import *
from steiner import * 

if __name__ == "__main__":
    
    print(f'start of main...........')
    originalImage = "dense_heat_map.png"
    originalDF = generateDFFromImg(originalImage)
    dupDF = createDuplicateDF(originalDF)
    G, pos, neighbors = generateGraphFromDF(dupDF,show = False)
    originalImg = generateImgFromDF(dupDF,originalImage,title="Original Image",show = True)
    
    startNodeCor = (90,180) ## [x,y] coordinates
    endNodeCor = (350,75) ## [x,y] coordinates
    reserveNodesCor = [(200,25), (225,175)]
    
    startNode = dupDF[(dupDF.x==startNodeCor[0])&(dupDF.y==startNodeCor[1])].index.values.astype(int)[0]
    endNode = dupDF[(dupDF.x==endNodeCor[0])&(dupDF.y==endNodeCor[1])].index.values.astype(int)[0]
    
    reserveNodes = []
    for rN in reserveNodesCor:
        reserveNodes.append(dupDF[(dupDF.x==rN[0])&(dupDF.y==rN[1])].index.values.astype(int)[0])
         
    terminalNodes = startNode + reserveNodes + endNode
    terminalNodesConnect = [(startNode,reserveNodes[0],2),
                          (startNode,reserveNodes[1],2),
                          (reserveNodes[0],reserveNodes[1],2),
                          (reserveNodes[0],endNode,2),
                          (reserveNodes[1],endNode,2)]
        
    # '''Gurobi Linear Programming'''
    print('\nFinding path using Gurobipy - weight = resistancePerUnit')
    gurobiResPath = runGurobiModel(G,originalDF, terminalNodes,terminalNodesConnect, weight = 'resistPerUnit')
    cost,resist = calCostResistance(G,gurobiResPath)
    plotPath(originalDF,originalImage,gurobiResPath,
              title='Gurobi Least Resistant Path - Cost:'+str(round(cost,2))+'  Resistance:'+str(round(resist,2)))
    print(f'\nOverLapping exists ?:{is_overlap_exists(gurobiResPath,show=False)}')
    
    print('\nFinding path using Gurobipy - weight = cost')    
    gurobiCostPath = runGurobiModel(G,originalDF, terminalNodes,terminalNodesConnect, weight = 'cost')
    cost,resist = calCostResistance(G,gurobiCostPath)
    plotPath(originalDF,originalImage,gurobiCostPath,title = 'Gurobi Least Cost Path - Cost:'+str(round(cost,2))+'  Resistance:'+str(round(resist,2)))
    print(f'\nOverLapping exists ?:{is_overlap_exists(gurobiCostPath,show=False)}')
    
    '''Dijkstra Path'''
    print('\nFinding path using Dijkstra - weight = resistPerUnit')
    dijResPath = runDijkstra(G,originalDF, terminalNodes,terminalNodesConnect, weight = 'resistPerUnit')
    cost,resist = calCostResistance(G,dijResPath)
    plotPath(originalDF,originalImage,dijResPath, title = 'Dijkstra Least Resistant Path - Cost:'+str(round(cost,2))+'  Resistance:'+str(round(resist,2)))
    print(f'\nOverLapping exists ?:{is_overlap_exists(dijResPath,show=False)}')
    
    print('\nFinding path using Dijkstra - weight = cost')
    dijCostPath = runDijkstra(G,originalDF, terminalNodes,terminalNodesConnect, weight = 'cost')
    cost,resist = calCostResistance(G,dijCostPath)
    plotPath(originalDF,originalImage,dijCostPath, title = 'Dijkstra Least Cost Path - Cost:'+str(round(cost,2))+'  Resistance:'+str(round(resist,2)))
    print(f'\nOverLapping exists ?:{is_overlap_exists(dijCostPath,show=False)}')
    
    print(f' Running steiner tree on Dijkstra Least Resistant Path')
    steinerLeastResistancePath = findSteinerPath(G, dijResPath, originalDF, neighbors, terminalNodes, terminalNodesConnect, step = 30, weight='resistance')
    cost,resist = calCostResistance(G,steinerLeastResistancePath)
    plotPath(originalDF,originalImage,steinerLeastResistancePath, title = 'Steiner : Least Resistance Path - Cost:'+str(round(cost,2))+'  Resistance:'+str(round(resist,2)))
    print(f'\nOverLapping exists ?:{is_overlap_exists(steinerLeastResistancePath,show=False)}')
    
    print(f' Running steiner tree on Dijkstra Least Cost Path')
    steinerLeastCostPath = findSteinerPath(G, dijCostPath, originalDF, neighbors, terminalNodes, terminalNodesConnect, step = 30, weight='cost')
    cost,resist = calCostResistance(G,steinerLeastCostPath)
    plotPath(originalDF,originalImage,steinerLeastCostPath, title = 'Steiner : Least Cost Path - Cost:'+str(round(cost,2))+'  Resistance:'+str(round(resist,2)))
    print(f'\nOverLapping exists ?:{is_overlap_exists(steinerLeastCostPath,show=False)}')
        
    print(f'end of main...........')
    