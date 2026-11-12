"""Algebre de Boole et tableaux de Karnaugh : les outils qui verifient chaque exercice de la video.

Une expression s'ecrit en somme de produits, avec une apostrophe pour la negation :
    "AB' + C"  veut dire  (A ET NON B) OU C

Le principe de toute la video : deux expressions sont egales si et seulement si elles donnent
la meme sortie sur TOUTES les lignes de la table de verite (2^n lignes pour n variables).
Le programme ne fait pas confiance aux simplifications : il les essaie toutes.

    python demo.py           # les exercices de la video
    python -m unittest -v    # les tests
"""
from itertools import combinations, product

# Ordre de Gray : deux cases voisines ne different que d'un seul bit. C'est l'ordre des lignes
# et des colonnes d'un tableau de Karnaugh (00, 01, 11, 10), et pas l'ordre binaire 00, 01, 10, 11.
GRAY = {1: ["0", "1"], 2: ["00", "01", "11", "10"]}


# --- Lire et evaluer une expression ----------------------------------------------------------

def et(*xs):
    """ET : 1 seulement si toutes les entrees valent 1."""
    return min(xs)


def ou(*xs):
    """OU : 1 des qu'au moins une entree vaut 1 (1 + 1 = 1 : on ne compte pas)."""
    return max(xs)


def non(x):
    """NON : l'inverse."""
    return 1 - x


def produits(expression):
    """ "AB' + C" -> [[("A", True), ("B", False)], [("C", True)]].  "1" = toujours vrai, "0" = jamais.

    Les variables sont des majuscules. Chaque apostrophe nie la lettre qui la precede : A'' redevient A.
    Une expression mal ecrite (« A + », « 'A », « a ») leve ValueError au lieu d'etre lue de travers :
    le programme sert de correcteur, il ne doit pas juger une expression que l'eleve n'a pas ecrite.
    """
    morceaux = expression.replace(" ", "").split("+")
    termes = []
    for morceau in morceaux:
        if morceau == "":
            raise ValueError(f"produit vide (un + en trop ?) dans {expression!r}")
        if morceau == "0":
            continue
        if morceau == "1":
            termes.append([])
            continue
        litteraux = []
        i = 0
        while i < len(morceau):
            c = morceau[i]
            if not ("A" <= c <= "Z"):
                raise ValueError(f"caractere inattendu {c!r} dans {expression!r} (variables en majuscules)")
            j = i + 1
            while j < len(morceau) and morceau[j] == "'":
                j += 1
            litteraux.append((c, (j - i - 1) % 2 == 0))
            i = j
        termes.append(litteraux)
    return termes


def lettres(expression):
    """Les variables utilisees par l'expression."""
    return {v for t in produits(expression) for v, _ in t}


def fonction(expression, variables=None):
    """Transforme le texte en fonction Python : f(valeurs) -> 0 ou 1. Le texte n'est lu qu'une fois.

    Avec `variables`, refuse une lettre qui n'en fait pas partie (ValueError).
    """
    termes = produits(expression)
    if variables is not None:
        inconnues = sorted(lettres(expression) - set(variables))
        if inconnues:
            raise ValueError(f"variable(s) inconnue(s) {', '.join(inconnues)} dans {expression!r}")

    def f(valeurs):
        for terme in termes:
            if all(valeurs[v] == (1 if positif else 0) for v, positif in terme):
                return 1
        return 0
    return f


def evaluer(expression, valeurs):
    """Valeur (0 ou 1) d'une somme de produits pour des valeurs {"A": 1, "B": 0, ...}."""
    return fonction(expression)(valeurs)


def _verifier_mintermes(liste, n):
    """Un minterme de n variables est un numero de ligne, de 0 a 2^n - 1."""
    for m in liste:
        if not (isinstance(m, int) and 0 <= m < 2 ** n):
            raise ValueError(f"minterme {m!r} hors de la table ({2 ** n} lignes, de 0 a {2 ** n - 1})")


def lignes(variables):
    """Les 2^n lignes de la table de verite, dans l'ordre binaire : 000, 001, 010..."""
    for bits in product((0, 1), repeat=len(variables)):
        yield dict(zip(variables, bits))


def table_de_verite(f, variables):
    """[(valeurs, sortie)] pour toutes les lignes. f est une expression (texte) ou une fonction."""
    f = fonction(f, variables) if isinstance(f, str) else f
    return [(v, f(v)) for v in lignes(variables)]


def differences(f, g, variables, indifferents=()):
    """Les lignes ou f et g ne donnent pas la meme sortie (liste vide = expressions egales).

    `indifferents` : numeros de lignes (mintermes) dont la sortie n'a pas d'importance (les X).
    """
    indifferents = frozenset(indifferents)
    _verifier_mintermes(indifferents, len(variables))
    f = fonction(f, variables) if isinstance(f, str) else f
    g = fonction(g, variables) if isinstance(g, str) else g
    return [v for v in lignes(variables)
            if numero(v, variables) not in indifferents and f(v) != g(v)]


def numero(valeurs, variables):
    """Numero de la ligne (le minterme) : A=1, B=0, C=1 -> 101 en binaire -> 5."""
    n = 0
    for v in variables:
        n = 2 * n + valeurs[v]
    return n


def mintermes(f, variables):
    """Numeros des lignes ou la sortie vaut 1 : la fonction s'ecrit alors Somme m(...)."""
    return [numero(v, variables) for v, s in table_de_verite(f, variables) if s]


def forme_canonique(liste_mintermes, variables):
    """La somme de mintermes ecrite en clair : chaque 1 de la table devient un produit complet."""
    _verifier_mintermes(liste_mintermes, len(variables))
    termes = []
    for m in liste_mintermes:
        bits = format(m, f"0{len(variables)}b")
        termes.append("".join(v if b == "1" else v + "'" for v, b in zip(variables, bits)))
    return " + ".join(termes) if termes else "0"


# --- Compter les portes logiques -------------------------------------------------------------

def portes(expression):
    """Nombre de portes pour cabler la somme de produits telle qu'elle est ecrite.

    Une porte NON par variable niee, une porte ET par produit d'au moins deux litteraux, une porte
    OU s'il y a au moins deux produits. (Le cablage en deux niveaux du cours, sans astuce.)
    """
    termes = produits(expression)
    nies = {v for t in termes for v, positif in t if not positif}
    portes_et = sum(1 for t in termes if len(t) >= 2)
    porte_ou = 1 if len(termes) >= 2 else 0
    return len(nies) + portes_et + porte_ou


def litteraux(expression):
    """Nombre total de lettres dans l'expression (le cout que Karnaugh minimise, apres le nombre de termes)."""
    return sum(len(t) for t in produits(expression))


# --- Karnaugh : afficher le tableau ----------------------------------------------------------

def karnaugh(liste_mintermes, variables, indifferents=()):
    """Le tableau de Karnaugh en texte. 3 variables : lignes A, colonnes BC. 4 variables : lignes AB, colonnes CD."""
    n = len(variables)
    if n not in (3, 4):
        raise ValueError("Karnaugh affiche ici 3 ou 4 variables")
    uns, indifferents = frozenset(liste_mintermes), frozenset(indifferents)
    _verifier_mintermes(uns | indifferents, n)
    haut = n // 2                        # 3 variables -> 1 en ligne ; 4 -> 2
    lignes_gray, colonnes_gray = GRAY[haut], GRAY[n - haut]
    titre = f"{variables[:haut]} \\ {variables[haut:]}"
    sortie = [f"{titre:>8} | " + "  ".join(colonnes_gray)]
    for l in lignes_gray:
        cases = []
        for c in colonnes_gray:
            m = int(l + c, 2)
            cases.append(" 1" if m in uns else (" X" if m in indifferents else " 0"))
        sortie.append(f"{l:>8} | " + "  ".join(cases))
    return "\n".join(sortie)


# --- Trouver la forme minimale : Quine-McCluskey, puis toutes les couvertures -----------------
#
# Ce que fait Karnaugh a l'oeil, le programme le fait par force brute (4 variables au plus).
# Il sert de juge : il dit si la reponse d'un exercice est juste, et si elle est minimale.

def _combiner(a, b):
    """Deux motifs ("01-1", "0111") qui ne different que d'un bit se fusionnent ("01-1")."""
    ecarts = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(ecarts) == 1 and "-" not in (a[ecarts[0]], b[ecarts[0]]):
        i = ecarts[0]
        return a[:i] + "-" + a[i + 1:]
    return None


def implicants_premiers(liste_mintermes, n, indifferents=()):
    """Les plus grands regroupements possibles (1, 2, 4, 8 cases) : les implicants premiers."""
    tous = set(liste_mintermes) | set(indifferents)
    _verifier_mintermes(tous, n)
    courants = {format(m, f"0{n}b") for m in tous}
    premiers = set()
    while courants:
        utilises, suivants = set(), set()
        for a, b in combinations(sorted(courants), 2):
            c = _combiner(a, b)
            if c:
                suivants.add(c)
                utilises.update((a, b))
        premiers |= courants - utilises
        courants = suivants
    return sorted(premiers)


def couvre(motif, m, n):
    """Le regroupement `motif` contient-il la case m ?"""
    return all(p == "-" or p == b for p, b in zip(motif, format(m, f"0{n}b")))


def motif_en_produit(motif, variables):
    """ "1-0-" -> "AC'" (les tirets sont les variables qui changent dans le groupe : elles disparaissent)."""
    texte = "".join(v if p == "1" else v + "'" for v, p in zip(variables, motif) if p != "-")
    return texte or "1"


def formes_minimales(liste_mintermes, variables, indifferents=()):
    """TOUTES les sommes de produits minimales (moins de termes, puis moins de lettres).

    Il peut y en avoir plusieurs, aussi justes l'une que l'autre : c'est pour ca qu'une correction
    de Karnaugh n'est pas forcement unique.
    """
    n = len(variables)
    if n > 4:
        # La recherche essaie toutes les combinaisons de groupes : au-dela de 4 variables, elle explose.
        raise ValueError("formes_minimales : 4 variables au plus (recherche exhaustive)")
    liste_mintermes, indifferents = sorted(set(liste_mintermes)), frozenset(indifferents)
    _verifier_mintermes(liste_mintermes, n)
    if not liste_mintermes:
        return ["0"]
    premiers = implicants_premiers(liste_mintermes, n, indifferents)
    for taille in range(1, len(premiers) + 1):
        solutions = []
        for choix in combinations(premiers, taille):
            if all(any(couvre(p, m, n) for p in choix) for m in liste_mintermes):
                solutions.append(choix)
        if solutions:
            nb_lettres = lambda s: sum(len(p) - p.count("-") for p in s)
            cout = min(map(nb_lettres, solutions))
            meilleures = [s for s in solutions if nb_lettres(s) == cout]
            # Les produits les plus courts d'abord, puis par ordre alphabetique : "C' + A'D' + BD'"
            ordre = lambda p: (len(p) - p.count("-"), motif_en_produit(p, variables))
            return sorted(" + ".join(motif_en_produit(p, variables) for p in sorted(s, key=ordre)) for s in meilleures)
    raise AssertionError("aucune couverture : impossible")


def juger(reponse, liste_mintermes, variables, indifferents=()):
    """Corrige une reponse d'eleve : juste ? minimale ? Renvoie un texte d'une ligne par verdict.

    Une reponse mal ecrite (un + en trop, une lettre inconnue) est rendue ILLISIBLE, sans planter.
    """
    indifferents = frozenset(indifferents)
    try:
        fonction(reponse, variables)
    except ValueError as erreur:
        return f"ILLISIBLE : {erreur}"
    attendu = forme_canonique(liste_mintermes, variables)
    faux = differences(reponse, attendu, variables, indifferents)
    if faux:
        lignes_fausses = ", ".join(format(numero(v, variables), f"0{len(variables)}b") for v in faux)
        return f"FAUSSE : differente sur {len(faux)} ligne(s) de la table ({lignes_fausses})"
    minimale = formes_minimales(liste_mintermes, variables, indifferents)[0]
    taille_reponse = (len(produits(reponse)), litteraux(reponse))
    taille_minimale = (len(produits(minimale)), litteraux(minimale))
    if taille_reponse > taille_minimale:
        return (f"JUSTE mais PAS MINIMALE : {taille_reponse[0]} termes et {taille_reponse[1]} lettres, "
                f"contre {taille_minimale[0]} termes et {taille_minimale[1]} lettres pour {minimale}")
    return "JUSTE et MINIMALE"
