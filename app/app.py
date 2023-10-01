#!/usr/bin/env python3

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError


from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Index(Resource):
    def get(self):
        return 'Welcome to superheroes app...'

class HeroesResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        serialized_heroes = [hero.serialize() for hero in heroes]
        return jsonify(serialized_heroes)
    
class HeroesById(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        
        if hero:
            return jsonify(hero.serialize())
        else:
            return {'error': 'Hero not found'}, 404
        
class PowersResource(Resource):
    def get(self):
        powers = Power.query.all()
        serialized_powers = [power.serialize() for power in powers ]
        
        return jsonify(serialized_powers)
    
class PowerById(Resource):
    def get(self, id):
        power = Power.query.get(id)
        
        if power:
            return jsonify(power.serialize())
        else:
            return {"error": "Power not found"}, 404  
        
    def patch(self, id):
        power = Power.query.get(id)

        if power is None:
            return {'error': 'Power not found'}

        try:
            data = request.get_json()

            if 'description' in data:
                new_description = data['description']
                if not new_description:
                    return jsonify({'errors': ['Description must be present']}), 400

                if len(new_description) < 20:
                    return {'errors': ['Description must be at least 20 characters long']}, 400

                power.description = new_description
                db.session.commit()
                return jsonify(power.serialize())

            else:
                return {'errors': ['No valid fields provided for update']}

        except ValueError as e:
            return jsonify({'errors': [str(e)]}), 400
                    
       
class HeroPowerResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            strength = data.get('strength')
            power_id = data.get('power_id')
            hero_id = data.get('hero_id')

            # Check if the power and hero exist
            power = Power.query.get(power_id)
            hero = Hero.query.get(hero_id)

            if not (power and hero):
                return jsonify({'errors': ['Power or Hero not found']})

            # Create a new HeroPower
            hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
            db.session.add(hero_power)
            db.session.commit()

            # Return the updated Hero data
            serialized_hero = hero.serialize()
            return jsonify(serialized_hero)

        except ValueError as e:
            return jsonify({'errors': [str(e)]})
                
            
        


api.add_resource(Index, '/')
api.add_resource(HeroesResource, '/heroes')
api.add_resource(HeroesById, '/heroes/<int:id>')
api.add_resource(PowersResource, '/powers')
api.add_resource(PowerById, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
