var path = require('path');

module.exports = {
  devtool: 'cheap-eval-source-map',
  entry: './src/graph.js',
  output: {
    filename: 'dist/graph.js'
  },
  module: {
  	rules: [
      { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader' },
    ]
  },
};