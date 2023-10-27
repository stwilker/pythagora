# Citation
Pythagora: A Python Package for Modeling the Impact of Social Networks in and Around Market Spaces on Market Outcomes

Developed by Sarah T. Wilker (Oberlin College / swilker@oberlin.edu) and Annie K. Lamar (Stanford University / kalamar@stanford.edu)

●	Suggested Citation (APA): Wilker, S. T. and Lamar, A. K. Pythagora. Version 1. Source code. Web address. 
●	Suggested Citation (MLA): Wilker, Sarah T. and Lamar, Annie K. Pythagora. Version 1. Source code. Web address. 
●	Suggested Citation (Chicago): Wilker, S. T. and Lamar, A. K. Pythagora. Version 1. Source code. Web address. 
●	Zotero download link  [I think this can’t be made until the base is published]

#Project Description
Pythagora is a code repository for modeling the impact of select types of social networks on production and consumption outcomes. Specifically, pythagora tests how individuals in small-world social networks and scale-free social networks (as well as control versions of these networks) buy and sell new types of pottery based on interactions within their social networks. Agents in pythagora have complex social lives: they belong to communities and are connected in social networks both inside and outside those communities. The purpose of this multidimensional social landscape is to test the impact of different types of social relationships on what individual agents buy and sell, and how these individual transactions build over time to create long-term production and consumption trends. 

While pythagora was designed to test popularity changes in pottery styles in the ancient Mediterranean world, it can be used to test popularity changes for any style of object (in an “assemblage” during any time period.  

#Installation
To run pythagora, first install the [generate] file. This file includes all methods needed to generate an initial market environment. Using these methods, you can generate an initial list of agents, including both buyers and sellers, add these agents to the market space, place the agents into communities, and establish an “assemblage” that will be bought and sold in the market. Pythagora does not require that you install any external packages, as all necessary external packages are included in the applicable py files. 

# Quick Start: Small-World Simulation
The small-world simulation contains all the methods you will use to model how consumption practices change among communities of buyers  as they move in and out of being in a small-world network. In practice, this means that buyers purchasing pots go from being minimally connected (long path lengths and high clustering for individual communities) to being maximally connected (short path lengths and low clustering for individual communities). To run the small-world simulation, you will first need to install the [generate] file. This file includes all methods needed to generate an initial market environment, within which the small-world simulation will take place. Once you have downloaded the [generate] file, install the [experiments] file,  which contains all necessary external and internal support packages for the small-world experiment. Once in the [experiments] file, select the small-world experiment. 

# Quick Start: Scale-Free Simulation
The scale-free simulation contains all the methods you will use to model how consumption practices change among communities of buyers  as they join a scale-free social network (i.e., a network that grows through preferential attachment) and this network determines their purchasing behavior in the market space. To run the scale-free simulation, you will first need to install the [generate] file. This file includes all methods needed to generate an initial market environment, within which the scale-free simulation will take place. Once you have downloaded the [generate] file, install the [experiments] file,  which contains all necessary external and internal support packages for the scale-free experiment. Once in the [experiments] file, select the scale-free experiment. 

