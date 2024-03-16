import { getApps, getApp, initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
// const firebaseConfig = {
//   apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
//   authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
//   projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
//   storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
//   messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
//   appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
// }

const firebaseConfig = {

  apiKey: "AIzaSyDHqDjAR_NvpF83fY0PQAE6HBgPkE92dh8",

  authDomain: "fir-cc97a.firebaseapp.com",

  projectId: "fir-cc97a",

  storageBucket: "fir-cc97a.appspot.com",

  messagingSenderId: "824691857064",

  appId: "1:824691857064:web:f6dd19ff73f1f5665a549d",

  measurementId: "G-0LX5H6TJ2G"

};

// Initialize Firebase
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp()
const auth = getAuth(app)
const db = getFirestore(app)

export { app, auth, db }
