import docker

# Docker SDK for Python
# [Documentation](https://docker-py.readthedocs.io/en/stable/index.html)

# Open Source Routing Machine (OSRM)
# https://hub.docker.com/r/osrm/osrm-backend
OSRM = [
    """docker run -t -v "${PWD}/data/GCA:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/planet_-114.516_50.685_7e77eeeb.osm.pbf""",
    """docker run -t -v "${PWD}/data/GCA:/data" osrm/osrm-backend osrm-partition /data/planet_-114.516_50.685_7e77eeeb.osrm  """,
    """docker run -t -v "${PWD}/data/GCA:/data" osrm/osrm-backend osrm-customize /data/planet_-114.516_50.685_7e77eeeb.osrm""",
    """docker run -t -i -p 8080:5000 -v "${PWD}/data/GCA:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/planet_-114.516_50.685_7e77eeeb.osrm"""
]

# Open Route Service (ORS)
# Install and run openrouteservice with docker
# https://giscience.github.io/openrouteservice/installation/Running-with-Docker.html

ORS_ARM = """docker run -dt -u "${UID}:${GID}" --name ors-app -p 8080:8080 -v $PWD/graphs:/ors-core/data/graphs -v $PWD/elevation_cache:/ors-core/data/elevation_cache -v $PWD/conf:/ors-conf -v $PWD/planet_-114.516_50.685_7e77eeeb.osm.pbf:/ors-core/data/osm_file.pbf -e "JAVA_OPTS=-Djava.awt.headless=true -server -XX:TargetSurvivorRatio=75 -XX:SurvivorRatio=64 -XX:MaxTenuringThreshold=3 -XX:+UseG1GC -XX:+ScavengeBeforeFullGC -XX:ParallelGCThreads=4 -Xms1g -Xmx2g" -e "CATALINA_OPTS=-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=9001 -Dcom.sun.management.jmxremote.rmi.port=9001 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=localhost" marteze/openrouteservice:latest"""


def initialize_ors_container():
    """
    - https://docs.docker.com/engine/reference/commandline/run/
    - https://docker-py.readthedocs.io/en/stable/containers.html?highlight=containers.run#docker.models.containers.ContainerCollection.run
    - https://giscience.github.io/openrouteservice/installation/Running-with-Docker.html
    
    TODO:
    - fix user configuration
    - automate directory creation
    
    APIError: 500 Server Error for http+docker://localhost/v1.41/containers/ef7f928c3e4c606090463a099dbbc9436c15754673fbed28f6408ce6240f8049/start: Internal Server Error ("unable to find user ${UID}: no matching entries in passwd file")
    """
    container = client.containers.run(
        image='marteze/openrouteservice:latest',
        detach=True,               # -d
        tty=True,                  # -t
        user='${UID}:${GID}',      # -u  Need to assign real user and group id numbers
        name='ors-app2',           # --name
        ports={'8080/tcp': 8080},  # -p
        volumes={                  # -v
            '/Users/kylemcelheran/data_bootcamp_projects/delivery-route-optimization/data/ORS2/graphs': {'bind': '/ors-core/data/graphs',
                            'mode': 'rw'},
            '/Users/kylemcelheran/data_bootcamp_projects/delivery-route-optimization/data/ORS2/elevation_cache': {'bind': '/ors-core/data/elevation_cache',
                                     'mode': 'rw'},
            '/Users/kylemcelheran/data_bootcamp_projects/delivery-route-optimization/data/ORS2/conf': {'bind': '/ors-conf',
                          'mode': 'rw'},
            '/Users/kylemcelheran/data_bootcamp_projects/delivery-route-optimization/data/ORS2/planet_-114.516_50.685_7e77eeeb.osm.pbf': {
                'bind': '/ors-core/data/osm_file.pbf',
                'mode': 'rw'
            }
        },
        environment={              # -e
            'JAVA_OPTS': (
                '-Djava.awt.headless=true -server -XX:TargetSurvivorRatio=75 ' +
                '-XX:SurvivorRatio=64 -XX:MaxTenuringThreshold=3 -XX:+UseG1GC ' +
                '-XX:+ScavengeBeforeFullGC -XX:ParallelGCThreads=4 -Xms1g -Xmx2g'
            ),
            'CATALINA_OPTS': (
                '-Dcom.sun.management.jmxremote ' +
                '-Dcom.sun.management.jmxremote.port=9001 ' +
                '-Dcom.sun.management.jmxremote.rmi.port=9001 ' +
                '-Dcom.sun.management.jmxremote.authenticate=false ' +
                '-Dcom.sun.management.jmxremote.ssl=false ' +
                '-Djava.rmi.server.hostname=localhost'
            )
        }
    )
    
    return container

client = docker.from_env()
container = client.containers.get('ors-app')
container.start()
container.stop()

if __name__ == '__main__':
    pass