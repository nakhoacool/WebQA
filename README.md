## To run Flask server
At the top directory, run
```bash
flask --app core/app.py run
```

To test QA with GET request, go to
- http://127.0.0.1:5000/qa/em%20gi%E1%BB%8Fi%20v%E1%BA%BD%20th%C3%AC%20n%C3%AAn%20h%E1%BB%8Dc%20g%C3%AC

To test QA with POST request, run
```bash
bash test_POST.sh

cat a.txt
```

## Docker Setup and Installation

1. Make sure Docker and Docker Compose are installed on your machine. If not, you can download them from [Docker's official website](https://www.docker.com/products/docker-desktop).

2. Clone the repository.

3. Build and run the Docker containers using Docker Compose. Navigate to the root directory of the project where the `docker-compose.yml` file is located and run the following command:

```sh
docker-compose up --build
```

This command will build the Docker images for the server and client services defined in the docker-compose.yml file, and then start the containers.

4. After that open another terminal window and run the following command:

```sh
docker compose watch
```

This command will watch for any changes in the source code and automatically rebuild the Docker images and restart the containers.

5. The server will be running at http://localhost:5000 and the client will be running at http://localhost:3000.
