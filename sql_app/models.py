from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime, func, Date
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    birthday = Column(Date)
    restaurants = relationship("Restaurant", back_populates="owner")
    orders_user = relationship("Order", back_populates="customer_order")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    currency = Column(String, default='euro')
    location = Column(String, index=True)
    phone = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="restaurants")

    dishes = relationship("Dish", back_populates="menu")
    restauranttables = relationship("RestaurantTable", back_populates="distribution")

    orders_restaurant = relationship("Order", back_populates="restaurant_order")


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    suitableDiet = Column(Integer)
    price = Column(Float)
    restaurant_menu_id = Column(Integer, ForeignKey("restaurants.id"))
    menu = relationship("Restaurant", back_populates="dishes")


class RestaurantTable(Base):
    __tablename__ = "restauranttables"

    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(Integer)
    restaurant_location_id = Column(Integer, ForeignKey("restaurants.id"))
    distribution = relationship("Restaurant", back_populates="restauranttables")
    orders_table = relationship("Order", back_populates="table_orders")


class Order_Dishes(Base):
    __tablename__ = 'ordersdishes'
    id = Column(Integer, primary_key=True)
    detail_id_dish = Column(Integer, ForeignKey("dishes.id"))
    detail_id_order = Column(ForeignKey('orders.id'))
    name_dish = Column(String)
    price_dish = Column(Integer)
    quantity = Column(Integer)
    main_order = relationship("Order", back_populates="details")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    number_costumers = Column(Integer)
    completed = Column(Boolean, default=False)
    total_amount = Column(Float, default=0)

    start_time = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    customer_id = Column(Integer, ForeignKey("users.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    table_id = Column(Integer, ForeignKey("restauranttables.id"))

    customer_order = relationship("User", back_populates="orders_user")
    restaurant_order = relationship("Restaurant", back_populates="orders_restaurant")
    table_orders = relationship("RestaurantTable", back_populates="orders_table")

    details = relationship("Order_Dishes", back_populates="main_order")
