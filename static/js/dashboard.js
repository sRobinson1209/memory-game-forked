// Data passed from Flask
const gameData = {{ game_data, tojson }};
        
// Prepare data for score percentage pie chart
const scoreData = {
    labels: Object.keys(gameData),
    datasets: [{
        data: Object.values(gameData).map(game => game.score_percentage),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
        hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
    }]
};

// Prepare data for time played pie chart
const timeData = {
    labels: Object.keys(gameData),
    datasets: [{
        data: Object.values(gameData).map(game => game.time_played),
        backgroundColor: ['#4BC0C0', '#FF9F40', '#9966FF'],
        hoverBackgroundColor: ['#4BC0C0', '#FF9F40', '#9966FF']
    }]
};

// Render score percentage pie chart
const ctx1 = document.getElementById('scorePieChart').getContext('2d');
new Chart(ctx1, {
    type: 'pie',
    data: scoreData,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return `${scoreData.labels[tooltipItem.dataIndex]}: ${scoreData.datasets[0].data[tooltipItem.dataIndex]}%`;
                    }
                }
            }
        }
    }
});

// Render time played pie chart
const ctx2 = document.getElementById('timePieChart').getContext('2d');
new Chart(ctx2, {
    type: 'pie',
    data: timeData,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        const minutes = timeData.datasets[0].data[tooltipItem.dataIndex];
                        return `${timeData.labels[tooltipItem.dataIndex]}: ${minutes} minutes`;
                    }
                }
            }
        }
    }
});