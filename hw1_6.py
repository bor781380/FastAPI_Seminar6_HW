# Задание №6
# 📌 Необходимо создать базу данных для интернет-магазина. База данных должна
# состоять из трех таблиц: товары, заказы и пользователи. Таблица товары должна
# содержать информацию о доступных товарах, их описаниях и ценах. Таблица
# пользователи должна содержать информацию о зарегистрированных
# пользователях магазина. Таблица заказы должна содержать информацию о
# заказах, сделанных пользователями.
# ○ Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY),
# имя, фамилия, адрес электронной почты и пароль.
# ○ Таблица товаров должна содержать следующие поля: id (PRIMARY KEY),
# название, описание и цена.
# ○ Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id
# пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус
# заказа.
# Создайте модели pydantic для получения новых данных и
# возврата существующих в БД для каждой из трёх таблиц
# (итого шесть моделей).
# 📌 Реализуйте CRUD операции для каждой из таблиц через
# создание маршрутов, REST API (итого 15 маршрутов).
# ○ Чтение всех
# ○ Чтение одного
# ○ Запись
# ○ Изменение
# ○ Удаление
from datetime import datetime
from typing import List
import os
import databases
import sqlalchemy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import ast


current_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(current_dir, "mydatabase.db")
DATABASE_URL = f"sqlite:///{db_file}"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_name", sqlalchemy.String(32)),
    sqlalchemy.Column("lastname", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(128)),

)

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("product_name", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(1024)),
    sqlalchemy.Column("price", sqlalchemy.Integer),

)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_user", sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column("id_product", sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column("date", sqlalchemy.DateTime),
    sqlalchemy.Column("status", sqlalchemy.String(10)),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)

app = FastAPI()

class UserIn(BaseModel): # модель используется при добавлении нового пользователя ИД база присвоит сама
    user_name: str = Field(title="Username", max_length=32)
    lastname: str = Field(title="Lastname", max_length=32)
    email: str = Field(title="Email", max_length=128)
    password: str = Field(title="Password", min_length=8)

class User(BaseModel): # модель используется при чтении пользователя ИД нам уже известен
    id: int
    user_name: str = Field(title="Username", max_length=32)
    lastname: str = Field(title="Lastname", max_length=32)
    email: str = Field(title="Email", max_length=128)
    password: str = Field(title="Password", min_length=8)

class ProductIn(BaseModel):
    product_name: str = Field(title="Product_name", max_length=32)
    description: str = Field(title="Description", max_length=1024)
    price: int = Field(title="Price")

class Product(BaseModel):
    id: int
    product_name: str = Field(title="Product_name", max_length=32)
    description: str = Field(title="Description", max_length=1024)
    price: int = Field(title="Price")

class OrderIn(BaseModel):
    id_user: int
    id_product: List[int]
    date: datetime = Field(title="Date")
    status: str = Field(title="Status")

class Order(BaseModel):
    id: int
    id_user: int
    id_product: List[int]
    date: datetime = Field(title="Date")
    status: str = Field(title="Status")



@app.get("/fake_users/{count}") #гет запрос по добавлению фейковых пользователей
async def create_fake_users(count: int):
    for i in range(count):
        query = users.insert().values(user_name=f'user{i}', lastname=f'user{i}', email=f'mail{i}@mail.ru', password=f'user{i}{i}{i}{i}{i}')
        await database.execute(query)
    return {'message': f'{count} fake users create'}

@app.get("/fake_products/{count}") #гет запрос по добавлению фейковых записей в таблицу товаров
async def create_fake_products(count: int):
    for i in range(count):
        query = products.insert().values(product_name=f'product{i}', description=f'description {i}', price=f'{int(1000+i)}')
        await database.execute(query)
    return {'message': f'{count} fake users create'}

#********************USERS**********************

@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(user_name=user.user_name, lastname=user.lastname, email=user.email, password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}

#********************PRODUCT**********************

@app.get("/products/", response_model=List[Product])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)

@app.get("/products/{products_id}", response_model=Product)
async def read_product(product_id: int):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)

@app.post("/products/", response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(product_name=product.product_name, description=product.description, price=product.price)
    last_record_id = await database.execute(query)
    return {**product.dict(), "id": last_record_id}

@app.put("/products/{products_id}", response_model=Product)
async def update_product(product_id: int, new_product: ProductIn):
    query = products.update().where(products.c.id == product_id).values(**new_product.dict())
    await database.execute(query)
    return {**new_product.dict(), "id": product_id}

@app.delete("/products/{products_id}")
async def delete_product(product_id: int):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': 'Product deleted'}

#********************ORDERS**********************


@app.get("/orders/", response_model=List[Order])
async def read_orders():
    query = orders.select()
    rows = await database.fetch_all(query)
    orders_list = []
    for row in rows:
        id_product = ast.literal_eval(row["id_product"])
        order = {
            "id": row["id"],
            "id_user": row["id_user"],
            "id_product": id_product,
            "date": row["date"],
            "status": row["status"],
        }
        orders_list.append(order)
    return orders_list


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    rows = await database.fetch_all(query)
    if len(rows) == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    row = rows[0]
    id_product = ast.literal_eval(row["id_product"])
    return {
        "id": row["id"],
        "id_user": row["id_user"],
        "id_product": id_product,
        "date": row["date"],
        "status": row["status"],
    }


@app.post("/orders", response_model=Order)
async def create_order(order_in: OrderIn):
    id_product_str = str(order_in.id_product)
    query = orders.insert().values(
        id_user=order_in.id_user,
        id_product=id_product_str,
        date=order_in.date,
        status=order_in.status
    )
    order_id = await database.execute(query)
    return {**order_in.dict(), "id": order_id}

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(
        id_user=new_order.id_user,
        id_product=str(new_order.id_product),
        date=new_order.date,
        status=new_order.status
    )
    await database.execute(query)
    return {**new_order.dict(), "id": order_id}

@app.delete("/orders/{orders_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Orders deleted'}

# запуск сервера uvicorn HW6.hw1_6:app --reload