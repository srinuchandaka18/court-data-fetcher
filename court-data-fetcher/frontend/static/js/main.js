// Global state
let isSearching = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Court Data Fetcher initialized');
    
    // Initialize form
    populateYears();
    
    // Add event listeners
    const searchForm = document.getElementById('searchForm');
    searchForm.addEventListener('submit', handleFormSubmit);
    
    // Add input validation
    addInputValidation();
});

function populateYears() {
    const yearSelect = document.getElementById('filing_year');
    const currentYear = new Date().getFullYear();
    
    // Clear existing options except the first one
    yearSelect.innerHTML = '<option value="">Select Year</option>';
    
    // Add years from current year back to 1950
    for (let year = currentYear; year >= 1950; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }
}

function addInputValidation() {
    const caseNumberInput = document.getElementById('case_number');
    
    caseNumberInput.addEventListener('input', function(e) {
        // Remove invalid characters
        e.target.value = e.target.value.replace(/[^0-9A-Za-z/-]/g, '');
    });
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (isSearching) {
        return; // Prevent duplicate submissions
    }
    
    // Reset UI state
    hideError();
    hideResults();
    
    // Validate form
    const formData = new FormData(event.target);
    const validation = validateFormData(formData);
    
    if (!validation.valid) {
        displayError(validation.message);
        return;
    }
    
    // Start search
    isSearching = true;
    showLoading();
    updateSearchButton(true);
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            displayResults(result.data);
        } else {
            displayError(result.error || 'An error occurred while searching');
        }
        
    } catch (error) {
        console.error('Search error:', error);
        displayError('Network error: Please check your connection and try again');
    } finally {
        hideLoading();
        updateSearchButton(false);
        isSearching = false;
    }
}

function validateFormData(formData) {
    const case_type = formData.get('case_type');
    const case_number = formData.get('case_number');
    const filing_year = formData.get('filing_year');
    
    if (!case_type) {
        return { valid: false, message: 'Please select a case type' };
    }
    
    if (!case_number) {
        return { valid: false, message: 'Please enter a case number' };
    }
    
    if (!filing_year) {
        return { valid: false, message: 'Please select a filing year' };
    }
    
    return { valid: true };
}

function displayResults(data) {
    console.log('Displaying results:', data);
    
    // Update basic case information
    updateElement('parties-names', data.parties_names);
    updateElement('filing-date', data.filing_date);
    updateElement('next-hearing', data.next_hearing_date);
    updateElement('case-status', data.case_status);
    
    // Update search duration
    if (data.search_duration) {
        updateElement('search-duration', data.search_duration.toFixed(2));
    }
    
    // Display PDF links
    displayPdfLinks(data.pdf_links);
    
    showResults();
    
    // Smooth scroll to results
    document.getElementById('results').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value || 'Not available';
        
        // Add visual feedback for empty values
        if (!value || value === 'Not found' || value === 'Not available') {
            element.style.color = '#9ca3af';
            element.style.fontStyle = 'italic';
        } else {
            element.style.color = '';
            element.style.fontStyle = '';
        }
    }
}

function displayPdfLinks(pdfLinks) {
    const pdfList = document.getElementById('pdf-list');
    pdfList.innerHTML = '';
    
    if (!pdfLinks || pdfLinks.length === 0) {
        pdfList.innerHTML = '<p class="no-docs">No documents available</p>';
        return;
    }
    
    pdfLinks.forEach((pdf, index) => {
        const pdfItem = document.createElement('div');
        pdfItem.className = 'document-item';
        
        const documentInfo = document.createElement('div');
        documentInfo.className = 'document-info';
        
        const documentTitle = document.createElement('div');
        documentTitle.className = 'document-title';
        documentTitle.textContent = pdf.title || `Document ${index + 1}`;
        
        documentInfo.appendChild(documentTitle);
        
        const downloadBtn = document.createElement('a');
        downloadBtn.className = 'download-btn';
        downloadBtn.href = `/download_pdf?url=${encodeURIComponent(pdf.url)}`;
        downloadBtn.target = '_blank';
        downloadBtn.textContent = 'Download';
        
        pdfItem.appendChild(documentInfo);
        pdfItem.appendChild(downloadBtn);
        pdfList.appendChild(pdfItem);
    });
}

function displayError(message) {
    document.getElementById('error-message').textContent = message;
    showError();
    
    // Smooth scroll to error
    document.getElementById('error').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
    });
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showResults() {
    document.getElementById('results').classList.remove('hidden');
}

function hideResults() {
    document.getElementById('results').classList.add('hidden');
}

function showError() {
    document.getElementById('error').classList.remove('hidden');
}

function hideError() {
    document.getElementById('error').classList.add('hidden');
}

function updateSearchButton(isLoading) {
    const searchBtn = document.getElementById('searchBtn');
    const btnText = searchBtn.querySelector('.btn-text');
    const btnSpinner = searchBtn.querySelector('.btn-spinner');
    
    if (isLoading) {
        searchBtn.disabled = true;
        btnText.textContent = 'Searching...';
        btnSpinner.style.display = 'inline';
    } else {
        searchBtn.disabled = false;
        btnText.textContent = 'Search Case';
        btnSpinner.style.display = 'none';
    }
}

function startNewSearch() {
    // Clear form
    document.getElementById('searchForm').reset();
    
    // Hide results and errors
    hideResults();
    hideError();
    
    // Scroll to form
    document.getElementById('searchForm').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

function printResults() {
    window.print();
}
