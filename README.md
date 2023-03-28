# TP0: Docker + Comunicaciones + Concurrencia

Se presenta una guía de ejercicios que los alumnos deberán resolver teniendo en cuenta las consideraciones generales descritas al pie de este archivo.

## Caso de uso

### Cliente

Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias.
Enviara al servidor los datos de las apuestas realizadas por los clientes, que lee de un archivo.
Al finalizar de enviar apuestas, consultara por los ganadores de su agencia.

### Servidor

Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)`.
Al finalizar la rifa, deberá responder a los clientes con los ganadores de cada agencia cuando estos lo soliciten.
Las solicitudes de los clientes son atendidas de manera concurrente.

### Comunicación:

Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:

- Definición de un protocolo para el envío de los mensajes.
- Serialización de los datos.
- Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
- Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).
- Límite máximo de paquete de 8kB.

## Protocolo de comunicación

#### Formato de los mensajes

**Mensajes Cliente**: Cuando un cliente manda un mensaje al servidor, primero manda un uint16_t que representa la longitud del mensaje, y luego el mensaje en sí como string-utf8. Estos mensajes no pueden superar los 8kB.
**Mensajes Servidor**:Cuando el servidor responde a un cliente, manda directamente el mensaje como string-utf8, cuyo fin es marcado por un fin de linea.

#### Tipos de mensaje

**Mensajes Cliente**:

- `BETS`: Indica que el cliente enviará apuestas.
  - El cliente enviara _chunks_ con información sobre apuestas
    - Cada _chunk_ tendrá una cantidad configurable de apuestas separadas por punto y coma ";"
    - Cada apuesta se representa como los campos separados por coma ","
    - El cliente espera la respuesta de cada _chunk_ antes de enviar el siguiente
  - `CLOSE`: Indica que el cliente no enviará más apuestas.
- `ASK`: Indica que el cliente quiere saber los ganadores de su agencia.
  - El cliente espera la respuesta del servidor con los ganadores de su agencia.

**Mensajes Servidor**:

- En respuesta a un _chunk_ de `BETS`
  - `OK`: Indica que las apuestas fueron almacenadas correctamente.
  - `ERROR`: Indica que hubo un error al almacenar las apuestas.
- En respuesta a `ASK`
  - Si finalizo la rifa, el servidor responde con un string con los documentos ganadores de la agencia del cliente, separados por coma ","
  - `REFUSE`: Indica que el servidor se niega a responder la consulta, ya que la rifa no finalizo.

## Mecanismos de sincronización

Mecanismos utilizados en el servidor para garantizar su correcta operación de modo concurrente.

### Exclusión mutua

Se utilizaron **Locks** para garantizar la exclusión mutua en las siguientes secciones críticas:

- `store_bets`: No se debe llamar a la función `store_bets` mientras se está ejecutando la misma función en otro proceso.
- `check_winners`: Se verifica si los ganadores fueron calculados, y si no lo fueron se calculan (cargando las apuestas desde el archivo y verificando una por una). Esta operación es atómica, de modo que solo se calcularan una vez.
- `finished_clients`: Se verifica si todos los clientes terminaron de mandar apuestas, agregando al cliente que esta haciendo la consulta. Esta operación es atómica, para que no haya condiciones de carrera.

### Memoria compartida

Se utiliza un diccionario compartido para almacenar los siguientes datos:

- `finished_clients`: Lista de ids de clientes que terminaron de enviar apuestas.
- `all_clients_finished`: Indica si todos los clientes terminaron de enviar apuestas.
- `winners`: Lista de apuestas ganadoras de la rifa.

## Instrucciones de uso

El repositorio cuenta con un **Makefile** que posee encapsulado diferentes comandos utilizados recurrentemente en el proyecto en forma de targets. Los targets se ejecutan mediante la invocación de:

- **make \<target\>**:
  Los target imprescindibles para iniciar y detener el sistema son **up** y **down**, siendo los restantes targets de utilidad para el proceso de _debugging_ y _troubleshooting_.

Los targets disponibles son:

- **up**: Inicializa el ambiente de desarrollo (buildear docker images del servidor y cliente, inicializar la red a utilizar por docker, etc.) y arranca los containers de las aplicaciones que componen el proyecto.
- **down**: Realiza un `docker-compose stop` para detener los containers asociados al compose y luego realiza un `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene.
- **logs**: Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose.
- **docker-image**: Buildea las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **up**, por lo cual se lo puede utilizar para testear nuevos cambios en las imágenes antes de arrancar el proyecto.
- **build**: Compila la aplicación cliente para ejecución en el _host_ en lugar de en docker. La compilación de esta forma es mucho más rápida pero requiere tener el entorno de Golang instalado en la máquina _host_.

## Parte 1: Introducción a Docker

En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:

Modificar la definición del DockerCompose para agregar un nuevo cliente al proyecto.

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.

### Ejercicio N°1.1:

Definir un script (en el lenguaje deseado) que permita crear una definición de DockerCompose con una cantidad configurable de clientes.

#### Como ejecutar:

Podemos utilizar el script `python3 compose_n_clients.py N` para crear un archivo `docker-compose-dev.yaml` con N clientes.

### Ejercicio N°2:

Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera un nuevo build de las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida afuera de la imagen (hint: `docker volumes`).

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.
Si detenemos los contenedores y modificamos la configuración, podemos volver a levantarlos y verificar que los cambios se hayan aplicado.
También podríamos verificar la correcta modificación del archivo ejecutando comandos dentro del contenedor.

### Ejercicio N°3:

Crear un script que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un EchoServer, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado. Netcat no debe ser instalado en la máquina _host_ y no se puede exponer puertos del servidor para realizar la comunicación (hint: `docker network`).

#### Como ejecutar:

Descontinuado, ya que a partir de la parte 2 se modifica el protocolo de comunicación.

### Ejercicio N°4:

Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.
Si detenemos un proceso mientras se está ejecutando, podemos ver que el mismo se detiene de forma correcta a traves de los logs.

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base al código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:

Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo [caso de uso](#caso-de-uso).

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.
Podemos verificar la correcta modificación del archivo `bets.csv` ejecutando comandos dentro del contenedor.

### Ejercicio N°6:

Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento. La cantidad de apuestas dentro de cada _batch_ debe ser configurable.
El servidor, por otro lado, deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.
Podemos verificar la correcta modificación del archivo `bets.csv` ejecutando comandos dentro del contenedor.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo, no podrá responder consultas por la lista de ganadores.
Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.
Podemos verificar la correcta modificación del archivo `bets.csv` ejecutando comandos dentro del contenedor.

> Nota: Si modificamos la cantidad de clientes en el compose: recordar modificar la cantidad de clientes en la configuración del servidor.

## Parte 3: Repaso de Concurrencia

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo.
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

En caso de que el alumno implemente el servidor Python utilizando _multithreading_, deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

#### Como ejecutar:

Podemos utilizar el comando `make up` y luego visualizar los logs para verificar el funcionamiento.
Podemos verificar la correcta modificación del archivo `bets.csv` ejecutando comandos dentro del contenedor (Veremos mezcladas apuestas de diferentes agencias).

> Nota: Si modificamos la cantidad de clientes en el compose: recordar modificar la cantidad de clientes en la configuración del servidor.

## Consideraciones Generales

Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios.
El _fork_ deberá contar con una sección de README que indique como ejecutar cada ejercicio.
La Parte 2 requiere una sección donde se explique el [protocolo de comunicación](#protocolo-de-comunicación) implementado.
La Parte 3 requiere una sección que expliquen los [mecanismos de sincronización](#mecanismos-de-sincronización) utilizados.

Finalmente, se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección provistos [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).
