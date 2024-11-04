// Rhythm and input variables
let rhythm = [];
let userInput = [];
let startTime;
let index = 0;
let isPlaying = false;
let canvas, ctx;

// Variables for visual cue animation
const beatDuration = 1000;  // Total time for a beat to visually warn the player
const beatRadius = 100;  // The size of the fully expanded circle
let activeCircles = [];

// Initialize the canvas and context after the DOM is fully loaded
function initializeCanvas() {
    canvas = document.getElementById('canvas');
    if (canvas) {
        ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error("Canvas context is not available!");
        } else {
            console.log("Canvas and context initialized successfully.");
        }
    } else {
        console.error("Canvas element is not found!");
    }
}

// Fetch the rhythm from the backend
async function fetchRhythm() {
    try {
        const response = await fetch('http://127.0.0.1:5000/generate_rhythm?length=4');
        const data = await response.json();

        console.log("Rhythm data received:", data);

        if (data && data.rhythm) {
            rhythm = data.rhythm;
            console.log("Rhythm sequence:", rhythm);
            playRhythm();
        } else {
            document.getElementById('feedback').textContent = "Error: Invalid rhythm data received";
        }

    } catch (error) {
        console.error('Error fetching rhythm:', error);
        document.getElementById('feedback').textContent = "Error: Unable to fetch rhythm";
    }
}

// Play the rhythm sequence
async function playRhythm() {
    document.getElementById('feedback').textContent = "Listen to the rhythm...";
    document.getElementById('play-again').style.display = 'none';

    // Clear the active circles array to avoid overlap between phases
    activeCircles = [];

    // Play each beat in the rhythm and create expanding circle for each beat
    for (let i = 0; i < rhythm.length; i++) {
        const beatTime = rhythm[i] * 1000;  // Get the duration of the current beat
        activeCircles.push({ start: performance.now(), beatTime: beatTime, phase: 'playback' });
        await new Promise((resolve) => setTimeout(resolve, beatTime));  // Wait for each beat
    }

    // After the playback, transition to the input phase
    prepareForInputPhase();
}

// Prepare for the input phase, creating circles for each beat, and delay each one
async function prepareForInputPhase() {
    document.getElementById('feedback').textContent = "Repeat the rhythm...";
    isPlaying = true;
    startTime = performance.now();
    index = 0;

    activeCircles = [];

    for (let i = 0; i < rhythm.length; i++) {
        const beatTime = rhythm[i] * 1000;

        // Create the expanding circle for input phase
        activeCircles.push({ start: performance.now(), beatTime: beatTime, phase: 'input' });

        // Add delay between each beat for input phase
        await new Promise((resolve) => setTimeout(resolve, beatTime));
    }
}

// Capture spacebar presses
document.addEventListener('keydown', (event) => {
    if (event.code === 'Space' && isPlaying) {
        const currentTime = (performance.now() - startTime) / 1000;
        userInput.push(currentTime);
        index++;

        console.log("User pressed space, registered input:", currentTime);

        if (index === rhythm.length) {
            isPlaying = false;
            evaluateInput();
        }
    }
});

function evaluateInput() {
    let correctHits = 0;
    const tolerance = 0.3;  // Set to 0.1 seconds for more precision

    // Variable to accumulate the expected beat times
    let accumulatedTime = 0;

    // Compare each player input to the corresponding beat in the rhythm
    for (let i = 0; i < rhythm.length; i++) {
        accumulatedTime += rhythm[i];  // Sum up the time of the previous beats
        const expectedBeat = accumulatedTime;  // This is now the cumulative time of the beat
        const playerInput = userInput[i];  // This is when the player pressed space

        // Calculate the difference between the player's input and the expected beat
        const difference = Math.abs(playerInput - expectedBeat);

        // Log the expected beat, player input, and the difference between them
        console.log(`Expected beat: ${expectedBeat}, Player input: ${playerInput}, Difference: ${difference}`);

        // If the difference is within the tolerance, consider it a correct hit
        if (difference < tolerance) {
            correctHits++;
        }
    }

    // Display feedback based on how many correct hits the player got
    if (correctHits === rhythm.length) {
        document.getElementById('feedback').textContent = "Perfect! You matched the rhythm.";
    } else {
        document.getElementById('feedback').textContent = `${correctHits}/${rhythm.length} correct!`;
    }

    // Show the "Play Again" button
    document.getElementById('play-again').style.display = 'block';
}

// Visual cue animation logic
function drawCircles() {
    if (!ctx) {
        console.error("Canvas context is not initialized.");
        return;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);  // Clear canvas before each frame

    // Draw the static target circle
    drawTargetCircle();

    const currentTime = performance.now();

    // Draw active circles for playback and input phases
    activeCircles = activeCircles.filter(circle => {
        const elapsedTime = currentTime - circle.start;
        const progress = elapsedTime / beatDuration;
        if (progress >= 1) return false;

        const radius = beatRadius * progress;
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, radius, 0, Math.PI * 2);

        // Color the circles differently during playback and input phases
        if (circle.phase === 'playback') {
            ctx.strokeStyle = "white";
        } else if (circle.phase === 'input') {
            ctx.strokeStyle = "green";  // Green for player's input
        }

        ctx.stroke();
        return true;
    });

    requestAnimationFrame(drawCircles);
}

// Draw the static target circle
function drawTargetCircle() {
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, beatRadius, 0, Math.PI * 2);
    ctx.strokeStyle = "gray";  // Static target circle in gray
    ctx.stroke();
}

// Reset the game state to play again
function resetGame() {
    rhythm = [];
    userInput = [];
    index = 0;
    activeCircles = [];  // Reset active circles when the game restarts
    document.getElementById('feedback').textContent = "Fetching new rhythm...";
    fetchRhythm();
}

// Ensure canvas is initialized after DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeCanvas();  // Initialize canvas after DOM is ready
    fetchRhythm();
    requestAnimationFrame(drawCircles);  // Ensure the animation loop continues
});
