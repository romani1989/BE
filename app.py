from flask import Flask, jsonify, request
from datetime import datetime
from flask_admin import Admin
from flask_restx import Api, Resource, fields
from models import User, Reservation, Disponibilita, Professional,DisponibilitaModelView,ProfessionalModelView,UserModelView,ReservationModelView
from db import db
from flask_cors import CORS
from cf import genera_codice_fiscale


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

api = Api(app, doc='/docs') 


db.init_app(app)


admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')


admin.add_view(ReservationModelView(Reservation, db.session))  
admin.add_view(UserModelView(User, db.session)) 
admin.add_view(ProfessionalModelView(Professional, db.session))  
admin.add_view(DisponibilitaModelView(Disponibilita, db.session)) 

#modelli 
user_model = api.model('User', {
    'nome': fields.String(required=True, description='Nome utente'),
    'cognome': fields.String(required=True, description='Cognome utente'),
    'data_nascita': fields.String(required=True, description='Data di nascita (YYYY-MM-DD)'),
    'sesso_biologico': fields.String(required=True, description='Sesso biologico (M/F)'),
    'nazione_nascita': fields.String(required=True, description='Nazione di nascita'),
    'provincia_nascita': fields.String(required=True, description='Provincia di nascita'),
    'comune_nascita': fields.String(required=True, description='Comune di nascita'),
    'codice_fiscale': fields.String(required=True, description='Codice fiscale'),
    'email': fields.String(required=True, description='Indirizzo email'),
    'cellulare': fields.String(required=True, description='Numero di cellulare'),
    'password': fields.String(required=True, description='Password'),
    'conferma_password': fields.String(required=True, description='Conferma password')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email dell\'utente'),
    'password': fields.String(required=True, description='Password dell\'utente')
})

reservation_model = api.model('Reservation', {
    'user_id': fields.Integer(required=True, description="ID dell'utente"),
    'professional_id': fields.Integer(required=True, description="ID del professionista"),
    'data': fields.String(required=True, description="Data della prenotazione"),
    'orario': fields.String(required=True, description="Orario della prenotazione"),
    'stato': fields.String(default='in attesa', description="Stato della prenotazione")
})

role_model = api.model('Role', {
    'role': fields.String(required=True, description='Il ruolo da assegnare all\'utente')
})


@api.route('/api/register')
class Register(Resource):
    @api.expect(user_model)
    def post(self):
        """Registra un nuovo utente"""
        data = request.get_json()
        
        
        nome = data.get('nome')
        cognome = data.get('cognome')
        data_nascita = data.get('data_nascita')
        sesso_biologico = data.get('sesso_biologico')
        nazione_nascita = data.get('nazione_nascita')
        provincia_nascita = data.get('provincia_nascita')
        comune_nascita = data.get('comune_nascita')
        codice_fiscale = data.get('codice_fiscale')
        email = data.get('email')
        cellulare = data.get('cellulare')
        password = data.get('password')
        conferma_password = data.get('conferma_password')
        trattamento_dati = data.get('consenso_trattamento_dati', False)  # Ottieni il consenso (default False)
        
        # Verifica dei campi obbligatori
        required_fields = [nome, cognome, data_nascita, sesso_biologico, nazione_nascita, provincia_nascita,
                    comune_nascita, codice_fiscale, email, cellulare, password, conferma_password]
        if not all(required_fields):
            return {'message': 'Tutti i campi sono obbligatori'}, 400
        
        
        if password != conferma_password:
            return {'message': 'Le password non coincidono'}, 400
        
        
        if User.query.filter_by(email=email).first():
            return {'message': 'Email già in uso'}, 400
        
        
        if User.query.filter_by(codice_fiscale=codice_fiscale).first():
            return {'message': 'Codice fiscale già in uso'}, 400

        # Creazione del nuovo utente
        new_user = User(
            nome=nome,
            cognome=cognome,
            data_nascita=datetime.strptime(data_nascita, '%Y-%m-%d'),
            sesso_biologico=sesso_biologico,
            nazione_nascita=nazione_nascita,
            provincia_nascita=provincia_nascita,
            comune_nascita=comune_nascita,
            codice_fiscale=codice_fiscale,
            email=email,
            cellulare=cellulare,
            role='cliente',
            consenso_trattamento_dati=trattamento_dati 
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return {
            'message': 'Utente registrato con successo',
            'user': {
                'nome': new_user.nome,
                'cognome': new_user.cognome,
                'email': new_user.email,
                'role': new_user.role  
            }
        }, 201
        

@api.route('/api/genera_codice_fiscale')
class GeneraCodiceFiscale(Resource):
    def post(self):
        """Genera il codice fiscale basato sui dati ricevuti"""
        data = request.get_json()
        nome = data.get('nome')
        cognome = data.get('cognome')
        data_nascita = data.get('data_nascita')
        sesso = data.get('sesso')
        comune = data.get('comune')

        if not all([nome, cognome, data_nascita, sesso, comune]):
            return {'message': 'Tutti i campi sono obbligatori per generare il codice fiscale'}, 400

        codice_fiscale = genera_codice_fiscale(nome, cognome, data_nascita, sesso, comune)
        return {'codice_fiscale': codice_fiscale}, 200


@api.route('/api/users')
class Users(Resource):
    @api.doc('get_users') 
    def get(self): 
        """Ottieni tutti gli utenti"""
        users = User.query.all()
        return [{'id': user.id, 'nome': user.nome, 'email': user.email, 'role': user.role} for user in users]
    
@api.route('/api/users/<int:id>')
class UserDetail(Resource):
    @api.doc('get_user')
    def get(self, id):
        """Ottieni i dettagli di un singolo utente"""
        user = User.query.get(id)
        if not user:
            return {'message': 'Utente non trovato'}, 404
        return {
            'id': user.id,
            'nome': user.nome,
            'cognome': user.cognome,
            'data_nascita': user.data_nascita.strftime('%Y-%m-%d'),
            'sesso_biologico': user.sesso_biologico,
            'nazione_nascita': user.nazione_nascita,
            'provincia_nascita': user.provincia_nascita,
            'comune_nascita': user.comune_nascita,
            'codice_fiscale': user.codice_fiscale,
            'email': user.email,
            'cellulare': user.cellulare,
            'consenso' : user.consenso_trattamento_dati
        }
    
    def delete(self, id):
        """Cancellare un utente"""
        user = User.query.get(id)
        if user is None:
            return {'message': 'User not found'}, 404
        db.session.delete(user)  
        db.session.commit()  
        return {'message': 'User deleted successfully'}, 200

@api.route('/api/login')
class Login(Resource):
    @api.expect(api.model('Login', {
        'email': fields.String(required=True, description='Email dell\'utente'),
        'password': fields.String(required=True, description='Password dell\'utente')
    }))
    def post(self):
        """Login utente"""
        data = request.get_json()

        if not data:
            return {'message': 'Richiesta non valida, manca il corpo JSON'}, 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Email e password sono obbligatorie'}, 400

        
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            return {
                'message': 'Login effettuato con successo',
                'token': str(user.id),  
                'user_id': user.id,  
                'name': user.nome  
            }, 200
        else:
            return {'message': 'Credenziali non valide'}, 401

@api.route('/api/reservations')
class Reservations(Resource):
    @api.doc('get_reservations')
    def get(self):
        """Ottieni tutte le prenotazioni"""
        reservations = Reservation.query.all()
        return [{'id': reservation.id, 'user_id': reservation.user_id, 'data': reservation.data.strftime('%Y-%m-%d'), 'orario': reservation.orario, 'stato': reservation.stato} for reservation in reservations]



@api.route('/api/reservations/add')
class AddReservation(Resource):
    @api.doc('add_reservataion')
    @api.expect(reservation_model)
    def post(self):
        """Aggiungi una nuova prenotazione"""
        data = request.get_json()
        user_id = data.get('user_id')
        professional_id = data.get('professional_id')  
        data_visita = data.get('data')
        orario = data.get('orario')
        stato = data.get('stato', 'in attesa')  
        formatted_date = datetime.strptime(data_visita, '%Y-%m-%d').date()

        
        user = User.query.get(user_id)
        if not user:
            return {'message': f'User with ID {user_id} does not exist'}, 400

        
        professional = Professional.query.get(professional_id)
        if not professional:
            return {'message': f'Professional with ID {professional_id} does not exist'}, 400

        
        disponibilita = Disponibilita.query.filter_by(data=formatted_date, orario=orario, professional_id=professional_id).first()
        if not disponibilita:
            return {'message': f'Orario non disponibile per il professionista {professional_id}, scegli un altro orario'}, 400

        
        
        existing_reservation = Reservation.query.filter_by(data=formatted_date, orario=orario, professional_id=professional_id).first()
        if existing_reservation:
            return {'message': 'Orario già prenotato, scegli un altro orario'}, 400

        
        reservation = Reservation(
            user_id=user_id,
            professional_id=professional_id,
            data=formatted_date,
            orario=orario,
            stato=stato
        )

        db.session.add(reservation)
        db.session.commit()

        return {'message': 'Prenotazione aggiunta con successo', 'id': reservation.id}, 201



@api.route('/api/disponibilita/<int:id>')
class DisponibilitaResource(Resource):
    @api.doc('revoke_disponibilita')
    def delete(self, id):
        """Revoca una disponibilità"""
        
        disponibilita = Disponibilita.query.get(id)
        
        if not disponibilita:
            return {'message': 'Verifica perché la disponibilità non esiste'}, 404
        
        
        db.session.delete(disponibilita)
        db.session.commit()
        
        return {'message': 'Disponibilità revocata con successo'}, 200


@api.route('/api/professionals')
class Professionals(Resource):
    @api.doc('get_professionals')
    def get(self):
        """Ottieni tutti i professionisti"""
        professionals = Professional.query.all()
        return [{'id': p.id, 'nome': p.nome, 'specializzazione': p.specializzazione, "immagine": p.image_url} for p in professionals]

    @api.doc('add_professional')
    @api.expect(api.model('Professional', {
        'nome': fields.String(required=True, description="Nome del professionista"),
        'specializzazione': fields.String(required=True, description="Specializzazione (medico, nutrizionista, psicologo)"),
        'immagine': fields.String(required=True,description="Immagine Doc")
    }))
    def post(self):
        """Aggiungi un nuovo professionista"""
        data = request.get_json()
        nome = data.get('nome')
        img=data.get("immagine")
        specializzazione = data.get('specializzazione')
        
        if Professional.query.filter_by(nome=nome, specializzazione=specializzazione).first():
            return {'message': 'Professionista già presente'}, 400
        
        new_professional = Professional(nome=nome, specializzazione=specializzazione, image_url=img)
        db.session.add(new_professional)
        db.session.commit()
        
        return {'message': 'Professionista aggiunto con successo'}, 201



@api.route('/api/reservations/<int:id>')
class ReservationDetail(Resource):
    @api.doc('get_reservation')
    def get(self, id):
        """Ottieni i dettagli di una prenotazione"""
        reservation = Reservation.query.get(id)
        if reservation is None:
            return {'message': 'Reservation not found'}, 404
        
        
        return {
            'id': reservation.id,
            'user_id': reservation.user_id,
            'data': reservation.data.strftime('%Y-%m-%d'),
            'orario': reservation.orario,
            'stato': reservation.stato
        }
    
    
    @api.expect(user_model)
    def put(self, user_id):
        """Aggiorna i dati di un utente"""
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Utente non trovato'}, 404

        data = request.get_json()
        user.nome = data.get('nome', user.nome)
        user.cognome = data.get('cognome', user.cognome)
        user.data_nascita = datetime.strptime(data.get('data_nascita', user.data_nascita.strftime('%Y-%m-%d')), '%Y-%m-%d')
        user.sesso_biologico = data.get('sesso_biologico', user.sesso_biologico)
        user.nazione_nascita = data.get('nazione_nascita', user.nazione_nascita)
        user.provincia_nascita = data.get('provincia_nascita', user.provincia_nascita)
        user.comune_nascita = data.get('comune_nascita', user.comune_nascita)
        user.cellulare = data.get('cellulare', user.cellulare)

        db.session.commit()
        return {'message': 'Profilo aggiornato con successo'}
    
    
    
@api.route('/api/professionals/<int:professional_id>/disponibilita', methods=['GET', 'POST'])
class DisponibilitaProfessional(Resource):
    def get(self, professional_id):
        """Restituisce tutte le date disponibili future per un professionista"""
        
        today = datetime.today().date() 

        disponibilita = (
            db.session.query(Disponibilita.data)
            .filter(Disponibilita.professional_id == professional_id)
            .filter(Disponibilita.data >= today)
            .distinct()
            .all()
        )

        
        available_dates = [d[0].strftime('%Y-%m-%d') for d in disponibilita]

        return jsonify({"available_dates": available_dates})

    @api.doc('add_disponibilita')
    @api.expect(api.model('Disponibilita', {
        'data': fields.String(required=True, description="Data della disponibilità (YYYY-MM-DD)"),
        'orario': fields.String(required=True, description="Orario della disponibilità (HH:MM)")
    }))
    def post(self, professional_id):
        """Aggiungi una disponibilità per un professionista"""
        
        
        if not request.is_json:
            return {"message": "Il Content-Type deve essere application/json"}, 415

        data = request.get_json()
        data_visita = data.get('data')
        orario = data.get('orario')

        if not data_visita or not orario:
            return {"message": "Data e orario sono obbligatori"}, 400

        try:
            formatted_date = datetime.strptime(data_visita, '%Y-%m-%d').date()
        except ValueError:
            return {"message": "Formato data non valido (YYYY-MM-DD)"}, 400

        existing = Disponibilita.query.filter_by(professional_id=professional_id, data=formatted_date, orario=orario).first()
        if existing:
            return {"message": "Disponibilità già esistente per questa data e orario"}, 400

        nuova_disponibilita = Disponibilita(professional_id=professional_id, data=formatted_date, orario=orario)
        db.session.add(nuova_disponibilita)
        db.session.commit()

        return {
            "message": "Disponibilità aggiunta con successo",
            "disponibilita": {
                "id": nuova_disponibilita.id,
                "professional_id": nuova_disponibilita.professional_id,
                "data": nuova_disponibilita.data.strftime('%Y-%m-%d'),
                "orario": nuova_disponibilita.orario
            }
        }, 201
    
    @api.doc('update_reservation')
    @api.expect(reservation_model)
    def put(self, id):
        """Aggiorna una prenotazione"""
        data = request.get_json()
        reservation = Reservation.query.get(id)
        
        if reservation is None:
            return {'message': 'Reservation not found'}, 404
        
        
        reservation.user_id = data.get('user_id', reservation.user_id)
        reservation.data = datetime.strptime(data.get('data', reservation.data.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        reservation.orario = data.get('orario', reservation.orario)
        reservation.stato = data.get('stato', reservation.stato)
        
        db.session.commit()
        return {'message': 'Reservation updated successfully'}

    @api.doc('delete_reservation')
    def delete(self, id):
        """Elimina una prenotazione"""
        reservation = Reservation.query.get(id)
        
        if reservation is None:
            return {'message': 'Reservation not found'}, 404
        
        db.session.delete(reservation)
        db.session.commit()
        return {'message': 'Reservation deleted successfully'}

@api.route('/api/reservations/user/<int:user_id>')
class UserReservations(Resource):
    def get(self, user_id):
        """Recupera tutti gli appuntamenti di un utente specifico"""
        reservations = Reservation.query.filter_by(user_id=user_id).all()

        if not reservations:
            return {"message": "Nessun appuntamento trovato"}, 200

        results = []
        for res in reservations:
            professional = Professional.query.get(res.professional_id)
            results.append({
                "id": res.id,
                "data": res.data.strftime('%Y-%m-%d'),
                "orario": res.orario,
                "stato": res.stato,
                "professional_name": professional.nome if professional else "Non disponibile"
            })
        return results, 200
    

@api.route('/api/professionals/<int:professional_id>/orari', methods=['POST'])
class OrariProfessional(Resource):
    def post(self, professional_id):
        """Restituisce tutti gli orari disponibili per un professionista in una data specifica"""

        
        data = request.get_json()

        if not data or 'data' not in data:
            return {"message": "Data richiesta nel payload JSON"}, 400  

        try:
            data_selezionata = datetime.strptime(data['data'], '%Y-%m-%d').date()
        except ValueError:
            return {"message": "Formato data non valido (YYYY-MM-DD)"}, 400  

        
        disponibilita = (
            db.session.query(Disponibilita.orario)
            .filter(Disponibilita.professional_id == professional_id)
            .filter(Disponibilita.data == data_selezionata)
            .all()
        )

        
        available_times = [d[0] for d in disponibilita]

        return jsonify({"available_times": available_times})

@api.route('/api/reservations/<int:id>', methods=['DELETE'])
class DeleteReservation(Resource):
    def delete(self, id):
        """Elimina una prenotazione"""
        reservation = Reservation.query.get(id)
        
        if not reservation:
            return {'message': 'Prenotazione non trovata'}, 404
        
        db.session.delete(reservation)
        db.session.commit()
        
        return {'message': 'Prenotazione eliminata con successo'}, 200

@api.route('/api/users/<int:user_id>', methods=['PUT'])
class UpdateUser(Resource):
    def put(self, user_id):
        """Aggiorna i dati di un utente esistente"""
        user = User.query.get(user_id)
        if not user:
            return {'message': 'Utente non trovato'}, 404

        data = request.get_json()
        
        # Aggiorna i dati solo se forniti nella richiesta
        user.nome = data.get('nome', user.nome)
        user.cognome = data.get('cognome', user.cognome)
        user.data_nascita = datetime.strptime(data.get('data_nascita', user.data_nascita.strftime('%Y-%m-%d')), '%Y-%m-%d')
        user.sesso_biologico = data.get('sesso_biologico', user.sesso_biologico)
        user.nazione_nascita = data.get('nazione_nascita', user.nazione_nascita)
        user.provincia_nascita = data.get('provincia_nascita', user.provincia_nascita)
        user.comune_nascita = data.get('comune_nascita', user.comune_nascita)
        user.codice_fiscale = data.get('codice_fiscale', user.codice_fiscale)
        user.email = data.get('email', user.email)
        user.cellulare = data.get('cellulare', user.cellulare)
        user.consenso_trattamento_dati = data.get('consenso', user.consenso_trattamento_dati)

        db.session.commit()
        return {'message': 'Profilo aggiornato con successo'}, 200


if __name__ == '__main__':
    app.run(debug=True) 