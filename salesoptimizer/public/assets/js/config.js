export const apiConfig = {
    apiUrl: process.env.NODE_ENV === 'production' 
        ? "https://crossover.proxy.rlwy.net:32542/api"
        : "http://localhost:8000/api"
};