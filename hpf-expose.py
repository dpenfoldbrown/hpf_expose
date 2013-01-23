##
## Initial version of HPF DB expose website
## dpb 1/14/2013
##

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
from hpf.hddb.db import Sequence, Protein, Domain

# Flask init
app = Flask(__name__)
app.debug = True

# DB init
SESSION = None


## UTILITY FUNCTIONS

def get_session():
    """
    Initializes and returns the global session object
    """
    from hpf.hddb.db import ScopedSession
    global SESSION
    if SESSION:
        return SESSION
    else:
        return ScopedSession()

def get_search_fields(request_fields):
    """
    Takes a request.form/args/values dict (for POST, GET, and both method forms),
    or any multi-dict, and returns the two common search fields for this site:
    type (eg: hpf_id, keyword, etc) and term (the term to search for or fetch).
    TODO: should return a nice error if keys are not in multi-dict
    For now, leaves the request, as a key error/400 bad request exception will
    be raised when trying to fetch non-entities
    """
    if 'type' not in request_fields:
        pass
    elif 'term' not in request_fields:
        pass
    return request_fields['type'], request_fields['term']
        


## ROUTES

@app.route('/')
def index():
   """
   Homepage
   """
   return render_template('index.html')


@app.route('/sequence', methods=['GET','POST'])
def sequence():
    """
    The sequence index page
    """
    if request.method == 'POST':
        type, search_term = get_search_fields(request.form)
        return redirect(url_for('fetch_sequence', sequence_id=search_term))
    
    return render_template('sequence.html')

@app.route('/sequence/<int:sequence_id>')
def fetch_sequence(sequence_id):
    """
    Sequence display page. Includes sequence, proteins? domains?
    """
    sess = get_session()
    seq_dbo = sess.query(Sequence).get(sequence_id)
    return render_template('sequence.html', seq_dbo=seq_dbo)


@app.route('/experiment', methods=['GET','POST'])
def experiment():
    """
    Experiment index page
    """
    return render_template('experiment.html')

@app.route('/experiment/<int:experiment_id>')
def fetch_experiment(experiment_id):
    """
    Experiment display page. Includes: info/names, counts (prot.), source, etc
    """
    return "TODO"


@app.route('/protein', methods=['GET', 'POST'])
def protein():
    """
    The protein index page
    """
    if request.method == 'POST':
        type, search_term = get_search_fields(request.form)

        if type == "hpf_id":
            return redirect(url_for('fetch_protein', protein_id=search_term))
        elif type == "seq_id":
            pass
        elif type == "ac":
            pass
        elif type == "keyword":
            pass
    
    return render_template('protein.html')

@app.route('/protein/<int:protein_id>')
def fetch_protein(protein_id):
    """
    Protein display page, fetches protein by ID and displays
    """
    sess = get_session()
    p = sess.query(Protein).get(protein_id)
    return render_template('protein.html', protein_dbo=p)


@app.route('/domain', methods=['GET','POST'])
def domain():
    """
    Domain index page
    """
    return render_template('domain.html')

@app.route('/domain/<int:domain_id>')
def fetch_domain(domain_id):
    """
    Domain display page. Includes: all info, sequence, ginzu info, region,
    and known v unknown structure display
    """
    return "TODO"

@app.route('/blast')
def blast():
    """
    Current blast placeholder page
    """
    return render_template('blast.html')

@app.route('/about')
def about():
    """
    About page
    """
    return render_template('about.html')

if __name__ == "__main__":
    app.run()
