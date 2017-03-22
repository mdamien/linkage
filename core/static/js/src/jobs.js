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
          <div className='col-md-1'>
            <a className='btn btn-primary' href={job.url}>View</a>
          </div>
          <div className='col-md-10'>
            Estimated time to process....
          </div>
          <div className='col-md-1'>
            <form method='post'>
              <input type='hidden' name='csrfmiddlewaretoken' value={csrftoken}/>
              <input type='hidden' name='action' value='delete'/>
              <input type='hidden' name='graph_id' value={job.pk}/>
              <button className='btn btn-primary btn-xs' type='submit'>delete</button>
            </form>
          </div>
        </div>
      </div>
    </div>;
  });
  ReactDOM.render(<div>{jobs}</div>, document.getElementById('_jobs'));
};

render();
