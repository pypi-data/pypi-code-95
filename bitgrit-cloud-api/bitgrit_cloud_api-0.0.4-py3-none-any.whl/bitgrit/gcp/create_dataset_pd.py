import os
import time
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def create_gcp_connection():
    # Use JSON file or default credentials
    # credentials = GoogleCredentials.from_stream("serviceAccount.json")
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('compute', 'v1', credentials=credentials)


def create_disk(service, disk_project, disk_zone, disk_name, disk_size_gb):
    create_disk_body = {
        "name": disk_name,
        "sizeGb": disk_size_gb
    }
    request = service.disks().insert(project=disk_project,
                                     zone=disk_zone, body=create_disk_body)
    request.execute()


def wait_disk_ready_status(service, disk_project, disk_zone, disk_name):
    request = service.disks().get(
        project=disk_project,
        zone=disk_zone,
        disk=disk_name)
    response = request.execute()
    while response["status"] != "READY":
        request = service.disks().get(
            project=disk_project,
            zone=disk_zone,
            disk=disk_name)
        response = request.execute()
        while response["status"] != "READY":
            request = service.disks().get(
                project=disk_project,
                zone=disk_zone,
                disk=disk_name)
            response = request.execute()


def attach_disk(service, vm_project, vm_zone, vm_name,
                disk_project, disk_zone, disk_name):

    attached_disk_body = {
        "source": "https://www.googleapis.com/compute/v1/projects/" +
                  disk_project +
                  "/zones/" +
                  disk_zone +
                  "/disks/" +
                  disk_name,
        "deviceName": disk_name
    }

    request = service.instances().attachDisk(
        project=vm_project,
        zone=vm_zone,
        instance=vm_name,
        body=attached_disk_body)
    request.execute()


def wait_attached_disk_path(vm_all_disks_path, vm_disk_name):
    attached_disks_list = os.popen("sudo ls "+vm_all_disks_path).read()
    while vm_disk_name not in attached_disks_list:
        attached_disks_list = os.popen("sudo ls "+vm_all_disks_path).read()


def detach_disk(service, vm_project, vm_zone, vm_name, disk_name):
    request = service.instances().detachDisk(
        project=vm_project,
        zone=vm_zone,
        instance=vm_name,
        deviceName=disk_name)
    request.execute()


def delete_disk(service, disk_project, disk_zone, disk_name):
    request = service.disks().delete(project=disk_project,
                                     zone=disk_zone, disk=disk_name)
    request.execute()


if __name__ == "__main__":

    disk_project = "bitgrit-competition-platform"
    disk_zone = "us-east1-b"
    disk_name = "disk-first-dataset"
    disk_size_gb = "1"

    vm_project = "bitgrit-competition-platform"
    vm_zone = "us-east1-b"
    vm_name = "test-competition"
    vm_all_disks_path = "/dev/disk/by-id"
    vm_disk_name = "scsi-0Google_PersistentDisk_"+disk_name
    vm_disk_path = vm_all_disks_path+"/"+vm_disk_name

    vm_mount_disk_path = "/mnt/disk-data"
    vm_dataset_path = "/home/avelichk/test.txt"

    # Create connection to GCP
    service = create_gcp_connection()
    print("Connected to GCP resources")

    # Create Persistent Disk
    create_disk(
        service=service,
        disk_project=disk_project,
        disk_zone=disk_zone,
        disk_name=disk_name,
        disk_size_gb=disk_size_gb)
    print("Disk {} was created\n".format(disk_name))

    # Wait for READY status for the Disk
    print("Wait for READY disk status")
    wait_disk_ready_status(
        service=service,
        disk_project=disk_project,
        disk_zone=disk_zone,
        disk_name=disk_name)
    print("Disk status is READY")

    # Attach disk to the VM
    attach_disk(
        service=service,
        vm_project=vm_project,
        vm_zone=vm_zone,
        vm_name=vm_name,
        disk_project=disk_project,
        disk_zone=disk_zone,
        disk_name=disk_name)
    print("Disk {} was attached".format(disk_name))

    # Wait for attached path in the VM
    wait_attached_disk_path(
        vm_all_disks_path=vm_all_disks_path,
        vm_disk_name=vm_disk_name)
    print("Disk path was created {}".format(vm_disk_path))

    # Create mount folder
    os.system("sudo mkdir "+vm_mount_disk_path)
    print("Mount folder was created")

    # Format the disk with ext4 filesystem. It will delete all data on the disk
    os.system(
        "sudo mkfs.ext4 -F -E " +
        "lazy_itable_init=0,lazy_journal_init=0,discard " +
        vm_disk_path)
    print("Disk was formatted")

    # Mount disk to the VM mount path
    os.system("sudo mount -o discard,defaults " +
              vm_disk_path+" "+vm_mount_disk_path)
    print("Disk is mounted")

    # Copy dataset to the instance
    os.system("sudo cp "+vm_dataset_path+" "+vm_mount_disk_path)
    print("Dataset is copied")

    # Unmount disk
    os.system("sudo umount "+vm_disk_path)
    print("Disk {} is unmounted".format(disk_name))

    # Delete mount directory
    os.system("sudo rm -rf "+vm_mount_disk_path)
    print("Mount dir is deleted")

    # Detach disk from the VM
    detach_disk(service=service, vm_project=vm_project,
                vm_zone=vm_zone, vm_name=vm_name, disk_name=disk_name)
    print("Disk {} was detached".format(disk_name))
