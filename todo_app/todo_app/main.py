# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from todo_app import settings 
from sqlmodel import Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends, HTTPException, Path
from todo_app.models import Todo


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Todo API", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000/", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session

# 01 Define the route to read route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 02 Define the route to create_todo Todos in database
@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    # Add the new todo item to the session
    session.add(todo)
    # Commit the transaction to save the changes to the database
    session.commit()
    # Refresh the todo item to ensure it reflects any changes made during the commit
    session.refresh(todo)
    # Return the created Todo item with its updated attributes.
    return todo

# 03 Define the route to read all Todos in database
@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

# 04 Define the route to read a Todo item by its ID
@app.get("/todos/{todo_id}/")
def read_todo_by_id(todo_id: int = Path(..., title="The ID of the Todo item to read"), session: Session = Depends(get_session)):
    # Retrieve the Todo item from the database
    todo = session.get(Todo, todo_id)
    # Check if the Todo item exists
    if not todo:
        # If Todo item does not exist, raise HTTPException with 404 status code
        raise HTTPException(status_code=404, detail="Todo not found")
    # Return the Todo item as JSON response
    return todo

# 05 Define the route to update a Todo item
@app.put("/todos/{todo_id}/")
def update_todo(todo_id: int, updated_todo: Todo, session: Annotated[Session, Depends(get_session)]):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    # Update fields of the existing Todo with data from updated_todo
    for field in updated_todo.dict(exclude_unset=True):
        setattr(todo, field, getattr(updated_todo, field))
    session.commit()
    session.refresh(todo)
    return todo


# 06 Define the route to delete a Todo item
@app.delete("/todos/{todo_id}/")
def delete_todo_by_id(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    # Retrieve the Todo item from the database
    todo = session.get(Todo, todo_id)
    # Check if the Todo item exists
    if not todo:
        # If Todo item does not exist, raise HTTPException with 404 status code
        raise HTTPException(status_code=404, detail="Todo not found")
    # Delete the Todo item from the session
    session.delete(todo)
    session.commit()
    # Return a JSON response indicating successful deletion
    return {"message": "Todo deleted successfully"}

# 07 Define the route to delete all Todos
@app.delete("/todos/")
def delete_all_todos(session: Annotated[Session, Depends(get_session)]):
    # Retrieve all Todo items from the database
    todos = session.exec(select(Todo)).all()
    # Delete each Todo item
    for todo in todos:
        session.delete(todo)
    # Commit the transaction to save the changes to the database
    session.commit()
    # Return a JSON response indicating the successful deletion of all Todo items
    return {"message": "All Todo items deleted successfully"}


# 08 Define the route to partially update a Todo item using PATCH
@app.patch("/todos/{todo_id}/")
def partial_update_todo(todo_id: int, updated_todo: Todo, session: Annotated[Session, Depends(get_session)]):
    # Retrieve the Todo item from the database
    todo = session.get(Todo, todo_id)
    # Check if the Todo item exists
    if not todo:
        # If Todo item does not exist, raise HTTPException with 404 status code
        raise HTTPException(status_code=404, detail="Todo not found")
    # Update only the provided fields of the existing Todo with data from updated_todo
    for field, value in updated_todo.dict(exclude_unset=True).items():
        setattr(todo, field, value)
    session.commit()
    session.refresh(todo)
    return todo
