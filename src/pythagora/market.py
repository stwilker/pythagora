"""
This module contains methods that support the purchasing and removal of items in the market.
"""

import collections
import random


def get_neighbors_pots(node, graph):
    """
    Returns a list of items owned by a buyer's neighbors.
    @param node: target buyer
    @param graph: graph containing buyer representing current market state
    @return: a list of items owned by a buyer's neighbors
    """
    neighbor_pots_list = []
    nearest_neighbors = graph.neighbors(node)
    for buyer in list(nearest_neighbors):
        neighbor_pots_list.append(buyer.purchased_pot)
        for second_degree in graph.neighbors(buyer):
            if second_degree != node:
                neighbor_pots_list.append(second_degree.purchased_pot)
    return neighbor_pots_list


def get_most_popular_pot(pots_list):
    """
    Returns the most popular item in the market (based on buyers' purchases).
    @param pots_list: list of pots owned by buyers in the market
    @return: the most popular item in the pots_list
    """
    current_max = 0
    popular_pot = pots_list[0]
    for pot in pots_list:
        num_pots = pots_list.count(pot)
        if num_pots > current_max:
            current_max = num_pots
            popular_pot = pot
    return popular_pot


def check_for_pot_death(G, death_threshold):
    """
    Checks if any items are to be removed from the market.
    @param G: graph representing current market state
    @param death_threshold: percentage at which an item is removed from the market
    @return: list of remaining items in market
    """
    all_pots = collections.defaultdict(int)
    for buyer in G:
        all_pots[buyer.purchased_pot] += 1
    remaining_pots = []
    for pot in all_pots.keys():
        if all_pots.get(pot) / len(G.nodes) >= death_threshold:
            remaining_pots.append(pot)
    return remaining_pots


def change_all_buyer_intentions(G, upper_threshold, lower_threshold, death_threshold):
    """

    @param G: graph representing current market state
    @param upper_threshold: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_threshold: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_threshold: percentage at which an item is removed from the market
    @return: graph representing market state with changed buyer intentions
    """
    remaining_pots = check_for_pot_death(G, death_threshold)
    neighbors_pots = []
    for buyer in G:
        neighbors_pots = get_neighbors_pots(buyer, G)
        num_same_pots = 0
        for pot in neighbors_pots:
            if pot == buyer.purchased_pot:
                num_same_pots = num_same_pots + 1
        if len(neighbors_pots) != 0:
            percent = num_same_pots / len(neighbors_pots)
            # Case 1: Percent of neighbor's pots >= upper threshold
            if percent >= upper_threshold:
                buyer.intention = get_most_popular_pot(neighbors_pots)
            # Case 2: Percent of neighbor's pots < upper threshold AND > lower threshold
            # Case 3: Percent of neighbor's pots <= lower threshold
            elif percent <= lower_threshold:
                buyer.intention = random.choice(remaining_pots)
    return G


def buy_pots(G):
    """
    Every buyer purchases their intended item.
    @param G: graph representing current market state
    @return: graph representing the market state with purchased items
    """
    for buyer in G:
        buyer.purchased_pot = buyer.intention
    return G
