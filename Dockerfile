# Use the official Python image as the base image
FROM python:3.11

# Install graphviz
RUN apt update -y
RUN apt install graphviz graphviz-dev -y

# Update pip and install requirements
RUN pip install --upgrade pip
RUN pip install toml setuptools

# add app user
RUN groupadd gennifer_user && useradd -ms /bin/bash -g gennifer_user gennifer_user

# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app

# Install the required packages for the api
RUN pip install -r requirements.txt

# Clone pybkb and install dependencies and install
RUN git clone --single-branch --branch master https://github.com/di2ag/pybkb.git
RUN cd pybkb && pip install -r requirements.txt && python setup.py install

# chown all the files to the app user
RUN chown -R gennifer_user:gennifer_user /app

USER gennifer_user

# Copy the current directory contents into the container at /app
COPY . /app

# Start the Flask app
CMD ["flask", "--app", "bkb_grn", "run", "--host", "0.0.0.0", "--debug"]
