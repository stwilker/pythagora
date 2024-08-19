"""The experiments module is the primary module with which users will interact. From this module, you can run every
kind of experiment and adjust every parameter.

Simulation/Experiment Types
===========================

This module implements two main network protocols: small-world and scale-free. For both types, we also implement a
control model.

Small-World Network
-------------------

The small-world experiment tests how consumption practices among individual communities change as they become more
interconnected. When the small-world experiment starts, buyers are very well-connected to their individual community
(high clustering) and very disconnected from those outside of their community (long average path length). As the
experiment runs, random “rewired” connections link agents in different communities, shortening the distance between
individual communities and reducing the amount of clustering in the network. Over time, different communities become
so well-connected (short average path length) that there is no significant clustering within individual communities.
The network becomes a small-network for a limited time between these two extremes, specifically when the
network has relatively high clustering within individual communities and relatively short path lengths between agents
across communities. The Small-world experiment can be run with different start structures (details in experiment
options below).

Scale-Free Network
------------------

The scale-free experiment tests how consumption practices change among communities of buyers change as they join a
scale-free social network. In scale-free networks, agents are added to the social network over time (network growth).
These additional agents connect to those already in the network through the process of preferential attachment,
which means that agents that have more social connections already will gain more connections over time than those
with fewer starting connections. A novel feature of this package is the “community bonus” parameter, which allows you
to test how preexisting community affiliation impacts purchasing preferences. Buyers entering the simulation are
assigned an initial community designation, and when the community bonus is set at greater than 1.0, buyers are
incentivized to connect and compare with those who share their existing community designation. When the community
bonus is set at less than 1.0, buyers are incentivized to connect and compare with those who do not share their
community affiliation. When simulations are run without a community bonus, buyers are motivated to connect with the
most popular individual in their network (preferential attachment) regardless of personal closeness.

Experimental Controls
---------------------

To create a control (or comparison) to a small-world model, a random network is constructed with all of the buyers in
the market. Agents are initially connected to four random agents regardless of designated community affiliation,
rather than being connected within their existing community groups as is the case in the small-world experiment.
Following this set up, connections are formed and rewired in the same way as those in the small-world experiment.

The scale-free control tests how social networks between buyers change when a network grows randomly over time. The
fundamental difference between a scale-free network and a random network is the presence of preferential attachment,
which means that a random growth network when compared to the scale-free network can specifically examine the impact
of preferential attachment on purchasing preferences. The scale-free control network can be run with or without the
“community bonus” parameter, which means it can also test the impact of preexisting community designation on social
connection and consumer behavior.

Changeable Experiment Parameters
================================

Number of Buyers
----------------
B{Parameter:} C{number_of_buyers}

How many buyers do you want in your market simulation?

Minimum Number of Communities
-----------------------------
B{Parameter:} C{minimum_number_of_communities}

What is the minimum number of buyer communities in the market simulation?

Minimum Community Fill
----------------------
B{Parameter:} C{minimum_community_fill}

What is the minimum number of buyers that must be in a community for the community to exist?

Assemblage
----------
B{Parameter:} C{assemblage}

The list of items for sale in the marketplace. We use the word `assemblage` because this software was developed
for analysis of ancient ceramics markets; the algorithms work the same for any list of items and are not field specific.

Number of Epochs
----------------
B{Parameter:} C{number_of_epochs}

Number of market or purchasing iterations to run in the simulation. This is how many times the buyers will purchase
items from the market.

Upper Threshold
---------------
B{Parameter:} C{upper_threshold}

The upper threshold is the percentage of buyers that must own a particular item to change a buyer's purchasing
intention to the dominant item. For a given hypothetical buyer, if the percentage of their social connections
(graph neighbors) purchasing the same item is greater than or equal to their upper threshold, they change their
intention to purchase that item. In short: How popular does a particular item need to be to begin influencing others'
purchase decisions (and be worth the cost and risk associated with changing one's behavior)?

Lower Threshold
---------------
B{Parameter:} C{lower_threshold}

The lower threshold is the maximum percentage of buyers that may own a particular item to change a buyer's purchasing
intention to a random item. For a given hypothetical buyer, if the percentage of their social connections (graph
neighbors) purchasing any possible item is less than the lower threshold, the buyer changes their intention to
purchase a random item. In short: How unpopular does a particular item need to be to cause a buyer to purchase a new
item at random (retaining no loyalty to the item they currently own)?

Death Threshold
---------------
B{Parameter:} C{death_threshold}

The death threshold is the percentage at which a pot is removed from the market. If the demand for a pot (i.e. buyers
who purchased that pot) drops below the death threshold, then the pot is removed from the market. If a Seller was
selling this item, they are automatically assigned the most popular item.  In short: How unpopular does an item need
to be before it is removed from the market altogether?

Probability of Rewire (Small World Only)
----------------------------------------
B{Parameter:} C{probability_of_rewire}

In a small world experiment, this is the probability that a node will form new edges in an epoch.

Community Start Structure (Small World Only)
--------------------------------------------
B{Parameter:} C{community_start_structure}

In a small world experiment, this is the structure in which communities will be instantiated. The available options
are lattice or dense. The lattice is a ring lattice with each node connected to k=2 nearest neighbors. The dense
structure is a graph in which each node is connected to every other node.

Initial Set Size (Scale Free Only)
----------------------------------
B{Parameter:} C{initial_set_size}

In a scale free experiment, the initial set size defines the number of buyers who first enter the marketplace. These
buyers are the first to connect, compare, and purchase items.

Set Size (Scale Free Only)
--------------------------
B{Parameter:} C{set_size}

In a scale free experiment, the set size is the number of buyers added to the marketplace after the initial group.

Community Bonus (Scale Free Only)
---------------------------------
B{Parameter:} C{community_bonus}

Mathematically, the community bonus defines how much influence community affiliation has on buyer purchase intention.
A community bonus of less than 1 means that a buyer is less likely to purchase an item if a majority of their
community owns that item. A community bonus greater than 1 means that a buyer is more likely to purchase an item if a
majority of their community owns that item. Theoretically speaking, community bonuses model and test the influence of
established community affiliation on social connections and economic actions. All agents are sorted into community
groups during the start-up phase of the simulation. A positive (high value) community bonus causes agents to favor
new connections and item comparisons with individuals who share their preexisting community affiliation. A neutral
community bonus value (1.0) means that no community bonus exists, and social connection and item comparison occur
based solely on preferential attachment. A negative (low value) community bonus incentivizes agents to connect and
compare with individuals who do not share their preexisting community affiliation. The community bonus enhancement to
the scale free network protocol was developed by Sarah T. Wilker, PhD (2023). For more information, see: Wilker,
S. T. 2023. "The Social Life of Ancient Markets: Using Formal Network Approaches and Ceramic Data to Reconceptualize
Market Behavior in the Late Classical–Early Hellenistic (400–200 BCE) Southeast Aegean." PhD Dissertation,
Stanford University.

"""

from . import smallworld as sw
from . import scalefree as sf
from . import controls
from . import market
from . import generate
from . import logger
from datetime import timedelta
import time
import random


def small_world_simulation(number_of_buyers,
                           minimum_number_of_communities,
                           minimum_community_fill,
                           assemblage,
                           number_of_epochs,
                           upper_threshold,
                           lower_threshold,
                           death_threshold,
                           results_directory,
                           probability_of_rewire=0.5,
                           community_start_structure="dense",
                           verbose=True
                           ):
    """
    Run a small world simulation.

    @param number_of_buyers: number of buyers in marketspace
    @param minimum_number_of_communities: minimum number of communities to which buyers belong
    @param minimum_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param number_of_epochs: number of epochs (purchase cycles)
    @param upper_threshold: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_threshold: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_threshold: percentage at which an item is removed from the market
    @param results_directory: path to directory to store results files
    @param probability_of_rewire: probability that a node will form new edges in an epoch
    @param community_start_structure: structure in which communities will be instantiated
    @param verbose: if True, will print time log updates to screen
    """
    print("Initializing small world model...")
    small_world = sw.initialize_small_world(number_of_buyers,
                                            minimum_number_of_communities,
                                            minimum_community_fill,
                                            assemblage,
                                            community_start_structure
                                            )
    # Run first purchase cycle to assign every buyer an item
    small_world = market.buy_pots(small_world)

    print("Creating logging resources...")
    sw.make_small_world_graph_info_file(number_of_buyers,
                                        minimum_number_of_communities,
                                        minimum_community_fill,
                                        assemblage,
                                        number_of_epochs,
                                        upper_threshold,
                                        lower_threshold,
                                        death_threshold,
                                        results_directory,
                                        probability_of_rewire,
                                        community_start_structure)
    log = logger.Logger(results_directory, assemblage)
    log.log(small_world, 0, 0, 0, None)

    print("Beginning simulation...")
    start_time = start_time = time.monotonic()

    for epoch in range(1, number_of_epochs + 1):
        small_world = sw.small_world_rewire(small_world, probability_of_rewire, epoch, log)
        small_world = market.change_all_buyer_intentions(small_world, lower_threshold, upper_threshold, death_threshold)
        small_world = market.buy_pots(small_world)

        if verbose:
            end_time = time.monotonic()
            print("Epoch: " + str(epoch))
            print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))


def scale_free_simulation(number_of_buyers,
                          minimum_number_of_communities,
                          minimum_community_fill,
                          assemblage,
                          number_of_epochs,
                          upper_threshold,
                          lower_threshold,
                          death_threshold,
                          results_directory,
                          initial_set_size,
                          set_size,
                          community_bonus,
                          verbose=True):
    """
    Run a scale free simulation.

    @param number_of_buyers: number of buyers in marketspace
    @param minimum_number_of_communities: minimum number of communities to which buyers belong
    @param minimum_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param number_of_epochs: number of epochs (purchase cycles)
    @param upper_threshold: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_threshold: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_threshold: percentage at which an item is removed from the market
    @param results_directory: path to directory to store results files
    @param initial_set_size: number of buyers in market at initialization
    @param set_size: number of buyers added to market after initialization
    @param community_bonus: degree to which community affiliation impacts purchase intention
    @param verbose: if True, will print time log updates to screen
    """
    print("Creating logging resources...")
    log = logger.Logger(results_directory, assemblage, model_type="scale_free")
    sf.make_sf_graph_info_file(number_of_buyers,
                               minimum_number_of_communities,
                               minimum_community_fill,
                               assemblage,
                               number_of_epochs,
                               upper_threshold,
                               lower_threshold,
                               death_threshold,
                               results_directory,
                               community_bonus,
                               initial_set_size,
                               set_size)
    print("Initializing scale free model...")
    start_time = start_time = time.monotonic()
    scale_free, buyers = sf.initialize_scale_free(number_of_buyers,
                                                  minimum_number_of_communities,
                                                  minimum_community_fill,
                                                  assemblage,
                                                  initial_set_size,
                                                  community_bonus,
                                                  log)
    scale_free = market.buy_pots(scale_free)
    epoch = 1
    # while there's nodes not in the graph, add them in sets
    remaining_buyers = []
    for buyer in buyers:
        if buyer not in scale_free.nodes:
            remaining_buyers.append(buyer)
    last = False
    while not last:
        set_to_last = False
        next_node_set = []
        if len(remaining_buyers) < set_size or len(remaining_buyers) == set_size:
            for bu in remaining_buyers:
                next_node_set.append(bu)
            set_to_last = True
        else:
            next_node_set = random.sample(remaining_buyers, set_size)
        for b in next_node_set:
            remaining_buyers.remove(b)
        scale_free = sf.build_scale_free_network(next_node_set, scale_free, community_bonus, log, epoch, buyers)
        scale_free = market.change_all_buyer_intentions(scale_free,
                                                        lower_threshold,
                                                        upper_threshold,
                                                        death_threshold)
        scale_free = market.buy_pots(scale_free)
        if verbose:
            end_time = time.monotonic()
            print("Epoch: " + str(epoch))
            print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))
        epoch += 1
        if set_to_last:
            last = True
    if epoch < number_of_epochs + 1:
        for e in range(epoch, number_of_epochs + 1):
            scale_free = market.change_all_buyer_intentions(scale_free,
                                                            lower_threshold, upper_threshold, death_threshold)
            scale_free = market.buy_pots(scale_free)
            log.log(scale_free, e, 0, 0, buyers)
            if verbose:
                end_time = time.monotonic()
                print("Epoch: " + str(epoch))
                print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))
            epoch += 1


def control_simulation_small_world(number_of_buyers,
                                   minimum_number_of_communities,
                                   minimum_community_fill,
                                   assemblage,
                                   epochs,
                                   upper_threshold,
                                   lower_threshold,
                                   death_threshold,
                                   results_directory,
                                   rewire_prob,
                                   link_prob=0.5,
                                   verbose=True):
    """
    Run a control simulation using small world network protocol.

    @param number_of_buyers: number of buyers in marketspace
    @param minimum_number_of_communities: minimum number of communities to which buyers belong
    @param minimum_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param epochs: number of epochs (purchase cycles)
    @param upper_threshold: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_threshold: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_threshold: percentage at which an item is removed from the market
    @param results_directory: path to directory to store results files
    @param rewire_prob: probability that a node will form new edges in an epoch
    @param link_prob: probability any two nodes (buyers) will be linked in random graph initialization
    @param verbose: verbose: if True, will print time log updates to screen
    """
    print("Initializing control model using small world protocol...")
    my_group = generate.initialize_market_environment(number_of_buyers,
                                                      minimum_number_of_communities,
                                                      minimum_community_fill,
                                                      assemblage)
    graph = controls.make_random_graph(my_group, probability_of_link=link_prob)
    graph = market.buy_pots(graph)

    print("Creating logging resources...")
    sw.make_small_world_graph_info_file(number_of_buyers,
                                        minimum_number_of_communities,
                                        minimum_community_fill,
                                        assemblage,
                                        epochs,
                                        upper_threshold,
                                        lower_threshold,
                                        death_threshold,
                                        results_directory,
                                        rewire_prob,
                                        "random")

    log = logger.Logger(results_directory, assemblage)

    print("Beginning simulation...")
    start_time = start_time = time.monotonic()

    for epoch in range(epochs):
        graph = sw.small_world_rewire(graph, rewire_prob, epoch, log)
        graph = market.change_all_buyer_intentions(graph, lower_threshold, upper_threshold, death_threshold)
        graph = market.buy_pots(graph)

        if verbose:
            end_time = time.monotonic()
            print("Epoch: " + str(epoch))
            print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))


def control_simulation_scale_free(number_of_buyers,
                                  minimum_number_of_communities,
                                  minimum_community_fill,
                                  assemblage,
                                  number_of_epochs,
                                  upper_threshold,
                                  lower_threshold,
                                  death_threshold,
                                  results_directory,
                                  initial_set_size,
                                  set_size,
                                  community_bonus,
                                  verbose=True):
    """
    Run a control experiment using scale free network protocol.

    @param number_of_buyers: number of buyers in marketspace
    @param minimum_number_of_communities: minimum number of communities to which buyers belong
    @param minimum_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param number_of_epochs: number of epochs (purchase cycles)
    @param upper_threshold: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_threshold: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_threshold: percentage at which an item is removed from the market
    @param results_directory: path to directory to store results files
    @param initial_set_size: number of buyers in market at initialization
    @param set_size: number of buyers added to market after initialization
    @param community_bonus: degree to which community affiliation impacts purchase intention
    @param verbose: if True, will print time log updates to screen
    """
    print("Creating logging resources...")
    log = logger.Logger(results_directory, assemblage, model_type="scale_free")
    controls.make_sf_control_graph_info_file(number_of_buyers,
                                             minimum_number_of_communities,
                                             minimum_community_fill,
                                             assemblage,
                                             number_of_epochs,
                                             upper_threshold,
                                             lower_threshold,
                                             death_threshold,
                                             results_directory,
                                             community_bonus,
                                             initial_set_size,
                                             set_size)
    print("Initializing scale free control model...")
    start_time = start_time = time.monotonic()
    scale_free, buyers = controls.initialize_scale_free_control(number_of_buyers,
                                                                minimum_number_of_communities,
                                                                minimum_community_fill,
                                                                assemblage,
                                                                initial_set_size,
                                                                community_bonus,
                                                                log)
    scale_free = market.buy_pots(scale_free)
    epoch = 1

    # while there's nodes not in the graph, add them in sets
    remaining_buyers = []
    for buyer in buyers:
        if buyer not in scale_free.nodes:
            remaining_buyers.append(buyer)
    while len(remaining_buyers) != 0:
        if len(remaining_buyers) < set_size:
            next_node_set = remaining_buyers
        else:
            next_node_set = random.sample(remaining_buyers, set_size)
        for b in next_node_set:
            remaining_buyers.remove(b)
        scale_free = controls.build_scale_free_control_network(next_node_set, scale_free, community_bonus,
                                                               log, epoch, buyers)
        scale_free = market.change_all_buyer_intentions(scale_free, lower_threshold, upper_threshold, death_threshold)
        scale_free = market.buy_pots(scale_free)
        if verbose:
            end_time = time.monotonic()
            print("Epoch: " + str(epoch))
            print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))
        epoch += 1

    # if all buyers have been added, simulate remaining epochs
    if epoch < number_of_epochs + 1:
        for e in range(epoch, number_of_epochs + 1):
            scale_free = market.change_all_buyer_intentions(scale_free,
                                                            lower_threshold, upper_threshold, death_threshold)
            scale_free = market.buy_pots(scale_free)
            log.log(scale_free, e, 0, 0, buyers)
            if verbose:
                end_time = time.monotonic()
                print("Epoch: " + str(epoch))
                print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))
            epoch += 1
