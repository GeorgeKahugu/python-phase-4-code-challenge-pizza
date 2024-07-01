from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__  = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade="all, delete-orphan", lazy=True)
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self, include_relationships=True):
        restaurant_dict = {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }
        if include_relationships:
            restaurant_dict['restaurant_pizzas'] = [rp.to_dict() for rp in self.restaurant_pizzas]
        return restaurant_dict


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False )
    ingredients = db.Column(db.String, nullable = False)

    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', cascade="all, delete-orphan", lazy=True)
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.pizzas')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
        }  
   
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError('Price must be between 1 and 30')
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'restaurant_id': self.restaurant_id,
            'pizza_id': self.pizza_id,
            'pizza': self.pizza.to_dict(),
            'restaurant': self.restaurant.to_dict(include_relationships=False)
        }