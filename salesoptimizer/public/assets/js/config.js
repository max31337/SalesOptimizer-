export const apiConfig = {
    apiUrl: window.location.hostname === 'salesoptimizer.vercel.app'
        ? "https://crossover.proxy.rlwy.net:32542/api"
        : "http://localhost:8000/api"
};