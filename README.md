# Algèbre de Boole et tableau de Karnaugh : cours et exercices corrigés

Code de la vidéo de la chaîne [IT Skills Maker](https://www.youtube.com/@ItSkillsMaker) (lien de la vidéo ajouté à la
publication).

Python pur, sans aucune bibliothèque à installer (Python 3.11 ou plus récent). Tout est exécuté, et les sorties réelles
sont dans [`preuves/`](preuves/).

Le principe : deux expressions sont égales si elles donnent la même sortie sur **toutes** les lignes de la table de
vérité. Le programme ne fait confiance à aucune simplification, il les essaie toutes.

| Fichier | Contenu |
|---|---|
| `boole.py` | Lecture d'une somme de produits (`"AB' + C"`, l'apostrophe nie la lettre), table de vérité, comparaison ligne par ligne, mintermes, forme canonique, nombre de portes, tableau de Karnaugh en code de Gray, toutes les formes minimales (Quine-McCluskey), correction d'une copie (`juger`) |
| `demo.py` | L'accroche et les 7 exercices de la vidéo |
| `test_boole.py` | 21 tests, dont les 256 fonctions de 3 variables |

```
python demo.py
python -m unittest -v
```

## Les exercices

1. Simplifier `AB + ABC + A'B`.
2. Complémenter `AB + C'` avec De Morgan.
3. Le vote à la majorité de trois juges : de la table de vérité à la forme minimale.
4. Karnaugh à 4 variables : `Σm(0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14)`, puis les quatre coins `Σm(0, 2, 8, 10)`.
5. Les cas indifférents : un chiffre BCD supérieur ou égal à 5.
6. Une fonction qui a deux formes minimales : `Σm(0, 1, 2, 5, 6, 7)`.
7. Trouver l'erreur : trois copies pour la fonction de l'exercice 4.

Pour corriger votre propre réponse :

```python
from boole import juger
print(juger("C' + A'D' + BD'", [0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14], "ABCD"))
# JUSTE et MINIMALE
```
