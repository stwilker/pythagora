from networkx.algorithms.bipartite.centrality import betweenness_centrality
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality
import networkx as nx
import os
import csv
from agents import Buyer
import smallworld
import matplotlib.pyplot as plt
import scipy.sparse.linalg
import scipy.sparse
import numpy as np
import scipy as sp
import itertools
from networkx.readwrite import json_graph

class Logger:
 
  def __init__(self, directory_path, assemblage, model_type='small_world', save_images=True):
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
    
  def get_community_names(self, graph):
    comm_names = []
    for buyer in graph:
      if buyer.community not in comm_names:
        comm_names.append(buyer.community)
    return comm_names

  def get_community_distributions(self, graph):
    community_distributions = {}
    #l = {}
    #for pot in self.assemblage:
      #l[pot] = 0
    #if self.model == "scale_free":
      #l['no_pot_choice'] = 0
    for name in self.get_community_names(graph):
      community_distributions[name] = [0, {}]
    for buyer in graph:
      community_distributions[buyer.community][0] += 1
      if buyer.purchased_pot in community_distributions[buyer.community][1].keys():
        community_distributions[buyer.community][1][buyer.purchased_pot] += 1
      else:
        community_distributions[buyer.community][1][buyer.purchased_pot] = 1
    return community_distributions

  def get_pot_distributions(self, graph):
    pot_distribution = {}
    for pot in self.assemblage:
      pot_distribution[pot] = 0
    if self.model == "scale_free":
      pot_distribution['no_pot_choice'] = 0
    for buyer in graph:
      pot_distribution[buyer.purchased_pot] += 1
    return pot_distribution
  
  def get_degree_stats(self, graph):
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
  
  def count_community_connections(self, graph):
    inter = 0
    intra = 0
    for edge in graph.edges():
      if edge[0].community == edge[1].community:
        intra += 1
      else: 
        inter += 1
    return inter, intra

  def initialize_results_logger(self, graph, all_buyers_in_market):
    self.field_names = ["epoch", "timestep"]
    if self.model == 'scale_free':
      self.community_names = []
      for b in all_buyers_in_market:
        if b.community not in self.community_names:
          self.community_names.append(b.community)
    else:
      self.community_names = self.get_community_names(graph)
    #num buyers in each community
    for comm_name in self.community_names:
      self.field_names.append("num_buyers_" + comm_name)
    #an array of the pot distribution for each community
    for comm_name in self.community_names:
      self.field_names.append("pot_distrib_" + comm_name)
    #number of buyers per pot over entire network
    for pot in self.assemblage:
      self.field_names.append(pot + "_buyers")
    #network metrics
    self.field_names.append("num_nodes")
    self.field_names.append("num_edges")
    self.field_names.append("avg_degree")
    self.field_names.append("min_degree")
    self.field_names.append("max_degree")
    self.field_names.append("network_diameter")
    self.field_names.append("avg_path_length")
    self.field_names.append("avg_clustering_coef")
    self.field_names.append("triadic_closure")
    #number of intra community connections
    self.field_names.append("intra_connectivity")
    #for each community, number of external community connections
    self.field_names.append("inter_connectivity")
    #small world specific metrics
    if self.model == 'small_world':
      #small world index
      self.field_names.append("swi")
      #number of rewires in current epoch
      self.field_names.append("num_rewires")
    self.field_names.append("snapshot")
    self.graph_writer.writerow(self.field_names)


  def log_small_world(self, small_world_graph, timestamp, num_rewires):
    if not self.initialized:
      self.initialize_results_logger(small_world_graph, [])
      self.initialized = True
    info = [timestamp[0], timestamp[1]] #epoch, timestep
    community_buyers = self.get_community_distributions(small_world_graph)
    #buyers per community
    for item in community_buyers.keys(): #each item is a tuple
      number_of_buyers = community_buyers.get(item)[0]
      info.append(item + "_" + str(number_of_buyers))
    #pots per community
    for item in community_buyers.keys(): #each item is a tuple
      info.append(item + str(community_buyers.get(item)[1]))
    #pot distribution over network
    pot_distribs = self.get_pot_distributions(small_world_graph)
    for pot in pot_distribs.keys():
      info.append(pot + "_" + str(pot_distribs.get(pot)))
    info.append(small_world_graph.number_of_nodes())
    info.append(small_world_graph.number_of_edges())
    #info.append(nx.average_neighbor_degree(small_world_graph))
    avg, min, max = self.get_degree_stats(small_world_graph)
    info.append(avg)
    info.append(min)
    info.append(max)
    if nx.is_connected(small_world_graph):
      info.append(nx.diameter(small_world_graph))
      info.append(nx.average_shortest_path_length(small_world_graph))
    else:
      info.append("not_connected")
      info.append("not_connected")
    info.append(smallworld.clustering_coefficient(small_world_graph))
    info.append(nx.transitivity(small_world_graph))
    inter, intra = self.count_community_connections(small_world_graph)
    info.append(intra)
    info.append(inter)
    info.append(self.swi_curr_epoch)
    self.swi_curr_epoch = []
    #if nx.is_connected(small_world_graph):
      #info.append(smallworld.get_SWI_index(small_world_graph))
    #else:
      #print("? not connected? " + str(nx.is_connected))
      #info.append("not_connected")
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
    if not self.initialized:
      self.initialize_results_logger(scale_free_graph, all_buyers_in_market)
      self.initialized = True
    info = [timestamp[0], timestamp[1]] #epoch, timestep
    if timestamp[0] !=0 :
      community_buyers = self.get_community_distributions(scale_free_graph)
      for item in self.community_names:
        #number_of_buyers = None
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
    avg, min, max = self.get_degree_stats(scale_free_graph)
    info.append(avg)
    info.append(min)
    info.append(max)
    if nx.is_connected(scale_free_graph):
      info.append(nx.diameter(scale_free_graph))
      info.append(nx.average_shortest_path_length(scale_free_graph))
    elif not nx.is_connected(scale_free_graph):
      info.append("not_connected")
      info.append("not_connected")
    info.append(smallworld.clustering_coefficient(scale_free_graph))
    info.append(nx.transitivity(scale_free_graph))
    inter, intra = self.count_community_connections(scale_free_graph)
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

  def get_buyer_community_centralities(self, graph, buyer):
    g = graph.copy()
    for b in graph:
      if b.community != buyer.community:
        g.remove_node(b)
    e_c = nx.eigenvector_centrality(g, max_iter=10000)
    for i in e_c.keys():
      if i.name == buyer.name:
        eigen_cent = e_c.get(i)
    b_c = nx.betweenness_centrality(g)
    for k in b_c.keys():
      if k.name == buyer.name:
        betwe_cent = b_c.get(k)
    return eigen_cent, betwe_cent

  def log_buyers(self, graph, timestamp):
    e_centrality = nx.eigenvector_centrality(graph, max_iter=10000)
    b_centrality = nx.betweenness_centrality(graph)

    for buyer in graph:
      buyer_row = [timestamp[0], timestamp[1]]
      buyer_row.append(buyer.name)
      buyer_row.append(buyer.community)
      buyer_row.append(buyer.purchased_pot)
      buyer_row.append(buyer.intention)
      buyer_row.append(e_centrality[buyer])
      buyer_row.append(b_centrality[buyer])
      e, b = self.get_buyer_community_centralities(graph, buyer)
      buyer_row.append(e)
      buyer_row.append(b)
      self.buyer_writer.writerow(buyer_row)
  
  def log_comms_matrix(self, graph, epoch, timestep, all_buyers_in_market):
    if not self.matrix_init:
      self.matrix_fields = ["epoch", "timestep"]
      if self.model == 'scale_free':
        communities = []
        for b in all_buyers_in_market:
          if b.community not in communities:
            communities.append(b.community)
      else:
        communities = self.get_community_names(graph)
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
    if nx.is_connected(graph):
      self.swi_curr_epoch.append(smallworld.get_SWI_index(graph))
    else:
      self.swi_curr_epoch.append("nc")

  def log (self, graph, epoch, timestep, num_rewires, all_buyers_in_market):
    if self.model == 'small_world':
      self.log_small_world(graph, (epoch, timestep), num_rewires)
    if self.model == 'scale_free':
      self.log_scale_free(graph, (epoch, timestep), all_buyers_in_market)
    self.log_buyers(graph, [epoch, timestep])
    self.log_comms_matrix(graph, epoch, timestep, all_buyers_in_market)