import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

// Add some performance monitoring
const renderApp = () => {
  const startTime = performance.now();
  
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  
  const endTime = performance.now();
  console.log(`🚀 CryptoAI Analytics loaded in ${(endTime - startTime).toFixed(2)}ms`);
};

renderApp();

// Service Worker registration (optional)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}