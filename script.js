document.getElementById('generateBtn').addEventListener('click', async () => {
    const btn = document.getElementById('generateBtn');
    const spinner = btn.querySelector('.spinner');
    const btnText = btn.querySelector('.btn-text');
    const statusPanel = document.getElementById('statusPanel');
    const statusMsg = document.getElementById('statusMsg');

    // UI Loading State
    spinner.classList.remove('hidden');
    btnText.style.opacity = '0';
    btn.disabled = true;
    statusPanel.classList.remove('hidden');
    statusMsg.innerText = "Initiating Vercel Cloud Runtime...";

    // Collect Data
    const payload = {
        script: document.getElementById('scriptType').value,
        count: parseInt(document.getElementById('imgCount').value, 10),
        seed: parseInt(document.getElementById('randomSeed').value, 10),
        custom_text: document.getElementById('customText').value.trim() || null
    };

    try {
        statusMsg.innerText = "Synthesizing manuscript images & markdown... (This may take up to 10s)";
        
        // Calling Vercel Serverless Function
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            let errorText = await response.text();
            throw new Error(`Server Error: ${response.status} - ${errorText}`);
        }

        statusMsg.innerText = "Downloading Artifacts...";
        
        // Receive ZIP Blob
        const blob = await response.blob();
        if (blob.size === 0) throw new Error("Received an empty file.");

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${payload.script}_dataset_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        a.remove();
        
        statusMsg.innerText = "Generation & Download Complete!";
        statusMsg.style.color = "#4ade80"; // Success green

    } catch (err) {
        statusMsg.innerText = err.message;
        statusMsg.style.color = "#f87171"; // Error red
        console.error(err);
    } finally {
        // Reset UI State
        spinner.classList.add('hidden');
        btnText.style.opacity = '1';
        btn.disabled = false;
        
        // Return color after 3s if error/success
        setTimeout(() => {
            statusMsg.style.color = "var(--text-muted)";
            statusPanel.classList.add('hidden');
        }, 5000);
    }
});
