import requests

url = "https://taskforce-api-zxag.onrender.com/task"

def getTask():
    response = requests.get(f"{url}/get")
    return response.json()

def deleteTask(idTask):
    response = requests.delete(f"{url}/delete/{idTask}")
    return response

def createTask(nmTarefa):
    response = requests.post(f"{url}/create/{nmTarefa}")
    return response

def marcarTask(idTask):
    response = requests.put(f"{url}/put/marcar/{idTask}")
    return response