# Providing Server AKA Super_Forge

Alpha version of the project. The project is a server that provides a RESTful API to manage various aspects of a server, such as creating database users, installing packages, and more. The server is built using Quart and runs as a Linux service.

## Table of Contents

- [Installation](#installation)
- [After-Installation Step](#after-installation-step)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install the project, follow these steps:

```bash
# Clone the repository
git clone https://github.com/dkaliinin505/providing_server.git

# Change into the directory
cd providing_server

# Pre-Install the requirements
python3 install.py

# Run the following command to continue installation
{your_path}/providing_server/providing_env/bin/python install.py
```

## After-Installation Step

Also, you need to open ports `5000,80,443` on your server, or hosting.
After that you can use this service via your public IP.

You also need to edit the .env file and update the HOST key with the public address of your server.

Open the .env file and make the following changes:
    
```
# .env
HOST=your_public_server_ip
```
Replace `your_public_server_ip` with the actual public IP address of your server. This step is crucial for ensuring that the service is accessible via your public IP.

By following these instructions, you'll have the project installed and configured correctly on your server.

## Usage
After installing the project, the server is managed as a Linux service named providingServer. Below are some commands to manage the service and use the provided API.

## Managing the Service

To manage the `providingServer` service, use the following commands:

### Check Service Status
```bash
sudo systemctl status providingServer
```

### Start the Service
```bash
sudo systemctl start providingServer
```

### Stop the Service
```bash
sudo systemctl stop providingServer
```

### Restart the Service
```bash
sudo systemctl restart providingServer
```

## Using the API

Here are some examples of how to use the API endpoints provided by the server.

### Create a Database User

To create a new database user, send a `POST` request to the `/create-database-user` endpoint with the following JSON payload:

```json
{
    "db_user": "new_user",
    "db_user_password": "user_password",
    "db_privileges": ["ALL PRIVILEGES"],
    "db_host": "3.73.182.116"
}
```

### Delete a Database User

To delete an existing database user, send a `DELETE` request to the `/delete-database-user` endpoint with the following query parameters:

```bash
curl -X DELETE "http://your_server_ip:5000/delete-database-user?db_user=example_user"
```

### Create a Database

To create a new database, send a `POST` request to the `/create-database` endpoint with the following JSON payload:

```json
{
    "db_name": "example_database",
    "create_user": true,
    "db_user": "example_user",
    "db_user_password": "user_password",
    "db_privileges": ["ALL PRIVILEGES"],
    "db_host": "3.73.182.116"
}
```

### Install a Package

To install a package, send a `POST` request to the `/install-package` endpoint with the following JSON payload:

```json
{
    "package_name": "nginx",
    "config": {
        "memory_limit": "512M",
        "pm_max_children": 20
    }
}
```

### Check Task Status

To check the status of a background task, send a `GET` request to the `/task-status/<task_id>` endpoint:

```bash
curl -X GET "http://your_server_ip:5000/task-status/1"
```

This will return the status of the task with the specified `task_id`.

## Additional Commands

You can use other commands and endpoints provided by the server to manage various aspects of your server. Refer to the API Documentation section for more details.

## API Documentation

Follow this [link](https://app.swaggerhub.com/apis-docs/DP101196/Super_forge/1.0.0-oas3) to see the API documentation on SwaggerHub.

