#!/usr/bin/env python
import docker

from systemd.log.Logger import Logger


class Docker:
    dockerClient = docker.from_env()
    logger = Logger.getLogger(__name__)

    def runContainer(self, runParams):
        if runParams.image is None:
            raise ValueError("Could not start docker container! Docker image is empty!")

        if (runParams.network is None
                or runParams.network not in ['bridge', 'none', 'container', 'host']):
            runParams.network = "bridge"

        preparedVolumes = self.__prepareContainerVolumes(runParams.volumes)

        self.logger.debug(
            "Prepare to run new container with image: <<%s>>, cmd:<<%s>>, network:<<%s>>, volumes:<<%s>>",
            runParams.image,
            runParams.cmd,
            runParams.network,
            preparedVolumes
        )
        dockerContainer = self.dockerClient.containers.run(
            image=runParams.image,
            command=runParams.cmd,
            detach=True,
            auto_remove=True,
            privileged=runParams.privileged,
            network_mode=runParams.network,
            volumes=preparedVolumes
        )
        self.logger.debug("Successfully run new docker container with id: <<%s>>: ", dockerContainer.short_id)

        return dockerContainer

    def __prepareContainerVolumes(self, volumes):
        if volumes is None:
            return {}

        preparedVolumes = {}

        for volume in volumes:
            volumeItemsList = volume.split(':')

            if len(volumeItemsList) < 2:
                self.logger.error(
                    "Passed volume: <<%s>> is not correct and will be skipped! Only format: <path>:<path> or <path>:<path>:<mode>(default mode: rw)" % volume
                )
                continue

            volumeMountMode = 'rw'

            if len(volumeItemsList) == 3:
                volumeMountMode = volumeItemsList[2]

            preparedVolumes[volumeItemsList[0]] = {'bind': volumeItemsList[1], 'mode': volumeMountMode}

        return preparedVolumes

    def stopContainer(self, dockerContainer):
        if dockerContainer is None:
            raise ValueError("Could not stop docker container! Container identifier is empty!")

        dockerContainer.stop()

        self.logger.debug("Successfully stopped container with id: <<%s>>", dockerContainer.short_id)

    def copyDataToContainer(self, dockerContainer, dataOriginalPath, dataContainerPath):
        if dockerContainer is None:
            raise ValueError("Could not copy data to container! Container is empty!")
        elif dataOriginalPath is None:
            self.logger.debug("Archive data path is not present. Skipping step")

            return
        elif (dataOriginalPath is not None
                and dataContainerPath is None):
            raise ValueError("Could not copy data to container! Data container path is emtpy!")

        self.logger.debug(
            "Preparing to copy data from host path: <<%s>> to docker container path: <<%s>>",
            dataOriginalPath,
            dataContainerPath
        )

        with open(dataOriginalPath, 'r') as dataStream:
            # put_archive() required exists folder so create before
            self.executeCommand(dockerContainer, ["mkdir -p %s" % dataContainerPath])

            dockerContainer.put_archive(
                path=dataContainerPath,
                data=dataStream
            )

        self.logger.debug("Data archive successfully copied to docker container")

    def executeCommand(self, dockerContainer, shellCommandsList):
        if shellCommandsList is None:
            raise ValueError("Could not execute shell command! Command list is empty!")

        for shellCommand in shellCommandsList:
            exitCode, stdout = dockerContainer.exec_run(shellCommand)

            if (0 == exitCode
                    and len(stdout.decode('utf-8')) < 1):
                continue

            if (0 == exitCode):
                self.logger.debug(stdout.decode('utf-8'))
            else:
                raise Exception(stdout.decode('utf-8'))