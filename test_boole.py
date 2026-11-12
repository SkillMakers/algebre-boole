"""Tests : chaque resultat cite dans la video est verifie ici.

    python -m unittest -v
"""
import unittest

from boole import (differences, et, forme_canonique, formes_minimales, implicants_premiers, juger, karnaugh,
                   mintermes, non, ou, portes, produits)


class TestLecture(unittest.TestCase):

    def test_lecture_d_une_somme_de_produits(self):
        """L'apostrophe nie la lettre qui la precede."""
        # GIVEN
        expression = "AB' + C"
        # WHEN
        termes = produits(expression)
        # THEN
        self.assertEqual(termes, [[("A", True), ("B", False)], [("C", True)]])

    def test_minterme_numero_de_la_ligne(self):
        """A=1, B=0, C=1 est la ligne 101, soit 5 : AB'C est le minterme m5."""
        # GIVEN
        expression = "AB'C"
        # WHEN / THEN
        self.assertEqual(mintermes(expression, "ABC"), [5])


class TestLois(unittest.TestCase):

    def test_de_morgan_et_absorption_vraies_sur_toutes_les_lignes(self):
        """(A + B)' = A'B', (AB)' = A' + B', A + AB = A, A + A'B = A + B, A + BC = (A + B)(A + C)."""
        # GIVEN
        lois = [
            (lambda v: non(ou(v["A"], v["B"])), "A'B'", "AB"),
            (lambda v: non(et(v["A"], v["B"])), "A' + B'", "AB"),
            ("A + AB", "A", "AB"),
            ("A + A'B", "A + B", "AB"),
            ("A + BC", lambda v: et(ou(v["A"], v["B"]), ou(v["A"], v["C"])), "ABC"),
        ]
        for gauche, droite, variables in lois:
            with self.subTest(droite=droite):
                # WHEN / THEN
                self.assertEqual(differences(gauche, droite, variables), [])

    def test_l_erreur_classique_de_de_morgan_est_fausse_sur_deux_lignes(self):
        """(A + B)' n'est pas A' + B' : elles different pour A,B = 01 et 10."""
        # GIVEN
        gauche = lambda v: non(ou(v["A"], v["B"]))
        # WHEN
        faux = differences(gauche, "A' + B'", "AB")
        # THEN
        self.assertEqual([(v["A"], v["B"]) for v in faux], [(0, 1), (1, 0)])


class TestExercices(unittest.TestCase):

    def test_accroche_quatre_produits_egalent_une_porte_nor(self):
        """A'B'C'D' + A'B'CD' + AB'C'D' + AB'CD' = B'D' = NON(B OU D) ; 9 portes contre 3 en deux niveaux."""
        # GIVEN
        depart = "A'B'C'D' + A'B'CD' + AB'C'D' + AB'CD'"
        # WHEN
        minimale = formes_minimales(mintermes(depart, "ABCD"), "ABCD")
        # THEN
        self.assertEqual(minimale, ["B'D'"])
        self.assertEqual((portes(depart), portes("B'D'")), (9, 3))
        self.assertEqual(differences(depart, lambda v: non(ou(v["B"], v["D"])), "ABCD"), [])

    def test_ex1_simplification_algebrique(self):
        """AB + ABC + A'B = B."""
        # GIVEN
        f = "AB + ABC + A'B"
        # WHEN / THEN
        self.assertEqual(differences(f, "B", "ABC"), [])

    def test_ex2_complement_par_de_morgan(self):
        """(AB + C')' = A'C + B'C, et pas A'B' + C (fausse sur 000 et 111)."""
        # GIVEN
        complement = lambda v: non(ou(et(v["A"], v["B"]), non(v["C"])))
        # WHEN
        juste = differences(complement, "A'C + B'C", "ABC")
        faux = differences(complement, "A'B' + C", "ABC")
        # THEN
        self.assertEqual(juste, [])
        self.assertEqual(["".join(str(v[x]) for x in "ABC") for v in faux], ["000", "111"])

    def test_ex3_majorite(self):
        """Vote a 3 : Somme m(3, 5, 6, 7) = AB + AC + BC ; 8 portes en canonique, 4 en minimale."""
        # GIVEN
        majorite = lambda v: 1 if v["A"] + v["B"] + v["C"] >= 2 else 0
        # WHEN
        m = mintermes(majorite, "ABC")
        minimales = formes_minimales(m, "ABC")
        cout = (portes(forme_canonique(m, "ABC")), portes(minimales[0]))
        # THEN
        self.assertEqual(m, [3, 5, 6, 7])
        self.assertEqual(minimales, ["AB + AC + BC"])
        self.assertEqual(cout, (8, 4))

    def test_ex4_karnaugh_quatre_variables_et_quatre_coins(self):
        """Somme m(0,1,2,4,5,6,8,9,12,13,14) = C' + A'D' + BD' ; Somme m(0,2,8,10) = B'D' (les 4 coins)."""
        # GIVEN
        m4 = [0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14]
        # WHEN / THEN
        self.assertEqual(formes_minimales(m4, "ABCD"), ["C' + A'D' + BD'"])
        self.assertEqual(formes_minimales([0, 2, 8, 10], "ABCD"), ["B'D'"])

    def test_ex5_les_cas_indifferents_raccourcissent(self):
        """Chiffre BCD >= 5 : 9 lettres sans les X, 5 avec (A + BC + BD)."""
        # GIVEN
        bcd = [5, 6, 7, 8, 9]
        # WHEN
        sans, avec = formes_minimales(bcd, "ABCD"), formes_minimales(bcd, "ABCD", range(10, 16))
        # THEN
        self.assertEqual(sans, ["A'BC + A'BD + AB'C'"])
        self.assertEqual(avec, ["A + BC + BD"])

    def test_ex6_deux_formes_minimales(self):
        """Somme m(0, 1, 2, 5, 6, 7) a deux corriges minimaux, tous deux justes."""
        # GIVEN
        m6 = [0, 1, 2, 5, 6, 7]
        # WHEN
        formes = formes_minimales(m6, "ABC")
        # THEN
        self.assertEqual(formes, ["A'B' + AC + BC'", "A'C' + AB + B'C"])
        for forme in formes:
            self.assertEqual(juger(forme, m6, "ABC"), "JUSTE et MINIMALE")

    def test_ex7_les_trois_copies(self):
        """Copie 1 : bord oublie, juste mais pas minimale. Copie 2 : couvre la case 1010, fausse."""
        # GIVEN
        m4 = [0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 14]
        # WHEN / THEN
        self.assertTrue(juger("C' + A'CD' + BCD'", m4, "ABCD").startswith("JUSTE mais PAS MINIMALE"))
        self.assertEqual(juger("C' + D'", m4, "ABCD"), "FAUSSE : differente sur 1 ligne(s) de la table (1010)")
        self.assertEqual(juger("C' + A'D' + BD'", m4, "ABCD"), "JUSTE et MINIMALE")


class TestOutils(unittest.TestCase):

    def test_karnaugh_suit_l_ordre_de_gray(self):
        """Colonnes 00, 01, 11, 10 : la case m3 (011) est en 3e colonne, m2 (010) en 4e."""
        # GIVEN
        m = [2]
        # WHEN
        premiere_ligne = karnaugh(m, "ABC").splitlines()[1]
        # THEN
        self.assertEqual(premiere_ligne.split("|")[1].split(), ["0", "0", "0", "1"])

    def test_formes_minimales_justes_sur_toutes_les_fonctions_a_3_variables(self):
        """Les 256 fonctions de 3 variables : la forme minimale trouvee est toujours egale a la fonction."""
        for code in range(256):
            # GIVEN : la fonction dont la table s'ecrit en binaire `code` (bit i = sortie de la ligne i)
            m = [i for i in range(8) if code >> i & 1]
            with self.subTest(m=m):
                # WHEN
                forme = formes_minimales(m, "ABC")[0]
                # THEN
                self.assertEqual(differences(forme, forme_canonique(m, "ABC"), "ABC"), [])

    def test_implicants_premiers_du_vote(self):
        """Majorite : trois groupes de deux cases, et aucun plus grand."""
        # GIVEN
        m = [3, 5, 6, 7]
        # WHEN / THEN
        self.assertEqual(implicants_premiers(m, 3), ["-11", "1-1", "11-"])


class TestCopiesMalEcrites(unittest.TestCase):
    """Le correcteur ne doit jamais juger une expression que l'eleve n'a pas ecrite."""

    def test_un_plus_en_trop_est_illisible(self):
        """« A + » n'est pas « A + 1 » : la copie est rendue illisible."""
        # GIVEN
        reponse = "A + "
        # WHEN
        verdict = juger(reponse, [0, 1, 2, 3], "AB")
        # THEN
        self.assertTrue(verdict.startswith("ILLISIBLE"))

    def test_une_lettre_inconnue_est_illisible(self):
        """Une variable hors de la table, ou une minuscule, ne fait pas planter le correcteur."""
        for reponse in ("A + E", "a + b"):
            with self.subTest(reponse=reponse):
                # GIVEN : la reponse de la boucle
                # WHEN
                verdict = juger(reponse, [1, 2, 3], "AB")
                # THEN
                self.assertTrue(verdict.startswith("ILLISIBLE"))

    def test_deux_apostrophes_s_annulent(self):
        """A'' = A."""
        # GIVEN
        double = "A''"
        # WHEN
        termes = produits(double)
        # THEN
        self.assertEqual(termes, [[("A", True)]])

    def test_apostrophe_sans_lettre_refusee(self):
        """Une apostrophe sans lettre devant n'est pas lue en silence."""
        # GIVEN
        expression = "'A"
        # WHEN / THEN
        with self.assertRaises(ValueError):
            produits(expression)

    def test_minterme_hors_table_refuse(self):
        """La ligne 9 n'existe pas avec 3 variables (8 lignes)."""
        # GIVEN
        trop_grand = [9]
        # WHEN / THEN
        with self.assertRaises(ValueError):
            forme_canonique(trop_grand, "ABC")

    def test_indifferents_donnes_par_un_generateur(self):
        """Les X passes en generateur ne sont pas perdus en route."""
        # GIVEN
        x = (i for i in range(10, 16))
        # WHEN
        verdict = juger("A + BC + BD", [5, 6, 7, 8, 9], "ABCD", x)
        # THEN
        self.assertEqual(verdict, "JUSTE et MINIMALE")


if __name__ == "__main__":
    unittest.main()
