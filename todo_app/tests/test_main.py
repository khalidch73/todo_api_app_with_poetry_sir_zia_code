from fastapi.testclient import TestClient
from sqlmodel import Field, Session, SQLModel, create_engine, select
from todo_app.main import app, get_session, Todo
from todo_app import settings

# Test 01 for read_root
def test_read_main():
    # Setup: Create a TestClient instance
    client = TestClient(app)
    # Send GET request to the root endpoint
    response = client.get("/")
    
    # Assert that the response status code is 200 OK
    assert response.status_code == 200
    
    # Assert that the response JSON matches the expected value
    assert response.json() == {"Hello": "World"}

# Test 02 for create_todo
def test_write_main():
    # Setup: Create a TestClient instance and a database engine
    client = TestClient(app)
    connection_string = str(settings.TEST_DATABASE_URL).replace("postgresql", "postgresql+psycopg")
    engine = create_engine(connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    
    # Create tables in the test database
    SQLModel.metadata.create_all(engine)  
    
    with Session(engine) as session:  
        def get_session_override():  
                return session  
        app.dependency_overrides[get_session] = get_session_override 
        
        # Send POST request to create a new Todo item
        todo_content = "buy bread"
        response = client.post("/todos/", json={"content": todo_content})
        
        # Assert that the response status code is 200 OK
        assert response.status_code == 200
        
        # Assert that the returned Todo item matches the expected content
        data = response.json()
        assert data["content"] == todo_content

# Test 03 for read_todos
def test_read_list_main():
    # Setup: Create a TestClient instance and a database engine
    client = TestClient(app)
    connection_string = str(settings.TEST_DATABASE_URL).replace("postgresql", "postgresql+psycopg")
    engine = create_engine(connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    
    # Create tables in the test database
    SQLModel.metadata.create_all(engine)  
    
    with Session(engine) as session:  
        def get_session_override():  
                return session  
        app.dependency_overrides[get_session] = get_session_override 
        
        # Send GET request to retrieve all Todo items
        response = client.get("/todos/")
        
        # Assert that the response status code is 200 OK
        assert response.status_code == 200

# Test 04 for read_todo_by_id
def test_read_todo_by_id():
    # Setup: Create a TestClient instance
    client = TestClient(app)
    
    # Create a Todo item
    todo_content = "Test Todo"
    response_create = client.post("/todos/", json={"content": todo_content})
    
    # Assert that the response status code is 200 OK
    assert response_create.status_code == 200
    
    # Retrieve the created Todo item
    created_todo = response_create.json()
    
    # Send GET request to retrieve the Todo item by its ID
    response_read = client.get(f"/todos/{created_todo['id']}/")
    
    # Assert that the response status code is 200 OK
    assert response_read.status_code == 200
    
    # Assert that the returned Todo item matches the created Todo item
    assert response_read.json() == created_todo

# Test 05 for update_todo
def test_update_todo():
    # Setup: Create a TestClient instance
    client = TestClient(app)
    
    # Create a Todo item
    todo_content = "Test Todo"
    response_create = client.post("/todos/", json={"content": todo_content})
    
    # Assert that the response status code is 200 OK
    assert response_create.status_code == 200
    
    # Retrieve the created Todo item
    created_todo = response_create.json()
    
    # Update the content of the Todo item
    updated_content = "Updated Todo"
    response_update = client.put(f"/todos/{created_todo['id']}/", json={"content": updated_content})
    
    # Assert that the response status code is 200 OK
    assert response_update.status_code == 200
    
    # Retrieve the updated Todo item
    response_read = client.get(f"/todos/{created_todo['id']}/")
    
    # Assert that the response status code is 200 OK
    assert response_read.status_code == 200
    
    # Assert that the content of the Todo item was updated
    updated_todo = response_read.json()
    assert updated_todo['content'] == updated_content

# Test 06 for delete_todo_by_id
def test_delete_todo_by_id():
    # Setup: Create a TestClient instance
    client = TestClient(app)

    # Create a Todo item to delete
    todo_content = "Test Todo"
    response_create = client.post("/todos/", json={"content": todo_content})
    assert response_create.status_code == 200
    created_todo = response_create.json()

    # Delete the Todo item
    response_delete = client.delete(f"/todos/{created_todo['id']}/")
    assert response_delete.status_code == 200

    # Verify that the Todo item was deleted from the database
    response_read = client.get(f"/todos/{created_todo['id']}/")
    assert response_read.status_code == 404


# Test 07 for delete_all_todos
def test_delete_all_todos():
    # Setup: Create a TestClient instance
    client = TestClient(app)

    # Create multiple Todo items
    todo_contents = ["Test Todo 1", "Test Todo 2", "Test Todo 3"]
    for content in todo_contents:
        response_create = client.post("/todos/", json={"content": content})
        assert response_create.status_code == 200

    # Delete all Todo items
    response_delete = client.delete("/todos/")
    assert response_delete.status_code == 200

    # Verify that all Todo items were deleted from the database
    response_read_all = client.get("/todos/")
    assert response_read_all.status_code == 200
    todos = response_read_all.json()
    assert len(todos) == 0

# Test 08 for partial_update_todo
def test_partial_update_todo():
    # Setup: Create a TestClient instance
    client = TestClient(app)

    # Create a Todo item
    todo_content = "Test Todo"
    response_create = client.post("/todos/", json={"content": todo_content})
    assert response_create.status_code == 200
    created_todo = response_create.json()

    # Update the content of the Todo item partially
    updated_content = "Updated Todo"
    response_partial_update = client.patch(f"/todos/{created_todo['id']}/", json={"content": updated_content})
    assert response_partial_update.status_code == 200

    # Retrieve the updated Todo item
    response_read = client.get(f"/todos/{created_todo['id']}/")
    assert response_read.status_code == 200

    # Assert that the content of the Todo item was partially updated
    updated_todo = response_read.json()
    assert updated_todo['content'] == updated_content
