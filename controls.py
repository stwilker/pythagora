import random
import networkx as nx
import generate
import logger
from logger import Logger
import os 
import time
from datetime import date
from datetime import datetime, timedelta
import csv
import marketspace
import smallworld
import scalefree as sf

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
                            set_size,
                            probability_of_link):
  if not os.path.exists(results_dir):
    os.makedirs(results_dir)
  info_filename = results_dir + "/graph_info.csv"
  info_log = open(info_filename, "w+")
  writer = csv.writer(info_log)
  fields = ["experiment", "date", "time", "number of buyers", "initial_set_size",
            "set size", "min num communities", "min community fill",
            "assemblage", "total epochs", "upper threshold",
            "lower threshold", "death threshold", "community bonus", "probability of link"]
  writer.writerow(fields)
  info = ["scale free", str(date.today()), str((datetime.now()).strftime("%H:%M:%S")), str(num_buyers),
          str(initial_set_size), str(set_size), str(min_num_communities), str(min_community_fill), 
          assemblage, str(epochs), str(upper_thresh), str(lower_thresh),
          str(death_thresh), str(community_bonus), str(probability_of_link)]
  writer.writerow(info)

def build_scale_free_control_network(set_of_nodes, G, community_bonus, 
                                    logger, epoch, all_buyers_in_market,
                                    probability_of_link):
  #make a stack with our buyers
  while len(set_of_nodes) != 0:
    current_node = set_of_nodes.pop()
    # add our node to the graph space
    t = len(G.nodes)
    # assign probabilities to each node
    probs = {} # (nodes, probabilities)

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

      print(t)
      print(current_node.name)
      print(selected_node[0].name)
    #move this line up to allow self loops
    G.add_node(current_node)
    if t != 0:
      G.add_edge(current_node, selected_node[0])
  logger.log(G, epoch, 0, 0, all_buyers_in_market)
  return G

def initialize_scale_free_control (number_of_buyers, 
                                  minimum_number_of_communities, 
                                  minimum_community_fill,
                                  assemblage, 
                                  initial_set_size,
                                  community_bonus, 
                                  logger, 
                                  probability_of_link
                                  ):
  my_group = generate.initialize_market_environment(number_of_buyers, 
                                                     minimum_number_of_communities, 
                                                     minimum_community_fill, 
                                                     assemblage)
  G = nx.Graph()
  buyers_in_market = my_group.get_all_buyers_in_group()
  for b in buyers_in_market:
    b.purchased_pot = b.intention
  set_of_nodes = random.sample(buyers_in_market, initial_set_size)
  G = build_scale_free_control_network(set_of_nodes, G, community_bonus, logger, 0, buyers_in_market, probability_of_link)
  
  return G, buyers_in_market

def random_experiment_control_scale_free(number_of_buyers, 
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
                                        probability_of_link,
                                        verbose = True):
  print("Creating logging resources...")
  logger = Logger(results_directory, assemblage, model_type="scale_free")
  make_sf_control_graph_info_file(number_of_buyers,
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
                          set_size,
                          probability_of_link)
  print("Initilizing scale free control model...")
  start_time = start_time = time.monotonic()
  scale_free, buyers = initialize_scale_free_control(number_of_buyers,
                                minimum_number_of_communities,
                                minimum_community_fill,
                                assemblage,
                                initial_set_size,
                                community_bonus,
                                logger,
                                probability_of_link)
  scale_free = marketspace.buy_pots(scale_free)
  epoch = 1
  #while there's nodes not in the graph, add them in sets
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
    scale_free = build_scale_free_control_network(next_node_set, scale_free, community_bonus, logger, epoch, buyers, probability_of_link)
    scale_free = marketspace.change_all_buyer_intentions(scale_free,
                                lower_threshold, 
                                upper_threshold,
                                death_threshold)
    scale_free = marketspace.buy_pots(scale_free)
    if verbose:
      end_time = time.monotonic()
      print("Epoch: " + str(epoch))
      print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))
    epoch += 1
  if epoch < number_of_epochs+1:
    for e in range(epoch, number_of_epochs+1):
      scale_free = marketspace.change_all_buyer_intentions(scale_free,
                                lower_threshold, upper_threshold, death_threshold)
      scale_free = marketspace.buy_pots(scale_free)
      logger.log(scale_free, e, 0, 0, buyers)
      if verbose:
        end_time = time.monotonic()
        print("Epoch: " + str(epoch))
        print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))
      epoch += 1


def make_random_graph(group_of_communities, probability_of_link=0.5):
  #start with N isolated nodes
  #select node pair
  #generate a random number [0, 1)
  #connect based on prob
  #repeat for N(N-1)/2 node pairs.
  buyers_in_market = group_of_communities.get_all_buyers_in_group()
  G = nx.Graph()
  for buyer in buyers_in_market:
    G.add_node(buyer)
  list_of_nodes = list(G.nodes())
  stack = [(node1, node2) for spot_in_list, node1 in enumerate(list_of_nodes) for node2 in list_of_nodes[spot_in_list + 1:]]
  random.shuffle(stack)
  while len(stack) != 0:
    current_pair = stack.pop()
    if random.random() < probability_of_link:
      node1 = current_pair[0]
      node2 = current_pair[1]
      G.add_edge(node1, node2)
  return G

#Experiment 5: Control small world; experiment 6 without growth; 
def small_world_control (number_of_buyers,
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
  print("Initilizing small world control model...")
  my_group = generate.initialize_market_environment(number_of_buyers, 
                                                    minimum_number_of_communities, 
                                                    minimum_community_fill, 
                                                    assemblage)
  graph = make_random_graph(my_group, probability_of_link=link_prob)
  graph = marketspace.buy_pots(graph)
  print("Creating logging resources...")
  #create graph_info.txt here
  if not os.path.exists(results_directory):
    os.makedirs(results_directory)
  info_filename = results_directory + "/graph_info.txt"
  info_log = open(info_filename, "w+")
  #graph info
  logger = Logger(results_directory, assemblage)
  start_time = start_time = time.monotonic()
  for epoch in range(epochs):
    graph = smallworld.small_world_rewire(graph, rewire_prob, epoch, logger)
    graph = marketspace.change_all_buyer_intentions(graph,
                                lower_threshold, 
                                upper_threshold,
                                death_threshold)
    graph = marketspace.buy_pots(graph)
    if verbose:
      end_time = time.monotonic()
      print("Epoch: " + str(epoch))
      print("Time elapsed: %s seconds " % timedelta(seconds=end_time - start_time))