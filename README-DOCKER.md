# DRAW - Docker

## Before starting the analysis make sure you have installed Docker on your Linux machie, recommended version 19.03.8. It is the only installation needed, the rest does Docker itself.

To get the image of DRAW, execute the following command:
```console
$ docker build . -t draw
```

To run the container and bind folders, where you store the input data and want to save config files and output data, type the command below. \
Make sure folders, you are pathing, are exclusively dedicated for anaysed data, otherwise you will add every file form given directory to docker container.
```
$ docker run -v ${PWD}:/app/input \
-v ${PWD}:/app/config_files \
-v ${PWD}:/app/output \
-p 2000:2000 -p 5000:5000 \
-it draw
```

To stop the docker from running use Ctrl + c


Options glossary: \
--tag, -t Tag docker container. \
--publish , -p	Publish a container’s port(s) to the host \
--volume , -v	Bind mount a volume \
--interactive, -it Run container in interactive mode