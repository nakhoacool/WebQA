# Use a specific version of Python
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /core

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Use Gunicorn as WSGI server
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()" ]

# Expose port
EXPOSE 5000