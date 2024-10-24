# WebQA
A RAG based chat bot that can incoporate external knowledge source.

This bot is developed to perform QA task for:
- TDT (Tôn Đức Thắng university)
- UEH (University of Economics Ho Chi Minh city)

## Data
All the dataset is hosted on https://huggingface.co/BroDeadlines
TDT dataset
```
Text data: https://huggingface.co/datasets/BroDeadlines/TEST.TDT.edu_tdt_proposition_data/viewer/default/INDEX.medium_index_TDT_clean
QA dataset: https://huggingface.co/datasets/BroDeadlines/QA.TDT.FQA_tu_van_hoc_duong/viewer/default/INDEX.medium_index_TDT
```

UEH dataset
```
Text data: https://huggingface.co/datasets/BroDeadlines/TEST.UEH.ueh_copora_data
QA dataset: https://huggingface.co/datasets/BroDeadlines/QA.UEH.QA_tu_van_tuyen_sinh
```

## System architecture

![WebQA architecture](./docs/images/system_architecture.png)

## Guides
### How to run

At the top of parent directory, run

```bash
cd client
npm i
npm run dev
```

At the top directory, run

```bash
cd core
pip install -r deploy_req.txt
cd ../
flask --app core/app.py run
```

### Config API keys
The source code is provided with API keys so only need to config these keys if you need.

For Python Back-end
```
cd core/.keys
ls
```

For NextJS Front-end
```
cat client/.env
```

To get the ca.cert
```
docker cp elasticsearch-es01-1:/usr/share/elasticsearch/config/certs/ca/ca.crt /home/ubuntu/elasticsearch
```

### Docker Setup and Installation

1. Make sure Docker and Docker Compose are installed on your machine. If not, you can download them from [Docker's official website](https://www.docker.com/products/docker-desktop).

2. Clone the repository.

3. Build and run the Docker containers using Docker Compose. Navigate to the root directory of the project where the `docker-compose.yml` file is located and run the following command:

```sh
docker compose up --build -d
```

This command will build the Docker images for the server and client services defined in the docker-compose.yml file, and then start the containers.

4. The server will be running at http://localhost:5000 and the client will be running at http://localhost:3000.
