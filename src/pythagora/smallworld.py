"""
This module contains methods to initialize and compute metrics for a small world simulation.
"""

import networkx as nx
import generate
import math
from datetime import date
from datetime import datetime
import random
import os
import csv


def make_lattice_from_nodes(G):
    """
    Construct a lattice structure out of existing nodes.
    @param G: NetworkX graph object containing nodes
    @return: restructured NetworkX graph object
    """

    # Step 1: Create a ring structure
    count = 0
    node1 = {}
    node2 = {}
    first_node = {}
    for node in G.nodes:
        if count == 0:
            node1 = node
            first_node = node
            count = count + 1
        else:
            node2 = node
            G.add_edge(node1, node2)
            node1 = node2
            count = count + 1
    G.add_edge(first_node, node2)

    # Step 2: Fill in the lattice
    edges_to_add = {}
    for node in G.nodes:
        neighbors = G.neighbors(node)
        for n in neighbors:
            next_neighbors = G.neighbors(n)
            for m in next_neighbors:
                if m != node:
                    if node in edges_to_add.keys():
                        edges_to_add[node].append(m)
                    else:
                        edges_to_add[node] = [m]
    for key in edges_to_add.keys():
        for value in edges_to_add[key]:
            if (key, value) not in G.edges:
                G.add_edge(key, value)
    return G


def form_community_lattice(community):
    """
    Instantiate a Graph and construct a lattice containing all community members.
    @param community: community containing buyers/members
    @return: NetworkX Graph object in lattice structure
    """
    G = nx.Graph()
    for buyer in community.list_of_buyers:
        G.add_node(buyer)
    return make_lattice_from_nodes(G)


def form_community_lattices(community_set):
    """
    Instantiate a graph and add a group of communities in lattice structures.
    @param community_set: list of communities (with members) to add (CommunitySet)
    @return: NetworkX Graph object with communities in lattice structure
    """
    G = nx.Graph()
    graph_list = []
    # Step 1: Build individual community lattices
    for community in community_set.list_of_communities:
        next_G = form_community_lattice(community)
        graph_list.append(next_G)
    # Step 2: Compose graphs of individual communities
    for graph in graph_list:
        G = nx.compose(G, graph)
    return G


def form_dense_community(community):
    """
    Returns a graph with all possible edges added.
    @param community: community of buyers to fully connect
    @return: a fully connected community of buyers
    """
    return nx.complete_graph(community.list_of_buyers)


def form_dense_communities(community_set):
    """
    Returns a graph of fully connected communities.
    @param community_set: List of communities (CommunitySet)
    @return: a graph of fully connected communities
    """
    # Step 1: Build individual dense communities
    G = nx.Graph()
    graph_list = []
    for community in community_set.list_of_communities:
        next_G = form_dense_community(community)
        graph_list.append(next_G)
    # Step 2: Compose graphs of individual dense communities
    for graph in graph_list:
        G = nx.compose(G, graph)
    return G


def connect_initial_communities(G):
    """
    Connects communities at the start of the simulation.
    @param G: graph containing disconnected communities
    @return: graph containing connected communities
    """
    while not nx.is_connected(G):
        # sort buyers
        community_dict = {}
        for node in G.nodes.items():
            buyer = node[0]
            if buyer.community in community_dict.keys():
                community_dict[buyer.community].append(buyer)
            else:
                community_dict[buyer.community] = [buyer]
        # select our random nodes
        random_nodes = []
        for community in community_dict.keys():
            random_nodes.append(random.choice(community_dict[community]))
        # rewiring
        new_edges = []
        delete_edges = []
        is_first_node = True
        for node in random_nodes:
            if is_first_node:
                first_node = node
                prev_node = node
                if len(list(G.edges(node))) == 0:
                    raise RuntimeError("Minimum community fill too small to ensure connectivity.")
                rand_edge_prev_node = random.choice(list(G.edges(prev_node)))
                delete_edges.append(rand_edge_prev_node)
                is_first_node = False
            else:
                new_edges.append([prev_node, node])
                if len(list(G.edges(node))) == 0:
                    raise RuntimeError("Minimum community fill too small to ensure connectivity.")
                rand_edge_current = random.choice(list(G.edges(node)))
                delete_edges.append(rand_edge_current)
                prev_node = node
        new_edges.append([first_node, node])
        for e in new_edges:
            G.add_edge(e[0], e[1])
        for r in delete_edges:
            if (r[0], r[1]) in G.edges:
                G.remove_edge(r[0], r[1])
    return G


def initialize_small_world(num_buyers,
                           num_communities,
                           min_community_fill,
                           assemblage,
                           community_structure="dense"):
    """
    Sets up a small world graph for an experiment.
    @param num_buyers: number of buyers in market
    @param num_communities: number of communities in market
    @param min_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in market
    @param community_structure: structure to initialize communities; can be dense or lattice (default: dense)
    @return: small world graph of communities
    """
    my_group = generate.initialize_market_environment(num_buyers, num_communities, min_community_fill, assemblage)
    if community_structure == "lattice":
        swg = form_community_lattices(my_group)
    else:
        swg = form_dense_communities(my_group)
    sw_graph = connect_initial_communities(swg)
    return sw_graph


def clustering_coefficient(G):
    """
    Returns the average clustering coefficient for specified graph.
    This is a shortcut method to the `average_clustering()` method from NetworkX.

    A clustering coefficient is a measure of how much nodes cluster together in a graph.
    @param G: target graph for computation
    @return: average clustering coefficient for specified graph
    """
    return nx.average_clustering(G)


def net_avg_degree(G):
    """
    Returns average degree of nodes in a graph.
    @param G: target graph for computation
    @return: average degree of nodes in a graph
    """
    degree_object = G.degree() # returns list of degrees as tuples
    total_degree = 0
    for pair in degree_object:
        total_degree += pair[1] # add all degrees
    return total_degree / len(degree_object)


def get_SWI_index(G):
    """
    Computes small world index (SWI).

    Let n be the number of nodes in the graph.
    Let k be the average degree of nodes in the graph.
    Let L_path be the average shortest path length of nodes in the graph.

    @param G: target graph for computation
    @return: small world index of inputted graph
    """
    # graph metrics
    n = len(list(G.nodes))
    k = net_avg_degree(G)
    L_path = nx.average_shortest_path_length(G)

    # lattice metrics
    L_p_lattice = (n * (n + k - 2)) / (2 * k * (n - 1))
    cc_lattice = (3 / 4) * ((k - 2) / (k - 1))

    # Moore and random metrics
    cc_random = ((k - 1) / n)
    L_p_random = math.log(n) / math.log(k)

    # small world index (SWI)
    SWI_part1 = ((L_path - L_p_lattice) / (L_p_random - L_p_lattice))
    avg_cc = clustering_coefficient(G)
    SWI_part2 = ((avg_cc - cc_random) / (cc_lattice - cc_random))
    SWI_index = SWI_part1 * SWI_part2

    return SWI_index


def is_small_world(G, small_world_index_threshold=0.5):
    """
    Checks if a network qualifies as a small world.
    @param G: potential small world network
    @param small_world_index_threshold: qualifying SWI
    @return: True if qualifies as small world, False otherwise
    """
    if get_SWI_index(G) >= small_world_index_threshold:
        return True
    else:
        return False


def small_world_rewire(G, prob_rewire, epoch, logger):
    """
    Rewires the small world network.
    @param G: current network structure
    @param prob_rewire: probability of rewire for each node
    @param epoch: current epoch (for logger)
    @param logger: logging object
    @return: rewired graph
    """
    graph = G.copy()
    # Check user-inputted probability for rewiring
    if prob_rewire == 0:
        return graph
    if prob_rewire > 1:
        prob_rewire = 1

    edges = graph.edges()
    nodes = list(graph.nodes)
    time_step = 0
    num_rewires = 0

    for node in nodes:
        edge_count = 0
        for edge in G.edges(node):
            edge_count += 1
            # check if this node has more edges than neighbors/2
            if edge_count > len(list(G.neighbors(node))) / 2:
                break
            node1 = edge[0]  # this is the node that stays the same
            node2 = edge[1]  # this is the node that changes
            dice_roll = random.uniform(0, 1)
            if dice_roll <= prob_rewire or prob_rewire == 1:  # rewire!
                acceptable_node = False
                while not acceptable_node:
                    ran = random.randint(0, len(nodes) - 1)
                    node3 = nodes[ran]
                    if node3 != node1 and node3 != node2:
                        acceptable_node = True
                graph.add_edge(node1, node3)
                graph.remove_edges_from([edge])
                num_rewires += 1

            logger.log_swi(graph, epoch, time_step)
            time_step += 1

    logger.log(graph, epoch, time_step, num_rewires, None)
    return graph


def make_small_world_graph_info_file(num_buyers,
                                     min_num_communities,
                                     min_community_fill,
                                     assemblage,
                                     epochs,
                                     upper_thresh,
                                     lower_thresh,
                                     death_thresh,
                                     results_dir,
                                     prob_rewire,
                                     start_structure):
    """
    Creates an information file (.csv) for this small world experiment.
    @param num_buyers: number of buyers in market
    @param min_num_communities: minimum number of communities
    @param min_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale in market
    @param epochs: number of market iterations
    @param upper_thresh: % of buyers that must own a particular item to change a buyer's intention to that item
    @param lower_thresh: max % of buyers that may own a particular item to change a buyer's intention to random item
    @param death_thresh: percentage at which a pot is removed from the market
    @param results_dir: directory path in which to store the file
    @param prob_rewire: probability that a node is rewired each epoch
    @param start_structure: structure in which communities are initialized (dense or lattice)
    """
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    info_filename = results_dir + "/graph_info.csv"
    info_log = open(info_filename, "w+")
    writer = csv.writer(info_log)
    fields = ["experiment", "date", "time", "number of buyers", "start structure",
              "min num communities", "min community fill",
              "assemblage", "total epochs", "upper threshold",
              "lower threshold", "death threshold", "probability of rewire"]
    writer.writerow(fields)
    info = ["small world", str(date.today()), str((datetime.now()).strftime("%H:%M:%S")), str(num_buyers),
            start_structure, str(min_num_communities), str(min_community_fill),
            assemblage, str(epochs), str(upper_thresh), str(lower_thresh),
            str(death_thresh), str(prob_rewire)]
    writer.writerow(info)
    info_log.close()
