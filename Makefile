

SHELL := /bin/bash

all: 
	source venv/bin/activate
	mkdir -p ./src/auto_generated
	python3 -m grpc_tools.protoc -Isrc/protos --python_out=src/auto_generated --grpc_python_out=src/auto_generated src/protos/measurement.proto

clean:
	rm -rf src/auto_generated

check:
	python3 -m unittest discover ./tests