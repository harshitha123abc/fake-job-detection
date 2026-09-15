document.addEventListener('DOMContentLoaded', function() {
    const checkBtn = document.getElementById('checkBtn');
    const resultDiv = document.getElementById('result');
    const statusDiv = document.getElementById('status');
    const scoreFill = document.getElementById('scoreFill');
    const scoreSpan = document.getElementById('score');
    const reasoningDiv = document.getElementById('reasoning');
    const agentBreakdownDiv = document.getElementById('agentBreakdown');

    checkBtn.addEventListener('click', async () => {
        checkBtn.disabled = true;
        checkBtn.textContent = 'Analyzing...';
        resultDiv.style.display = 'block';
        statusDiv.className = 'status loading';
        statusDiv.textContent = 'Analyzing job posting...';

        try {
            // Get the current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Extract job text from the page
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractJobText' });
            const jobText = response.jobText;

            if (!jobText || jobText.trim().length < 10) {
                throw new Error('No job posting text found on this page. Please make sure you\'re on a job posting page.');
            }

            // Send to API
            const apiResponse = await fetch('http://localhost:5000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'test123' // You should store this securely
                },
                body: JSON.stringify({
                    description: jobText
                })
            });

            if (!apiResponse.ok) {
                throw new Error(`API Error: ${apiResponse.status}`);
            }

            const result = await apiResponse.json();

            // Update UI
            updateResults(result);

        } catch (error) {
            console.error('Error:', error);
            statusDiv.className = 'status danger';
            statusDiv.textContent = `Error: ${error.message}`;
            scoreFill.style.width = '0%';
            scoreSpan.textContent = '0';
        } finally {
            checkBtn.disabled = false;
            checkBtn.textContent = 'Check This Job Posting';
        }
    });

    function updateResults(result) {
        const riskScore = result.risk_score || 0;
        const riskLevel = result.risk_level || 'Unknown';

        scoreSpan.textContent = riskScore;
        scoreFill.style.width = `${riskScore}%`;

        // Set status and colors
        if (riskLevel === 'Low') {
            statusDiv.className = 'status safe';
            scoreFill.className = 'score-fill safe-fill';
            statusDiv.textContent = '✅ Low Risk - Appears Legitimate';
        } else if (riskLevel === 'Medium') {
            statusDiv.className = 'status warning';
            scoreFill.className = 'score-fill warning-fill';
            statusDiv.textContent = '⚠️ Medium Risk - Exercise Caution';
        } else {
            statusDiv.className = 'status danger';
            scoreFill.className = 'score-fill danger-fill';
            statusDiv.textContent = '🚨 High Risk - Potential Scam';
        }

        // Show reasoning
        if (result.reasoning && result.reasoning.length > 0) {
            reasoningDiv.innerHTML = `<strong>Analysis:</strong><br>${result.reasoning.join('<br>')}`;
        }

        // Show agent breakdown
        if (result.agent_breakdown) {
            let breakdown = '<strong>Agent Analysis:</strong><br>';
            Object.entries(result.agent_breakdown).forEach(([agent, score]) => {
                const confidence = Math.round(score * 100);
                breakdown += `<div class="agent-result">${agent}: ${confidence}% confidence</div>`;
            });
            agentBreakdownDiv.innerHTML = breakdown;
        }
    }
});