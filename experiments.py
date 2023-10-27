import smallworld as sw
import scalefree as sf
import marketspace
from datetime import datetime, timedelta
import time
import random
import logger
from logger import Logger
from importlib import reload
reload(logger)

def small_world_simulation (number_of_buyers,
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
  print("Initilizing small world model...")
  small_world = sw.initialize_small_world(number_of_buyers, 
                                       minimum_number_of_communities, 
                                       minimum_community_fill,
                                       assemblage, 
                                       community_start_structure
                                       )
  small_world = marketspace.buy_pots(small_world)
  print("Creating logging resources...")
  sw.make_sw_graph_info_file(number_of_buyers,
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
  logger = Logger(results_directory, assemblage)
  logger.log(small_world, 0, 0, 0, None)
  print("Beginning simulation...")
  start_time = start_time = time.monotonic()
  for epoch in range(1, number_of_epochs+1):
    small_world = sw.small_world_rewire(small_world, probability_of_rewire, epoch, logger)
    small_world = marketspace.change_all_buyer_intentions(small_world,
                                lower_threshold, 
                                upper_threshold,
                                death_threshold)
    small_world = marketspace.buy_pots(small_world)
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
                          verbose = True):
  print("Creating logging resources...")
  logger = Logger(results_directory, assemblage, model_type="scale_free")
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
  print("Initilizing scale free model...")
  start_time = start_time = time.monotonic()
  scale_free, buyers = sf.initialize_scale_free(number_of_buyers,
                                minimum_number_of_communities,
                                minimum_community_fill,
                                assemblage,
                                initial_set_size,
                                community_bonus,
                                logger)
  scale_free = marketspace.buy_pots(scale_free)
  epoch = 1
  #while there's nodes not in the graph, add them in sets
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
    scale_free = sf.build_scale_free_network(next_node_set, scale_free, community_bonus, logger, epoch, buyers)
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
    if set_to_last:
      last = True
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