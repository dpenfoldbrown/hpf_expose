##
## Initial version of HPF DB expose website
## dpb 1/14/2013
##

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
from hpf.hddb.db import ScopedSession, Sequence, Protein, Domain

# Flask init
app = Flask(__name__)
app.debug = True

# DB init
SESSION = None

def get_session():
    """
    Initializes and returns the global session object
    """
    global SESSION
    if SESSION:
        return SESSION
    else:
        return ScopedSession()
    

@app.route('/')
def index():
   """
   Homepage
   """
   return render_template('index.html')


@app.route('/sequence')
def sequence():
    """
    The sequence index page
    """
    return render_template('sequence.html')

@app.route('/sequence/<int:sequence_id>')
def fetch_sequence(sequence_id):
    """
    Sequence display page. Includes sequence, proteins? domains?
    """
    sess = get_session()
    seq_dbo = sess.query(Sequence).get(sequence_id)
    return render_template('sequence.html', seq_dbo=seq_dbo)


@app.route('/experiment')
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
    if 'term' in request.form and 'field' in request.form:
        field = request.form['field']
        search_term = request.form['term']

        if field == "hpf_id":
            return redirect(url_for('fetch_protein', protein_id=search_term))
        elif field == "seq_id":
            pass
        elif field == "ac":
            pass
        elif field == "keyword":
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


@app.route('/domain')
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
