function fetchStatus() {
    const toggleBtn = document.getElementById('motorToggleBtn');
    fetch('motor.php')
        .then(res => res.json())
        .then(data => {
            document.getElementById('tankLevel').textContent =
                (typeof data.tankLevel === 'number') ? `${data.tankLevel} cm` : 'Unknown';
            document.getElementById('motorStatus').textContent =
                data.motorStatus === 'ON' ? 'ON' : 'OFF';

            // Update mode display
            const mode = data.mode || 'Auto';
            updateModeValue(mode);

            // Control motor button based on mode
            const isManualMode = mode === 'Manual';

            if (data.motorStatus === 'ON') {
                toggleBtn.textContent = 'Turn Motor OFF';
                toggleBtn.classList.add('on');
            } else {
                toggleBtn.textContent = 'Turn Motor ON';
                toggleBtn.classList.remove('on');
            }

            // Enable/disable motor button based on mode
            toggleBtn.disabled = !isManualMode;

            if (!isManualMode) {
                toggleBtn.title = 'Motor control is disabled in Auto mode';
            } else {
                toggleBtn.title = '';
            }

            // Update dropdowns and selected values
            updateConfigValue('valve1Duration', data.valve1Duration);
            updateConfigValue('valve2Duration', data.valve2Duration);
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

function setConfig(key, value) {
    fetch('motor.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `${key}=${value}`
    })
        .then(res => res.json())
        .then(() => fetchStatus())
        .catch(err => {
            alert('Failed to set config. Network error.');
            fetchStatus();
            console.error('Set config error:', err);
        });
}

function populateDropdown(selectId) {
    const select = document.getElementById(selectId);
    for (let i = 1; i <= 15; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `${i} min`;
        select.appendChild(option);
    }
}

function updateConfigValue(id, value) {
    const select = document.getElementById(id);
    const selectedSpan = document.getElementById(`selected${id.charAt(0).toUpperCase() + id.slice(1)}`);
    if (value) {
        select.value = value;
        selectedSpan.textContent = `${value} min`;
    }
}

function updateModeValue(mode) {
    const select = document.getElementById('modeSelect');
    const selectedSpan = document.getElementById('selectedMode');
    if (mode) {
        select.value = mode;
        selectedSpan.textContent = mode;
    }
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

// Populate dropdowns
populateDropdown('valve1Duration');
populateDropdown('valve2Duration');

// Add event listeners for dropdowns
document.getElementById('valve1Duration').addEventListener('change', function() {
    setConfig('valve1Duration', this.value);
});

document.getElementById('valve2Duration').addEventListener('change', function() {
    setConfig('valve2Duration', this.value);
});

// Add event listener for mode selection
document.getElementById('modeSelect').addEventListener('change', function() {
    setConfig('mode', this.value);
});

fetchStatus();
setInterval(fetchStatus, 3000);
