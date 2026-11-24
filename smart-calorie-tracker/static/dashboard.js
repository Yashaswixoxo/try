// DOM Elements
const logoutBtn = document.getElementById('logoutBtn');
const userGreeting = document.getElementById('userGreeting');
const notification = document.getElementById('notification');
const dashboardUploadArea = document.getElementById('dashboardUploadArea');
const dashboardImageInput = document.getElementById('dashboardImageInput');
const dashboardDetectBtn = document.getElementById('dashboardDetectBtn');
const dashboardResultSection = document.getElementById('dashboardResultSection');

// Tab Management
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // Update active tab button
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`${tab}Tab`).classList.add('active');
    });
});

// Logout
logoutBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/logout');
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        showNotification('Logout failed', 'error');
    }
});

// Image Upload for Dashboard
dashboardUploadArea.addEventListener('click', () => {
    dashboardImageInput.click();
});

dashboardUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dashboardUploadArea.style.borderColor = '#8A9A7B';
});

dashboardUploadArea.addEventListener('dragleave', () => {
    dashboardUploadArea.style.borderColor = '#B8C5A8';
});

dashboardUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleDashboardImageUpload(files[0]);
    }
});

dashboardImageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleDashboardImageUpload(e.target.files[0]);
    }
});

let dashboardSelectedImage = null;

function handleDashboardImageUpload(file) {
    if (!file.type.startsWith('image/')) {
        showNotification('Please upload an image file', 'error');
        return;
    }
    
    dashboardSelectedImage = file;
    dashboardUploadArea.innerHTML = `
        <div class="upload-icon">✓</div>
        <p style="color: #6B8E5F; font-weight: 600;">${file.name}</p>
        <p class="text-small">Image ready for detection</p>
    `;
}

// Detect Calories (Dashboard)
dashboardDetectBtn.addEventListener('click', async () => {
    if (!dashboardSelectedImage) {
        showNotification('Please upload an image first', 'error');
        return;
    }
    
    const weight = document.getElementById('dashboardWeightInput').value;
    
    const formData = new FormData();
    formData.append('image', dashboardSelectedImage);
    formData.append('weight', weight);
    
    dashboardDetectBtn.disabled = true;
    dashboardDetectBtn.textContent = 'Detecting...';
    
    try {
        const response = await fetch('/detect-calorie', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayDashboardResult(data);
            showNotification('Calorie logged successfully!', 'success');
        } else {
            showNotification(data.error || 'Detection failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        dashboardDetectBtn.disabled = false;
        dashboardDetectBtn.textContent = 'Detect & Log Calories';
    }
});

function displayDashboardResult(data) {
    document.getElementById('dashboardFoodName').textContent = data.food_name.replace('_', ' ').toUpperCase();
    document.getElementById('dashboardConfidence').textContent = `${data.confidence}%`;
    document.getElementById('dashboardCalories').textContent = `${data.calories} kcal`;
    document.getElementById('dashboardWeight').textContent = `${data.weight}g`;
    
    dashboardResultSection.classList.remove('hidden');
    dashboardResultSection.scrollIntoView({ behavior: 'smooth' });
}

// BMI Calculator
const calculateBmiBtn = document.getElementById('calculateBmiBtn');
const bmiResultSection = document.getElementById('bmiResultSection');

calculateBmiBtn.addEventListener('click', async () => {
    const height = document.getElementById('heightInput').value;
    const weight = document.getElementById('bmiWeightInput').value;
    
    if (!height || !weight) {
        showNotification('Please enter both height and weight', 'error');
        return;
    }
    
    try {
        const response = await fetch('/bmi-calculator', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ height, weight })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayBmiResult(data);
            showNotification('BMI calculated and saved!', 'success');
        } else {
            showNotification(data.error || 'BMI calculation failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
});

function displayBmiResult(data) {
    document.getElementById('bmiValue').textContent = data.bmi;
    document.getElementById('bmiCategory').textContent = data.category;
    
    // Update category color
    const categoryElement = document.getElementById('bmiCategory');
    const colors = {
        'Underweight': '#7FB3D5',
        'Normal': '#6B8E5F',
        'Overweight': '#C9A76B',
        'Obese': '#B87A6F'
    };
    categoryElement.style.color = colors[data.category] || '#6B7864';
    
    bmiResultSection.classList.remove('hidden');
    bmiResultSection.scrollIntoView({ behavior: 'smooth' });
}

// Analytics
let currentPeriod = 'daily';
let calorieChart = null;
let foodChart = null;

const periodBtns = document.querySelectorAll('.period-btn');
periodBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        currentPeriod = btn.dataset.period;
        
        // Update active button
        periodBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Load analytics
        loadAnalytics(currentPeriod);
    });
});

async function loadAnalytics(period) {
    try {
        const response = await fetch(`/analytics/${period}`);
        const data = await response.json();
        
        if (response.ok) {
            updateStats(data);
            updateCharts(data);
            updateRecentEntries(data.recent_entries);
        } else {
            showNotification('Failed to load analytics', 'error');
        }
    } catch (error) {
        showNotification('Network error loading analytics', 'error');
    }
}

function updateStats(data) {
    document.getElementById('totalCalories').textContent = data.total_calories.toFixed(0);
    document.getElementById('avgCalories').textContent = data.average_calories.toFixed(0);
    document.getElementById('totalEntries').textContent = data.total_entries;
    
    if (data.latest_bmi) {
        document.getElementById('latestBmi').textContent = data.latest_bmi.bmi.toFixed(1);
    }
}

function updateCharts(data) {
    // Calorie Trend Chart
    const dates = Object.keys(data.daily_breakdown).sort();
    const calories = dates.map(date => data.daily_breakdown[date]);
    
    if (calorieChart) {
        calorieChart.destroy();
    }
    
    const calorieCtx = document.getElementById('calorieChart').getContext('2d');
    calorieChart = new Chart(calorieCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Calories',
                data: calories,
                borderColor: '#8A9A7B',
                backgroundColor: 'rgba(138, 154, 123, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Food Frequency Chart
    const foods = Object.keys(data.food_frequency);
    const frequencies = Object.values(data.food_frequency);
    
    if (foodChart) {
        foodChart.destroy();
    }
    
    const foodCtx = document.getElementById('foodChart').getContext('2d');
    foodChart = new Chart(foodCtx, {
        type: 'bar',
        data: {
            labels: foods.map(f => f.replace('_', ' ')),
            datasets: [{
                label: 'Frequency',
                data: frequencies,
                backgroundColor: [
                    '#8A9A7B',
                    '#B8C5A8',
                    '#C9A76B',
                    '#D4A59A',
                    '#6B8E5F',
                    '#5F6F52'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateRecentEntries(entries) {
    const tbody = document.getElementById('recentEntriesTable');
    
    if (!entries || entries.length === 0) {
        tbody.innerHTML = '进步<td colspan="4" class="text-center text-muted">No entries yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = entries.map(entry => `
        <tr>
            <td>${new Date(entry.timestamp).toLocaleString()}</td>
            <td>${entry.food_name.replace('_', ' ')}</td>
            <td>${entry.weight}g</td>
            <td>${entry.calories.toFixed(1)} kcal</td>
        </tr>
    `).join('');
}

function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}

// Load initial analytics when on analytics tab
document.addEventListener('DOMContentLoaded', () => {
    loadAnalytics('daily');
});

//faq responsive

function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        // Remove existing event listener to avoid duplicates
        question.removeEventListener('click', question.clickHandler);
        
        // Create handler function
        const handler = () => {
            // Close other FAQs
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current FAQ
            item.classList.toggle('active');
        };
        
        // Store handler to remove later if needed
        question.clickHandler = handler;
        
        // Add event listener
        question.addEventListener('click', handler);
    });
}

// Initialize FAQ when about tab becomes active
const aboutTabBtn = document.querySelector('.tab-btn[data-tab="about"]');
if (aboutTabBtn) {
    aboutTabBtn.addEventListener('click', () => {
        setTimeout(initFaqAccordion, 100);
    });
}

// Initialize on page load in case about tab is active  
document.addEventListener('DOMContentLoaded', () => {
    initFaqAccordion();
     //Document Object Model to masnipulate dcuments acess html elements 
});