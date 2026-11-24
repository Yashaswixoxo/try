// DOM Elements
const loginModal = document.getElementById('loginModal');
const signupModal = document.getElementById('signupModal');
const loginBtn = document.getElementById('loginBtn');
const signupBtn = document.getElementById('signupBtn');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const detectBtn = document.getElementById('detectBtn');
const resultSection = document.getElementById('resultSection');
const notification = document.getElementById('notification');

// Modal Controls
loginBtn.addEventListener('click', () => {
    loginModal.classList.remove('hidden');
});

signupBtn.addEventListener('click', () => {
    signupModal.classList.remove('hidden');
});

document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
        loginModal.classList.add('hidden');
        signupModal.classList.add('hidden');
    });
});

document.getElementById('switchToSignup').addEventListener('click', (e) => {
    e.preventDefault();
    loginModal.classList.add('hidden');
    signupModal.classList.remove('hidden');
});

document.getElementById('switchToLogin').addEventListener('click', (e) => {
    e.preventDefault();
    signupModal.classList.add('hidden');
    loginModal.classList.remove('hidden');
});

// Close modal on outside click
window.addEventListener('click', (e) => {
    if (e.target === loginModal) loginModal.classList.add('hidden');
    if (e.target === signupModal) signupModal.classList.add('hidden');
});

// Signup Form
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Account created! Redirecting to payment...', 'success');
            signupForm.reset();
            signupModal.classList.add('hidden');
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 800);
            } else {
                loginModal.classList.remove('hidden');
            }
        } else {
            showNotification(data.error || 'Signup failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
});

// Login Form
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Login successful!', 'success');
            loginModal.classList.add('hidden');
            loginForm.reset();
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else if (response.status === 402) {
            showNotification(data.error || 'Membership payment required', 'error');
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
});

// Image Upload
uploadArea.addEventListener('click', () => {
    imageInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#8A9A7B';
});

uploadArea.addEventListener('dragleave', (e) => {
    uploadArea.style.borderColor = '#B8C5A8';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageUpload(files[0]);
    }
});

imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleImageUpload(e.target.files[0]);
    }
});

let selectedImage = null;

function handleImageUpload(file) {
    if (!file.type.startsWith('image/')) {
        showNotification('Please upload an image file', 'error');
        return;
    }
    
    selectedImage = file;
    uploadArea.innerHTML = `
        <div class="upload-icon">✓</div>
        <p style="color: #6B8E5F; font-weight: 600;">${file.name}</p>
        <p class="text-small">Image ready for detection</p>
    `;
}

// Detect Calories
detectBtn.addEventListener('click', async () => {
    if (!selectedImage) {
        showNotification('Please upload an image first', 'error');
        return;
    }
    
    const weight = document.getElementById('weightInput').value;
    
    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('weight', weight);
    
    detectBtn.disabled = true;
    detectBtn.textContent = 'Detecting...';
    
    try {
        const response = await fetch('/detect-calorie', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult(data);
            showNotification('Calorie detection successful!', 'success');
        } else {
            showNotification(data.error || 'Detection failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        detectBtn.disabled = false;
        detectBtn.textContent = 'Detect Calories';
    }
});

function displayResult(data) {
    document.getElementById('foodName').textContent = data.food_name.replace('_', ' ').toUpperCase();
    document.getElementById('confidence').textContent = `${data.confidence}%`;
    document.getElementById('calories').textContent = `${data.calories} kcal`;
    document.getElementById('weight').textContent = `${data.weight}g`;
    
    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}