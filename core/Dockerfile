FROM python:3
WORKDIR /core
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD [ "python", "./app.py" ]