// DOM Elements
const loginForm = document.getElementById('loginForm');
const phoneInput = document.getElementById('phoneNumber');
const passwordInput = document.getElementById('password');
const phoneError = document.getElementById('phoneError');
const passwordError = document.getElementById('passwordError');
const togglePassword = document.getElementById('togglePassword');
const eyeSlash = document.getElementById('eyeSlash');
const loginButton = document.getElementById('loginButton');
const buttonText = document.querySelector('.button-text');
const loadingSpinner = document.getElementById('loadingSpinner');

// State
let isPasswordVisible = false;
let isLoading = false;

// Password visibility toggle
togglePassword.addEventListener('click', function() {
    isPasswordVisible = !isPasswordVisible;

    if (isPasswordVisible) {
        passwordInput.type = 'text';
        eyeSlash.style.display = 'none';
    } else {
        passwordInput.type = 'password';
        eyeSlash.style.display = 'block';
    }
});

// Form validation
function validatePhone(phone) {
    return phone.length >= 10;
}

function validatePassword(password) {
    return password.length >= 6;
}

function showError(element, message) {
    element.textContent = message;
    element.classList.add('show');
}

function hideError(element) {
    element.classList.remove('show');
}

function setLoading(loading) {
    isLoading = loading;
    loginButton.disabled = loading;

    if (loading) {
        buttonText.classList.add('hide');
        loadingSpinner.classList.add('show');
    } else {
        buttonText.classList.remove('hide');
        loadingSpinner.classList.remove('show');
    }
}

// Form submission
loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Clear previous errors
    hideError(phoneError);
    hideError(passwordError);

    // Get form data
    const phoneNumber = phoneInput.value.trim();
    const password = passwordInput.value;

    // Validate inputs
    let isValid = true;

    if (!validatePhone(phoneNumber)) {
        showError(phoneError, 'Phone number must be at least 10 digits');
        isValid = false;
    }

    if (!validatePassword(password)) {
        showError(passwordError, 'Password must be at least 6 characters');
        isValid = false;
    }

    if (!isValid) {
        return;
    }

    // Set loading state
    setLoading(true);

    try {
        // ** BACKEND INTEGRATION POINT **
        // Replace this section with your actual backend API call

        // Example with fetch API:
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Login successful
            console.log('Login successful:', data);

            // Show success message
            alert('Login successful!');

            // Store auth token if provided
            if (data.token) {
                localStorage.setItem('authToken', data.token);
            }

            // Redirect to Google page on successful login
            window.location.href = 'https://www.google.com';
        } else {
            // Login failed
            throw new Error(data.message || 'Login failed');
        }

        // Simulated API call for demo purposes
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Simulate success
        console.log('Login data:', { phoneNumber, password });
        alert('Login successful! (This is a demo)');

        // Simulate error (uncomment to test error handling)
        // throw new Error('Invalid credentials');

    } catch (error) {
        console.error('Login error:', error);

        // Handle different types of errors based on the message from the backend
        // The Flask backend returns {\'msg\': \'Invalid credentials\'} for 401
        if (error.message === 'Invalid credentials') {
            showError(passwordError, 'Invalid phone number or password');
        } else if (error.message && error.message.includes('network')) {
            alert('Network error. Please check your connection and try again.');
        } else {
            alert('Login failed: ' + (error.message || 'Please try again later.'));
        }
    } finally {
        setLoading(false);
    }
});

// ** ADDITIONAL BACKEND INTEGRATION HELPERS **

// Function to make authenticated API requests
function makeAuthenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('authToken');

    return fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? Bearer ${token} : '',
            ...options.headers
        }
    });
}

// Function to check if user is authenticated
function isAuthenticated() {
    const token = localStorage.getItem('authToken');
    return !!token;
}

// Function to logout user
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/';
}

// Function to handle API errors globally
function handleApiError(error, response) {
    if (response && response.status === 401) {
        // Unauthorized - redirect to login
        logout();
        return;
    }

    console.error('API Error:', error);
    throw error;
}

// ** BACKEND INTEGRATION EXAMPLES **

/*
// Example 1: Node.js/Express backend
async function loginWithNodeJS(phoneNumber, password) {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phoneNumber, password })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
    }

    return await response.json();
}

// Example 2: PHP backend
async function loginWithPHP(phoneNumber, password) {
    const formData = new FormData();
    formData.append('phoneNumber', phoneNumber);
    formData.append('password', password);

    const response = await fetch('login.php', {
        method: 'POST',
        body: formData
    });

    const result = await response.text();

    try {
        return JSON.parse(result);
    } catch (e) {
        throw new Error('Invalid response from server');
    }
}

// Example 3: Firebase Authentication
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from './firebase-config.js';

async function loginWithFirebase(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        return userCredential.user;
    } catch (error) {
        throw new Error(error.message);
    }
}

// Example 4: Django backend
async function loginWithDjango(phoneNumber, password) {
    // Get CSRF token first
    const csrfResponse = await fetch('/get-csrf-token/');
    const csrfData = await csrfResponse.json();

    const response = await fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfData.csrfToken
        },
        body: JSON.stringify({
            phone_number: phoneNumber,
            password: password
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
    }

    return await response.json();
}
*/

// Input formatting (optional)
phoneInput.addEventListener('input', function(e) {
    // Remove any non-digit characters
    let value = e.target.value.replace(/\D/g, '');

    // Format as phone number (you can customize this)
    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{0,4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{0,3})/, '($1) $2');
    }

    e.target.value = value;
});

// Real-time validation feedback
phoneInput.addEventListener('blur', function() {
    const phone = this.value.replace(/\D/g, '');
    if (phone && !validatePhone(phone)) {
        showError(phoneError, 'Phone number must be at least 10 digits');
    } else {
        hideError(phoneError);
    }
});

passwordInput.addEventListener('blur', function() {
    if (this.value && !validatePassword(this.value)) {
        showError(passwordError, 'Password must be at least 6 characters');
    } else {
        hideError(passwordError);
    }
});