# Realtor.ca Scraper

## Installation de l'environnement

1. Créer un environnement virtuel Python :

```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Installer ChromeDriver :

- Sur macOS (avec Homebrew) :

```bash
brew install chromedriver
```

4. Configurer les variables d'environnement :

- Copier le fichier `.env.example` en `.env`
- Modifier les valeurs selon votre configuration

5. Démarrer MongoDB :

```bash
mongod
```

## Utilisation

Pour exécuter le scraper :

```bash
python realtor.py
```
