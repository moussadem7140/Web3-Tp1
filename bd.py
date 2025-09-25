"""
Connexion à la BD
"""

import types
import contextlib
import mysql.connector
@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user="root",
        password="fP:!snc^>>4W$+.", # verifier ca toujours
        host="127.0.0.1",
        database="demo_jeux",
        raise_on_warnings=True
    )

    # Pour ajouter la méthode getCurseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir *tous* les enregistrements dans un dictionnaire"""
    curseur = self.cursor(dictionary=True, buffered=True)
    try:
        yield curseur
    finally:
        curseur.close()
