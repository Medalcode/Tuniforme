# Usar una imagen base oficial de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos
COPY requirements.txt requirements.txt

# Instalar las dependencias
RUN pip install -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . .

# Exponer el puerto en el que la aplicación correrá
EXPOSE 8000

# Comando para correr la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tuniforme.wsgi:application"]