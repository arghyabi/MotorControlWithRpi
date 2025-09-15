function fetchStatus() {
    const toggleBtn = document.getElementById('motorToggleBtn');
    fetch('motor.php')
        .then(res => res.json())
        .then(data => {
            document.getElementById('tankLevel').textContent =
                (typeof data.tankLevel === 'number') ? `${data.tankLevel} cm` : 'Unknown';
            document.getElementById('motorStatus').textContent =
                data.motorStatus === 'ON' ? 'ON' : 'OFF';
            if (data.motorStatus === 'ON') {
                toggleBtn.textContent = 'Turn Motor OFF';
                toggleBtn.classList.add('on');
            } else {
                toggleBtn.textContent = 'Turn Motor ON';
                toggleBtn.classList.remove('on');
            }
            toggleBtn.disabled = false;
        })
        .catch(err => {
            document.getElementById('tankLevel').textContent = 'Error';
            document.getElementById('motorStatus').textContent = 'Error';
            toggleBtn.textContent = 'Network Error';
            toggleBtn.disabled = true;
            console.error('Fetch status error:', err);
        });
}

function setMotor(status) {
    fetch('motor.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `motorStatus=${status}`
    })
        .then(res => res.json())
        .then(() => fetchStatus())
        .catch(err => {
            alert('Failed to set motor status. Network error.');
            fetchStatus();
            console.error('Set motor error:', err);
        });
}

const motorToggleBtn = document.getElementById('motorToggleBtn');
motorToggleBtn.onclick = function() {
    motorToggleBtn.disabled = true;
    if (motorToggleBtn.classList.contains('on')) {
        setMotor('OFF');
    } else {
        setMotor('ON');
    }
};

fetchStatus();
setInterval(fetchStatus, 3000);
