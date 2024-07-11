# Use the official Ubuntu 20.04 base image
FROM ubuntu:20.04

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.9 and required system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    wget \
    curl \
    libopenmpi-dev \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.9 as the default Python
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install pip for Python 3.9
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3 get-pip.py \
    && rm get-pip.py

# Install gurobipy (assuming you have the appropriate license setup process)
RUN pip install gurobipy

# Copy the pycity_scheduling package to the container
COPY pycity_scheduling /opt/pycity_scheduling
WORKDIR /opt/pycity_scheduling

# Install the pycity_scheduling package
RUN pip install --upgrade pip \
    && pip install .

# Create the solvers directory and copy solver executables there
RUN mkdir /opt/solvers

# Assuming you have solver executables locally, you would COPY them to /opt/solvers
# For example:
COPY solver_bin/ /opt/solvers/
# COPY local/path/to/solver2 /opt/solvers/
RUN chmod +x /opt/solvers/scip

# Add the solvers directory to the PATH
ENV PATH="/opt/solvers/:${PATH}"

# Set the working directory
WORKDIR /

# Command to run the container
CMD ["bash"]
