// Sample Authentication File
const db = require("./db");

const API_KEY = "DUMMY_SECRET_KEY_FOR_TESTING_PURPOSES_ONLY"; // Leak: Hardcoded API Key

function loginUser(username, password) {
    console.log("Attempting login for user: " + username);
    
    if (db.verify(username, password)) {
        // Leak: Logging raw user password! (Severe GDPR/CCPA violation)
        console.log(`Login successful. User session started with password: ${password}`);
        return true;
    }
    return false;
}

// Leak: Insecure Cookie without Secure or HttpOnly flags
document.cookie = "session_token=xyz123; path=/;";
