document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileUpload = document.getElementById('file-upload');
    const uploadBtn = document.getElementById('upload-btn');
    const progressContainer = document.getElementById('progress-container');
    const uploadProgress = document.getElementById('upload-progress');
    const progressText = document.getElementById('progress-text');
    const resultsContainer = document.getElementById('results-container');

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const files = fileUpload.files;
        if (files.length === 0) {
            alert('Please select at least one PDF file.');
            return;
        }

        // Show progress container
        progressContainer.classList.remove('d-none');
        uploadProgress.style.width = '0%';
        progressText.textContent = 'Preparing files...';
        resultsContainer.innerHTML = '';
        
        // Create FormData
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        // Disable upload button
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        // Simulate progress (actual progress tracking not supported by fetch API)
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += 5;
                uploadProgress.style.width = progress + '%';
                
                if (progress < 30) {
                    progressText.textContent = 'Uploading files...';
                } else if (progress < 60) {
                    progressText.textContent = 'Extracting text from PDFs...';
                } else {
                    progressText.textContent = 'Processing with AI and generating embeddings...';
                }
            }
        }, 500);
        
        // Send the files to the server
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            clearInterval(progressInterval);
            uploadProgress.style.width = '100%';
            progressText.textContent = 'Processing complete!';
            return response.json();
        })
        .then(data => {
            // Display results
            displayResults(data);
            
            // Re-enable upload button
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-cloud-upload-alt me-2"></i>Upload and Process';
        })
        .catch(error => {
            clearInterval(progressInterval);
            uploadProgress.style.width = '100%';
            uploadProgress.classList.remove('bg-primary', 'progress-bar-animated', 'progress-bar-striped');
            uploadProgress.classList.add('bg-danger');
            progressText.textContent = 'Error: ' + error.message;
            
            // Re-enable upload button
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-cloud-upload-alt me-2"></i>Upload and Process';
        });
    });
    
    // Function to display results
    function displayResults(results) {
        resultsContainer.innerHTML = '<h4 class="mb-3">Processing Results</h4>';
        
        if (!Array.isArray(results)) {
            resultsContainer.innerHTML += `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Invalid response from server
                </div>
            `;
            return;
        }
        
        if (results.length === 0) {
            resultsContainer.innerHTML += `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No files were processed
                </div>
            `;
            return;
        }
        
        results.forEach(result => {
            const statusClass = result.status === 'success' ? 'success' : 'error';
            const statusIcon = result.status === 'success' ? 'check-circle' : 'times-circle';
            
            let fileItemHtml = `
                <div class="file-item ${statusClass} mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5>
                                <i class="fas fa-file-pdf me-2"></i>
                                ${result.filename}
                            </h5>
                            <p class="mb-1">
                                <span class="badge bg-${result.status === 'success' ? 'success' : 'danger'}">
                                    <i class="fas fa-${statusIcon} me-1"></i>
                                    ${result.status === 'success' ? 'Success' : 'Error'}
                                </span>
                                <span class="ms-2">${result.message}</span>
                            </p>
                        </div>
                    </div>
            `;
            
            // Add metadata display for successful processing
            if (result.status === 'success' && result.document_ids && result.document_ids.length > 0) {
                fileItemHtml += `
                    <div class="file-meta mt-2">
                        <p class="mb-1"><strong>Document IDs:</strong> ${result.document_ids.length} chunks stored in database</p>
                        <p class="mb-0">
                            <span class="expand-btn" onclick="toggleMetadata(this)">
                                <i class="fas fa-chevron-down me-1"></i>
                                Show Document IDs
                            </span>
                        </p>
                        <div class="metadata-display mt-2" style="display: none;">
                            <pre>${JSON.stringify(result.document_ids, null, 2)}</pre>
                        </div>
                    </div>
                `;
            }
            
            fileItemHtml += `</div>`;
            resultsContainer.innerHTML += fileItemHtml;
        });
    }
});

// Function to toggle metadata display
function toggleMetadata(element) {
    const metadataDisplay = element.parentElement.nextElementSibling;
    const isHidden = metadataDisplay.style.display === 'none';
    
    metadataDisplay.style.display = isHidden ? 'block' : 'none';
    
    // Update button text
    if (isHidden) {
        element.innerHTML = '<i class="fas fa-chevron-up me-1"></i>Hide Document IDs';
    } else {
        element.innerHTML = '<i class="fas fa-chevron-down me-1"></i>Show Document IDs';
    }
}
