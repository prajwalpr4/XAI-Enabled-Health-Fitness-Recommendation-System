/**
 * Firebase Web Configuration
 * Client-side Firebase initialization for the Health & Fitness XAI System
 * 
 * This file initializes Firebase for use in the web browser
 * Used for real-time database access, authentication, and analytics
 */

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBHf4FVhmTwwZr8QiD8BoirBeHN911Xhas",
  authDomain: "xai-fitness.firebaseapp.com",
  databaseURL: "https://xai-fitness-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "xai-fitness",
  storageBucket: "xai-fitness.firebasestorage.app",
  messagingSenderId: "1037654115350",
  appId: "1:1037654115350:web:a492decd85d2d84a17e137",
  measurementId: "G-S7267BXNWZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Analytics
const analytics = getAnalytics(app);

// Initialize Firebase Authentication
const auth = getAuth(app);

// Initialize Firebase Realtime Database
const database = getDatabase(app);

// Export Firebase services for use in other modules
export { app, analytics, auth, database };

/**
 * Usage in other JavaScript files:
 * 
 * import { auth, database } from './firebase-config.js';
 * import { signInWithEmailAndPassword } from 'firebase/auth';
 * import { ref, get } from 'firebase/database';
 * 
 * // Example: Sign in user
 * signInWithEmailAndPassword(auth, email, password)
 *   .then(userCredential => {
 *     console.log('User signed in:', userCredential.user);
 *   })
 *   .catch(error => {
 *     console.error('Sign in error:', error);
 *   });
 * 
 * // Example: Read data from database
 * const userRef = ref(database, 'users/' + userId);
 * get(userRef).then(snapshot => {
 *   if (snapshot.exists()) {
 *     console.log('User data:', snapshot.val());
 *   }
 * });
 */
