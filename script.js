let playerCount = 2;  // Default to 2 players
let players = [];

function showPlayerInputs() {
    const container = document.getElementById('playerContainer');
    container.innerHTML = '';
    
    if (playerCount === 2) {
        for (let i = 0; i < 2; i++) {
            container.innerHTML += `<label>Player ${i + 1} Name:</label><input type="text" id="player${i}"><br>`;
        }
    } else if (playerCount === 4) {
        for (let i = 0; i < 4; i++) {
            container.innerHTML += `<label>Player ${i + 1} Name:</label><input type="text" id="player${i}"><br>`;
        }
    }
    container.innerHTML += `<label>Team 1 Score:</label><input type="number" id="score0"><br>`;
    container.innerHTML += `<label>Team 2 Score:</label><input type="number" id="score1"><br>`;
    container.innerHTML += `<button onclick="submitScores()">Submit Scores</button>`;
}

function setPlayerCount(count) {
    playerCount = count;
    showPlayerInputs();
}

function submitScores() {
    players = [];
    for (let i = 0; i < playerCount; i++) {
        players.push({name: elo_rating.getElementById(`player${i}`).value});
    }
    var team1Score = parseInt(elo_rating.getElementById('score0').value);
    var team2Score = parseInt(elo_rating.getElementById('score1').value);

    var data = {
        "player_names": players.map(player => player.name),
        "team1_score": team1Score,
        "team2_score": team2Score,
        "game_type": playerCount === 2 ? "one player" : "two player"
    };

    console.log('Sending data:', data);

    fetch('http://localhost:8000/update_elo_rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json(); // Parse JSON data from the response
    })
    .then(result => {
        console.log('Received result:', result);
        displayEloScores(result); // Pass the result to the function that updates the UI
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function displayEloScores(result) {
    const scoreBoard = elo_rating.getElementById('scoreBoard');
    scoreBoard.innerHTML = '';

    const previousScores = result.previous_scores;
    const updatedScores = result.updated_scores;

    for (let player in previousScores) {
        scoreBoard.innerHTML += `<p>${player}: Previous ELO: ${previousScores[player]}, Updated ELO: ${updatedScores[player]}</p>`;
    }

    document.getElementById('finalScores').style.display = 'block';
}
