"""Les exercices de la video, executes : chaque reponse est verifiee sur toute la table de verite.

    python demo.py
"""
import sys

from boole import (differences, et, forme_canonique, formes_minimales, juger, karnaugh, litteraux, mintermes,
                   non, numero, ou, portes, table_de_verite)


# Hors des f-strings : une apostrophe ou des guillemets dans une f-string ne passent qu'a partir de Python 3.12.
MINI_ACCROCHE = "B'D'"
MINI_EX4 = "C' + A'D' + BD'"


def titre(texte):
    print(f"\n--- {texte}")


def verifier(nom, f, g, variables, indifferents=()):
    """Affiche si deux expressions sont egales, en essayant toutes les lignes (sauf les cas indifferents)."""
    indifferents = frozenset(indifferents)
    faux = differences(f, g, variables, indifferents)
    n = 2 ** len(variables) - len(indifferents)
    if faux:
        detail = ", ".join("".join(str(v[x]) for x in variables) for v in faux)
        print(f"{nom:<38} FAUX : {len(faux)} ligne(s) sur {n} different ({variables} = {detail})")
    else:
        print(f"{nom:<38} vrai sur les {n} lignes")


def main():
    print(f"Python {sys.version.split()[0]}")

    titre("Accroche : quatre produits de quatre lettres, et une seule porte NOR")
    depart = "A'B'C'D' + A'B'CD' + AB'C'D' + AB'CD'"
    print(f"F = {depart}")
    print(f"portes : {portes(depart)} (4 NON, 4 ET, 1 OU)")
    print(f"forme minimale : {formes_minimales(mintermes(depart, 'ABCD'), 'ABCD')[0]}  ({portes(MINI_ACCROCHE)} portes)")
    verifier("F = NON(B OU D), une porte NOR", depart, lambda v: non(ou(v["B"], v["D"])), "ABCD")

    titre("Table de verite de F = AB + C'")
    print("A B C | F")
    for v, s in table_de_verite("AB + C'", "ABC"):
        print(f"{v['A']} {v['B']} {v['C']} | {s}")

    titre("Les lois, verifiees sur toutes les lignes")
    V = "AB"
    verifier("A + A'      = 1 (complement)", lambda v: ou(v["A"], non(v["A"])), lambda v: 1, V)
    verifier("A . A'      = 0", lambda v: et(v["A"], non(v["A"])), lambda v: 0, V)
    verifier("A + AB      = A (absorption)", "A + AB", "A", V)
    verifier("A(A + B)    = A (absorption)", lambda v: et(v["A"], ou(v["A"], v["B"])), "A", V)
    verifier("A + A'B     = A + B", "A + A'B", "A + B", V)
    verifier("(A + B)'    = A'B' (De Morgan)", lambda v: non(ou(v["A"], v["B"])), "A'B'", V)
    verifier("(AB)'       = A' + B' (De Morgan)", lambda v: non(et(v["A"], v["B"])), "A' + B'", V)
    verifier("(A + B)'    = A' + B' (l'erreur)", lambda v: non(ou(v["A"], v["B"])), "A' + B'", V)
    verifier("A + BC      = (A + B)(A + C)", "A + BC", lambda v: et(ou(v["A"], v["B"]), ou(v["A"], v["C"])), "ABC")

    titre("Ex 1 : simplifier F = AB + ABC + A'B")
    verifier("AB + ABC = AB (absorption)", "AB + ABC", "AB", "ABC")
    verifier("AB + A'B = B (B(A + A') = B)", "AB + A'B", "B", "ABC")
    verifier("F = B", "AB + ABC + A'B", "B", "ABC")

    titre("Ex 2 : complementer F = AB + C' avec De Morgan")
    verifier("F' = (A' + B')C", lambda v: non(ou(et(v["A"], v["B"]), non(v["C"]))),
             lambda v: et(ou(non(v["A"]), non(v["B"])), v["C"]), "ABC")
    verifier("F' = A'C + B'C", lambda v: non(ou(et(v["A"], v["B"]), non(v["C"]))), "A'C + B'C", "ABC")
    verifier("F' = A'B' + C (l'erreur)", lambda v: non(ou(et(v["A"], v["B"]), non(v["C"]))), "A'B' + C", "ABC")

    titre("Ex 3 : le vote a la majorite (3 juges A, B, C) : de la table a l'expression")
    majorite = lambda v: 1 if v["A"] + v["B"] + v["C"] >= 2 else 0
    print("A B C | F")
    for v, s in table_de_verite(majorite, "ABC"):
        print(f"{v['A']} {v['B']} {v['C']} | {s}   (ligne {numero(v, 'ABC')})")
    m = mintermes(majorite, "ABC")
    canonique = forme_canonique(m, "ABC")
    print(f"F = Somme m{tuple(m)} = {canonique}  ({portes(canonique)} portes)")
    print(karnaugh(m, "ABC"))
    print(f"forme minimale : AB + AC + BC  ({portes('AB + AC + BC')} portes)")
    print(f"le programme trouve : {formes_minimales(m, 'ABC')}")
    verifier("F = AB + AC + BC", majorite, "AB + AC + BC", "ABC")

    titre("Ex 4 : Karnaugh a 4 variables, F = Somme m(0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14)")
    m4 = [0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14]
    print(karnaugh(m4, "ABCD"))
    print(f"forme canonique : {len(m4)} termes, {litteraux(forme_canonique(m4, 'ABCD'))} lettres, "
          f"{portes(forme_canonique(m4, 'ABCD'))} portes")
    print(f"forme minimale  : C' + A'D' + BD'  ({portes(MINI_EX4)} portes)")
    print(f"le programme trouve : {formes_minimales(m4, 'ABCD')}")
    verifier("F = C' + A'D' + BD'", forme_canonique(m4, "ABCD"), "C' + A'D' + BD'", "ABCD")

    titre("Ex 4 bis : les quatre coins, F = Somme m(0, 2, 8, 10)")
    print(karnaugh([0, 2, 8, 10], "ABCD"))
    print(f"le programme trouve : {formes_minimales([0, 2, 8, 10], 'ABCD')}")

    titre("Ex 5 : les cas indifferents. Chiffre BCD (0 a 9) >= 5 ; 10 a 15 n'existent pas (X)")
    bcd = [5, 6, 7, 8, 9]
    print(karnaugh(bcd, "ABCD", range(10, 16)))
    print(f"sans les X : {formes_minimales(bcd, 'ABCD')}")
    print(f"avec les X : {formes_minimales(bcd, 'ABCD', range(10, 16))}")
    verifier("A + BC + BD (les 6 X ignores)", lambda v: 1 if numero(v, "ABCD") >= 5 else 0,
             "A + BC + BD", "ABCD", range(10, 16))

    titre("Ex 6 : deux corriges differents, tous les deux justes. F = Somme m(0, 1, 2, 5, 6, 7)")
    m6 = [0, 1, 2, 5, 6, 7]
    print(karnaugh(m6, "ABC"))
    for forme in formes_minimales(m6, "ABC"):
        print(f"minimale : {forme:<16} -> {juger(forme, m6, 'ABC')}")

    titre("Ex 7 : trouver l'erreur. Trois copies pour F = Somme m(0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14)")
    for copie, reponse in (("copie 1", "C' + A'CD' + BCD'"), ("copie 2", "C' + D'"), ("copie 3", "C' + A'D' + BD'")):
        print(f"{copie} : F = {reponse:<20} -> {juger(reponse, m4, 'ABCD')}")


if __name__ == "__main__":
    main()
