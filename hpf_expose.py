##
## Initial version of HPF DB expose website
## dpb 1/14/2013
##

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
from flask.ext.sqlalchemy import SQLAlchemy

from hpf.hddb.db import Sequence, Experiment, Protein, Domain, SequenceAc, Structure

## Flask init
app = Flask(__name__)

## Logging init (could also add an SMTP mail handler to mail on ERRORs)
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    log_file = "hpf_expose.log"
    log_bytes = 10 * 1024 * 1024
    
    file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=log_bytes, backupCount=0)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s ' '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

## DB init (using Flask's SQLalchemy extension. Which is good - manages session scope)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dpb:dpb_nyu@handbanana.bio.nyu.edu:3306/hpf'
db = SQLAlchemy(app)


## UTILITY FUNCTIONS

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
    seq_dbo = db.session.query(Sequence).get(sequence_id)
    if seq_dbo:
        return render_template('sequence.html', seq_dbo=seq_dbo)
    return render_template('sequence.html', seq_dbo=None)


@app.route('/experiment', methods=['GET',])
def experiment():
    """
    Experiment index page
    """
    if is_search(request):
        type, search_term = get_search_fields(request.args)
        whole_search = "{0} : {1}".format(type, search_term)
        
        if type == "hpf_id":
            experiments = db.session.query(Experiment).filter_by(id=search_term).all()
        elif type == "tax_id":
            experiments = db.session.query(Experiment).filter_by(taxonomy_id=search_term).all()
        elif type == "organism":
            experiments = db.session.query(Experiment).filter(Experiment.short_name.like("%{0}%".format(search_term))).all()
        else:
            return render_template('bad_search.html', request=request)
        return render_template('experiment.html', experiments=dict((e.id, e) for e in experiments), search=whole_search)
    return render_template('experiment.html')

@app.route('/experiment/<int:experiment_id>')
def fetch_experiment(experiment_id):
    """
    Experiment display page. Includes: info/names, counts (prot.), source, etc
    """
    e = db.session.query(Experiment).get(experiment_id)
    if e:
        return render_template('experiment.html', experiments={e.id: e})
    return render_template('experiment.html', experiments={})


@app.route('/embed-struct/<int:structure_id>', methods=['GET',])
def embed_structure(structure_id, ):
    """
    A very simple page consisting only of GLMol embedding components. Meant for filling
    in iframe on domain page. Takes a structure id, fetches structure DBO, and passes
    it to template to render.
    """
    s = db.session.query(Structure).get(structure_id)
    if s:
        return render_template('embed_structure.html', structure=s)
    return render_template('embed_structure.html')


@app.route('/protein', methods=['GET',])
def protein():
    """
    The protein index page. When given terms, send a dict (id->db.Protein) of proteins to the template
    """
    if is_search(request):
        type, search_term = get_search_fields(request.args)
        whole_search = "{0} : {1}".format(type, search_term)

        if type == "hpf_id":
            proteins = db.session.query(Protein).filter_by(id=search_term).all()
        elif type == "seq_id":
            proteins = db.session.query(Protein).filter_by(sequence_key=search_term).all()
        elif type == "ac":
            acs = db.session.query(SequenceAc).filter_by(ac=search_term).all()
            proteins = [a.protein for a in acs if a.protein]
        elif type == "keyword":
            acs = db.session.query(SequenceAc).filter(SequenceAc.description.like("%{0} %".format(search_term))).all()
            proteins = [a.protein for a in acs if a.protein]
        else:
            return render_template('bad_search.html', request=request)

        return render_template('protein.html', proteins=dict((p.id, p) for p in proteins), search=whole_search)
    
    return render_template('protein.html')

@app.route('/protein/<int:protein_id>')
def fetch_protein(protein_id):
    """
    Protein display page, fetches protein by ID and displays
    """
    p = db.session.query(Protein).get(protein_id)
    if p:
        return render_template('protein.html', proteins={p.id: p})
    return render_template('protein.html', proteins={})


@app.route('/domain', methods=['GET',])
def domain():
    """
    Domain index page
    """
    if is_search(request):
        type, search_term = get_search_fields(request.args)
        whole_search = "{0} : {1}".format(type, search_term)

        if type == "hpf_id":
            domains = db.session.query(Domain).filter_by(id=search_term).all()
        elif type == "seq_id":
            domains = db.session.query(Domain).filter_by(domain_sequence_key=search_term).all()
        elif type == "prediction_code":
            domains = db.session.query(Domain).filter_by(ibm_prediction_code=search_term).all()
        elif type == "protein_id":
            protein = db.session.query(Protein).get(search_term)
            domains = protein.domains
        else:
            return render_template('bad_search.html', request=request)
        
        return render_template('domain.html', domains=dict((d.id, d) for d in domains), search=whole_search)
    
    return render_template('domain.html')

@app.route('/domain/<int:domain_id>')
def fetch_domain(domain_id):
    """
    Domain display page. Includes: all info, sequence, ginzu info, region,
    and known v unknown structure display
    """
    d = db.session.query(Domain).get(domain_id)
    if d:
        return render_template('domain.html', domains={d.id: d})
    return render_template('domain.html', domains={})

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
    app.run(host='0.0.0.0')

