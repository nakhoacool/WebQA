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