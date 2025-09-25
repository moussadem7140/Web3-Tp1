"""
Une application Flask des plus simples !
"""

from flask import Flask

app = Flask(__name__)

#  ajouter une nouvelle "page" /a-propos affichant votre nom

if __name__ == '__main__':
    app.run(debug=True)
    