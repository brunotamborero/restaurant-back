from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Order_dishesBase(BaseModel):
    detail_id_dish: int
    quantity: int


class Order_dishesCreate(Order_dishesBase):
    id: int
    name_dish: str
    price_dish: int
    detail_id_order: int


class Order_dishes(Order_dishesBase):
    name_dish: str
    price_dish: int
    class Config:
        orm_mode = True


class Group_Order_dishes(BaseModel):
    dishes: List[Order_dishesBase]


class OrderBase(BaseModel):
    number_costumers: int
    customer_id: Optional[int]
    restaurant_id: int
    table_id: int


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    total_amount: float
    completed: bool = False
    details: List[Order_dishes] = []
    start_time: datetime
    time_updated: Optional[datetime] = None

    class Config:
        orm_mode = True


class RestaurantTableBase(BaseModel):
    capacity: int
    table_number: int



class RestaurantTableCreate(RestaurantTableBase):
    pass


class RestaurantTable(RestaurantTableBase):
    id: int
    restaurant_location_id: int


    class Config:
        orm_mode = True

class SuitableDiet(str, Enum):
    VEGAN = 'Vegan'
    VEGETARIAN = 'Vegetarian'

class DishBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    suitableDiet: Optional[SuitableDiet] = None


class DishCreate(DishBase):
    pass


class Dish(DishBase):
    id: int
    restaurant_menu_id: int

    class Config:
        orm_mode = True

class CurrencyType(str, Enum):
    EURO = 'Euro'
    DOLLAR = 'Dollar'
    POUND = 'Pound'

class RestaurantBase(BaseModel):
    name: str
    currency: Optional[CurrencyType] = 'euro'
    location: Optional[str] = None
    phone: Optional[str] = None


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int
    owner_id: int
    dishes: List[Dish] = []
    restauranttables: List[RestaurantTable] = []
    orders_restaurant: List[Order] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    name: str
    id: int



class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    birthday: Optional[date] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    restaurants: List[Restaurant] = []
    orders_user: List[Order] = []

    class Config:
        orm_mode = True
