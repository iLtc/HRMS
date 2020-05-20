# HRMS

A Human Resources Management System based on P2P network.

This system includes three different types of nodes: **Central Node**, **Service Node**, and **Client Node**.

**Central Node** is **required** for the P2P network to keep a list of active nodes.

**Service Node** will provide different services, such as user authentication, clock in and out, etc., to the P2P network. There may be one or more Service Nodes in the system that provide the same or different services.

**Client Node** is **required** for the user to interact with other Service Nodes and will provide a web interface using Flask, Bootstrap, and jQuery.

## Installation

Click [here](https://github.com/iLtc/HRMS/archive/master.zip) to download the project.

After unzipping the project and going to the project folder, use the following command to install the required dependencies.

```
pip3 install -r requirements.txt
```

## How to Use

### Central Node

*The Central Node should be the first one to start the last one to shut down. Otherwise, you may encounter unexpected errors.*

To start the Central Node, use the following command.

```
python3 central_server.py
```