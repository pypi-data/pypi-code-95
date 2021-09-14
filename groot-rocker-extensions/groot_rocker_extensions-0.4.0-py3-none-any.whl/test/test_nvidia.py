#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#

##############################################################################
# Imports
##############################################################################

import getpass
import io
import os
import pathlib
import pwd

import docker

import groot_rocker
import groot_rocker.console as console

from . import utilities

##############################################################################
# Methods
##############################################################################


def remove_image(name: str):
    docker_client = groot_rocker.core.get_docker_client()
    docker_client.remove_image(image=name)

##############################################################################
# Tests
##############################################################################


class Nvidia(utilities.ExtensionTestCase):
    """
    By default, this test cleans up images and containers so that the user
    does not have to deal with dangling images (inadvertantly that also
    means that it's not caching between runs, but will make use of cached
    images in a single run).

    To debug via images, comment out the relevant explicit docker_client.remove_image
    command in remove_image() or instead, comment them individually below.
    """

    @classmethod
    def setUpClass(self):
        client = groot_rocker.core.get_docker_client()
        self.dockerfile_tags = []
        for distro_version in ['18.04', '20.04']:
            dockerfile = (
                f"FROM ubuntu:{distro_version}\n"
                "RUN apt-get update && apt-get install glmark2 -y && apt-get clean\n"
                "CMD glmark2 --validate\n"
            )
            dockerfile_tag = "groot:" + f"test_nvidia_{distro_version}"
            iof = io.BytesIO((dockerfile % locals()).encode())
            image_id = client.build(fileobj=iof, tag=dockerfile_tag, forcerm=True)
            for unused_e in image_id:
                pass
            self.dockerfile_tags.append(dockerfile_tag)

    @classmethod
    def tearDownClass(self):
        # For quick debugging, comment out this method
        for image_name in self.dockerfile_tags:
            print(f"Image Name: {image_name}")
            # If the os detector images were made
            print(f"Teardown {image_name}")
            remove_image(name=image_name)
        try:
            remove_image("groot:os_detect_builder")
        except docker.errors.ImageNotFound:
            # some test methods do not build the os_detect_builder, that's ok
            pass

    def test_glmark2_validate_nvidia_not_enabled(self):
        for tag in self.dockerfile_tags:
            docker_tag = "groot:test_no_glmark2"
            dig = groot_rocker.core.DockerImageGenerator(
                active_extensions=[],
                cliargs={},
                base_image=tag
            )
            result = dig.build(image_name=docker_tag)
            utilities.assert_details(text="No Nvidia GLMark2 Build Result", expected=0, result=result)
            self.assertEqual(result, 0)
            result = dig.run()
            utilities.assert_details(text="No Nvidia GLMark2 Run Result", expected=1, result=result)
            self.assertEqual(result, 1)
            remove_image(name=docker_tag)

    def test_glmark2_validate_nvidia_enabled(self):
        extensions = groot_rocker.core.list_plugins()
        desired_extensions = ['nvidia', 'user']
        active_extensions = [e() for e in extensions.values() if e.get_name() in desired_extensions]
        for tag in self.dockerfile_tags:
            docker_tag = "groot:test_glmark2"
            dig = groot_rocker.core.DockerImageGenerator(
                active_extensions=active_extensions,
                cliargs={},
                base_image=tag
            )
            result = dig.build(image_name=docker_tag)
            utilities.assert_details(text="Nvidia GLMark2 Build Result", expected=0, result=result)
            self.assertEqual(result, 0)
            result = dig.run()
            utilities.assert_details(text="Nvidia GLMark2 Run Result", expected=0, result=result)
            self.assertEqual(result, 0)
            remove_image(name=docker_tag)

    def test_base_image_does_not_exist(self):
        mock_cli_args = {'base_image': 'ros:does-not-exist'}
        print(console.green + f"Checking base image '{mock_cli_args['base_image']}'" + console.reset)
        with self.assertRaises(SystemExit) as cm:
            self.extension.get_environment_subs(mock_cli_args)
        self.assertEqual(cm.exception.code, 1)
        utilities.assert_details(text="Base image does not exist", expected="SystemExit", result="SystemExit")

    def test_unsupported_base_image_version(self):
        mock_cli_args = {'base_image': 'ubuntu:17.04'}
        print(console.green + f"Checking base image '{mock_cli_args['base_image']}'" + console.reset)
        with self.assertRaises(SystemExit) as cm:
            self.extension.get_environment_subs(mock_cli_args)
        self.assertEqual(cm.exception.code, 1)
        utilities.assert_details(text="Unsupported Version", expected="SystemExit", result="SystemExit")
        remove_image("groot:os_detect_" + mock_cli_args['base_image'].replace(":", "_"))

    def test_unsupported_base_image_os(self):
        mock_cli_args = {'base_image': 'fedora'}
        print(console.green + f"Checking base image '{mock_cli_args['base_image']}'" + console.reset)
        with self.assertRaises(SystemExit) as cm:
            self.extension.get_environment_subs(mock_cli_args)
        self.assertEqual(cm.exception.code, 1)
        utilities.assert_details(text="Unsupported OS", expected="SystemExit", result="SystemExit")
        remove_image("groot:os_detect_" + mock_cli_args['base_image'].replace(":", "_"))
