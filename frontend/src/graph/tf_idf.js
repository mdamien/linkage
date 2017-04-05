import {n_best_elems} from './utils';

// topic2terms is a list of topics with each term frequency inside each topic
export default function tfidf(topic2terms) {
  // compute specificity-to-topic for each terms
  // returns a list of topics with each term = [freq, specificity]
  return topic2terms.map((freqs) => {
    var max_freq_topic = n_best_elems(freqs, 1)[0][1];
    return freqs.map((freq, i) => {
      if (freq < 0.000001) {
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
        tfidf: freq, // tf*idf,
      };
    })
  });
}
