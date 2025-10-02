# Local PostgreSQL and Redis Setup Guide

By default, this application uses a file-based SQLite database for persistence. While this is convenient for local testing—allowing you to start fresh by simply deleting a single file in the `/backend` directory—it does not provide a realistic representation of a production environment. This guide will walk you through setting up PostgreSQL and Redis for local development using Docker to better simulate a production setup.

## Prerequisites

* **Docker**: Ensure that Docker is installed and running on your system. You can download it from the [official Docker website](https://www.docker.com/products/docker-desktop/).

## 1. PostgreSQL Setup (with pgvector)

We will use the `pgvector` image, which includes the PostgreSQL extension for vector similarity search.

### Run PostgreSQL Container

Open your terminal and run the following command to start a PostgreSQL container:

```bash
docker run --name pgvector_postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -p 5434:5432 -d pgvector/pgvector:pg16
```

* `--name pgvector_postgres`: Assigns a name to the container for easy reference.
* `-e POSTGRES_PASSWORD=postgres`: Sets the password for the default `postgres` user.
* `-e POSTGRES_DB=postgres`: Creates a default database named `postgres`.
* `-p 5434:5432`: Maps port `5434` on your local machine to port `5432` inside the container. Note that we use `5434` to avoid conflicts with any existing PostgreSQL installations you may have running locally.
* `pgvector/pgvector:pg16`: Specifies the Docker image to use (PostgreSQL 16 with pgvector).

### Configure PostgreSQL Environment Variables

Add the following variables to your `.env` file to connect the application to the PostgreSQL container:

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5434/postgres"
VECTOR_DB=pgvector
```

## 2. Redis Setup

Next, set up a Redis container for features like WebSocket support.

### Run Redis Container

Run the following command in your terminal to start a Redis container:

```bash
docker run --name redis -p 6381:6379 -d redis:latest
```

* `--name redis`: Assigns the name `redis` to the container.
* `-p 6381:6379`: Maps port `6381` on your local machine to the Redis port `6379` inside the container. Note that we use `6381` to avoid conflicts with any existing Redis installations you may have running locally.
* `-d`: Runs the container in detached mode.
* `redis:latest`: Uses the latest official Redis image.

### Configure Environment Variables

Add the following variables to your `.env` file to enable WebSocket and Redis functionalities:

```env
ENABLE_WEBSOCKET_SUPPORT=true
WEBSOCKET_REDIS_URL="redis://:@localhost:6380"
REDIS_URL="redis://localhost:6380"
WEBSOCKET_MANAGER=redis
```

After updating your `.env` file and ensuring both containers are running, your local development environment will be configured to use PostgreSQL and Redis.
