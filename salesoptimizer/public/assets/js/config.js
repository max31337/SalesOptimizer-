export const apiConfig = {
    apiUrl: window.location.hostname === 'salesoptimizer.vercel.app'
        ? "https://noble-warmth-production.up.railway.app/api"  // Use the full Railway URL
        : "http://localhost:8000/api"
};