from db import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView

#db modelli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)
    sesso_biologico = db.Column(db.String(10), nullable=False)
    nazione_nascita = db.Column(db.String(50), nullable=False)
    provincia_nascita = db.Column(db.String(50), nullable=False)
    comune_nascita = db.Column(db.String(50), nullable=False)
    codice_fiscale = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cellulare = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cliente')
    consenso_trattamento_dati = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    
    reservations = db.relationship('Reservation', cascade="all, delete-orphan", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.nome}, Role: {self.role}>"

# Modello Reservation
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    orario = db.Column(db.String(10), nullable=False)
    stato = db.Column(db.String(20), nullable=False, default="in attesa")
    
    user = db.relationship('User', back_populates='reservations')
    professional = db.relationship('Professional', backref='reservations')

    def __repr__(self):
        return f"Reservation('{self.id}','{self.user_id}', '{self.data}', '{self.orario}', '{self.stato}')"


# Modello Professional
class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    specializzazione = db.Column(db.String(50), nullable=False)  # medico, nutrizionista, psicologo
    disponibilita = db.relationship('Disponibilita', backref='professional', lazy=True)  # Relazione con Disponibilita
    image_url =db.Column(db.String(100), nullable=True) #foto doc

    def __repr__(self):
        return f"Professional('{self.id}', '{self.nome}', '{self.specializzazione}')"


# Modello Disponibilita
class Disponibilita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)  # Relazione con Professional
    data = db.Column(db.Date, nullable=False)
    orario = db.Column(db.String(10), nullable=False) 
    
    def __repr__(self):
        return f"Disponibilita('{self.id}', '{self.professional_id}', '{self.data}', '{self.orario}')"

class UserModelView(ModelView):
    column_list = ['id','nome','cognome','data_nascita','sesso_biologico','nazione_nascita','provincia_nascita','comune_nascita','codice_fiscale','email','cellulare','password_hash','role','consenso_trattamento_dati','created_at']
    column_labels = { 'id': 'ID', 'nome': 'Nome','cognome':'Cognome', 'data_nascita': 'Data di nascita', 'sesso_biologico': 'Sesso Biologico','nazione_nascita': 'Nazione di Nascita','provincia_nascita': 'Provincia di Nascita', 'comune_nascita' : 'Comune di Nascita', 'codice_fiscale': 'Codice Fiscale','email':'email','cellulare':'Cellulare', 'password_hash':'password_hash', 'created_at' : 'creato il','role':'Ruolo' ,'consenso_trattamento_dati':'consenso' }

class ReservationModelView(ModelView):  
    column_list = ['id','user_id','professional_id','data','orario','stato' ]     
    column_labels = { 'id': 'Reservation ID', 'user_id': 'Id utente','professional_id':'ID professionista','data':'Data Apt','stato': 'stato Apt' }

class ProfessionalModelView(ModelView):
    column_list = ['id','nome','specializzazione','disponibilita','image_url']
    column_labels =  { 'id': 'ID', 'nome': 'Nome', 'specializzazione' : 'specializzazione','image_url':'Image'}

class DisponibilitaModelView(ModelView):
    column_list = ['id','professional_id','data','orario']
    column_labels = { 'id': 'ID', 'professional_id': 'professione', 'data' : 'data','orario': 'orario' }
