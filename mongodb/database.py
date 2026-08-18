import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio  


load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")

#Inicializar el cliente de MongoDB
client = AsyncIOMotorClient(MONGO_URL)

# Selecionar la base de datos (se creara automaticamente si no existe)
database = client.ambiente502

# Seleccionar la coleccion (se creara automaticamente si no existe)
collection = database.mesas

# Funcion para probar la conexion a la base de datos
async def test_conection():
    try:
        #1.Verificar la conexion al servidor de MongoDB
        await client.admin.command('ping')
        print("Conexion a MongoDB exitosa.")
        #Crear documento de prueba
        doctest = {
            "nombre": "Samuel",
            "edad":"17",
            "genero":"masculino"
        }
        
        # Guardar el documetno en la coleccion
        print("Guardando docuemtno de prueba en la coleccion...")
        result= await collection.insert_one(doctest)
        inserted_id = result.inserted_id

        print(f"Documento guardado con ID: {result,inserted_id}")

        #Buscar el dato guardado en la coleccion
        datarequest = await collection.find_one({"_id":result.inserted_id})
        print(f"docuemto encontrado: {datarequest}")

    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")

if __name__ == "__main__":
# Ejecuta la prueba de conexion.
    asyncio.run(test_conection())