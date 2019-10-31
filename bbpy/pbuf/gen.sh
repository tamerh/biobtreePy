#!/bin/bash

#python -m pip install protobuf
#python -m pip install --upgrade pip
#python -m pip install grpcio
#python -m pip install requests
#python -m pip install grpcio-tools

rm app_*
rm attr_*

python -m grpc_tools.protoc --python_out=.  --grpc_python_out=. app.proto
python -m grpc_tools.protoc --python_out=.   attr.proto
