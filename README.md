# Network Design for Multispecies Conservation
- Goal: Find Optimal Paths connecting different nodes from an image meeting the connectivity requirements
- Processes: Mixed-integer Linear programming, Dijkstra Algorithm and Steiner Paths (traced on Dijkstra's Path)
	- Evaluated on an image replicating WildLife Conversation

## Code and Resources Used
Python Version: 3.7\
Packages: pandas, numpy, tensorflow, matplotlib, networkx, gurobipy, seaborn, PIL\
For Web Framework Requirements: ```pip install -r requirements.txt```\

## Inspiration:
- Robust Network Design for Multispecies Conservation
	- Written by:
		-	Ronan Le Bras, Bistra Dilkina, Yexiang Xue, and Carla P. Gomes from Cornell University
		-	Kevin S. McKelvey and Michael K. Schwartz from the US Forest Service
		-	Claire A. Montgomery from Oregon State University
		- 	Le Bras, R., Dilkina, B., Xue, Y., Gomes, C., McKelvey, K., Schwartz, M., & Montgomery, C. (2013). . In AAAI Conference on Artificial Intelligence. Retrieved from https://www.aaai.org/ocs/index.php/AAAI/AAAI13/paper/view/6497/6855

## How To:
- Prerequisite : Gurobi Licence (https://www.gurobi.com/downloads/gurobi-optimizer-eula/)
- Create conda env (optional): Open command prompt and go to required directory and enter command ```conda create --prefix ./env_name python=3.7```
  - Activate conda env: ```conda activate env_name```
- Clone git repo (git bash): ```git init``` ```git clone repo_url```
- In conda env (command prompt):
  - Install packages : ```pip install -r requirements.txt```
- To run:
  - ```python main.py```

## Code
	- /sampleImage/: Contain the original image used for tracing paths
	- /generator.py: Contains code for generating graph from image, calculating resistance & cost based on 
					 the RGB colors, generate image from dataframe,..
	- /milp.py: Contains code for implementation of Mixed Integer Linear Programming using Gurobipy.
	- /dijkstra.py: Contains code for implementation of Dijkstra's Algorithm to trace paths
	- /steiner.py: Contains code for implementation of Steiner Algorithm to trace paths
	- /main.py : Contains main code to read the image, set the start, end and reserve nodes and commands to
				 execute the algorithms to trace paths

## Problem Statement 
	![Alt text](/sampleImage/dense_heat_map.png?raw=true "Original Image") \
	Considering the image as forest/conservative area to find 2 non-overlapping paths that \
	connects all the four reserves with Least Resistance/Least Cost as below.
	![Alt text](/outputImages/Original_Image_indicating_Paths.png?raw=true " ") \

## Assumptions	
	- In the image, Green shows the least resistance paths.
	- Red (except the reserve nodes highlighted) are high resistance areas (considered as
		human habitant areas or volcanic locations etc.)
	- Blue is considered as mountainous or large water source areas and therefore high 
		resistance areas for terrestrial animals.
	- Wildlife migration paths involve connecting the reserve nodes.

## Approach
	- Reads the original image from sampleImage/ directory
	- Creates a dataframe with columns x-position, y-position, red, green, blue from the image. 
	- Resistance of each pixel is calculated based on the RGB values. 
	- More greenish pixel is considered as least resistance path for the wildlife to navigate.
	- Cost of each pixel is derived from the Normal Distribution and multiplied with Resistance values
		to simulate near approximation of the costs.
	- Start, End and reserve nodes are set
	- terminalNodesConnect : is a tuple ( startnode, endnode, no_of_alternate_paths)
	- Calls milp.py, dijkstra.py and steiner.py to trace the paths.
	- The output images are displayed using Grey scale to view the traced paths clearly.
	
### Notes:
	- Steiner Paths are re-traced using Dijkstra's path as the minimum spanning path.

## Output:
	- Each model traces different paths for Least Resistance and Least Cost paths, connecting all the nodes 
		with two alternative paths (as defined in terminalNodesConnect list).
	- Mixed Integer Linear Programming model resulted in the least cost effective and least resistant paths 
		when compared to Dijkstra's and Steiner paths.
	![Alt text](/outputImages/Gurobi_LeastResistancePath.png?raw=true "Gurobi_LeastResistancePath")
	![Alt text](/outputImages/Gurobi_LeastCostPath.png?raw=true "Gurobi_LeastCostPath")
	![Alt text](/outputImages/Dijkstra_LeastResistancePath.png?raw=true "Dijkstra_LeastResistancePath")
	![Alt text](/outputImages/Dijkstra_LeastCostPath.png?raw=true "Dijkstra_LeastCostPath")
	![Alt text](/outputImages/Steiner_LeastResistancePath.png?raw=true "Steiner_LeastResistancePath")
	![Alt text](/outputImages/Steiner_LeastCostPath.png?raw=true "Steiner_LeastCostPath")
	
## Reference: 
	- Le Bras, R., Dilkina, B., Xue, Y., Gomes, C., McKelvey, K., Schwartz, M., & Montgomery, C. (2013). . 
	In AAAI Conference on Artificial Intelligence. Retrieved from https://www.aaai.org/ocs/index.php/AAAI/AAAI13/paper/view/6497/6855
	- Dilkina, B. (2016, November 8). Network Design Approaches to Multi-Species Biodiversity Conservation [Conference Presentation]. 
	Computational Sustainability Virtual Seminar Series #4. Retrieved from https://www.youtube.com/watch?v=O4XCocHZ8Bc
	- Steiner Tree problem. GeeksforGeeks. (2016, December 12). Retrieved May 3, 2022, from https://www.geeksforgeeks.org/steiner-tree/ 
	- https://www.tensorflow.org
