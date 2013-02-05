##
## Initial version of HPF DB expose website
## dpb 1/14/2013
##

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
from hpf.hddb.db import Sequence, Protein, Domain, SequenceAc

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
    from hpf.hddb.db import Session
    global SESSION
    if SESSION:
        return SESSION
    else:
        SESSION = Session()
        return SESSION

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
        
def is_search(request):
    """
    Takes a request object, checks for fields in either form or args (values
    in flask, a combined multidict) that indicates a search request.
    Returns True if fields multidict has keys 'type' and 'term', otherwise false
    """
    return ('type' in request.values) and ('term' in request.values)


## ROUTES

@app.route('/')
def index():
   """
   Homepage
   """
   return render_template('index.html')


@app.route('/sequence', methods=['GET',])
def sequence():
    """
    The sequence index page
    """
    if is_search(request):
        type, search_term = get_search_fields(request.args)
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


@app.route('/experiment', methods=['GET',])
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


@app.route('/protein', methods=['GET',])
def protein():
    """
    The protein index page
    """
    if is_search(request):
        type, search_term = get_search_fields(request.args)
        whole_search = "{0} : {1}".format(type, search_term)
        sess = get_session()

        if type == "hpf_id":
            proteins = sess.query(Protein).filter_by(id=search_term).all()
        elif type == "seq_id":
            proteins = sess.query(Protein).filter_by(sequence_key=search_term).all()
        elif type == "ac":
            acs = sess.query(SequenceAc).filter_by(ac=search_term).all()
            proteins = [a.protein for a in acs if a.protein]
        elif type == "keyword":
            acs = sess.query(SequenceAc).filter(SequenceAc.description.like("%{0} %".format(search_term))).all()
            proteins = [a.protein for a in acs if a.protein]
        else:
            return render_template('bad_search.html', request=request)

        return render_template('protein.html', proteins=proteins, search=whole_search)
    
    return render_template('protein.html')

@app.route('/protein/<int:protein_id>')
def fetch_protein(protein_id):
    """
    Protein display page, fetches protein by ID and displays
    """
    sess = get_session()
    p = sess.query(Protein).get(protein_id)
    if p:
        return render_template('protein.html', proteins=[p])
    return render_template('protein.html', proteins=[])


@app.route('/domain', methods=['GET',])
def domain():
    """
    Domain index page
    """
    if is_search(request):
        type, search_term = get_search_fields(request.args)
        whole_search = "{0} : {1}".format(type, search_term)
        sess = get_session()

        if type == "hpf_id":
            domains = sess.query(Domain).filter_by(id=search_term).all()
        
        elif type == "seq_id":
            domains = sess.query(Domain).filter_by(domain_sequence_key=search_term).all()
        
        elif type == "prediction_code":
            domains = sess.query(Domain).filter_by(ibm_prediction_code=search_term).all()
        
        elif type == "protein_id":
            protein = sess.query(Protein).get(search_term)
            domains = protein.domains
        
        else:
            return render_template('bad_search.html', request=request)
        
        return render_template('domain.html', domains=domains, search=whole_search)
    
    return render_template('domain.html')

@app.route('/domain/<int:domain_id>')
def fetch_domain(domain_id):
    """
    Domain display page. Includes: all info, sequence, ginzu info, region,
    and known v unknown structure display
    """
    s = get_session()
    d = s.query(Domain).get(domain_id)
    if d:
        return render_template('domain.html', domains=[d])
    return render_template('domain.html', domains=None)

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
