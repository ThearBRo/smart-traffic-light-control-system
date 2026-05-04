
    let trafficChart;
    document.addEventListener('DOMContentLoaded', function() {
        const ctx = document.getElementById('trafficChart').getContext('2d');
        
        trafficChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Road A', 'Road B', 'Road C', 'Road D'],
                datasets: [{
                    label: 'Total Open Times',
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        refreshChart();
    });

    function refreshChart() {
        fetch('/get_stats')
        .then(res => res.json())
        .then(data => {

            const stats = data.stats;
            
            trafficChart.data.datasets[0].data = [
                stats.A, 
                stats.B, 
                stats.C, 
                stats.D
            ];
            

            trafficChart.update();
            console.log("Chart updated with:", stats);
    })
    .catch(err => console.error("Error fetching data:", err));
}


    function autoDouble() {
        fetch('/double', { method: 'POST'})
        .then(res => res.json())
        .then(data => console.log('open double road'))
    }

    document.getElementById('timerForm').addEventListener('submit', function(e) {
        e.preventDefault();
    const road = document.getElementById('roadSelect').value;
    const ms = document.getElementById('msInput').value;
    const statusDiv = document.getElementById('statusMessage');

    statusDiv.innerHTML = "Sending...";
    statusDiv.className = "status-msg text-center text-primary";

        fetch(`/set_timer/${road}/${ms * 1000}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
                    if(data.status === "Success") {
                        statusDiv.innerHTML = `âœ… Road ${road} updated to ${ms} seconds!`;
                        statusDiv.className = "status-msg text-center text-success";
                    } else {
                        statusDiv.innerHTML = "âŒ Error sending to Arduino";
                        statusDiv.className = "status-msg text-center text-danger";
                    }
                })
            }
    )


    function autoTraffic(){
        fetch('/auto', { method: 'POST'})
        .then(res => res.json())
        .then(data => console.log("Arduino: " + data.arduino_msg));
    }

    function controlRoad(road) {
        fetch('/open_road/' + road, { method: 'POST' })
        .then(res => res.json())
        .then(data => {

            refreshChart();   
            
            console.log('Road opened {data}')
        });
    }

    function updateTimer() {
        const time = document.getElementById('timerInput').value;
        fetch('/set_timer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ time: time })
        })
        .then(res => res.json())
        .then(data => console.log("Status: " + data.arduino_msg));
    }

    function exportFileCsc() {
        fetch('/export_traffic')
        .then(() => console.log('Exported data'))
    }