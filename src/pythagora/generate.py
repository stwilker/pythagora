"""
Includes all methods needed to generate initial marketplace environment.
"""

import random
from agents import Buyer
from groups import Community
from groups import CommunitySet


def generate_initial_agents(num_buyers, assemblage):
    """
    Generates initial lists of buyers and sellers in the market.

    @param assemblage: list of items for sale in market
    @param num_buyers number of buyers to add to Market
    @return Market with initial agents
    """
    if num_buyers < 1:
        raise ValueError('Market must contain at least 9 buyers.')
    else:
        list_of_buyers = []
        for i in range(num_buyers):
            random_intention = random.choice(list(assemblage))
            b_name = "buyer_" + str(i)
            new_buyer = Buyer(random_intention, "no_pot_choice", "no_community_yet", b_name)
            list_of_buyers.append(new_buyer)
        return list_of_buyers


def minimum_community_fill(group_of_communities, min_community_fill):
    """
    Checks if each community has the specific minimum number of buyers.
    Note: Helper method for community generation.
    @param group_of_communities: CommunitySet object
    @param min_community_fill: minimum number of buyers in each community.
    @return True if all communities have minimum number of buyers; False otherwise.
    """
    for community in group_of_communities.list_of_communities:
        if len(community.list_of_buyers) < min_community_fill:
            return False
    return True


def get_inadequate_communities(group_of_communities, min_community_fill):
    """
    Gets a list of communities that do not contain the minimum number of buyers.
    Helper method for community generation.
    @param group_of_communities: CommunitySet object
    @param min_community_fill: minimum number of buyers in each community.
    @return list of communities with less than min num buyers.
    """
    inadequate = []
    for community in group_of_communities.list_of_communities:
        if len(community.list_of_buyers) < min_community_fill:
            inadequate.append(community)
    return inadequate


def make_initial_communities(list_of_buyers, min_number_of_communities, min_community_fill, assemblage):
    """
    Generate initial CommunitySet.
    @param list_of_buyers: buyers in the market
    @param min_number_of_communities: minimum number of communities
    @param min_community_fill: minimum number of buyers per community
    @param assemblage: list of items for sale
    @return: CommunitySet
    """
    if min_community_fill * min_number_of_communities > len(list_of_buyers):
        raise ValueError('Minimum conditions not possible.')
    # Make a stack and fill with buyers
    stack = list_of_buyers
    group = CommunitySet([], assemblage)
    # Sorting buyers into communities
    first_pass = True
    while len(stack) != 0:
        # Case 1: There are no communities; generate min num communities
        if first_pass:
            for i in range(min_number_of_communities):
                group.add_community(Community([], "#" + str(group.number_of_communities() + 1)))
            first_pass = False
        # Case 2: Any community has less than min num buyers
        elif not minimum_community_fill(group, min_community_fill):
            random_community = random.choice(get_inadequate_communities(group, min_community_fill))
            top_buyer = stack.pop()
            group.add_buyer_to_community_by_name(top_buyer, random_community)
        # Case 3: All communities have minimum number and there are less than min num buyers.
        elif len(stack) < min_community_fill:
            # Randomly choose between existing communities
            random_community = random.choice(group.list_of_communities)
            top_buyer = stack.pop()
            group.add_buyer_to_community_by_name(top_buyer, random_community)
        # Case 4: All communities have minimum number and there are more than min num buyers
        else:
            number_of_communities = group.number_of_communities()
            choice = random.choice(list(range(number_of_communities + 1)))
            top_buyer = stack.pop()
            if choice == number_of_communities:  # make new community
                new_community = Community([], "#" + str(group.number_of_communities() + 1))
                group.add_community(new_community)
                group.add_buyer_to_community_by_name(top_buyer, new_community)
            else:
                group.add_buyer_to_community_by_index(top_buyer, choice - 1)
    return group


def initialize_market_environment(num_buyers, min_communities, min_community_fill, assemblage):
    """
    Generate a generic initial market environment.

    @param num_buyers: number of buyers in market environment
    @param min_communities: minimum number of communities
    @param min_community_fill: minimum number of buyers per community
    @return CommunitySet object representing initialized market space
    """
    buyers = generate.generate_initial_agents(num_buyers, assemblage)
    return generate.make_initial_communities(buyers, min_communities, min_community_fill, assemblage)
