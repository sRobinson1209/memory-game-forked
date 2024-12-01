// Rhythm and input variables
let rhythm = [];
let userInput = [];
let startTime;
let index = 0;
let isPlaying = false;
let canvas, ctx;

// Timer variables
let stopwatchInterval;
let stopwatchDisplay = document.getElementById("stopwatch");   // Stopwatch display element
let stopwatchLog = document.getElementById("stopwatch-log");   // Log display element

// Variables for visual cue animation
const beatDuration = 1000;  // Total time for a beat to visually warn the player
const beatRadius = 100;     // Size of the fully expanded circle
let activeCircles = [];

// Game state variables
let currentStopwatchValue = 0; 
let playerTime = 0; //The time since the player's last input
let accumulatedTime = 0; //All the beat times added together. 
let gameMode; 
let currentRound = 1; 
let mistakes = 0; //The number of missed beats you've made so far, for survival mode. 
let tolerance = 0.15; //How lenient the game is on accepting a late/early input. 
let beatNumber = 4; //the number of rhythm beats to generate. Set to 4 by default.
let points = 0; 

/**
 * Initializes the canvas and context after the DOM is fully loaded.
 * Sets up the drawing area for visual rhythm cues.
 */
function initializeCanvas() 
{
    canvas = document.getElementById('canvas');
    
    if (canvas) 
    {
        ctx = canvas.getContext('2d');
        
        if (!ctx) 
        {
            console.error("Canvas context is not available!");
        } 
        else 
        {
            console.log("Canvas and context initialized successfully.");
        }
    } 

    else 
    {
        console.error("Canvas element is not found!");
    }
}

// Function to show the mode selection menu
function showModeSelectionMenu() 
{
    document.getElementById('mode-selection-menu').style.display = 'flex';
    document.getElementById('feedback').textContent = "Waiting for game mode selection...";  // Update feedback
}

// Event listeners for mode buttons
document.getElementById('relaxed-mode-button').addEventListener('click', () => startGame('Relaxed'));
document.getElementById('survival-mode-button').addEventListener('click', () => startGame('Survival'));

// Show the menu when the page loads without starting the game
document.addEventListener('DOMContentLoaded', showModeSelectionMenu);

/**
 * Records player input when spacebar is pressed and evaluates timing.
 */
document.addEventListener('keydown', (event) => 
{
    if (event.code === 'Space' && isPlaying) 
    {
        const currentTime = (performance.now() - startTime) / 1000;
        userInput.push(currentTime);

        /*
        These next few lines of code took hours of debugging. The only purpose of the playerTime variable is for the actual value side of the 
        history of log beats. Originally, I had a seperate timer for this, but that stopped working for some reason and I couldn't figure out why,
        so now the solution is just dependant on the userInput time, which was always stable. currentTime keeps counting up from when the player side
        initially starts until the game stops, so after adding it to playerTime, it needed to be subtracted from the total time of the accumulated beats
        so far so it would show a number that's under the time of the actual beat. Meaning, on beat 2, showing .78/.9 instead of 1.5/.9, despite both being
        registered as correct technically. 
        */
        playerTime = 0;
        playerTime += currentTime;
        playerTime -= accumulatedTime;  
        
        logBeat(rhythm[index], playerTime);

        accumulatedTime += rhythm[index];

        // Log the cumulative expected time and captured stopwatch value
        
        index++;

        console.log("User pressed space, registered input:", playerTime.toFixed(2));

        if (index === rhythm.length) 
        {
            isPlaying = false;
            clearInterval(stopwatchInterval);      // Stop the main stopwatch
            evaluateInput();
        }
    }
});

// Function to start the game based on selected mode
async function startGame(selectedMode) 
{
    console.log("Game starting with mode:", selectedMode);  // Debug log
    gameMode = selectedMode;  // Set the game mode

    currentRound = 1;  // Reset to the first round
    updateGameInfo();  // Set initial values for round and mode display

    document.getElementById('mode-selection-menu').style.display = 'none';  // Hide the menu
    document.getElementById('feedback').textContent = "Game starting...";  // Update feedback
    await new Promise(resolve => setTimeout(resolve, 1000)) //Wait for a sec so the previous line shows

    initializeCanvas();  // Initialize canvas
    fetchRhythm();       // Fetch rhythm only after mode selection
    requestAnimationFrame(drawCircles);  // Start drawing circles
}

/**
 * Progresses the game to the next round, resetting the round specific variables. 
 */
function nextRound() 
{
    rhythm = [];
    userInput = [];
    index = 0;
    activeCircles = [];
    stopwatchLog.innerHTML = "";  // Clear the log when progressing rounds
    currentRound++;
    accumulatedTime = 0;

    if(gameMode === 'Survival')
    {
        points += 10;
    }

    updateGameInfo()

    document.getElementById('feedback').textContent = "Fetching new rhythm...";
    fetchRhythm();
}

// Quit the game and return to the mode selection menu
function quitGame() 
{
    // Hide game elements
    document.getElementById('feedback').textContent = "Waiting for game mode selection...";
    document.getElementById('next-round').style.display = 'none';
    document.getElementById('quit-button').style.display = 'none';
    document.getElementById('stopwatch').textContent = "0.00";
    document.getElementById('stopwatch-log').innerHTML = "";  // Clear the log

    // Reset core game variables
    currentRound = 1;
    mistakes = 0; 
    tolerance = 0.15; 
    accumulatedTime = 0;
    stopwatchLog.innerHTML = "";
    rhythm = [];
    userInput = [];
    index = 0;
    activeCircles = [];

    // Show the mode selection menu
    document.getElementById('mode-selection-menu').style.display = 'flex';
    isPlaying = false;  // Ensure no ongoing game continues

    console.log("Game quit and reset. Ready for new game mode selection.");
}

/**
 * Fetches the rhythm from the Flask backend and triggers rhythm playback.
 */
async function fetchRhythm() 
{
    try 
    {

        //Set number of beat and thresehold variables.
        if ((currentRound % 3) == 0) 
        {
            beatNumber++;
        }

        if((gameMode === 'Survival') && (currentRound % 5 == 0)) 
        {
            tolerance = tolerance/1.1;
            console.log("Thresehold updated. New thresehold: " + tolerance);
        }



        const response = await fetch('http://127.0.0.1:5000/generate_rhythm?length=' + beatNumber);
        const data = await response.json();

        console.log("Rhythm data received:", data);

        if (data && data.rhythm) 
        {
            rhythm = data.rhythm.map(beat => beat); 
            playRhythm();          // Call a function to start the visual rhythm playback
        }
    } 
    catch (error) 
    {
        console.error('Error fetching rhythm:', error);
    }
}

/**
 * Plays the rhythm sequence with expanding visual circles for each beat.
 */
async function playRhythm() 
{
    document.getElementById('feedback').textContent = "Watch the rhythm...";
    document.getElementById('next-round').style.display = 'none';
    document.getElementById('quit-button').style.display = 'none';

    // Clear the active circles array to avoid overlap between phases
    activeCircles = [];

    // Sequentially play each beat in the rhythm
    for (let i = 0; i < rhythm.length; i++) 
    {
        const beatTime = rhythm[i] * 1000;  // Convert beat time to milliseconds
        
        // Start the main stopwatch for the current beat
        startStopwatch(rhythm[i]);  
        
        activeCircles.push({ start: performance.now(), beatTime: beatTime, phase: 'playback' });
        
        await new Promise((resolve) => setTimeout(resolve, beatTime));  // Wait for each beat
    }

    // After playback, switch to input phase and start player stopwatch
    prepareForInputPhase();
}

/**
 * Sets up the input phase, showing circles for each beat while player repeats the rhythm.
 */
async function prepareForInputPhase() 
{
    document.getElementById('feedback').textContent = "Repeat the rhythm...";
    isPlaying = true;
    startTime = performance.now();
    index = 0;

    activeCircles = [];

    // Show a new circle for each beat, prompting the player to match the timing
    for (let i = 0; i < rhythm.length; i++) 
    {
        const beatTime = rhythm[i] * 1000;

        // Start the stopwatch for the current beat
        startStopwatch(rhythm[i]);

        activeCircles.push({ start: performance.now(), beatTime: beatTime, phase: 'input' });

        await new Promise((resolve) => setTimeout(resolve, beatTime));
    }
}

/**
 * Logs the expected and actual time for each beat to the stopwatch log.
 * 
 * @param {number} expectedTime - The expected time for the beat.
 * @param {number} actualTime - The actual time when the player pressed the key.
 */
function logBeat(expectedTime, actualTime) 
{
    // Create a new log entry with expected and actual times
    const logEntry = document.createElement('div');
    logEntry.textContent = `Beat ${index + 1}: Expected - ${expectedTime.toFixed(2)}s, Actual - ${actualTime.toFixed(2)}s`;
    stopwatchLog.appendChild(logEntry);
}

/**
 * Compares user input timings to expected rhythm timings and provides feedback.
 */
async function evaluateInput() 
{
    let correctHits = 0;
    accumulatedTime = 0; //Reset cumuluatative time

    // Check each beat for accuracy
    for (let i = 0; i < rhythm.length; i++) 
    {
        accumulatedTime += rhythm[i];
        const expectedBeat = accumulatedTime;
        const playerInput = userInput[i];

        const difference = Math.abs(playerInput - expectedBeat);
        console.log(`Expected beat: ${expectedBeat}, Player input: ${playerInput}, Difference: ${difference}`);

        if (difference < tolerance) 
        {
            correctHits++;
        }

        else if (gameMode === 'Survival') 
        {
            mistakes++;
            console.log(`Missed beat! Total missed: ${mistakes}/3`);
        }
    }

    // Display results based on accuracy
    if (correctHits === rhythm.length) 
    {
        document.getElementById('feedback').textContent = "Perfect! You matched the rhythm.";
    } 
    else 
    {
        document.getElementById('feedback').textContent = `${correctHits}/${rhythm.length} correct!`;
    }

    // Check for survival mode game over
    if (gameMode === 'Survival' && mistakes >= 3) 
    {
        document.getElementById('feedback').textContent = "Game Over! You've missed too many beats.";
        await new Promise(resolve => setTimeout(resolve, 1000)) //Wait for a sec so the previous line shows
        quitGame();
    } 

    else 
    {
        document.getElementById('next-round').style.display = 'block';
        document.getElementById('quit-button').style.display = 'block';
    } 
}

// Function to update the displayed round and mode
function updateGameInfo() 
{
    document.getElementById('round-display').textContent = `Round: ${currentRound}`;
    document.getElementById('mode-display').textContent = `Mode: ${gameMode}`;

    if(gameMode === 'Survival')
    {
        document.getElementById('mistake-display').textContent = `Mistakes: ${mistakes}/3`;
        document.getElementById('mistake-display').style.display = 'block'
        document.getElementById('points-display').textContent = `Points: ${points}`;
        document.getElementById('points-display').style.display = 'block'
    }  
}

/**
 * Draws the expanding and static circles for visual rhythm cues.
 */
function drawCircles() 
{
    if (!ctx) 
    {
        console.error("Canvas context is not initialized.");
        return;
    }
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);  // Clear canvas before each frame
    drawTargetCircle();

    const currentTime = performance.now();

    // Draw active circles for playback and input phases
    activeCircles = activeCircles.filter(circle => 
    {
        const elapsedTime = currentTime - circle.start;
        const progress = elapsedTime / circle.beatTime;  // Use the specific beat duration for animation
        
        // Remove the circle after its full duration has passed
        if (progress >= 1) return false;

        const radius = beatRadius * progress;
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, radius, 0, Math.PI * 2);

        // Set circle color based on phase
        if (circle.phase === 'playback') 
        {
            ctx.strokeStyle = "white";
        } 
        else if (circle.phase === 'input') 
        {
            ctx.strokeStyle = "green";
        }

        ctx.stroke();
        return true;
    });

    requestAnimationFrame(drawCircles);
}

/**
 * Draws the static target circle on the canvas.
 */
function drawTargetCircle() 
{
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, beatRadius, 0, Math.PI * 2);
    ctx.strokeStyle = "gray";
    ctx.stroke();
}

/**
 * Starts the stopwatch and updates the display up to the target cumulative beat time.
 * 
 * @param {number} cumulativeTime - The cumulative time in seconds for the current beat.
 */
function startStopwatch(cumulativeTime) 
{
    let currentTime = 0;
    clearInterval(stopwatchInterval);

    // Update the main stopwatch display every 10 milliseconds
    stopwatchInterval = setInterval(() => 
    {
        currentTime += 0.01;  // Increment time by 10ms
        currentStopwatchValue = currentTime;
        stopwatchDisplay.textContent = `${currentStopwatchValue.toFixed(2)} / ${cumulativeTime.toFixed(2)}`;  
        
        // Stop the stopwatch interval when reaching the target cumulative time
        if (currentTime >= cumulativeTime) 
        {
            clearInterval(stopwatchInterval);
        }
    }, 10);
}

//A simple accessor, figured it might be useful for passing points value to the website.
function returnPoints()
{
    return points;
}