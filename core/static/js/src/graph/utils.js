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

var hashIt = function(s) {
  return Math.abs(s.toString().split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0)*1.2;return a&a},0)) * 3423;
};

var hashedColor = s => COLORS[hashIt(s) % COLORS.length];

export {
  hashedColor,
  COLORS
}