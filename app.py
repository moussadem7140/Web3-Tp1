"""
Une application Flask des plus simples !
"""

from flask import Flask, render_template, request, redirect, abort, make_response
import bd 
from flask.logging import create_logger
import re 


app = Flask(__name__)
logger = create_logger(app)
pas_html= re.compile('<.*?>')

@app.route('/langue_fr_CA')
def langue_fr_CA():
    reponse = make_response(redirect('/'))
    reponse.set_cookie('langue', 'fr_CA')
    return reponse
@app.route('/langue_fr_FR')
def langue_fr_FR():
    reponse = make_response(redirect('/'))
    reponse.set_cookie('langue', 'fr_FR')
    return reponse

@app.route('/langue_en_CA')
def langue_en_CA():
    reponse = make_response(redirect('/'))
    reponse.set_cookie('langue', 'en_CA')
    return reponse

def liste_categories():
    try:
        with bd.creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("SELECT * FROM categories")
                liste_categories = curseur.fetchall()
        return liste_categories
    except Exception as e:
        logger.exception(e)
        abort(500)
        
@app.route('/')
def index():
    try:
        with bd.creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("SELECT * FROM services JOIN categories on services.id_categorie= categories.id_categorie where actif=1 order by date_creation  DESC ")
                liste_services = curseur.fetchmany(5)
        return render_template('index.jinja', liste=liste_services, langue=request.cookies.get('langue', 'fr_CA'))
    except Exception as e:
        logger.exception(e)
        abort(500)
@app.route('/liste_services')
def liste_service():
    try:
        with bd.creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("SELECT * FROM services JOIN categories on services.id_categorie= categories.id_categorie order by date_creation  DESC ")
                liste_services = curseur.fetchall()
        return render_template('liste_services.jinja', liste=liste_services, langue=request.cookies.get('langue', 'fr_CA'))
    except Exception as e:
        logger.exception(e)
        abort(500)

@app.route('/ajoutModif')
def ajout_modif():
    if not request.args.get('id_service', type=int, default=0) or not request.args.get('action', default='ajout'):
        abort(400)
    id_service = request.args.get('id_service', type=int, default=0)
    action = request.args.get('action', default='ajout')
    return render_template('ajout.jinja', action=action, categories=liste_categories(), id_service=id_service, langue= request.cookies.get('langue', 'fr_CA'))

@app.route('/validation', methods=['POST','GET'])
def validation(): 
    if not request.args.get('id_service', type=int, default=0) or not request.args.get('action', default='ajout'):
        abort(400)
    id_service = request.args.get('id_service', type=int, default=0)
    action = request.args.get('action', default='ajout')

    if request.method == 'POST':
        validation = True
        class_titre = ""
        class_description = ""
        class_localisation = ""
        class_categorie = ""
        class_photo = ""
        class_cout = ""
        titre= request.form['titre']
        if not titre or len(titre) > 50 or re.match(pas_html, titre):
            class_titre = "is-invalid"
            validation = False
        description = request.form['description']
        if not description or len(description) > 2000 or len(description) < 5 or re.match(pas_html, description):
            class_description = "is-invalid"
            validation = False
        localisation = request.form['localisation']
        if not localisation or len(localisation) > 50 or re.match(pas_html, localisation):
            class_localisation = "is-invalid"
            validation = False
        cout = request.form['cout']
        categorie = request.form['categorie']
        if not categorie :
            class_categorie = "is-invalid"
            validation = False
        status = 'status' in request.form
        photo = request.form['photo']
        if photo:
            if not re.match('[A-Za-z0-9\-.]{6,50}', photo) or re.match(pas_html, photo):
                class_photo = "is-invalid"
                validation = False
        if validation is True:
            try:
                with bd.creer_connexion() as connexion:
                    with connexion.get_curseur() as curseur:
                        if action == 'ajout':
                            curseur.execute(
                        "INSERT INTO services VALUES (Null, %(categorie)s, %(titre)s, %(description)s, %(localisation)s, Now(), %(actif)s, %(cout)s, %(photo)s)",
                        {'categorie': categorie, 'titre': titre, 'description': description, 'localisation': localisation, 'actif': status, 'cout': cout, 'photo': photo})
                        else:
                            curseur.execute("UPDATE services SET  titre= %(titre)s, description=%(description)s, localisation= %(localisation)s, actif=%(actif)s, cout= %(cout)s, photo=%(photo)s where id_service= %(indice)s", {
                                      'titre': titre, 'description': description, 'localisation': localisation, 'actif': status, 'cout': cout, 'photo': photo, 'indice': id_service}) 
            except Exception as e:
                logger.exception(e)
                abort(500)            
            return redirect('/comfirmation')
        else:
            return render_template('ajout.jinja', action=action, class_titre=class_titre, class_description=class_description, class_localisation=class_localisation, class_categorie=class_categorie, class_photo=class_photo, class_cout=class_cout,categories=liste_categories(), id_service= id_service, langue=request.cookies.get('Langue', 'fr_CA'))
    else:
            return render_template('ajout.jinja', action=action, class_titre=class_titre, class_description=class_description, class_localisation=class_localisation, class_categorie=class_categorie, class_photo=class_photo, class_cout=class_cout,categories=liste_categories(), id_service= id_service, langue=request.cookies.get('Langue', 'fr_CA'))

@app.route('/details')
def detail():
    if not request.args.get('id_service', type=int):
        abort(400)
    id_service = request.args.get('id_service', type=int)
    try:
        with bd.creer_connexion() as connexion:
            with connexion.get_curseur() as curseur:
                curseur.execute("SELECT nom_categorie, actif, titre, localisation, photo, cout, date_creation, S.description, id_service FROM services S JOIN categories C on S.id_categorie= C.id_categorie where id_service=%(id_service)s", {'id_service': id_service})
                service = curseur.fetchone()
    except Exception as e:
        logger.exception(e)
        abort(500)
    return render_template('details.jinja', service=service) 

@app.route('/comfirmation')
def comfirmation():
    return render_template('confirmation.jinja')

@app.errorhandler(404)
def not_found(e):
    """Fonction qui gère l'erreur 404"""
    logger.exception(e)
    # c'est quoi l'erreur 404 ? ca signifie quoi ?
    return render_template("erreur.jinja", message = "page introuvable", code="404"), 404

@app.errorhandler(400)
def not_found1(e):
    """Fonction qui gère l'erreur 404"""
    logger.exception(e)
    # c'est quoi l'erreur 404 ? ca signifie quoi ?
    return render_template("erreur.jinja", message = "page introuvable", code="400"), 400

@app.errorhandler(500)
def bot_found2(e):
    """Pour les erreurs 500"""
    logger.exception(e)
    return render_template(
        'erreur.jinja',
        message="Oups! Une erreur est survenue côté de la base de donnée. ", code="500"), 500

if __name__ == '__main__':
    app.run(debug=True) 

