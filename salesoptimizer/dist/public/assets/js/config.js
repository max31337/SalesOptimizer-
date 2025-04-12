export const apiConfig = {
    apiUrl: window.location.hostname === 'salesoptimizer.vercel.app'
        ? "/api"  // Use relative path to let Vercel handle the proxy
        : "http://localhost:8000/api"
};