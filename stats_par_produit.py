import pandas as pd

url = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSC4KusfFzvOsr8WJRgozzsCxrELW4G4PopUkiDbvrrV2lg0S19-zeryp02MC9WYSVBuzGCUtn8ucZW/pub?output=csv"
)

print('Chargement des données depuis le CSV...')
df = pd.read_csv(url)
print('Colonnes détectées:', list(df.columns))

# Candidates pour nom produit / quantité / prix / chiffre d'affaires
candidates_product = [
    'produit', 'product', 'nom_produit', 'produit_nom', 'article', 'item', 'libelle', 'name'
]
candidates_q = ['qte', 'quantite', 'quantity', 'qty', 'qte_vendue', 'volume']
candidates_price = [
    'prix', 'price', 'pu', 'prix_unitaire', 'prix_unit', 'montant', 'ca', 'chiffre_affaires', 'total'
]
candidates_revenue = ['chiffre_affaires', 'ca', 'revenu', 'revenue', 'total_montant', 'montant']

product_col = next((c for c in candidates_product if c in df.columns), None)
q_col = next((c for c in candidates_q if c in df.columns), None)
price_col = next((c for c in candidates_price if c in df.columns), None)
revenue_col = next((c for c in candidates_revenue if c in df.columns), None)

# Si pas de colonne produit évidente, essayer d'inférer
if product_col is None:
    for c in df.columns:
        if df[c].dtype == object and df[c].nunique() <= 200:
            product_col = c
            print(f"Inférence: j'utilise la colonne '{product_col}' comme produit")
            break

# Si pas de colonne qte évidente, prendre une colonne numérique plausible
if q_col is None:
    for c in df.select_dtypes(include=['int', 'float']).columns:
        if df[c].min() >= 0:
            q_col = c
            print(f"Inférence: j'utilise la colonne '{q_col}' comme quantité")
            break

# Calculer le chiffre d'affaires si nécessaire
if revenue_col is None:
    if price_col is not None and q_col is not None:
        df['_revenue_calc'] = df[price_col] * df[q_col]
        revenue_col = '_revenue_calc'
        print(f"Chiffre d'affaires calculé: '{price_col}' * '{q_col}' -> '{revenue_col}'")
    else:
        print("Aucune colonne de chiffre d'affaires trouvée ni calculable (prix/qte manquants).")

if product_col is None:
    raise SystemExit("Impossible d'identifier une colonne produit ; merci de préciser le nom de la colonne produit dans le fichier.")

print('\nColonnes utilisées:')
print(' produit =', product_col)
print(' qte     =', q_col)
print(' prix    =', price_col)
print(' revenu  =', revenue_col)

# Conversion des colonnes numériques au besoin
if q_col is not None:
    df[q_col] = pd.to_numeric(df[q_col], errors='coerce')
if revenue_col is not None:
    df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')

# Groupe par produit
group = df.groupby(product_col)


results = pd.DataFrame(index=group.size().index)

# Chiffre d'affaires: total, moyenne et médiane
if revenue_col is not None:
    results['ca_total'] = group[revenue_col].sum()
    results['ca_moyenne'] = group[revenue_col].mean()
    results['ca_mediane'] = group[revenue_col].median()
else:
    results['ca_total'] = pd.NA
    results['ca_moyenne'] = pd.NA
    results['ca_mediane'] = pd.NA

# Volume des ventes: moyenne, médiane, écart-type, variance
if q_col is not None:
    results['qte_moyenne'] = group[q_col].mean()
    results['qte_mediane'] = group[q_col].median()
    results['qte_ecart_type'] = group[q_col].std()
    results['qte_variance'] = group[q_col].var()
else:
    results['qte_moyenne'] = pd.NA
    results['qte_mediane'] = pd.NA
    results['qte_ecart_type'] = pd.NA
    results['qte_variance'] = pd.NA


# Arrondir pour lisibilité
results = results.round(3)


print('\nStatistiques par produit (extrait):')
print(results.head(20).to_string())

print('\nChiffre d\'affaires total par produit:')
for produit, ca in results['ca_total'].items():
    print(f" - {produit} : {ca}")

# Sauvegarder
out_csv = 'stats_par_produit.csv'
results.to_csv(out_csv)
print(f"\nRésultats sauvegardés dans '{out_csv}'")
