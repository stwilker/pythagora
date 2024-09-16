"""This module implements support methods for the control experiments for both the small world and scale free network
protocols. This includes initialization methods and information file generation. This file is the equivalent of
`scalefree.py` and `smallworld.py` for control simulations."""

import random
import networkx as nx
from . import generate
import os
from datetime import date
from datetime import datetime
import csv
from . import scalefree as sf


def make_sf_control_graph_info_file(num_buyers,
                                    min_num_communities,
                                    min_community_fill,
                                    assemblage,
                                    epochs,
                                    upper_thresh,
                                    lower_thresh,
                                    death_thresh,
                                    results_dir,
                                    community_bonus,
                                    initial_set_size,
                                    set_size):
    """
    Creates an information file (.csv) for this control experiment.

    @param num_buyers: number of buyers in marketspace
    @param min_num_communities: minimum number of communities to which buyers belong
    @param min_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param epochs: number of epochs (purchase cycles)
    @param upper_thresh: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_thresh: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_thresh: percentage at which an item is removed from the market
    @param results_dir: path to directory to store results files
    @param initial_set_size: number of buyers in market at initialization
    @param set_size: number of buyers added to market after initialization
    @param community_bonus: degree to which community affiliation impacts purchase intention
    """
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    info_filename = results_dir + "/graph_info.csv"
    info_log = open(info_filename, "w+")
    writer = csv.writer(info_log)
    fields = ["experiment", "date", "time", "number of buyers", "initial_set_size",
              "set size", "min num communities", "min community fill",
              "assemblage", "total epochs", "upper threshold",
              "lower threshold", "death threshold", "community bonus"]
    writer.writerow(fields)
    info = ["scale free", str(date.today()), str((datetime.now()).strftime("%H:%M:%S")), str(num_buyers),
            str(initial_set_size), str(set_size), str(min_num_communities), str(min_community_fill),
            assemblage, str(epochs), str(upper_thresh), str(lower_thresh),
            str(death_thresh), str(community_bonus)]
    writer.writerow(info)


def build_scale_free_control_network(set_of_nodes, G, community_bonus,
                                     logger, epoch, all_buyers_in_market):
    """
    Constructs a control network for a scale-free network simulation.

    @param set_of_nodes: random subset of buyers
    @param G: graph representing initial market state
    @param community_bonus: bonus to purchase probability from being in the same community
    @param logger: logging object
    @param epoch: current epoch (for logger)
    @param all_buyers_in_market: list of all buyers in market
    @return: graph representing initial market state in scale free structure
    """
    # make a stack with our buyers
    while len(set_of_nodes) != 0:
        current_node = set_of_nodes.pop()
        # add our node to the graph space
        t = len(G.nodes)
        # move add_node line above t assignment to allow self loops
        G.add_node(current_node)
        # assign probabilities to each node
        probs = {}  # (nodes, probabilities)
        if t != 0:
            for node in G.nodes():
                if node.community == current_node.community:
                    probs[node] = 1 * community_bonus
                else:
                    probs[node] = 1
            normalized_probs = sf.safe_normalize(probs)
            population = list(normalized_probs.keys())
            w = []
            for p in normalized_probs.keys():
                w.append(normalized_probs[p])
            selected_node = random.choices(population, weights=w)
            G.add_edge(current_node, selected_node[0])
    logger.log(G, epoch, 0, 0, all_buyers_in_market)
    return G


def initialize_scale_free_control(number_of_buyers,
                                  minimum_number_of_communities,
                                  minimum_community_fill,
                                  assemblage,
                                  initial_set_size,
                                  community_bonus,
                                  logger):
    """

    @param number_of_buyers: number of buyers in marketspace
    @param minimum_number_of_communities: minimum number of communities to which buyers belong
    @param minimum_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param initial_set_size: number of buyers in market at initialization
    @param community_bonus: degree to which community affiliation impacts purchase intention
    @param logger: logging object
    @return: Graph, new set of buyers currently in the market
    """
    my_group = generate.initialize_market_environment(number_of_buyers,
                                                      minimum_number_of_communities,
                                                      minimum_community_fill,
                                                      assemblage)
    G = nx.Graph()
    buyers_in_market = my_group.get_all_buyers_in_community_set()
    for b in buyers_in_market:
        b.purchased_pot = b.intention
    set_of_nodes = random.sample(buyers_in_market, initial_set_size)
    G = build_scale_free_control_network(set_of_nodes, G, community_bonus, logger, 0, buyers_in_market)
    return G, buyers_in_market


def make_random_graph(group_of_communities, probability_of_link=0.5):
    """
    Construct a random graph.

    @param group_of_communities: a CommunitySet object
    @param probability_of_link: probability that any two nodes (buyers) have an edge
    @return: graph representing randomized market state
    """
    buyers_in_market = group_of_communities.get_all_buyers_in_community_set()
    G = nx.Graph()
    for buyer in buyers_in_market:
        G.add_node(buyer)
    list_of_nodes = list(G.nodes())
    stack = [(node1, node2) for spot_in_list, node1 in enumerate(list_of_nodes) for node2 in
             list_of_nodes[spot_in_list + 1:]]
    random.shuffle(stack)
    # start with N isolated nodes
    # select node pair
    # generate a random number [0, 1)
    # connect based on prob
    # repeat for N(N-1)/2 node pairs.
    while len(stack) != 0:
        current_pair = stack.pop()
        if random.random() < probability_of_link:
            node1 = current_pair[0]
            node2 = current_pair[1]
            G.add_edge(node1, node2)
    return G
