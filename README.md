Prima di avviare il progetto, assicurati di avere installato i seguenti strumenti:

Python 3.9+
pip 
Visual Studio Code 
Git 


# Clonazione del backend
git clone https://github.com/romani1989/BE.git
cd BE


# Installa Flask 
pip install flask flask-admin flask-restx flask-cors flask-sqlalchemy
 

# Inizializzazione del database
python3 init_db.py o python init_db.py ( Database creato con successo!)

# Avvio del server Flask
python3 app.py o python app.py

# Avviare Admin Panel in locale
accedi al link http://127.0.0.1:5000/admin/ 

# Avviare Swagger
accedi al link http://127.0.0.1:5000/docs