from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# Configurazione per SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Il file del database si chiamerà 'site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Evita il log delle modifiche

db = SQLAlchemy(app)

api = Api(app, doc='/docs')  # La documentazione Swagger sarà disponibile su /docs

# Modello User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Modello Reservation
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    orario = db.Column(db.String(10), nullable=False)
    stato = db.Column(db.String(20), nullable=False, default="in attesa")
    
    user = db.relationship('User', backref=db.backref('reservations', lazy=True))

    def __repr__(self):
        return f"Reservation('{self.id}','{self.user_id}', '{self.data}', '{self.orario}', '{self.stato}')"

# Codice per creare le tabelle nel database
with app.app_context():
    db.create_all()

# Aggiungi Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

class ReservationModelView(ModelView):  
    column_list = ['id','user_id','data','orario','stato' ]     
    column_labels = { 'id': 'Reservation ID', 'user_id': 'Id utente', 'data':'Data Apt','stato': 'stato Apt' }

# Aggiungi la vista per Reservation e User nel pannello admin
admin.add_view(ReservationModelView(Reservation, db.session))
admin.add_view(ModelView(User, db.session))

# Definiamo i modelli per Swagger (documentazione)
user_model = api.model('User', {
    'username': fields.String(required=True, description="Username dell'utente"),
    'email': fields.String(required=True, description="Email dell'utente"),
    'password': fields.String(required=True, description="Password dell'utente")
})

reservation_model = api.model('Reservation', {
    'user_id': fields.Integer(required=True, description="ID dell'utente"),
    'data': fields.String(required=True, description="Data della prenotazione"),
    'orario': fields.String(required=True, description="Orario della prenotazione"),
    'stato': fields.String(default='in attesa', description="Stato della prenotazione")
})

# Aggiungi risorse e operazioni alla documentazione Swagger

@api.route('/api/users')
class Users(Resource):
    @api.doc('get_users')
    def get(self):
        """Ottieni tutti gli utenti"""
        users = User.query.all()  # Recupera tutti gli utenti dal database
        return [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    
    @api.doc('add_user')
    @api.expect(user_model)  # Definisce la struttura dei dati che il client deve inviare
    def post(self):
        """Aggiungi un nuovo utente"""
        data = request.get_json()  # Ottieni i dati inviati con la richiesta POST
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user = User(username=username, email=email)  # Crea un nuovo utente
        user.set_password(password)  # Imposta la password per l'utente
        db.session.add(user)  # Aggiungi l'utente al database
        db.session.commit()  # Salva le modifiche
        return {'message': 'User added successfully'}, 201

@api.route('/api/users/<int:id>')
class UserDetail(Resource):
    @api.doc('get_user')
    def get(self, id):
        """Ottieni i dettagli di un singolo utente"""
        user = User.query.get(id)
        if user is None:
            return {'message': 'User not found'}, 404
        return {'id': user.id, 'username': user.username, 'email': user.email}
    def delete(self, id):
        """Cancellare un utente"""
        user = User.query.get(id)
        if user is None:
            return {'message': 'User not found'}, 404
        # TODO prima di eliminare utente eliminare reservation collegate
        db.session.delete(user)  # Elimina l'utente
        db.session.commit()  # Salva le modifiche nel database
        return {'message': 'User deleted successfully'}, 200
            

@api.route('/api/login')
class Login(Resource):
    @api.doc('login_user')
    @api.expect(user_model)
    def post(self):
        """Esegui il login di un utente"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return {'message': 'Login successful'}, 200
        return {'message': 'Invalid username or password'}, 401

@api.route('/api/reservations')
class Reservations(Resource):
    @api.doc('get_reservations')
    def get(self):
        """Ottieni tutte le prenotazioni"""
        reservations = Reservation.query.all()
        return [{'id': reservation.id, 'user_id': reservation.user_id, 'data': reservation.data.strftime('%Y-%m-%d'), 'orario': reservation.orario, 'stato': reservation.stato} for reservation in reservations]

    @api.doc('add_reservation')
    @api.expect(reservation_model)
    def post(self):
        """Aggiungi una nuova prenotazione"""
        data = request.get_json()
        user_id = data.get('user_id')
        data_visita = data.get('data')
        orario = data.get('orario')
        stato = data.get('stato', 'in attesa')  # Default stato = 'in attesa'
        formatted_date = datetime.strptime(data_visita, '%Y-%m-%d').date()
        reservation = Reservation(user_id=user_id, data=formatted_date, orario=orario, stato=stato)
        db.session.add(reservation)
        db.session.commit()
        return {'message': 'Reservation added successfully'}, 201

@api.route('/api/reservations/<int:id>')
class ReservationDetail(Resource):
    @api.doc('get_reservation')
    def get(self, id):
        """Ottieni i dettagli di una prenotazione"""
        reservation = Reservation.query.get(id)
        if reservation is None:
            return {'message': 'Reservation not found'}, 404
        return {'id': reservation.id, 'user_id': reservation.user_id, 'data': reservation.data, 'orario': reservation.orario, 'stato': reservation.stato}

if __name__ == '__main__':
    app.run(debug=True)
