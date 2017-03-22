import React from 'react';
import ReactDOM from 'react-dom';
import Cookies from 'js-cookie';

var csrftoken = Cookies.get('csrftoken');

function render() {
  var jobs = JOBS.map((job, i) => {
    /*
              L.div('.panel.panel-default') / (
              L.div('.panel-heading') / graph.name,
              L.div('.panel-body') / (
                  L.div('.row') / (
                      L.div('.col-md-1') / (
                          L.a('.btn.btn.btn-primary',
                              href=graph.get_absolute_url()) / 'View'
                      ),
                      L.div('.col-md-10') / (
                          'Estimated time to process: ',
                          L.strong / '4h00',
                          L.br,
                          'Time Left: ',
                          L.strong / '3h03',
                      ),
                      L.div('.col-md-1.text-right') / (
                          L.form(method='post') / (
                              L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                              L.input(type='hidden', name='action', value='delete'),
                              L.input(type='hidden', name='graph_id', value=str(graph.pk)),
                              L.button('.btn.btn-primary.btn-xs', type='submit') / 'delete', # L.span('.glyphicon.glyphicon-remove'),
                          )
                      )
                  )
              )
          ) for graph in graphs
    */
    return <div className='panel panel-default' key={i}>
      <div className='panel-heading'>{job.name}</div>
      <div className='panel-body'>
        <div className='row'>
          <div className='col-md-5'>
            <div><em>Auto-clustering between 2 and 10 topics and 2 and 10 clusters</em></div>
            <div>Est. time to process: <strong>3h30</strong> (~<strong>1h05</strong> left)</div>
          </div>
          <div className='col-md-7 text-right'>
            <form method='post'>
              <input type='hidden' name='csrfmiddlewaretoken' value={csrftoken}/>
              <input type='hidden' name='action' value='delete'/>
              <input type='hidden' name='graph_id' value={job.pk}/>
              <a className='btn btn-primary' href={job.url}>View</a>
              &nbsp;&nbsp;&nbsp;&nbsp;
              <button className='btn btn-danger' type='submit'>Delete</button>
            </form>
          </div>
        </div>
        <div className='row'>
          <div className="col-md-12">
              <br/>
              <div className="progress progress-striped active">
                  <div className="progress-bar" style={{width: '45%'}}></div>
              </div>
              <pre style={{maxHeight: 100}}>{`[2017-03-22 13:27:16,364: WARNING/Worker-2] number of swaps :1
[2017-03-22 13:27:16,370: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:16,403: WARNING/Worker-2] it1 : 1 lower bound : -170182 topics=5
[2017-03-22 13:27:16,403: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:16,476: WARNING/Worker-2] it1 : 54 lower bound : -193977 diff : 0.000133287 Q=5 K=5
[2017-03-22 13:27:16,964: WARNING/Worker-2] number of swaps :0
[2017-03-22 13:27:16,969: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:17,007: WARNING/Worker-2] it1 : 1 lower bound : -170148 topics=5
[2017-03-22 13:27:17,007: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:17,125: WARNING/Worker-2] it1 : 55 lower bound : -193944 diff : 0.000172536 Q=5 K=5
[2017-03-22 13:27:17,635: WARNING/Worker-2] number of swaps :0
[2017-03-22 13:27:17,641: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:17,695: WARNING/Worker-2] it1 : 1 lower bound : -170112 topics=5
[2017-03-22 13:27:17,695: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:17,784: WARNING/Worker-2] it1 : 56 lower bound : -193907 diff : 0.000188895 Q=5 K=5
[2017-03-22 13:27:18,272: WARNING/Worker-2] number of swaps :0
[2017-03-22 13:27:18,278: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:18,337: WARNING/Worker-2] it1 : 1 lower bound : -170087 topics=5
[2017-03-22 13:27:18,338: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:18,441: WARNING/Worker-2] it1 : 57 lower bound : -193882 diff : 0.000128123 Q=5 K=5
[2017-03-22 13:27:18,924: WARNING/Worker-2] number of swaps :0
[2017-03-22 13:27:18,929: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:18,966: WARNING/Worker-2] it1 : 1 lower bound : -170066 topics=5
[2017-03-22 13:27:18,966: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:19,032: WARNING/Worker-2] it1 : 58 lower bound : -193862 diff : 0.000107139 Q=5 K=5
[2017-03-22 13:27:19,608: WARNING/Worker-2] number of swaps :0
[2017-03-22 13:27:19,619: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:19,695: WARNING/Worker-2] it1 : 1 lower bound : -170043 topics=5
[2017-03-22 13:27:19,695: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:19,763: WARNING/Worker-2] it1 : 59 lower bound : -193839 diff : 0.000117989 Q=5 K=5
[2017-03-22 13:27:20,434: WARNING/Worker-2] number of swaps :0
[2017-03-22 13:27:20,447: WARNING/Worker-2] lda : 5 topics
[2017-03-22 13:27:20,488: WARNING/Worker-2] it1 : 1 lower bound : -170014 topics=5
[2017-03-22 13:27:20,489: WARNING/Worker-2] it1 : 1
[2017-03-22 13:27:20,593: WARNING/Worker-2] it1 : 60 lower bound : -193810 diff : 0.000149531 Q=5 K=5`}</pre>
          </div>
        </div>
      </div>
    </div>;
  });
  ReactDOM.render(<div>{jobs}</div>, document.getElementById('_jobs'));
};

render();
