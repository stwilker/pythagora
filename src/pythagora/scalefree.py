"""
This module contains methods to initialize and compute metrics for a scale free simulation.
"""

import math
import random
from . import generate
from datetime import date
from datetime import datetime
import os
import operator
import csv
import networkx as nx


def remove_zeroes(dictionary):
    """
    Removes dictionary pairs with values equal to zero.
    @param dictionary: input dictionary object
    @return: dictionary with zero value pairs removed
    """
    items_to_remove = []
    for i in dictionary.keys():
        if dictionary[i] == 0:
            items_to_remove.append(i)
    for item in items_to_remove:
        dictionary.pop(item)
    return dictionary


def get_normalization_factor(dictionary):
    """
    Computes the normalization factor of the dictionary's values.
    @param dictionary: input dictionary object
    @return: normalization factor of the dictionary's values
    """
    dictionary = remove_zeroes(dictionary)
    return 1.0 / math.fsum(dictionary.values())


def safe_normalize(dictionary):
    """
    Normalizes values in dictionary.
    @param dictionary: dictionary with non-normalized values
    @return: dictionary with normalized values
    """
    normalization_factor = get_normalization_factor(dictionary)
    for key in dictionary:
        dictionary[key] = dictionary[key] * normalization_factor
    key_for_max = max(dictionary.items(), key=operator.itemgetter(1))[0]
    diff = 1.0 - math.fsum(dictionary.values())
    dictionary[key_for_max] += diff
    return dictionary


def build_scale_free_network(set_of_nodes, G, community_bonus, logger, epoch, all_buyers_in_market):
    """
    Organizes buyers and communities into a scale free network structure.
    @param set_of_nodes: random subset of buyers
    @param G: graph representing initial market state
    @param community_bonus: bonus to purchase probability from being in the same community
    @param logger: logging object
    @param epoch: current epoch (for logger)
    @param all_buyers_in_market: list of all buyers in market
    @return: graph representing initial market state in scale free structure
    """
    # make a stack with our buyers
    stack = set_of_nodes
    timestep = 0
    while len(stack) != 0:
        current_node = stack.pop()
        t = len(G.nodes)
        # assign probabilities to each node
        probs = {}  # (nodes, probabilities)
        if t != 0:
            for node in G.nodes():
                k_i = G.degree(node)
                if node.community == current_node.community:
                    probs[node] = (k_i / (2 * t - 1)) * community_bonus
                else:
                    probs[node] = (k_i / (2 * t - 1))
            # probs[current_node] = 1 / (2*t - 1)
            normalized_probs = safe_normalize(probs)
            population = list(normalized_probs.keys())
            w = []
            for p in normalized_probs.keys():
                w.append(normalized_probs[p])
            selected_node = random.choices(population, weights=w)
            timestep += 1
        # add our node to the graph space
        # optional: move this line up to allow self loops
        G.add_node(current_node)
        if t == 0:
            G.add_edge(current_node, current_node)
        if t != 0:
            G.add_edge(current_node, selected_node[0])
        logger.log(G, epoch, timestep, 0, all_buyers_in_market)
    return G


def make_sf_graph_info_file(num_buyers,
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
    Creates an information file (.csv) for this scale free experiment.

    @param num_buyers: number of buyers in market
    @param min_num_communities: minimum number of communities
    @param min_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in market
    @param epochs: number of market iterations
    @param upper_thresh: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_thresh: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_thresh: percentage at which a pot is removed from the market
    @param results_dir: directory path in which to store the file
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


def initialize_scale_free(number_of_buyers,
                          minimum_number_of_communities,
                          minimum_community_fill,
                          assemblage,
                          initial_set_size,
                          community_bonus,
                          logger
                          ):
    """
    Initializes a scale free network world.

    @param number_of_buyers: number of buyers in marketspace
    @param minimum_number_of_communities: minimum number of communities to which buyers belong
    @param minimum_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in marketspace
    @param initial_set_size: number of buyers in market at initialization
    @param community_bonus: degree to which community affiliation impacts purchase intention
    @param logger: logging object
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
    G = build_scale_free_network(set_of_nodes, G, community_bonus, logger, 0, buyers_in_market)
    return G, buyers_in_market
