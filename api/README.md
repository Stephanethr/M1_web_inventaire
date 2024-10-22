# api

## Initialize the project

1. Create a virtual environment

```bash
python3 -m venv .venv
```

2. Activate the virtual environment
   for unix :

```bash
source .venv/bin/activate
```

for windows :

```bash
.venv\Scripts\activate
```

3. Create folder `static` in the root of the project if it does not exist

```bash
mkdir -p static
```

4. Mettre à jour pip

```bash
pip install --upgrade pip
```

4. Install the dependencies

```bash
pip install -r requirements.txt
```

5. Create `.env` file with `exemple.env` content, (in the root of the project)

6. Run the application

```bash
uvicorn main:app --reload
```

6. Open the browser and go to http://127.0.0.1:8000/docs

## Architecture

1. `main.py` - L'application FastAPI avec toutes les routes
2. `database.py` - Pour la connexion à la base de données, la création des tables et des sessions de base de données
3. `schemas.py` - Pour les schémas Pydantic qui sont utilisés pour la validation des données entrantes et sortantes et pour la documentation automatique de l'API avec Swagger et ReDoc
4. `services/` - Pour les fonctions qui utilisent les sessions de base de données pour effectuer des opérations sur la base de données
5. `tasks.py` - Fonctions utilitaires
6. `models.py` - Pour les modèles SQLAlchemy qui sont utilisés pour la création des tables de base de données
