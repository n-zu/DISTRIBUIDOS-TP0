import sys

if len(sys.argv) != 2:
    print("Usage: python3 compose_n_clients.py n")
    sys.exit(1)

clients = int(sys.argv[1])

yaml = '''version: "3.9"
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
    volumes:
      - ./server/config.ini:/config.ini
'''

for i in range(clients):
    yaml += f'''
  client{i+1}:
    container_name: client{i+1}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i+1}
      - CLI_LOG_LEVEL=DEBUG
      - NOMBRE=Santiago Lionel
      - APELLIDO=Lorca
      - DOCUMENTO=30904465
      - NACIMIENTO=1999-03-17
      - NUMERO=7574
    networks:
      - testing_net
    depends_on:
      - server
    volumes:
      - ./client/config.yaml:/config.yaml
'''


yaml += '''
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
'''

with open("docker-compose-dev.yaml", "w") as f:
    f.write(yaml)
