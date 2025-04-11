const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './assets/js/main.js',  // Remove 'salesoptimizer' from path
  output: {
    path: path.resolve(__dirname, 'dist'),  // Simplified output path
    filename: 'bundle.js',
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html'  // Remove 'salesoptimizer' from path
    })
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: 'babel-loader'
      }
    ]
  }
};