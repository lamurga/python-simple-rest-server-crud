# EJECUTAR

$ pip install -r requirements.txt
$ python main.py


# PRUEBAS
-------

curl "http://localhost:8080/"

# LISTAR
curl "http://localhost:8080/users"
# CREAR
curl -d "email=micorreo@empresa.com&text1=John&text2=Snow&text3=avlostronos" http://localhost:8080/users
# ACTUALIZAR
curl -X PUT -d '{"firstname": "John"}' "http://localhost:8080/user/1"
curl -X PUT -d '{"lastname": "Lennon"}' "http://localhost:8080/user/2"
curl "http://localhost:8080/users"
# ELIMINAR
curl -X DELETE "http://localhost:8080/user/2"
curl "http://localhost:8080/users"
