#SENTIMANTIC


##Docker

###Build (optional)

docker-compose build 

###Run project stack

Deploy:

```docker stack deploy -c docker-compose.yml sentimantic```

Check:

```docker stack ps sentimantic```

Execute main container's bash:

```docker exec -it sentimantic_py2Env.1.7ghpxfz6yasfjtd7pjtseqqn3 bash```

Re-deploy:

```docker stack rm sentimantic
docker stack deploy -c docker-compose.yml sentimantic```