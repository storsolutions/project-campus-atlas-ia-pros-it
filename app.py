import plotly.express as px
import pandas as pd

# Chargement des données (même source que le projet)
données = pd.read_csv(
	'https://docs.google.com/spreadsheets/d/e/2PACX-1vSC4KusfFzvOsr8WJRgozzsCxrELW4G4PopUkiDbvrrV2lg0S19-zeryp02MC9WYSVBuzGCUtn8ucZW/pub?output=csv'
)

# --- Graphe existant : quantité vendue par région (camembert)
figure = px.pie(données, values='qte', names='region', title='Quantité vendue par région')
figure.write_html('ventes-par-region.html')
print('ventes-par-region.html généré avec succès !')

# --- Préparer le calcul du chiffre d'affaires si possible
if 'prix' in données.columns and 'qte' in données.columns:
	try:
		données['_ca'] = données['prix'] * données['qte']
	except Exception:
		# forcer conversion numérique si besoin
		données['prix'] = pd.to_numeric(données['prix'], errors='coerce')
		données['qte'] = pd.to_numeric(données['qte'], errors='coerce')
		données['_ca'] = données['prix'] * données['qte']
else:
	données['_ca'] = pd.NA

# --- a) Ventes par produit (somme des quantités)
if 'produit' in données.columns and 'qte' in données.columns:
	grouped_q = données.groupby('produit', as_index=False)['qte'].sum()
	fig_produit = px.bar(
		grouped_q,
		x='produit',
		y='qte',
		title='Quantité vendue par produit',
		labels={'produit': 'Produit', 'qte': 'Quantité vendue'},
	)
	fig_produit.write_html('ventes-par-produit.html')
	print('ventes-par-produit.html généré avec succès !')
else:
	print("Colonne 'produit' ou 'qte' introuvable : impossible de générer 'ventes-par-produit.html'.")

# --- b) Chiffre d'affaires par produit
if 'produit' in données.columns and ('_ca' in données.columns and données['_ca'].notna().any()):
	grouped_ca = données.groupby('produit', as_index=False)['_ca'].sum()
	fig_ca = px.bar(
		grouped_ca,
		x='produit',
		y='_ca',
		title="Chiffre d'affaires par produit",
		labels={'produit': 'Produit', '_ca': "Chiffre d'affaires"},
	)
	fig_ca.write_html('ca-par-produit.html')
	print('ca-par-produit.html généré avec succès !')
else:
	print("Impossible de générer 'ca-par-produit.html' : colonne 'prix'/'qte' manquante ou non calculable.")
