#!/usr/bin/env python

import argparse
import traceback

from systemd.docker.Docker import Docker
from systemd.log.Logger import Logger


class App:
    logger = Logger.getLogger(__name__)

    def prepareArgumentParser(self):
        argParser = argparse.ArgumentParser()
        argParser.add_argument(
            '--image',
            required=True,
            help='Docker image name'
        )
        argParser.add_argument(
            '--network',
            help='Docker network type'
        )
        argParser.add_argument(
            '--volumes',
            nargs = '+',
            help='Docker container volumes'
        )
        argParser.add_argument(
            '--cmd',
            help='Docker container cmd. If not present default Dockerfile CMD will be used'
        )
        argParser.add_argument(
            '--data-archive',
            help='The path from *.tar archive will be read'
        )
        argParser.add_argument(
            '--data-unarchive-path',
            help='The path were *.tar archive will be placed and unarchived in the docker container'
        )
        argParser.add_argument(
            '--privileged',
            action="store_true",
            default=False,
            help='If present docker image will be run with root privileged'
        )
        argParser.add_argument(
            '--exec-commands',
            required=True,
            nargs = '+',
            help='List of commands that will be executed in the docker container'
        )
        return argParser

    def run(self, params):
        container = None

        try:
            docker = Docker()
            container = docker.runContainer(params)
            docker.copyDataToContainer(
                container,
                params.data_archive,
                params.data_unarchive_path
            )
            docker.executeCommand(container, params.exec_commands)
        finally:
            try:
                docker.stopContainer(container)
            except:
                # Ignore because we just try to stop the container
                pass

if __name__ == '__main__':
    logger = Logger.getLogger(__name__)

    try:
        app = App()
        args = app.prepareArgumentParser().parse_args()

        logger.debug("Run app with arguments: %s" % args)

        app.run(args)
    except Exception as exception:
        logger.error("Fatal error occurred! Reason: %s!", exception)

        traceback.print_exc()

        exit(1)