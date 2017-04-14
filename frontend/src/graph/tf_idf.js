import {n_best_elems} from './utils';

/* 
// topic2terms is a list of topics with each term frequency inside each topic
export default function tfidf(topic2terms) {
  // compute specificity-to-topic for each terms
  // returns a list of topics with each term = [freq, specificity]
  return topic2terms.map((freqs) => {
    var max_freq_topic = n_best_elems(freqs, 1)[0][1];
    return freqs.map((freq, i) => {
      if (freq < 0.001) {
        return {
          freq: freq,
          tfidf: freq, // tf*idf,
        };
      }
      var tf = 0.5 + 0.5*freq/max_freq_topic;
      var nb_of_time_in_topics = 0;
      topic2terms.forEach((freqs) => {
        nb_of_time_in_topics += freqs[i];
      });
      var idf = Math.log(topic2terms.length/(nb_of_time_in_topics));
      return {
        freq,
        tfidf: tf*idf,
      };
    })
  });
}
*/

/*

  En quelques mots, je calcule d’abord un indice d’entropie pour chaque mot
  (le mot est-il utilisé plus fréquemment dans un topic que dans les autres)
  et ensuite je pondère cette quantité par le \beta du mot dans le topic.
  On obtient ainsi un indice de représentativité du mot pour un topic donné.
  Le paramètre s permet de donner plus ou moins de poids à l'entropie.

terms <- function(res,n=20,s=2){
  words = colnames(res$beta)
  ent = apply(res$beta,2,function(x){y = x/sum(x); 1+sum(y*log(y))/log(res$K)})
  for (k in 1:res$K){
    spec = res$beta[k,] * ent^s
    Wk = words[order(spec,decreasing = TRUE)[1:n]]
    cat('* Topic',k,':'); print(paste(Wk,collapse = ', ')); cat('\n')
  }
}

ent[k] = 1+sum(y*log(y))/log(K) avec y = beta[k]/sum(beta[k])

puis: spec[k] = Beta[k] * ent^s

beta = freq des mots pour chaque topic
for each topic k:
   beta_t[k] = freq du mot pour tout les topics
   y = beta[k] / sum(beta_k)
   ent[k] = 1 + sum(y*log(y)) / log(K)
   spec[k] = beta[k] * ent**s
*/

export default function score_words_by_entropy(beta) {

  var arr_log = (arr) => arr.map(v => Math.log(v));
  var arr_div = (arr, b) => arr.map(v => v / b);
  var arr_pow = (arr, b) => arr.map(v => Math.pow(v, b));
  var arr_sum = arr => arr.reduce((a, b) => a + b, 0);

  var arr2_mul = (A, B) => A.map((a, i) => a * B[i]);

  var mat_cols = (mat, fn) => 
    mat[0].map((_, col) =>
      fn(mat.map((_, row) =>
        mat[row][col]
      ))
    );

  var s = 2.5;
  /*
  ent = apply(res$beta,2,
      function(x){
        y = x/sum(x);
        1 + sum(y*log(y))/log(res$K)
      })
  */
  var K = beta.length;
  var ent = mat_cols(beta, x /* arr of freq of the word for each topic */ => {
    var y = arr_div(x, arr_sum(x));
    return 1 + arr_sum(arr2_mul(y, arr_log(y))) / Math.log(K);
  });

  /*
    for (k in 1:res$K) {
    spec = res$beta[k,] * ent^s
  */
  var spec = beta.map((freqs, k) => {
    return arr2_mul(beta[k], arr_pow(ent, s));
  });

  return beta.map((freqs, k) => {
    return freqs.map((freq, i) => {
      return {
        freq: freq,
        tfidf: GRAPH.magic_too_big_to_display_X ? freq : spec[k][i],
      };
    })
  });
}
