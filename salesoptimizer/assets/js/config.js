const config = {
    development: {
        apiUrl: 'http://localhost:8000/api'
    },
    production: {
        apiUrl: 'https://SalesOptimizer-.railway.app/api'  // Replace with your Railway URL
    }
};

const environment = window.location.hostname === 'localhost' ? 'development' : 'production';
export const apiConfig = config[environment];