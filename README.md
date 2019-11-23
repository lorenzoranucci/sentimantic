# SENTIMANTIC


## Docker

### Build (optional)

docker-compose build 

### Run project stack

Swarm init:



```docker swarm init```

Deploy:

```docker stack deploy -c docker-compose.yml sentimantic```

Check:

```docker stack ps sentimantic```

Execute main container's bash:

```docker exec -it sentimantic_py2Env.1.7ghpxfz6yasfjtd7pjtseqqn3 bash```

Re-deploy:

```docker swarm leave --force```

```docker stack rm sentimantic ```

```docker stack deploy -c docker-compose.yml sentimantic ```

### Run project

