"""This module implements the Logger class and its supporting methods. The Logger class is the key to accessing
results from social network experiments without writing any analysis code in Python.

RESULTS FILES
=============

At construction, a directory path is provided to the Logger object. Inside this directory, Logger creates the following:

    1. A subdirectory named `/images`, where static network visualizations at each epoch will be stored.
    2. A file named `/buyers.csv`, where information about buyers (their current item, intention, etc.) will be recorded.
    3. A file named `/graphs.csv`, where information about the network will be recorded.
    4. A file named `/matrix.csv`, where information about communities will be recorded.

`matrix.csv` records the number of edges between each pair of communities (hence, it is a matrix).

In addition, experimental metadata is recorded in an info file at the beginning of any experiment (see: scalefree.py
and smallworld.py).

TIMESTAMPS
==========

The Logger object records the market state at every timestamp. A timestamp is a tuple that contains an
epoch and a timestep.

An epoch is every iteration of market purchases. One set of purchasing, rewiring,
and changing buyer intentions is an epoch. You can set the number of desired epochs when instantiating the
experiment.

Timesteps work differently depending on the experiment type. In a small world experiment, a timestep is every
instance that the graph considers an edge for rewiring. If there are `m` edges in the graph, there will be `m`
timesteps in each epoch. In a scale free experiment, a timestep is every instance that the graph considers a node for
random reassignment of purchase intention. If there are `n` nodes in the graph, then there will be `n` timesteps in
each epoch.

MAC OS USERS
============

Eigenvector centrality as implemented through NetworkX has limited functionality
on MacOS. If you encounter an error when computing eigenvector centrality, change the default parameter `macOS` in
the `get_buyer_community_centralities` method to `True`. For convenience, this is the first method in the file.
"""

import networkx as nx
import os
import csv
from . import smallworld
import itertools


def get_buyer_community_centralities(graph, buyer, macOS=False):
    """
    Returns the eigenvector and betweenness centralities for a particular buyer.
    Note: Eigenvector centrality as implemented through NetworkX has limited functionality on MacOS.
    You can change the above default parameter to True to avoid computing eigenvector centrality.
    If macOS is set to True, eigen_centrality will be returned as -1000.
    @param graph: graph representing current market state
    @param buyer: target buyer
    @return: eigenvector and betweenness centrality for target buyer
    """
    g = graph.copy()
    for b in graph:
        if b.community != buyer.community:
            g.remove_node(b)
    if not macOS:
        e_c = nx.eigenvector_centrality(g, max_iter=10000)
        for i in e_c.keys():
            if i.name == buyer.name:
                eigen_cent = e_c.get(i)
    else:
        eigen_cent = -1000
    b_c = nx.betweenness_centrality(g)
    for k in b_c.keys():
        if k.name == buyer.name:
            betwe_cent = b_c.get(k)
    return eigen_cent, betwe_cent


def get_community_names(graph):
    """
    Returns a list of the names of the communities in a market.
    @param graph: graph representing current market state
    @return: list of names of communities in the graph
    """
    comm_names = []
    for buyer in graph:
        if buyer.community not in comm_names:
            comm_names.append(buyer.community)
    return comm_names


def get_community_distributions(graph):
    """
    Gets distribution of buyers and purchased items in a community.
    The returned distribution graph is of the following form:
        - Key: community names, Value: [integer, dictionary2]
        - Key2: purchased item, Value2: number of buyers that purchased that item
    @param graph: graph representing current market state
    @return: tiered dictionary of purchase distributions across communities
    """
    community_distributions = {}
    for name in get_community_names(graph):
        community_distributions[name] = [0, {}]
    for buyer in graph:
        community_distributions[buyer.community][0] += 1
        if buyer.purchased_pot in community_distributions[buyer.community][1].keys():
            community_distributions[buyer.community][1][buyer.purchased_pot] += 1
        else:
            community_distributions[buyer.community][1][buyer.purchased_pot] = 1
    return community_distributions


def get_degree_stats(graph):
    """
    Returns min, max, and mean of node degrees in the graph.
    @param graph: graph representing current market state
    @return: min, max, and mean of node degrees in the graph
    """
    max_degree = 0
    min_degree = 1000
    total_degree = 0
    for buyer in graph:
        if graph.degree(buyer) > max_degree:
            max_degree = graph.degree(buyer)
        if graph.degree(buyer) < min_degree:
            min_degree = graph.degree(buyer)
        total_degree += graph.degree(buyer)
    avg_degree = total_degree / len(graph.nodes)
    return avg_degree, min_degree, max_degree


def count_community_connections(graph):
    """
    Counts the number of edges between buyers of different communities.
    @param graph: graph representing current market state
    @return: number of edges between buyers of different communities
    """
    inter = 0
    intra = 0
    for edge in graph.edges():
        if edge[0].community == edge[1].community:
            intra += 1
        else:
            inter += 1
    return inter, intra


class Logger:
    """
    Logger objects track market states throughout experiments for future analysis.
    """

    def __init__(self, directory_path, assemblage, model_type='small_world', save_images=True):
        """
        Instantiates a Logger object.
        @param directory_path: path of directory to store results files
        @param assemblage: list of items for sale in marketplace
        @param model_type: scale free or small world (default: small world)
        @param save_images: save static images of graphs throughout training (default: True)
        """
        self.model = model_type
        self.images = save_images
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        if self.images:
            self.images_path = directory_path + "/images"
            if not os.path.exists(self.images_path):
                os.makedirs(self.images_path)
        buyer_log_filename = directory_path + "/buyers.csv"
        self.buyer_log = open(buyer_log_filename, "w+")
        graph_log_filename = directory_path + "/graphs.csv"
        self.graph_log = open(graph_log_filename, "w+")
        matrix_log_filename = directory_path + "/matrix.csv"
        self.matrix_log = open(matrix_log_filename, "w+")
        self.initialized = False
        self.matrix_init = False
        self.matrix_fields = []
        self.buyer_fields = ["epoch", "timestep",
                             "name", "community",
                             "current_pot", "current_intention",
                             "eigenvector_cent_net", "betweenness_cent_net",
                             "eigenvector_cent_comm", "betweenness_cent_comm"]
        self.buyer_writer = csv.writer(self.buyer_log)
        self.buyer_writer.writerow(self.buyer_fields)
        self.graph_writer = csv.writer(self.graph_log)
        self.matrix_writer = csv.writer(self.matrix_log)
        self.assemblage = assemblage
        self.swi_curr_epoch = []
        self.field_names = []
        self.community_names = []

    def get_pot_distributions(self, graph):
        """
        Get distributions of purchased items in marketplace.
        @param graph: graph representing the current market state
        @return: distribution in dictionary form of purchased items
        """
        pot_distribution = {}
        for pot in self.assemblage:
            pot_distribution[pot] = 0
        if self.model == "scale_free":
            pot_distribution['no_pot_choice'] = 0
        for buyer in graph:
            pot_distribution[buyer.purchased_pot] += 1
        return pot_distribution

    def initialize_results_logger(self, graph, all_buyers_in_market):
        """
        Sets up the logger with field names and heading information.
        @param graph: graph representing the current market state
        @param all_buyers_in_market: list of all buyers in market
        """
        self.field_names = ["epoch", "timestep"]
        if self.model == 'scale_free':
            self.community_names = []
            for b in all_buyers_in_market:
                if b.community not in self.community_names:
                    self.community_names.append(b.community)
        else:
            self.community_names = get_community_names(graph)
        # num buyers in each community
        for comm_name in self.community_names:
            self.field_names.append("num_buyers_" + comm_name)
        # an array of the pot distribution for each community
        for comm_name in self.community_names:
            self.field_names.append("pot_distrib_" + comm_name)
        # number of buyers per pot over entire network
        for pot in self.assemblage:
            self.field_names.append(pot + "_buyers")
        # network metrics
        self.field_names.append("num_nodes")
        self.field_names.append("num_edges")
        self.field_names.append("avg_degree")
        self.field_names.append("min_degree")
        self.field_names.append("max_degree")
        self.field_names.append("network_diameter")
        self.field_names.append("avg_path_length")
        self.field_names.append("avg_clustering_coef")
        self.field_names.append("triadic_closure")
        # number of intra community connections
        self.field_names.append("intra_connectivity")
        # for each community, number of external community connections
        self.field_names.append("inter_connectivity")
        # small world specific metrics
        if self.model == 'small_world':
            # small world index
            self.field_names.append("swi")
            # number of rewires in current epoch
            self.field_names.append("num_rewires")
        self.field_names.append("snapshot")
        self.graph_writer.writerow(self.field_names)

    def log_small_world(self, small_world_graph, timestamp, num_rewires):
        """
        Logs statistics about the market at a particular timestep in a small world experiment.
        @param small_world_graph: graph representing current market state
        @param timestamp: a list containing the epoch and timestep
        @param num_rewires: number of nodes that were rewired this timestep
        """
        if not self.initialized:
            self.initialize_results_logger(small_world_graph, [])
            self.initialized = True
        info = [timestamp[0], timestamp[1]]  # epoch, timestep
        community_buyers = get_community_distributions(small_world_graph)
        # buyers per community
        for item in community_buyers.keys():  # each item is a tuple
            number_of_buyers = community_buyers.get(item)[0]
            info.append(item + "_" + str(number_of_buyers))
        # pots per community
        for item in community_buyers.keys():  # each item is a tuple
            info.append(item + str(community_buyers.get(item)[1]))
        # pot distribution over network
        pot_distribs = self.get_pot_distributions(small_world_graph)
        for pot in pot_distribs.keys():
            info.append(pot + "_" + str(pot_distribs.get(pot)))
        info.append(small_world_graph.number_of_nodes())
        info.append(small_world_graph.number_of_edges())
        avg, minimum, maximum = get_degree_stats(small_world_graph)
        info.append(avg)
        info.append(minimum)
        info.append(maximum)
        if nx.is_connected(small_world_graph):
            info.append(nx.diameter(small_world_graph))
            info.append(nx.average_shortest_path_length(small_world_graph))
        else:
            info.append("not_connected")
            info.append("not_connected")
        info.append(smallworld.clustering_coefficient(small_world_graph))
        info.append(nx.transitivity(small_world_graph))
        inter, intra = count_community_connections(small_world_graph)
        info.append(intra)
        info.append(inter)
        info.append(self.swi_curr_epoch)
        self.swi_curr_epoch = []
        info.append(num_rewires)
        if self.images:
            graph_data = []
            for edge in small_world_graph.edges():
                graph_data.append([edge[0].name, edge[1].name])
            info.append(graph_data)
        else:
            info.append("n/a")
        self.graph_writer.writerow(info)

    def log_scale_free(self, scale_free_graph, timestamp, all_buyers_in_market):
        """
         Logs statistics about the market at a particular timestep in a scale free experiment.
         @param scale_free_graph: graph representing current market state
         @param timestamp: a list containing the epoch and timestep
         @param all_buyers_in_market: list of all buyers in market
         """
        if not self.initialized:
            self.initialize_results_logger(scale_free_graph, all_buyers_in_market)
            self.initialized = True
        info = [timestamp[0], timestamp[1]]  # epoch, timestep
        if timestamp[0] != 0:
            community_buyers = get_community_distributions(scale_free_graph)
            for item in self.community_names:
                # number_of_buyers = None
                number_of_buyers = 0
                if item in community_buyers.keys():
                    number_of_buyers = community_buyers.get(item)[0]
                info.append(item + "_" + str(number_of_buyers))
            for item in self.community_names:
                number_of_buyers = 0
                if item in community_buyers.keys():
                    number_of_buyers = community_buyers.get(item)[1]
                info.append(item + "_" + str(number_of_buyers))
            pot_distribs = self.get_pot_distributions(scale_free_graph)
            for pot in self.assemblage:
                if pot in pot_distribs.keys():
                    info.append(pot + "_" + str(pot_distribs.get(pot)))
                else:
                    info.append(pot + "_0")
        elif timestamp[0] == 0:
            community_distributions = {}
            for name in self.community_names:
                community_distributions[name] = 0
            for buyer in scale_free_graph:
                community_distributions[buyer.community] += 1
            for item in self.community_names:
                if item in community_distributions.keys():
                    number_of_buyers = community_distributions.get(item)
                else:
                    number_of_buyers = 0
                info.append(item + "_" + str(number_of_buyers))
            for item in self.community_names:
                info.append(item + "_0")
            for pot in self.assemblage:
                info.append(pot + "_0")
        info.append(scale_free_graph.number_of_nodes())
        info.append(scale_free_graph.number_of_edges())
        avg, minimum, maximum = get_degree_stats(scale_free_graph)
        info.append(avg)
        info.append(minimum)
        info.append(maximum)
        if nx.is_connected(scale_free_graph):
            info.append(nx.diameter(scale_free_graph))
            info.append(nx.average_shortest_path_length(scale_free_graph))
        elif not nx.is_connected(scale_free_graph):
            info.append("not_connected")
            info.append("not_connected")
        info.append(smallworld.clustering_coefficient(scale_free_graph))
        info.append(nx.transitivity(scale_free_graph))
        inter, intra = count_community_connections(scale_free_graph)
        info.append(intra)
        info.append(inter)
        if self.images:
            graph_data = []
            for edge in scale_free_graph.edges():
                graph_data.append([edge[0].name, edge[1].name])
            info.append(graph_data)
        else:
            info.append("n/a")
        self.graph_writer.writerow(info)

    def log_buyers(self, graph, timestamp):
        """
        Log buyers and their states at a particular timestep.
        @param graph: graph representing the current market state
        @param timestamp: a list containing the epoch and timestep
        """
        e_centrality = nx.eigenvector_centrality(graph, max_iter=10000)
        b_centrality = nx.betweenness_centrality(graph)

        for buyer in graph:
            buyer_row = [timestamp[0], timestamp[1], buyer.name, buyer.community, buyer.purchased_pot, buyer.intention,
                         e_centrality[buyer], b_centrality[buyer]]
            e, b = get_buyer_community_centralities(graph, buyer)
            buyer_row.append(e)
            buyer_row.append(b)
            self.buyer_writer.writerow(buyer_row)

    def log_communities_matrix(self, graph, epoch, timestep, all_buyers_in_market):
        """
        Log communities and their states at a particular timestep.
        @param graph: graph representing the current market state
        @param epoch: current epoch
        @param timestep: current timestep
        @param all_buyers_in_market: list of all buyers in market
        """
        if not self.matrix_init:
            self.matrix_fields = ["epoch", "timestep"]
            if self.model == 'scale_free':
                communities = []
                for b in all_buyers_in_market:
                    if b.community not in communities:
                        communities.append(b.community)
            else:
                communities = get_community_names(graph)
            for c in list(itertools.combinations(communities, 2)):
                self.matrix_fields.append(str(c[0]) + "_" + str(c[1]))
            self.matrix_writer.writerow(self.matrix_fields)
            self.matrix_init = True
        current_row = []
        for mf in self.matrix_fields:
            if mf == 'epoch':
                current_row.append(epoch)
            elif mf == 'timestep':
                current_row.append(timestep)
            else:
                count = 0
                comms = mf.split("_")
                c1 = comms[0]
                c2 = comms[1]
                for edge in graph.edges:
                    if edge[0].community == c1 and edge[1].community == c2:
                        count += 1
                    elif edge[0].community == c2 and edge[1].community == c1:
                        count += 1
                current_row.append(count)
        self.matrix_writer.writerow(current_row)

    def log_swi(self, graph, epoch, timestep):
        """
        Log the current small world index.
        @param graph: graph representing the current market state
        @param epoch: current epoch
        @param timestep: current timestep
        """
        if nx.is_connected(graph):
            self.swi_curr_epoch.append(smallworld.get_SWI_index(graph))
        else:
            self.swi_curr_epoch.append("nc")

    def log(self, graph, epoch, timestep, num_rewires, all_buyers_in_market):
        if self.model == 'small_world':
            self.log_small_world(graph, (epoch, timestep), num_rewires)
        if self.model == 'scale_free':
            self.log_scale_free(graph, (epoch, timestep), all_buyers_in_market)
        self.log_buyers(graph, [epoch, timestep])
        self.log_communities_matrix(graph, epoch, timestep, all_buyers_in_market)
