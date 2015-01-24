Estimador de Resultados Electorales 2015
========================================

## Intro

## Definiciones

### Escenarios
- id
- resultado: (candidato_i => porcentaje_i)

### Preguntas
- id
- tipo (mayor menor, threshold individual, threshold total, ventaja ganador)
- argumentos (cosas)

#### Genericas
* [unCandidato] sacara [mas] votos que [unCandidato]? *

Tipo: 1
Argumentos: {[unCandidato] [unCandidato]}

* [unCandidato] sacara mas del X% de los votos? *
Tipo: 2
Argumentos: {[unCandidato] [XX]}

* [unCandidato] sacara menos del X% de los votos? *
Tipo: 3
Argumentos: {[unCandidato] [XX]}


#### Especificas

* Algun candidato sacara mas del X% de los votos? *
Tipo: 4
Argumentos: {[XX]}


* El ganador, le sacara al menos X% al segundo? *
Tipo: 5
Argumentos: {[XX]}

* Habra al menos N candidatos con mas de X% cada uno? ==> cuidar que N\*X <= 100 *
Tipo: 6
Argumentos: {[N] [XX]}


??? Preguntas sobre "EL RESTO"???
Como manejar "EL RESTO"
TODO: Computar el ratio de SI de cada pregunta, e insistir sobre aquellas que tienen ~.5 para discernir entre escenarios similares.


Dudoso
Habra ballotage?

### Deploy
Requisitos;
go 1.4.1
redis
python2

Instrucciones

Instalar go (descomprimir)
mkdir gomodules
Setear en .profile
export GOROOT = $(HOME)/gp
export GOPATH = $(HOME)/gomodules
go get github.com/fzzy/radix/redis

Instalar redis (con make) y montar el servidor andando
en el redis.conf setear

maxmemory-policy noeviction
maxmemory 100mb
bind 127.0.0.1


Instalar python-redis
sudo pip install python-redis

Correr Webserver:
./redis/redis-server (o daemonizarlo)
go run webserver.go

