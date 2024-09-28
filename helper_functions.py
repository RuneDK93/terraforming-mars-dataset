import pandas as pd
import numpy as np
import re
from collections import defaultdict


# Win probability function for pairwise comparisons
def win_prob(eloA, eloB):
    r = eloA - eloB
    s = 400
    p = 1 / (1 + 10 ** -(r / s))
    return p
    
def calculate_expected_scores(elos):
    """
    Calculate the expected scores for a 3-player game based on their Elo ratings.
    """
    expected_scores = np.zeros(3)
    
    # Compute the expected score for each player considering all opponents
    for i in range(3):
        for j in range(3):
            if i != j:
                expected_scores[i] += win_prob(int(elos[i]), int(elos[j]))
    
    return expected_scores



def corp_ranking(gamedict,sort_by):

    
    # Initialize dictionary to keep track of corporation stats
    corporation_stats = {}
    
    # Iterate through all games in gamedict
    for game_name, df in gamedict.items():
        # Ensure the dataframe is sorted by rank (if it's not already)
        df = df.sort_values('Rank')
    
        # Extract players' ELOs
        elos = df['Elo'].values
        corporations = df['Corporations'].values
        
        # Calculate expected scores for each player in the game
        pred_scores = calculate_expected_scores(elos)
    
        # Updated actual scores based on new win counting system
        actual_scores = np.array([2, 1, 0])
    
        # Calculate score differences
        score_diff = actual_scores - pred_scores
    
        # Update corporation stats
        for i, corp in enumerate(corporations):
            if corp not in corporation_stats:
                corporation_stats[corp] = {'participation_count': 0, 'first_place_wins': 0, 'score_diff_sum': 0.0}
    
            corporation_stats[corp]['participation_count'] += 1
            
            # Count wins as first place only
            if i == 0:  # i == 0 means the player is in the first row, hence the winner
                corporation_stats[corp]['first_place_wins'] += 1
                
            corporation_stats[corp]['score_diff_sum'] += score_diff[i]
    
    # Create the final dataframe
    corp_data = {
        'Corporation': [],
        'Participation Count': [],
        'Wins': [],        
        'Win Rate': [],
        'WAP': []
    }
    
    # Calculate the mean WAP for normalization
    total_wap_sum = 0
    total_participation = 0
    
    for corp, stats in corporation_stats.items():
        participation_count = stats['participation_count']
        first_place_wins = stats['first_place_wins']
        score_diff_sum = stats['score_diff_sum']
        wins = stats['first_place_wins']        
        
        # Calculate win ratio
        win_ratio = first_place_wins / participation_count
        wap = score_diff_sum / participation_count
    
        # Add data to the lists
        corp_data['Corporation'].append(corp)
        corp_data['Participation Count'].append(participation_count)
        corp_data['Wins'].append(wins)        
        corp_data['Win Rate'].append(round(win_ratio*100,2))
        corp_data['WAP'].append(round(wap,3))
        
        # Accumulate WAP values for normalization
     #   total_wap_sum += wap * participation_count
     #   total_participation += participation_count
    
    # Convert to DataFrame
    corp_df = pd.DataFrame(corp_data)
    
    
    corp_df = corp_df.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
    
    return corp_df



def log_stats(gamedict,logdict,sortby):
    # Initialize dictionaries to aggregate data across all games
    cards_stats = defaultdict(lambda: {"wins": 0, "plays": 0, "total_vp_diff": 0,"score_diff_sum": 0})
    milestone_stats = defaultdict(lambda: {"wins": 0, "plays": 0})
    award_stats = defaultdict(lambda: {"wins": 0, "plays": 0})
    award_score_stats = defaultdict(lambda: {"wins": 0, "plays": 0, "second_place_win": 0})
    
    # Loop through all games
    for game in logdict.keys():
        log = logdict[game]
        players = list(gamedict[game]['Player Names'])
        rank = list(gamedict[game]['Rank'])  # list of player ranks [1, 2, 3]
        vp = np.array(list(gamedict[game]['VP total'])).astype(int)  # list of player final scores
        generations = gamedict[game]['Generations'][0]
        elos = np.array(gamedict[game]['Elo']).astype(int)
        
        # Calculate expected scores for each player in the game
        pred_scores = calculate_expected_scores(elos)
    
        # Updated actual scores based on new win counting system
        actual_scores = np.array([2, 1, 0])
        
        # Calculate score differences
        score_diff = actual_scores - pred_scores    
        
    
        # Initialize dictionaries to store data for the current game
        player_cards = defaultdict(list)
        player_milestones = defaultdict(list)
        player_awards = defaultdict(list)
        cards_by_generation = defaultdict(lambda: defaultdict(list))
        
        # Initialize generation counter
        current_generation = 1
        
        # Process each line in the log
        for line in log.split('\n'):
            line = line.strip()
            
            # Check for new generation
            if "New generation" in line:
                gen_info = re.findall(r'New generation (\d+)', line)
                if gen_info:
                    current_generation = int(gen_info[0])
    
            # Check for player actions involving playing cards
            for player in players:
                if line.startswith(player) and "plays card" in line:
                    card_name = re.findall(r'plays card ([A-Z\s\-]+)', line)
                    if card_name:
                        card_name = card_name[0].strip()
                        player_cards[player].append(card_name)
                        cards_by_generation[current_generation][player].append(card_name)
                elif "claims milestone" in line:
                    milestone_info = re.findall(r'(\b' + re.escape(player) + r'\b)\sclaims milestone\s([\w\s]+)', line)
                    if milestone_info:
                        player, milestone = milestone_info[0]
                        player_milestones[player.strip()].append(milestone.strip())
                elif "funds" in line and "award" in line:
                    award_info = re.findall(r'(\b' + re.escape(player) + r'\b)\sfunds\s([\w\s]+)\saward', line)
                    if award_info:
                        player, award = award_info[0]
                        player_awards[player.strip()].append(award.strip())
        
        # Analyze all cards played in the game
        for player in players:
            player_rank = rank[players.index(player)]
            player_vp = vp[players.index(player)]

                        
            # Track card statistics
            for gen, cards in cards_by_generation.items():
                if player in cards:
                    for card in cards[player]:
                        cards_stats[card]["plays"] += 1
                        
                        
                        if player_rank == 1:
                            cards_stats[card]['score_diff_sum'] += score_diff[0]
                            
                        if player_rank == 2:
                            cards_stats[card]['score_diff_sum'] += score_diff[1]  
                                                                            
                        if player_rank == 3:
                            cards_stats[card]['score_diff_sum'] += score_diff[2]  
    
                        
                        
                        if player_rank == 1:
                            cards_stats[card]["wins"] += 1
                            
            # Track milestone statistics
            for milestone in player_milestones[player]:
                milestone_stats[milestone]["plays"] += 1
                if player_rank == 1:
                    milestone_stats[milestone]["wins"] += 1
    
            # Track award statistics
            for award in player_awards[player]:
                award_stats[award]["plays"] += 1
                if player_rank == 1:
                    award_stats[award]["wins"] += 1
                    
                    
        # Track award win and second-place statistics from the end-game section
        end_game_lines = log.split('\n')
        for line in end_game_lines:
            for player in players:
                player_rank = rank[players.index(player)]            
                if f"{player} scores 5 point/s for award" in line:
                    award_info = re.findall(r'for award\s([\w\s]+)\s', line)
                    if award_info:
                        award = award_info[0].strip()
                        award_score_stats[award]["plays"] += 1
                        
                        if player_rank == 1:
                            award_score_stats[award]["wins"] += 1                    
                        
                        
                elif f"{player} scores 2 point/s for award" in line:
                    award_info = re.findall(r'for award\s([\w\s]+)\s', line)
                    if award_info:
                        award = award_info[0].strip()                                       
                        if player_rank == 1:
                            award_score_stats[award]["second_place_win"] += 1                    
                                            
                    
    
    # Create separate DataFrames for cards, milestones, and awards
    # Cards DataFrame
    card_results = []
    for card, stats in cards_stats.items():
        win_ratio = stats["wins"] / stats["plays"] if stats["plays"] > 0 else 0
        wap =  stats["score_diff_sum"] / stats["plays"] if stats["plays"] > 0 else 0
        card_results.append({
            "Card": card,
            "Plays": stats["plays"],
            "Wins": stats["wins"],
            "Win Rate": round(win_ratio*100,2),
            "WAP": round(wap,3),        
        })
    df_cards = pd.DataFrame(card_results)
    
    # Milestones DataFrame
    milestone_results = []
    for milestone, stats in milestone_stats.items():
        win_ratio = stats["wins"] / stats["plays"] if stats["plays"] > 0 else 0
        milestone_results.append({
            "Milestone": milestone,
            "Plays": stats["plays"],
            "Wins": stats["wins"],
            "Win Rate": round(win_ratio*100,2)
        })
    df_milestones = pd.DataFrame(milestone_results)
    
    # Awards DataFrame
    award_results = []
    for award, stats in award_stats.items():
        win_ratio = stats["wins"] / stats["plays"] if stats["plays"] > 0 else 0
        award_results.append({
            "Award": award,
            "Plays": stats["plays"],
            "Wins": stats["wins"],
            "Win Rate": round(win_ratio*100,2)
        })
    df_awards = pd.DataFrame(award_results)
    
    
    # Awards score DataFrame
    award_score_results = []
    for award, stats in award_score_stats.items():
        win_ratio = stats["wins"] / stats["plays"] if stats["plays"] > 0 else 0
        second_place_win_ratio = stats["second_place_win"] / stats["plays"] if stats["plays"] > 0 else 0
        award_score_results.append({
            "Award": award,
            "Plays": stats["plays"],
            "Wins": stats["wins"],
            "Win Rate (1st Place)": round(win_ratio*100,2),
            "Win Rate (2nd Place)": round(second_place_win_ratio*100,2)        
        })
    df_awards_score = pd.DataFrame(award_score_results)
    
    
    
    # Filtering and sorting
    df_cards = df_cards[df_cards["Plays"] > 0].sort_values(by=sortby, ascending=False).reset_index(drop=True)
    df_milestones = df_milestones[df_milestones["Plays"] > 0].sort_values(by="Win Rate", ascending=False).reset_index(drop=True)
    df_awards = df_awards[df_awards["Plays"] > 0].sort_values(by="Win Rate", ascending=False).reset_index(drop=True)
    df_awards_score = df_awards_score[df_awards_score["Plays"] > 0].sort_values(by="Win Rate (1st Place)", ascending=False).reset_index(drop=True)

    return df_cards , df_milestones, df_awards, df_awards_score








def card_gen(gamedict,logdict,gens,sortby, min_plays=0):
    # Initialize dictionaries to aggregate data across all games
    cards_stats = defaultdict(lambda: {"wins": 0, "plays": 0, "total_vp_diff": 0,"score_diff_sum": 0})

    # Loop through all games
    for game in logdict.keys():
        log = logdict[game]
        players = list(gamedict[game]['Player Names'])
        rank = list(gamedict[game]['Rank'])  # list of player ranks [1, 2, 3]
        vp = np.array(list(gamedict[game]['VP total'])).astype(int)  # list of player final scores
        generations = gamedict[game]['Generations'][0]
        elos = np.array(gamedict[game]['Elo']).astype(int)
        
        # Calculate expected scores for each player in the game
        pred_scores = calculate_expected_scores(elos)
    
        # Updated actual scores based on new win counting system
        actual_scores = np.array([2, 1, 0])
        
        # Calculate score differences
        score_diff = actual_scores - pred_scores    
        
    
        # Initialize dictionaries to store data for the current game
        player_cards = defaultdict(list)
        cards_by_generation = defaultdict(lambda: defaultdict(list))
        
        # Initialize generation counter
        current_generation = 1
        
        # Process each line in the log
        for line in log.split('\n'):
            line = line.strip()
            
            # Check for new generation
            if "New generation" in line:
                gen_info = re.findall(r'New generation (\d+)', line)
                if gen_info:
                    current_generation = int(gen_info[0])
    
            # Check for player actions involving playing cards
            for player in players:
                if line.startswith(player) and "plays card" in line:
                    card_name = re.findall(r'plays card ([A-Z\s\-]+)', line)
                    if card_name:
                        card_name = card_name[0].strip()
                        player_cards[player].append(card_name)
                        cards_by_generation[current_generation][player].append(card_name)



        # Analyze all cards played in the game
        for player in players:
            for gen in gens:  # Include generations 1, 2, and 3
                if player in cards_by_generation[gen]:            
                    player_rank = rank[players.index(player)]
                    player_vp = vp[players.index(player)]

                        
                    # Track card statistics
                    for card in cards_by_generation[gen][player]:

                        cards_stats[card]["plays"] += 1
                        
                        
                        if player_rank == 1:
                            cards_stats[card]['score_diff_sum'] += score_diff[0]
                            
                        if player_rank == 2:
                            cards_stats[card]['score_diff_sum'] += score_diff[1]  
                                                                            
                        if player_rank == 3:
                            cards_stats[card]['score_diff_sum'] += score_diff[2]  
    
                        
                        
                        if player_rank == 1:
                            cards_stats[card]["wins"] += 1
                            

                    
                                
    
    # Create separate DataFrames for cards, milestones, and awards
    # Cards DataFrame
    card_results = []
    for card, stats in cards_stats.items():
        win_ratio = stats["wins"] / stats["plays"] if stats["plays"] > 0 else 0
        wap =  stats["score_diff_sum"] / stats["plays"] if stats["plays"] > 0 else 0
        card_results.append({
            "Card": card,
            "Plays": stats["plays"],
            "Wins": stats["wins"],
            "Win Rate": round(win_ratio*100,2),
            "WAP": round(wap,3),        
        })
    df_cards = pd.DataFrame(card_results)
    

    
    
    
    
    # Filtering and sorting
    df_cards = df_cards[df_cards["Plays"] > min_plays].sort_values(by=sortby, ascending=False).reset_index(drop=True)

    return df_cards 








