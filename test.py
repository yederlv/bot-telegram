import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Accede a una variable de entorno específica
valor = os.getenv('TOKEN')
print(valor)
