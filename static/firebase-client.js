/**
 * Firebase Client Library
 * Provides easy-to-use Firebase operations for the Health & Fitness XAI System
 * 
 * Usage:
 * import { FirebaseClient } from './firebase-client.js';
 * const fb = new FirebaseClient();
 * await fb.init();
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js";
import { getDatabase, ref, get, set, update, remove, push, onValue } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-database.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-analytics.js";

export class FirebaseClient {
  constructor() {
    this.app = null;
    this.auth = null;
    this.database = null;
    this.analytics = null;
    this.config = null;
    this.currentUser = null;
  }

  /**
   * Initialize Firebase
   */
  async init() {
    try {
      // Fetch Firebase config from backend
      const response = await fetch('/api/firebase-config');
      const data = await response.json();

      if (!data.success) {
        console.error('Failed to load Firebase config:', data.error);
        return false;
      }

      this.config = data.config;

      // Initialize Firebase
      this.app = initializeApp(this.config);
      this.auth = getAuth(this.app);
      this.database = getDatabase(this.app);
      this.analytics = getAnalytics(this.app);

      console.log('✓ Firebase initialized successfully');
      return true;
    } catch (error) {
      console.error('Firebase initialization error:', error);
      return false;
    }
  }

  /**
   * Register user
   */
  async register(email, password, name) {
    try {
      const userCredential = await createUserWithEmailAndPassword(this.auth, email, password);
      const user = userCredential.user;

      // Store user data in database
      await set(ref(this.database, 'users/' + user.uid), {
        email: email,
        name: name,
        created_at: new Date().toISOString(),
        uid: user.uid
      });

      console.log('✓ User registered:', email);
      return { success: true, user: user };
    } catch (error) {
      console.error('Registration error:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Sign in user
   */
  async signIn(email, password) {
    try {
      const userCredential = await signInWithEmailAndPassword(this.auth, email, password);
      const user = userCredential.user;

      // Update last login
      await update(ref(this.database, 'users/' + user.uid), {
        lastLogin: new Date().toISOString()
      });

      console.log('✓ User signed in:', email);
      return { success: true, user: user };
    } catch (error) {
      console.error('Sign in error:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Sign out user
   */
  async signOut() {
    try {
      await signOut(this.auth);
      console.log('✓ User signed out');
      return { success: true };
    } catch (error) {
      console.error('Sign out error:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return this.auth.currentUser;
  }

  /**
   * Listen to auth state changes
   */
  onAuthStateChanged(callback) {
    return onAuthStateChanged(this.auth, callback);
  }

  /**
   * Get user profile
   */
  async getUserProfile(uid) {
    try {
      const snapshot = await get(ref(this.database, 'users/' + uid + '/profile'));
      if (snapshot.exists()) {
        return { success: true, profile: snapshot.val() };
      }
      return { success: false, error: 'Profile not found' };
    } catch (error) {
      console.error('Error getting profile:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Update user profile
   */
  async updateUserProfile(uid, profileData) {
    try {
      profileData.updated_at = new Date().toISOString();
      await set(ref(this.database, 'users/' + uid + '/profile'), profileData);
      console.log('✓ Profile updated');
      return { success: true };
    } catch (error) {
      console.error('Error updating profile:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get user data
   */
  async getUserData(uid) {
    try {
      const snapshot = await get(ref(this.database, 'users/' + uid));
      if (snapshot.exists()) {
        return { success: true, data: snapshot.val() };
      }
      return { success: false, error: 'User not found' };
    } catch (error) {
      console.error('Error getting user data:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Store feedback
   */
  async storeFeedback(uid, feedbackData) {
    try {
      feedbackData.timestamp = new Date().toISOString();
      const feedbackRef = ref(this.database, 'users/' + uid + '/feedback');
      await push(feedbackRef, feedbackData);
      console.log('✓ Feedback stored');
      return { success: true };
    } catch (error) {
      console.error('Error storing feedback:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get user feedback
   */
  async getUserFeedback(uid) {
    try {
      const snapshot = await get(ref(this.database, 'users/' + uid + '/feedback'));
      if (snapshot.exists()) {
        const feedbackObj = snapshot.val();
        const feedbackArray = Object.values(feedbackObj);
        return { success: true, feedback: feedbackArray };
      }
      return { success: true, feedback: [] };
    } catch (error) {
      console.error('Error getting feedback:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Store tracking data
   */
  async storeTrackingData(uid, trackingData) {
    try {
      trackingData.timestamp = new Date().toISOString();
      const trackingRef = ref(this.database, 'users/' + uid + '/tracking');
      await push(trackingRef, trackingData);
      console.log('✓ Tracking data stored');
      return { success: true };
    } catch (error) {
      console.error('Error storing tracking data:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get user tracking data
   */
  async getUserTrackingData(uid) {
    try {
      const snapshot = await get(ref(this.database, 'users/' + uid + '/tracking'));
      if (snapshot.exists()) {
        const trackingObj = snapshot.val();
        const trackingArray = Object.values(trackingObj);
        return { success: true, tracking: trackingArray };
      }
      return { success: true, tracking: [] };
    } catch (error) {
      console.error('Error getting tracking data:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Store recommendations
   */
  async storeRecommendations(uid, recommendationsData) {
    try {
      recommendationsData.timestamp = new Date().toISOString();
      const recRef = ref(this.database, 'users/' + uid + '/recommendations');
      await push(recRef, recommendationsData);
      console.log('✓ Recommendations stored');
      return { success: true };
    } catch (error) {
      console.error('Error storing recommendations:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get user recommendations
   */
  async getUserRecommendations(uid) {
    try {
      const snapshot = await get(ref(this.database, 'users/' + uid + '/recommendations'));
      if (snapshot.exists()) {
        const recObj = snapshot.val();
        const recArray = Object.values(recObj);
        return { success: true, recommendations: recArray };
      }
      return { success: true, recommendations: [] };
    } catch (error) {
      console.error('Error getting recommendations:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Listen to real-time profile changes
   */
  onProfileChanged(uid, callback) {
    const profileRef = ref(this.database, 'users/' + uid + '/profile');
    return onValue(profileRef, snapshot => {
      if (snapshot.exists()) {
        callback({ success: true, profile: snapshot.val() });
      } else {
        callback({ success: false, error: 'Profile not found' });
      }
    });
  }

  /**
   * Listen to real-time feedback changes
   */
  onFeedbackChanged(uid, callback) {
    const feedbackRef = ref(this.database, 'users/' + uid + '/feedback');
    return onValue(feedbackRef, snapshot => {
      if (snapshot.exists()) {
        const feedbackObj = snapshot.val();
        const feedbackArray = Object.values(feedbackObj);
        callback({ success: true, feedback: feedbackArray });
      } else {
        callback({ success: true, feedback: [] });
      }
    });
  }

  /**
   * Listen to real-time tracking changes
   */
  onTrackingChanged(uid, callback) {
    const trackingRef = ref(this.database, 'users/' + uid + '/tracking');
    return onValue(trackingRef, snapshot => {
      if (snapshot.exists()) {
        const trackingObj = snapshot.val();
        const trackingArray = Object.values(trackingObj);
        callback({ success: true, tracking: trackingArray });
      } else {
        callback({ success: true, tracking: [] });
      }
    });
  }

  /**
   * Delete user data
   */
  async deleteUserData(uid) {
    try {
      await remove(ref(this.database, 'users/' + uid));
      console.log('✓ User data deleted');
      return { success: true };
    } catch (error) {
      console.error('Error deleting user data:', error.message);
      return { success: false, error: error.message };
    }
  }
}

// Export singleton instance
export const firebaseClient = new FirebaseClient();
