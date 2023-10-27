import networkx as nx
import generate
import math
import time
from datetime import date
from datetime import datetime
import marketspace
import random
import os
import csv

def make_lattice_from_nodes(G):
  #makes a ring
  count = 0; node1 = {}; node2 = {}; first_node = {}
  for node in G.nodes:
    if count == 0:
      node1 = node; first_node = node; count = count+1
    else:
      node2 = node
      G.add_edge(node1, node2)
      node1 = node2; count = count+1
  G.add_edge(first_node, node2)
  #fills in the lattice
  edges_to_add ={}
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
  G = nx.Graph()
  for buyer in community.list_of_buyers:
    G.add_node(buyer)
  return make_lattice_from_nodes(G)

def form_community_lattices(group_of_communities):
  G = nx.Graph()
  graph_list = []
  for community in group_of_communities.list_of_communities:
    next_G = form_community_lattice(community)
    graph_list.append(next_G)
  #compose all graphs
  for graph in graph_list:
    G = nx.compose(G, graph)
  return G

def form_dense_community(community):
  return nx.complete_graph(community.list_of_buyers)
   
def form_dense_communities(group_of_communities):
  G = nx.Graph()
  graph_list = []
  for community in group_of_communities.list_of_communities:
    next_G = form_dense_community(community)
    graph_list.append(next_G)
  #compose all graphs
  for graph in graph_list:
    G = nx.compose(G, graph)
  return G

def connect_initial_communities(G):
  while not nx.is_connected(G):
    #sort buyers
    community_dict = {}
    for node in G.nodes.items():
      buyer = node[0]
      if buyer.community in community_dict.keys():
        community_dict[buyer.community].append(buyer)
      else:
        community_dict[buyer.community] = [buyer]
    #select our random nodes
    random_nodes = []
    for community in community_dict.keys():
      random_nodes.append(random.choice(community_dict[community]))
    #rewiring
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

def initialize_small_world(num_buyers, num_communities, min_community_fill, assemblage, community_structure="dense"):
  my_group = generate.initialize_market_environment(num_buyers, num_communities, min_community_fill, assemblage)
  if community_structure == "lattice":
    swg = form_community_lattices(my_group)
  else: 
    swg = form_dense_communities(my_group)
  connect_initial_communities(swg)
  return swg

def clustering_coefficient(G):
  return nx.average_clustering(G)

def net_avg_degree (G):
  degree_object = G.degree()
  total_degree = 0
  for pair in degree_object:
    total_degree += pair[1]
  return total_degree / len(degree_object)

def get_SWI_index(G):
  #our graph metrics
  n = len(list(G.nodes))
  k = net_avg_degree(G)
  L_path = nx.average_shortest_path_length(G)
  #lattice metrics
  L_p_lattice = (n * (n+k-2) ) / (2 * k * (n-1) )
  cc_lattice = (3/4) * ((k-2)/(k-1))
  #Moore and random metrics
  #L_p_random = ((n^2)/(4*(n-1)))
  cc_random = ((k-1)/n) 
  L_p_random = math.log(n) / math.log(k)
  #small world index (SWI)
  SWI_part1 = ((L_path - L_p_lattice)/(L_p_random - L_p_lattice)) 
  avg_cc = clustering_coefficient(G)
  SWI_part2 = ((avg_cc - cc_random)/(cc_lattice - cc_random))
  SWI_index = SWI_part1 * SWI_part2
  return SWI_index

def is_small_world(G):
  if get_SWI_index(G) >= .5:
      return True
  else:
    return False

def small_world_rewire(G, prob_rewire, epoch, logger):
  graph = G.copy()
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
      if edge_count > len(list(G.neighbors(node)))/2:
        break
      node1 = edge[0] #this is the node that stays the same
      node2 = edge[1] #this is the node that changes
      dice_roll = random.uniform(0, 1)
      if dice_roll <= prob_rewire or prob_rewire == 1: #rewire!
        acceptable_node = False
        while acceptable_node == False:
          ran = random.randint(0, len(nodes) -1)
          node3 = nodes[ran]
          if node3 != node1 and node3 != node2:
            acceptable_node = True
        graph.add_edge(node1, node3)
        graph.remove_edges_from([edge])
        num_rewires += 1
      logger.log_swi(graph, epoch, time_step)
      time_step += 1
      #log swi for timestep
  logger.log(graph, epoch, time_step, num_rewires, None)
  return graph

def make_sw_graph_info_file(num_buyers,
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

