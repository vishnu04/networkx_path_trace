# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 18:55:12 2022

@author: vishnu
"""

import networkx as nx
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import transforms
from tensorflow import keras
from PIL import Image
import math
from PIL import ImageColor
import seaborn as sns


def timer(fn):
    from time import perf_counter
    
    def inner(*args, **kwargs):
        start_time = perf_counter()
        to_execute = fn(*args, **kwargs)
        end_time = perf_counter()
        execution_time = end_time - start_time
        print('{0} took {1:.8f}s to execute'.format(fn.__name__, execution_time))
        return to_execute
    
    return inner

@timer
def generateDFFromImg(image_name):
    colourImg = keras.preprocessing.image.load_img("../sampleImage/"+image_name)
    colourPixels = keras.preprocessing.image.img_to_array(colourImg)
    h, w = colourImg.size
    newsize = (w,h)
    indicesArray = np.moveaxis(np.indices(newsize), 0, 2)
    colourArray = np.array(colourPixels).reshape(colourPixels.shape)
    allArray = np.dstack((indicesArray, colourArray)).reshape((-1, 5))
    df = pd.DataFrame(allArray, columns=["y", "x", "red","green","blue"])
    df = df.astype({'red':'float32','green': 'float32','blue':'float32'})
    redWt = 1
    greenWt = 1
    blueWt = 1
    costNormalMean = 10
    costNormalStd = 3
    costEpsilon = 0.01
    resIncWt = 1
    df['resistance'] = (1 - (df.green / (redWt * df.red + greenWt * df.green + blueWt * df.blue+1))) * (1- 0.5 * df.green/255)
    np.random.seed(123)
    df['costDist'] = pd.DataFrame(np.random.normal(costNormalMean,costNormalStd, len(df)))
    df['costDist'] = df['costDist'] - min(df['costDist'])+ costEpsilon
    df['cost'] = df.resistance * df.costDist
    df['nonGreen'] = df['resistance'].apply(lambda x: resIncWt if x > 0.5 else 1)
    df['cost'] = df['cost'] * df['nonGreen']
    df['resistance'] = df['resistance'] * df['nonGreen']
    df = df.drop(columns=['costDist','nonGreen'])
    df = df.astype({'y':'int32','x': 'int32'})
    return df

@timer
def generateGraphFromDF(df,show=False):
    G = nx.MultiGraph()
    nRows = df.y.max()+1
    nCols = df.x.max()+1
    nodesList = []
    for index,row in df.iterrows():
        attrs = {'x':int(row.x), 'y':int(row.y), "resistance":row.resistance,"cost":row.cost}
        nodesList.append(index)
        G.add_node(index, **attrs)
    
    positions = {}
    n = 0
    for y_cor in range(nRows):
        for x_cor in range(nCols):
            positions[nodesList[n]] = (x_cor,y_cor)
            n += 1
            
    neighbors = {}
    for node in nodesList:
        rightNode = None
        uprightNode = None
        bottomrightNode = None
        leftNode = None
        upleftNode = None
        bottomleftNode = None
        bottomNode = None
        upNode = None
        
        (x_cor,y_cor) = positions[node]
        if x_cor != nCols-1:
            rightNode = node+1
        if x_cor != nCols-1 and y_cor < nRows-1:
            uprightNode = node+nCols+1
        if x_cor != 0:
            leftNode = node-1
        if x_cor != 0 and y_cor < nRows-1:
            upleftNode = node+nCols-1
        if x_cor != 0 and y_cor != 0:
            bottomleftNode = node-nCols-1
        if y_cor > 0:
            bottomNode = node-nCols
        if y_cor < nRows-1:
            upNode = node + nCols
        if x_cor != nCols-1 and y_cor != 0:
            bottomrightNode = node-nCols+1
        neighbors[node] = (leftNode,upleftNode,upNode,uprightNode,rightNode,bottomrightNode,bottomNode,bottomleftNode)    
        
    for node,neighborNodes in neighbors.items():
        for neighbor in neighborNodes:
            if neighbor != None:
                restDist = math.sqrt((G.nodes[node]['x']-G.nodes[neighbor]['x'])**2+(G.nodes[node]['y']-G.nodes[neighbor]['y'])**2)
                restPerUnitNeighbor = G.nodes[neighbor]['resistance']/restDist
                restPerUnitNode =  G.nodes[node]['resistance']/restDist
                G.add_edge(node,neighbor, resistance= G.nodes[neighbor]['resistance'], cost = G.nodes[neighbor]['cost'], resistDist = restDist, resistPerUnit = restPerUnitNeighbor)
                G.add_edge(neighbor,node, resistance= G.nodes[node]['resistance'], cost = G.nodes[node]['cost'], resistDist = restDist, resistPerUnit = restPerUnitNode)
    if show:
        nx.draw(G, pos = positions, with_labels=True,node_size = 1000, font_size = 20)
    return G,positions,neighbors 

@timer
def generateImgFromDF(df, originalImage,title,show):
    colourImg = keras.preprocessing.image.load_img("../sampleImage/"+originalImage)
    colourPixels = keras.preprocessing.image.img_to_array(colourImg)
    rgbDF = df.sort_values(by=['y','x'])[["red","green","blue"]]
    h, w = colourImg.size
    newsize = (h,w)
    
    cArray = np.array(rgbDF).reshape(colourPixels.shape)
    newImage = keras.preprocessing.image.array_to_img(cArray)
    if show == True:
        plt.figure(figsize=(20,20))
        plt.title(title)
        plt.imshow(newImage)
    return newImage

@timer
def createDuplicateDF(df):
    dupDF = df.copy()
    return dupDF

@timer
def generateRandomColors(n):
    rgbCol = []
    for col in sns.color_palette("husl", n).as_hex():
        rgbCol.append(ImageColor.getcolor(col, "RGB"))
    return rgbCol

@timer
def plotPath(df,originalImage,path,title, grey=True):
    print(f'plotting image from DF')
    ## plotting the paths
    dupDF = createDuplicateDF(df)
    rgbCol = generateRandomColors(n=len(path))
    ''' Uncomment for custom colors '''
    # rgbCol = []
    # for col in ['#055EF9','#F41A1A','#080001']:
    #     rgbCol.append(ImageColor.getcolor(col, "RGB"))
    ''' changing rgb values to display paths '''
    
    if grey==True:
        dupDF.red = 0.2989 * dupDF.red
        dupDF.green = 0.3 * dupDF.green
        dupDF.blue =  0.1140 * dupDF.blue
    for i in range(len(path)):
        for node in path[i]:
            dupDF.loc[node,['red','green','blue']] = list(rgbCol[i])
    newImg = generateImgFromDF(dupDF,originalImage,title,show = True)
    return

def is_overlap_exists(path,show=False):
    is_overlap = False
    for i in range(len(path)-1):
        for j in range(i+1,len(path)):
            path1 = path[i]
            path2 = path[j]
            overLapNodes = set(path1).intersection(path2)
            if len(overLapNodes) > 2:
                if show:
                    print(f'{i}-{j} intersecting nodes : {set(path1).intersection(path2)}')
                return True
            if show:
                print(f'{i}-{j} intersecting nodes : {set(path1).intersection(path2)}')
    return False


# @timer
def createSubGraph(G,alreadyIncludedNodes):
    if len(alreadyIncludedNodes) > 0:
        remainingNodes = G.nodes - alreadyIncludedNodes
        subG = G.__class__()
        subG.add_nodes_from((n,G.nodes[n]) for n in remainingNodes)
        if subG.is_multigraph():
            subG.add_edges_from((n, nbr, key, d)
            for n, nbrs in G.adj.items() if n in remainingNodes
            for nbr, keydict in nbrs.items() if nbr in remainingNodes
            for key, d in keydict.items())
        else:
            subG.add_edges_from((n, nbr, d)
                for n, nbrs in G.adj.items() if n in remainingNodes
                for nbr, d in nbrs.items() if nbr in remainingNodes)
        subG.graph.update(G.graph)
        return subG
    else:
        return G
    
def calCostResistance(G,pathList):
    cost = 0
    resistance = 0
    for path in pathList:
        for node in path:
            resistance += G.nodes[node]['resistance']
            cost += G.nodes[node]['cost']
    return cost,resistance