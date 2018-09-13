### grpc-test
```text
.
├── protos      --->协议声明文件 
│   └── route_guide.proto
├── python
│   └── route_guide
│       ├── route_guide_client.py   -->前端2线程
│       ├── route_guide_pb2_grpc.py -->pb2文件名，自动生成的代码
│       ├── route_guide_pb2.py      -->pb2文件名，自动生成的代码
│       ├── route_guide_server.py   -->服务器
│       └── run_codegen.py          -->代码生成脚本
└── README.md
```
