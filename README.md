# terraforming-mars-dataset
A dataset of 1,556 games from the board game Terraforming Mars.

All games are in 3-player basegame format with corporate era included. The games were played by the top 25 players in the world on Board Game Arena (BGA) for 3-player setting in season 18.

# Prelude update

The /prelude directory now contains stats from the current season 19 on BGA. These are 3-player games in basegame + prelude format. 

The current stats are computed based 1,616 games played by the current top 25 players.


# Technical details
Data is included as a python dictionary file saved as both a pickle and JSON file. 

My system had the current versions when saving the data.

python 3.8.2

numpy 1.24.4

pandas 1.3.3

matplotlib 3.3.2

# Overview of data 
An overview of the data can be found in this post:
https://www.reddit.com/r/TerraformingMarsGame/comments/1frbj1b/analysis_of_1500_3p_arena_games_base/

A full card win rate list is included in the repository as "cards.txt". The final corporation win rates for the Arena Season 18 Champion RoyalRook are also available as "RoyalRook_corps.txt".
