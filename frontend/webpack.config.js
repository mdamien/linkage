var path = require('path');
var webpack = require('webpack');

module.exports = function(env) {
  var prod = env == 'prod';

  var plugins = [
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor'
    }),
  ];

  if (prod) {
    plugins.push(new webpack.LoaderOptionsPlugin({
      minimize: true,
      debug: false
    }));
    plugins.push(new webpack.optimize.UglifyJsPlugin({
      beautify: false,
      mangle: {
          screw_ie8: true,
          keep_fnames: true
      },
      compress: {
          screw_ie8: true
      },
      comments: false
    }));
  }

  config = {
    devtool: 'source-map',
    entry: {
      graph: './src/graph.js',
      jobs: './src/jobs.js',
      vendor: ['react', 'react-dom', 'rc-slider', 'react-autocomplete'],
    },
    output: {
      filename: '[name].js',
      path: path.resolve(__dirname, '../core/static/js/dist')
    },
    module: {
      rules: [
        { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader' },
      ]
    },
    plugins: plugins,
  };

  if (prod) {
    delete config['devtool'];
  }

  return config;
};
