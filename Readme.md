# Project Name

Pycity_deployment in a docker

## Docker Deployment

### Prerequisites

- Docker Engine: [Install Docker](https://docs.docker.com/get-docker/)


### Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/anon98/pycity_dev.git (use --recursive to access the submodules)
   cd pycity_dev


2. **build the docker image**
    ```bash
    docker build -t pycity_scheduling:latest .

3. **Run the Docker Container** 
     ```bash
    docker run -it --rm -v $(pwd)/examples:/examples pycity_scheduling:latest
4. **Run the scripts**

    ```bash
    >>> examples/exaples_00__.py 