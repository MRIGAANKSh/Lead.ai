document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('agentForm');
    const statusMessage = document.getElementById('statusMessage');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const phoneNumber = document.getElementById('phoneNumber').value;
        const task = document.getElementById('task').value;

        // Show loading status
        statusMessage.textContent = 'Initiating voice call...';
        statusMessage.classList.remove('d-none', 'alert-danger');
        statusMessage.classList.add('alert-info');

        try {
            const response = await fetch('/api/initiate-call', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phoneNumber,
                    task
                })
            });

            const data = await response.json();

            if (response.ok) {
                statusMessage.textContent = 'Voice call initiated successfully!';
                statusMessage.classList.remove('alert-danger');
                statusMessage.classList.add('alert-success');
                form.reset();
            } else {
                throw new Error(data.message || 'Failed to initiate call');
            }
        } catch (error) {
            statusMessage.textContent = `Error: ${error.message}`;
            statusMessage.classList.remove('alert-success', 'alert-info');
            statusMessage.classList.add('alert-danger');
        }
    });
}); 