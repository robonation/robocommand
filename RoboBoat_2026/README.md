# RoboCommand

This is the message definitions and example server/client for the 2026 RoboBoat competition.

## Contents

* The Protocol Buffer message definition file, **report.proto**, can be found in the `./proto` folder.

* The Python and C++ compiled outputs of report.proto can be found in the `./msgs` folder.

* A simple python server for testing and debugging.

  * This test server is using the same TCP_library that the course server uses.

* A simple python client with setup instructions below.

* A simple C++ client example. 

## Dependencies

RoboCommand uses v6.32.1 of the protobuf runtime library and v32.1 of the protoc compiler.

## Running the python test server and client:

Setup up a python virtual environment:

    python -m venv venv

Activate the new environment:

    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Start the server:

    python -m examples.test_server

In a new terminal, activate the environment:

    source venv/bin/activate

Run the client to send a message:

    python -m examples.test_client

A message should have printed in the server's console.

You can update the message contents in the client script.

Run the server and test your own client software to ensure it behaves as expected.