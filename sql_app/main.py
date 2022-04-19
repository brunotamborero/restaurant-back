from typing import List
from datetime import timedelta

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware


from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8000/",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "name": user.name,  "id": user.id}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    db_user = crud.get_current_active_user(token, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant_me(restaurant: schemas.RestaurantCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    db_user = crud.get_current_active_user(token, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_user_restaurant(db=db, restaurant=restaurant, user_id=db_user.id)

@app.get("/restaurants/me", response_model=List[schemas.Restaurant])
def read_restaurant_user_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    db_user = crud.get_current_active_user(token, db)
    user_id = db_user.id
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    restaurants = crud.get_restaurants_user(db, user_id=user_id)
    return restaurants

@app.get("/restaurants/{user_id}", response_model=List[schemas.Restaurant])
def read_restaurant_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    restaurants = crud.get_restaurants_user(db, user_id=user_id)
    return restaurants


@app.get("/restaurant/{restaurant_id}", response_model=schemas.Restaurant)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@app.delete("/restaurant/{restaurant_id}", response_model=schemas.Restaurant)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    crud.delete_restaurant(db, restaurant_id=restaurant_id)
    return db_restaurant


@app.post("/restaurant/{restaurant_id}/dishes/", response_model=schemas.Dish)
def create_dish_for_restaurant(restaurant_id: int, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    return crud.create_dish_restaurant(db=db, dish=dish, restaurant_id=restaurant_id)

@app.get("/dishes/{restaurant_id}", response_model=List[schemas.Dish])
def menu_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    dishes = crud.get_restaurant_menu(db, restaurant_id=restaurant_id)
    return dishes

@app.delete("/dish/{dish_id}", response_model=schemas.Dish)
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = crud.delete_dish(db, dish_id=dish_id)
    return dish




@app.post("/restaurant/{restaurant_id}/restauranttables/", response_model=schemas.RestaurantTable)
def create_restaurant_tables(restaurant_id: int, restauranttable: schemas.RestaurantTableCreate,
                             db: Session = Depends(get_db)):
    if restauranttable.capacity < 1:
        raise HTTPException(status_code=405, detail="Table capacity has to be 1 or greater")
    return crud.create_restaurant_tables(db=db, restauranttable=restauranttable, restaurant_id=restaurant_id)


@app.get("/restauranttables/{restaurant_id}", response_model=List[schemas.RestaurantTable])
def restaurant_tables(restaurant_id: int, db: Session = Depends(get_db)):
    restauranttables = crud.get_restaurant_tables(db, restaurant_id=restaurant_id)
    return restauranttables

@app.get("/restauranttables/{restaurant_id}/{table_id}", response_model=schemas.RestaurantTable)
def restaurant_tables( restaurant_id: int, table_id: int, db: Session = Depends(get_db)):
    restauranttable = crud.get_restaurant_table(db, restaurant_id=restaurant_id, table_id=table_id)
    return restauranttable

@app.delete("/restauranttables/{table_id}", response_model=schemas.RestaurantTable)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    table = crud.delete_table(db, table_id=table_id)
    return table

@app.post("/order/", response_model=schemas.Order)
def create_new_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)


@app.put("/order/{order_id}", response_model=schemas.Order)
def add_dishes_order(order_id: int, order_dishes: schemas.Group_Order_dishes, db: Session = Depends(get_db)):
    return crud.add_dishes_order(order_id=order_id, order_dishes=order_dishes, db=db)


@app.get("/user/order/{user_id}/current", response_model=List[schemas.Order])
def get_current_orders_user(user_id: int, db: Session = Depends(get_db)):
    orders = crud.get_current_orders_user(db, user_id=user_id)
    return orders

@app.get("/user/order/{user_id}/finished", response_model=List[schemas.Order])
def get_finished_orders_restaurant(user_id: int, db: Session = Depends(get_db)):
    orders = crud.get_finished_orders_user(db, user_id=user_id)
    return orders

@app.get("/restaurant/order/{restaurant_id}/current", response_model=List[schemas.Order])
def get_current_orders_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    orders = crud.get_current_orders_restaurant(db, restaurant_id=restaurant_id)
    return orders

@app.get("/restaurant/order/{restaurant_id}/finished", response_model=List[schemas.Order])
def get_finished_orders_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    orders = crud.get_finished_orders_restaurant(db, restaurant_id=restaurant_id)
    return orders

@app.get("/order/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id)
    return order

@app.put("/order/finish/{order_id}", response_model=schemas.Order)
def finish_order(order_id: int, db: Session = Depends(get_db)):
    return crud.finish_order(db=db, order_id=order_id)
