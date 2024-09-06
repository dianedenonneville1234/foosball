import pandas as pd
import math
import numpy as np

# Load players data
players = pd.read_csv('players.csv')

def getEloRating(playerName):
    if playerName in players['Name'].values:
        return float(players.loc[players['Name'] == playerName, 'Score'])
    else:
        players.loc[len(players.index)] = [playerName, 1000.0, 0]         
        return 1000.0

def k_score(playerName):
    if playerName in players['Name'].values:
        game_num = float(players.loc[players['Name'] == playerName, 'Games'])
        return 50 / (1 + game_num / 300)
    else:      
        return 50 / (1 + 1 / 300)

def probability_one(r1, r2):
    return 1 / (1 + math.pow(10, (r1 - r2) / 400))

def probability_two(r1, r2, r3, r4):
    ep1 = (1.0 / (1.0 + math.pow(10, (r3 - r1) / 500)) + 1.0 / (1.0 + math.pow(10, (r4 - r1) / 500))) / 2
    ep2 = (1.0 / (1.0 + math.pow(10, (r3 - r2) / 500)) + 1.0 / (1.0 + math.pow(10, (r4 - r2) / 500))) / 2
    ep3 = (1.0 / (1.0 + math.pow(10, (r1 - r3) / 500)) + 1.0 / (1.0 + math.pow(10, (r2 - r3) / 500))) / 2
    ep4 = (1.0 / (1.0 + math.pow(10, (r1 - r4) / 500)) + 1.0 / (1.0 + math.pow(10, (r2 - r4) / 500))) / 2
    et1 = np.mean([ep1, ep2])
    et2 = np.mean([ep3, ep4])
    return [ep1, ep2, ep3, ep4, et1, et2]

def update_elo_rating(t1, t2, player_data, game_type='one player'):
    previous_scores = {}
    updated_scores = {}

    if game_type == 'one player':
        p1, p2 = player_data[0].lower(), player_data[1].lower()
        ra, rb = getEloRating(p1), getEloRating(p2)
        previous_scores = {p1: ra, p2: rb}
        ka, kb = k_score(p1), k_score(p2)
        outcome_a = t1 / (t1 + t2)
        expected_a = probability_one(ra, rb)
        expected_b = probability_one(rb, ra)
        ra += ka * (-outcome_a + expected_a)
        rb += kb * ((outcome_a - 1) + expected_b)
        ra, rb = max(ra, 1000), max(rb, 1000)
        updated_scores = {p1: ra, p2: rb}
        players.loc[players['Name'] == p1, 'Score'] = ra
        players.loc[players['Name'] == p2, 'Score'] = rb
        players.loc[players['Name'].isin([p1, p2]), 'Games'] += 1

    elif game_type == 'two player':
        p1, p2, p3, p4 = player_data[0].lower(), player_data[1].lower(), player_data[2].lower(), player_data[3].lower()
        ra, rb, rc, rd = getEloRating(p1), getEloRating(p2), getEloRating(p3), getEloRating(p4)
        previous_scores = {p1: ra, p2: rb, p3: rc, p4: rd}
        ka, kb, kc, kd = k_score(p1), k_score(p2), k_score(p3), k_score(p4)
        ep1, ep2, ep3, ep4, et1, et2 = probability_two(ra, rb, rc, rd)
        p = 2 + math.pow(np.log10(abs(t1 - t2) + 1), 3)
        f1, f2 = (1, -1) if t1 > t2 else (-1, 1)
        new_scores = np.array([ra, rb, rc, rd]) + np.array([f1, f1, f2, f2]) * np.array([ka, kb, kc, kd]) * p * abs(np.array([et1, et1, et1, et1]) - np.array([ep1, ep2, ep3, ep4]))
        new_scores = np.maximum(new_scores, 1000)
        updated_scores = {p1: new_scores[0], p2: new_scores[1], p3: new_scores[2], p4: new_scores[3]}
        players.loc[players['Name'] == p1, 'Score'] = new_scores[0]
        players.loc[players['Name'] == p2, 'Score'] = new_scores[1]
        players.loc[players['Name'] == p3, 'Score'] = new_scores[2]
        players.loc[players['Name'] == p4, 'Score'] = new_scores[3]

        players.loc[players['Name'].isin([p1, p2, p3, p4]), 'Games'] += 1

    players.to_csv('players.csv', mode='w', index=False)
    return {"previous_scores": previous_scores, "updated_scores": updated_scores}

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows all origins; adjust for production as needed

@app.route('/update_elo_rating', methods=['POST'])
def update_elo_rating_route():
    data = request.get_json()
    player_names = data['player_names']
    team1_score = data['team1_score']
    team2_score = data['team2_score']
    game_type = data['game_type']

    # Call the existing update_elo_rating function
    result = update_elo_rating(team1_score, team2_score, player_names, game_type=game_type)
    
    return jsonify(result)

