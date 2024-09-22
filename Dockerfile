# Utiliza una imagen base ligera de Python 3.9 (slim para reducir el tamaño)
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar solo los archivos necesarios para optimizar la cache
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto 8000 (puerto por defecto para FastAPI)
EXPOSE 8000

# Comando para ejecutar la aplicación FastAPI con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
