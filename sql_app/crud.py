from sqlalchemy.orm import Session
from . import models, schemas
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "9c434ec44f55cc86348580604024ae1477cae8c4232b5526f5b5ee5e3397e98e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, email: str):
    return db.query(models.User).filter(models.User.email == email).first()



def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)

        email: str = payload.get("sub")
        print(email)

        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
        print(token_data)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user




def get_current_active_user(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(payload)

    #current_user = get_current_user(token, db)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    token_data = schemas.TokenData(email=email)

    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
    #if current_user.disabled:
        #raise HTTPException(status_code=400, detail="Inactive user")
    #return current_user

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, name=user.name, birthday=user.birthday)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_dish(db: Session, dish_id: int):
    return db.query(models.Dish).filter(models.Dish.id == dish_id).first()

def get_restaurant(db: Session, restaurant_id: int):
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()




def create_user_restaurant(db: Session, restaurant: schemas.RestaurantCreate, user_id: int):
    db_restaurant = models.Restaurant(**restaurant.dict(), owner_id=user_id)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def get_restaurants_user(db: Session, user_id: int):
    return db.query(models.Restaurant).filter(models.Restaurant.owner_id == user_id).all()


def create_dish_restaurant(db: Session, dish: schemas.DishCreate, restaurant_id: int):
    db_dish = models.Dish(**dish.dict(), restaurant_menu_id=restaurant_id)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


def get_restaurant_menu(db, restaurant_id: int):
    return db.query(models.Dish).filter(models.Dish.restaurant_menu_id == restaurant_id).all()


def create_restaurant_tables(db: Session, restauranttable: schemas.RestaurantTableCreate, restaurant_id: int):
    db_restauranttable = models.RestaurantTable(**restauranttable.dict(), restaurant_location_id=restaurant_id)
    db.add(db_restauranttable)
    db.commit()
    db.refresh(db_restauranttable)
    return db_restauranttable


def get_restaurant_tables(db, restaurant_id: int):
    return db.query(models.RestaurantTable).filter(models.RestaurantTable.restaurant_location_id == restaurant_id).all()


def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def add_dishes_order(order_id: int, order_dishes: schemas.Group_Order_dishes, db: Session):
    total_amount = 0
    for d in order_dishes.dishes:
        db_order_dishes = models.Order_Dishes(**d.dict())
        db_order_dishes.detail_id_order = order_id
        dish = get_dish(db, db_order_dishes.detail_id_dish)
        price_dishes = dish.price * db_order_dishes.quantity
        total_amount = total_amount + price_dishes
        db_order_dishes.name_dish = dish.name
        db_order_dishes.price_dish = dish.price

        db.add(db_order_dishes)
        db.commit()
        db.refresh(db_order_dishes)
    db.query(models.Order).filter(models.Order.id == order_id).first().total_amount += total_amount
    db.commit()
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def finish_order (db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    order.completed = True
    db.commit()
    return order
