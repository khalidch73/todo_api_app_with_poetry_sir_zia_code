import requests


BASE_URL = "http://127.0.0.1:8000"

def create_todo():
    id = int(input("Enter Todo ID: "))
    content = input("Enter Todo content: ")
    response = requests.post(f"{BASE_URL}/todos/", json={"id": id, "content": content})
    if response.status_code == 200:
        print("Todo added successfully")

def delete_todo():
    todo_id = input("Enter Todo ID to delete: ")
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    if response.status_code == 200:
        print("Todo deleted successfully")

def update_todo():
    todo_id = input("Enter Todo ID to update: ")
    content = input("Enter new Todo Title: ")
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json={"id" : todo_id, "content": content})
    if response.status_code == 200:
        print("Todo updated successfully")

def get_todo_by_id():
    todo_id = input("Enter Todo ID to retrieve: ")
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    if response.status_code == 200:
        todo = response.json()
        print(f"ID: {todo['id']}, content: {todo['content']}")

def get_all_todos():
    response = requests.get(f"{BASE_URL}/todos/")
    if response.status_code == 200:
        todos = response.json()
        print("All Todos:")
        for todo in todos:
            print(f"ID: {todo['id']}, content: {todo['content']}") 

if __name__ == "__main__":
    while True:
        print("\n1. Create Todo")
        print("2. Delete Todo")
        print("3. Update Todo")
        print("4. Get Todo by ID")
        print("5. Get All Todos")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            create_todo()
        elif choice == "2":
            delete_todo()
        elif choice == "3":
            update_todo()
        elif choice == "4":
            get_todo_by_id()
        elif choice == "5":
            get_all_todos()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
