#!/usr/bin/env python3
"""
Script natif (sans pandas) pour déterminer le produit le plus vendu
et le produit le moins vendu en nombre d'unités vendues.

Usage: python3 stats_native.py

Le script récupère le CSV depuis la même URL que `app.py`.
"""
import csv
import io
import sys
import urllib.request

URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSC4KusfFzvOsr8WJRgozzsCxrELW4G4PopUkiDbvrrV2lg0S19-zeryp02MC9WYSVBuzGCUtn8ucZW/pub?output=csv"
)

# candidats de noms de colonnes
PRODUCT_CANDIDATES = ['produit', 'product', 'nom_produit', 'produit_nom', 'article', 'item', 'libelle', 'name']
QTE_CANDIDATES = ['qte', 'quantite', 'quantity', 'qty', 'qte_vendue', 'volume']


def fetch_csv_text(url):
    resp = urllib.request.urlopen(url)
    raw = resp.read()
    # essayer utf-8, sinon fallback
    try:
        text = raw.decode('utf-8')
    except Exception:
        text = raw.decode('latin-1')
    return text


def detect_columns(fieldnames):
    # renvoie (product_col, qte_col)
    lower = {fn.lower(): fn for fn in fieldnames}
    product_col = None
    qte_col = None
    for cand in PRODUCT_CANDIDATES:
        if cand in lower:
            product_col = lower[cand]
            break
    for cand in QTE_CANDIDATES:
        if cand in lower:
            qte_col = lower[cand]
            break
    # heuristique si manquant
    if product_col is None:
        # prendre première colonne non numérique probable
        for fn in fieldnames:
            if fn.lower() in ('date', 'region'):
                continue
            product_col = fn
            break
    return product_col, qte_col


def parse_number(v):
    if v is None:
        return 0.0
    s = str(v).strip()
    if s == '':
        return 0.0
    # enlever espaces et séparateurs fréquents
    s = s.replace(',', '.')
    # retirer séparateurs de milliers si présents (ex: 1 234)
    s = s.replace(' ', '')
    try:
        return float(s)
    except Exception:
        return 0.0


def main():
    print('Chargement du CSV...')
    try:
        text = fetch_csv_text(URL)
    except Exception as e:
        print('Erreur lors du téléchargement du CSV:', e, file=sys.stderr)
        sys.exit(1)

    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []
    if not fieldnames:
        print('Le CSV ne contient pas d\'en-têtes.', file=sys.stderr)
        sys.exit(1)

    product_col, qte_col = detect_columns(fieldnames)
    print('Colonnes détectées: produit ->', product_col, ', qte ->', qte_col)

    if product_col is None:
        print("Impossible d'identifier une colonne produit.")
        sys.exit(1)

    # Totaux par produit
    totals = {}
    rows = 0
    for row in reader:
        rows += 1
        prod = row.get(product_col, '').strip()
        if prod == '':
            prod = '<INCONNU>'
        # si qte_col introuvable, tenter d'inférer une colonne numérique
        if qte_col is None:
            # chercher une colonne qui ressemble à quantité
            q_val = 0.0
            for fn in fieldnames:
                if fn.lower() in ('date', 'region', product_col.lower()):
                    continue
                v = parse_number(row.get(fn, ''))
                if v != 0.0:
                    q_val = v
                    break
        else:
            q_val = parse_number(row.get(qte_col, ''))

        totals[prod] = totals.get(prod, 0.0) + q_val

    if rows == 0:
        print('Aucune ligne dans le CSV.')
        sys.exit(0)

    if not totals:
        print('Aucun total calculé (données manquantes).')
        sys.exit(0)

    # conversion des totaux en liste triée
    items = list(totals.items())
    # filtrer produits avec total 0 ? garder, mais signaler
    # trouver max et min
    max_val = max(items, key=lambda x: x[1])[1]
    min_val = min(items, key=lambda x: x[1])[1]

    most_sold = [p for p, v in items if v == max_val]
    least_sold = [p for p, v in items if v == min_val]

    print('\nRésultats:')
    print(f"Nombre de lignes traitées: {rows}")
    print(f"Nombre de produits distincts: {len(items)}")

    print('\nProduit(s) le plus vendu (unités):')
    for p in most_sold:
        print(f" - {p} : {totals[p]:.3f} unités")

    print('\nProduit(s) le moins vendu (unités):')
    for p in least_sold:
        print(f" - {p} : {totals[p]:.3f} unités")

    # sauvegarder résumé
    out = 'top_bottom_products.txt'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f"lignes_traites,{rows}\n")
        f.write(f"produits_distincts,{len(items)}\n")
        f.write('\n')
        f.write('most_sold\n')
        for p in most_sold:
            f.write(f"{p},{totals[p]:.3f}\n")
        f.write('\nleast_sold\n')
        for p in least_sold:
            f.write(f"{p},{totals[p]:.3f}\n")

    print(f"\nRésumé sauvegardé dans '{out}'")


if __name__ == '__main__':
    main()
