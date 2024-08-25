import sys

if len(sys.argv) != 3:
    print("Usage: python3 compose_n_clients.py output_file n_clients")
    sys.exit(1)

output_file = int(sys.argv[1])
clients = int(sys.argv[2])

yaml = '''
version: "3.9"
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net
'''

for i in range(clients):
    yaml += f'''
  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
'''

yaml += '''
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
'''

with open(output_file, "w") as f:
    f.write(yaml)
