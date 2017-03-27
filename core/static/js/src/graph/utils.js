import colorbrewer from './colorbrewer';

var COLORS = [
  '#1f77b4', '#aec7e8',
  '#ff7f0e', '#ffbb78',
  '#2ca02c', '#98df8a',
  '#d62728', '#ff9896',
  '#9467bd', '#c5b0d5',
  '#8c564b', '#c49c94',
  '#e377c2', '#f7b6d2',
  '#7f7f7f', '#c7c7c7',
  '#bcbd22', '#dbdb8d'
];

colorbrewer['bonus'] = {12:COLORS}

var hashIt = function(s) {
  return Math.abs(s.toString().split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0)*1.2;return a&a},0)) * 3423;
};

var get_color = (i, set='bonus') => {
  var colors = colorbrewer[set][12];
  return colors[i % colors.length];
};

var hashedColor = s => get_color(hashIt(s));

var edgesArr = X => {
  var edges = [];

  X.forEach(function(line, i) {
    var edge = line[0] + ',' + line[1];
    if (edges.indexOf(edge) === -1) {
      edges.push(edge);
    }
  });

  return edges;
}


const n_best_elems = (arr, n, key=v => v) => {
    var keyed_arr = arr.map((v, i) => [i, v]);
    var result = keyed_arr.sort((a, b) => {
      if (key(a[1]) < key(b[1])) {
        return 1;
      }
      if (key(a[1]) > key(b[1])) {
        return -1;
      }
      return 0;
    });
    return n ? result.slice(0, n) : result;
};

export {
  hashedColor,
  COLORS,
  get_color,
  edgesArr,
  n_best_elems,
}
