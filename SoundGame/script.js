//TASK #1: display the interface with the constant looping
//TASK #2: add in the user input part


// Fetch and generate the melody
fetch('http://127.0.0.1:5000/generate_melody')
    .then(response => response.json())
    .then(data => {
        console.log("Generated Melody:", data.melody);
        console.log("Level:", data.level);
        console.log("Score:", data.score);
    })
    .catch(error => console.error('Error:', error));

// Play the generated melody
fetch('http://127.0.0.1:5000/play_melody')
    .then(response => response.json())
    .then(data => {
        console.log(data.status);
    })
    .catch(error => console.error('Error:', error));

/**
 * next coding sesh, you need to get thge buttons to show
 */
