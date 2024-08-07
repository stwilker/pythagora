
# Pythagora: A Python Package for Modeling the Impact of Social Networks in and Around Market Spaces on Market Outcomes
Developed by Sarah T. Wilker & Annie K. Lamar 

## Citation

Please cite the Github repository for this project as follows:

Wilker, S.T. and Lamar, A.K. _Pythagora_. Version 1.0.0. github.com/stwilker/pythagora.

## Author Contributions


# Project Description
_Pythagora_ is a code repository for modeling the impact of select types of social networks on production and consumption outcomes. Specifically, pythagora tests how individuals in small-world social networks and scale-free social networks (as well as control versions of these networks) buy and sell new types of pottery based on interactions within their social networks. Agents in pythagora have complex social lives: they belong to communities and are connected in social networks both inside and outside those communities. The purpose of this multidimensional social landscape is to test the impact of different types of social relationships on what individual agents buy and sell, and how these individual transactions build over time to create long-term production and consumption trends. 

While _Pythagora_ was designed to test popularity changes in pottery styles in the ancient Mediterranean world, it 
can be used to test popularity changes for any style of object in an “assemblage” during any time period.  

# Installation & Dependencies

To install _Pythagora_, you can use pip:

`pip install pythagora`

_Pythagora_ also requires NetworkX (3.2), which can be installed by running this command:

`pip install networkx`

# Quick Start: Small-World Simulation
The small-world simulation contains all the methods you will use to model how consumption practices change among 
communities of buyers  as they move in and out of being in a small-world network. 
In practice, this means that buyers purchasing pots go from being minimally connected 
(long path lengths and high clustering for individual communities) to being maximally connected 
(short path lengths and low clustering for individual communities). The `generate.py` file includes all methods 
needed to generate an initial market environment, within which the small-world simulation will take place. 
The `experiments.py` file contains all necessary external and internal support packages for the 
small-world experiment. Here is an example of how to run a small word simulation:

`experiments.small_world_simulation (number_of_buyers=50, minimum_number_of_communities=3, minimum_community_fill=3, assemblage=['Pot1', 'Pot2', 'Pot3', Pot4'], number_of_epochs=800, upper_threshold=.66, lower_threshold=.33, death_threshold=0.5, results_directory='results/', probability_of_rewire=0.5, community_start_structure="dense", verbose=True)`

All numerical values in the above quickstart are softcoded. Replace the numbers, the assemblage values, and the name of your experiment run to best fit your needs. The community structure selected in this quickstart is "dense", but you may also select "lattice", which creates a minimally connected small-world network at the outset of the experiment run. The results of the experiment will be placed in the directory indicated by the `results_directory` parameter.

# Quick Start: Scale-Free Simulation
The scale-free simulation contains all the methods you will use to model how consumption practices change among communities of buyers  as they join a scale-free social network (i.e., a network that grows through preferential attachment) and this network determines their purchasing behavior in the market space. To run the scale-free simulation, you will first need to install the [generate] file. This file includes all methods needed to generate an initial market environment, within which the scale-free simulation will take place. Once you have downloaded the [generate] file, install the [experiments] file,  which contains all necessary external and internal support packages for the scale-free experiment. Once in the [experiments] file, select the scale-free experiment. To quickly run a scale-free simulation, use the following: 

`experiments.scale_free_simulation(number_of_buyers=50, </br> minimum_number_of_communities=5, minimum_community_fill=3, assemblage=['Pot1', 'Pot2', 'Pot3', Pot4'], number_of_epochs=800, upper_threshold=.66, lower_threshold=.33, death_threshold=0.5, results_directory='results/', initial_set_size=15, set_size=5, community_bonus=1, verbose=True)`

All numerical values in the above quickstart are softcoded. Replace the numbers, the assemblage values, and the name of your experiment run to best fit your needs. The community bonus in this experiment is set at 1, but you can change the community bonus to see how agents' choices change when they give more weight to their own community members. The results of the experiment will be placed in the directory indicated by the `results_directory` parameter.

# Quick Start: Controls/Random Simulations

To run _Pythagora_, first install the [generate] file. This file includes all methods needed to generate an initial 
market environment. Using these methods, you can generate an initial list of agents, including both buyers and sellers, add these agents to the market space, place the agents into communities, and establish an “assemblage” that will be bought and sold in the market. Pythagora does not require that you install any external packages, as all necessary external packages are included in the applicable py files. To quickly run a small-world control simulation, use the following: 

`experiments.small_world_control(number_of_buyers=50, minimum_number_of_communities=3, minimum_community_fill=3, assemblage=['Pot1', 'Pot2', 'Pot3', Pot4'], number_of_epochs=800, upper_threshold=.66, lower_threshold=.33, death_threshold=0.5, results_directory='results/', rewire_prob=0.5, link_prob=0.5, verbose=True)`
