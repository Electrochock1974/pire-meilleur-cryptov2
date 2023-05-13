#Pour installer les bibliothèques, 
#ouvrez un terminal ou Virtual Studio Code et faites Ctrl + ù, 
#puis tapez les commandes suivantes :

#pip install python

#pip install requests

#Les bibliothèques json et os sont déjà incluses dans Python.
#Pour lancer le script, exécutez la commande suivante :

#python script.py

#/!\ Il est important que le fichier script.py soit dans un dossier pour plus de simplicité.

#/!\ Tous les fichiers sont supprimés si vous relancez le script.

import requests
import os
import json
import glob
import locale
from datetime import datetime
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
current_date = datetime.now().strftime("%d %B %Y")

# Supprimer le fichier data.json s'il existe
if os.path.exists('data.json'):
    os.remove('data.json')

# Supprimer tous les fichiers qui commencent par "top_5_crypto_" et se terminent par ".txt"
for file in glob.glob("top_5_crypto_*.txt"):
    os.remove(file)

# Supprimer les dossiers top_gainers et top_losers s'ils existent
if os.path.exists("top_gainers"):
    os.system("rmdir /s /q top_gainers")
if os.path.exists("top_losers"):
    os.system("rmdir /s /q top_losers")

# Durées disponibles
durees_disponibles = {'1h': 'priceChange1h',
                      '24h': 'priceChange24h',
                      '7d': 'priceChange7d',
                      '30d': 'priceChange30d'}

# Durée par défaut
duree_par_defaut = '7d'

# Demander la durée à l'utilisateur
print(f"Veuillez choisir la durée pour le classement (parmi {', '.join(durees_disponibles.keys())}, par défaut {duree_par_defaut}): ")
duree = input().strip()

# Vérifier si la durée est valide, sinon utiliser la durée par défaut
if duree not in durees_disponibles:
    print(f"Pas de durée valide selectionné. La durée de {duree_par_defaut} à été utilisé.")
    duree = duree_par_defaut

# Obtenir les données JSON de l'API CoinMarketCap
url = f'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/spotlight?dataType=2&limit=30&rankRange=100&timeframe={duree}'
response = requests.get(url)
data = response.json()

# Écrire les données JSON dans un fichier
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Récupérer les données depuis le fichier JSON
with open('data.json', 'r') as f:
    data = json.load(f)

# Récupérer les 5 meilleures cryptos pour la durée demandée
gainers = sorted([item for item in data['data']['gainerList'] if item.get('priceChange', {}).get(durees_disponibles[duree]) is not None], key=lambda x: x['priceChange'][durees_disponibles[duree]], reverse=True)[:5]

# Récupérer les 5 pires cryptos pour la durée demandée
losers = sorted([item for item in data['data']['loserList'] if item.get('priceChange', {}).get(durees_disponibles[duree]) is not None], key=lambda x: x['priceChange'][durees_disponibles[duree]])[:5]

# Créer les dossiers d'images s'ils n'existent pas
if not os.path.exists("top_gainers"):
    os.makedirs("top_gainers")
if not os.path.exists("top_losers"):
    os.makedirs("top_losers")
# Télécharger les images pour les 5 meilleures cryptos
for crypto in gainers:
    img_url = f"https://s2.coinmarketcap.com/static/img/coins/128x128/{crypto['id']}.png"
    img_data = requests.get(img_url).content
    with open(f"top_gainers/{crypto['id']}.png", 'wb') as f:
        f.write(img_data)
# Télécharger les images pour les 5 pires cryptos
for crypto in losers:
    img_url = f"https://s2.coinmarketcap.com/static/img/coins/128x128/{crypto['id']}.png"
    img_data = requests.get(img_url).content
    with open(f"top_losers/{crypto['id']}.png", 'wb') as f:
        f.write(img_data)


# Créer le fichier texte avec le classement pour la durée sélectionnée
if duree == '1h':
    timeframe_text = '1 heure'
    time_key = 'priceChange1h'
elif duree == '24h':
    timeframe_text = '24 heures'
    time_key = 'priceChange24h'
elif duree == '7d':
    timeframe_text = '7 jours'
    time_key = 'priceChange7d'
else:
    timeframe_text = '30 jours'
    time_key = 'priceChange30d'

def format_price(price):
    if price >= 1.0:
        return f"${price:.2f}"
    else:
        return f"${price:.11f}"

# Formatage du pourcentage pour l'afficher avec deux chiffres après la virgule
def format_percentage(percentage):
    return f"{percentage:.2f}%"

# Formatage de la capitalisation boursière pour l'afficher en B (milliards) ou M (millions) si nécessaire
def format_market_cap(market_cap):
    if market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap/1_000_000:.2f}M"
    else:
        return f"${market_cap:.2f}"

# Ecriture des données de crypto-monnaie dans un fichier
def write_crypto_data(f, crypto_list, max_cryptos):
    data = []  # Créer une liste vide pour stocker les données
    for i, crypto in enumerate(crypto_list):
        price_str = format_price(crypto['priceChange']['price']).replace(',', '.')
        market_cap_str = format_market_cap(crypto['marketCap']).replace(',', '.')
        percentage_str = format_percentage(crypto['priceChange'][time_key])
        data.append(f"{market_cap_str},{crypto['symbol']},{percentage_str},{price_str}")  # Ajouter à la liste
    
    # Compléter avec des valeurs par défaut pour les cryptomonnaies manquantes
    for i in range(len(crypto_list), max_cryptos):
        data.append("N/A,N/A,N/A,N/A")
    
    f.write(",".join(data))  # Joindre les données avec une virgule et les écrire dans le fichier

# Ouverture du fichier texte pour écrire les données
with open(f'top_5_crypto_{duree}.txt', 'w', encoding='utf-8') as f:
    # Ecriture des en-têtes des colonnes
    f.write("meilleurcrypto,pirecrypto,données_exact,marketcap1,nom1,pourcent1,prix1,marketcap2,nom2,pourcent2,prix2,marketcap3,nom3,pourcent3,prix3,marketcap4,nom4,pourcent4,prix4,marketcap5,nom5,pourcent5,prix5,marketcap1_1,nom1_1,pourcent1_1,prix1_1,marketcap2_1,nom2_1,pourcent2_1,prix2_1,marketcap3_1,nom3_1,pourcent3_1,prix3_1,marketcap4_1,nom4_1,pourcent4_1,prix4_1,marketcap5_1,nom5_1,pourcent5_1,prix5_1\n")
    # Ecriture de l'indication de la précision des données
    f.write(f"true,false,*Données exactes au {current_date}. Le tableau n’est pas à l'échelle. N’est pas un conseil financier.,")
    # Ecriture des données des crypto-monnaies gagnantes
    write_crypto_data(f, gainers, 5) # Remplacez la valeur 5 par le nombre maximum de cryptos que vous voulez afficher
    # Séparation des données des cryptos gagnantes et perdantes par une virgule
    f.write(",")
    # Ecriture des données des crypto-monnaies perdantes
    write_crypto_data(f, losers, 5) # Remplacez la valeur 5 par le nombre maximum de cryptos que vous voulez afficher
    # Ajout d'une nouvelle ligne à la fin
    f.write("\n")  

# Fonction pour écrire un fichier de contrôle pour chaque crypto-monnaie
def write_control_file(crypto_list, filename, is_gainer=True):
    with open(filename, 'w', encoding='utf-8') as f:
        for i, crypto in enumerate(crypto_list):
            rank = i + 1
            price_str = format_price(crypto['priceChange']['price']).replace(',', '.')
            market_cap_str = format_market_cap(crypto['marketCap']).replace(',', '.')
            percentage_str = format_percentage(crypto['priceChange'][time_key])
            # Écrire les informations de chaque crypto-monnaie dans le fichier, en précisant si elle est gagnante ou perdante
            if is_gainer:
                f.write(f"{rank}. [{crypto['id']}.png] {crypto['name']} ({crypto['symbol']}): {percentage_str} de gain, Prix: {price_str}, Market Cap: {market_cap_str}\n")
            else:
                f.write(f"{rank}. [{crypto['id']}.png] {crypto['name']} ({crypto['symbol']}): {percentage_str} de perte, Prix: {price_str}, Market Cap: {market_cap_str}\n")

# Appel de la fonction pour écrire les fichiers de contrôle pour les cryptos gagnantes et perdantes
write_control_file(gainers, f'control_gainers_{duree}.txt')
write_control_file(losers, f'control_losers_{duree}.txt', is_gainer=False)

