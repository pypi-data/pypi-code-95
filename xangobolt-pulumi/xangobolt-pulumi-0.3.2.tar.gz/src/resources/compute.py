from pulumi import ResourceOptions
import pulumi_azure_native.compute as compute

def windows_vm(
        stem, 
        props=None, 
        net_int_id=None, 
        provider=None, 
        depends_on=None,
):
    win_vm = compute.VirtualMachine(
        f'vm-{stem}',
        vm_name=f'vm-{stem}',
        location=props.location,
        resource_group_name=props.resource_group_name,
        hardware_profile=compute.HardwareProfileArgs(
            vm_size=props.vm_size
        ),
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[compute.NetworkInterfaceReferenceArgs(
                id=net_int_id,
                primary=True,
            )],
        ),
        os_profile=compute.OSProfileArgs(
            admin_password="{your-password}",
            admin_username="{your-username}",
            computer_name=f'vm-{stem}',
            windows_configuration=compute.WindowsConfigurationArgs(
                enable_automatic_updates=True,
                patch_settings=compute.PatchSettingsArgs(
                    assessment_mode="ImageDefault",
                ),
                provision_vm_agent=True,
            ),
        ),
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                offer="WindowsServer",
                publisher="MicrosoftWindowsServer",
                sku="2019-Datacenter",
                version="latest",
            ),
            os_disk=compute.OSDiskArgs(
                caching="ReadWrite",
                create_option="FromImage",
                managed_disk=compute.ManagedDiskParametersArgs(
                    storage_account_type="Premium_LRS",
                ),
                name=f'osdisk-{stem}',
            ),
        ),
        tags=props.tags,
        opts=ResourceOptions(provider=provider,parent=self, depends_on=depends_on),
    )
    return win_vm



def linux_vm(
        stem, 
        props=None, 
        net_int_id=None, 
        provider=None, 
        depends_on=None,
):
    lin_vm = compute.VirtualMachine(
        f'vm-{stem}',
        vm_name=f'vm-{stem}',
        location=props.location,
        resource_group_name=props.resource_group_name,
        hardware_profile=compute.HardwareProfileArgs(
            vm_size=props.vm_size
        ),
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[compute.NetworkInterfaceReferenceArgs(
                id=net_int_id,
                primary=True,
            )],
        ),
        os_profile=compute.OSProfileArgs(
            admin_password="{your-password}",
            admin_username="{your-username}",
            computer_name=f'vm-{stem}',
            linux_configuration=compute.LinuxConfigurationArgs(
                patch_settings=compute.LinuxPatchSettingsArgs(
                    assessment_mode="ImageDefault",
                ),
            provision_vm_agent=True,
            ),
        ),
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                offer="UbuntuServer",
                publisher="Canonical",
                sku="20.04-LTS",
                version="latest",
        ),
        os_disk=compute.OSDiskArgs(
            caching="ReadWrite",
            create_option="FromImage",
            managed_disk=compute.ManagedDiskParametersArgs(
                storage_account_type="Premium_LRS",
            ),
            name=f'osdisk-{stem}',
        ),
    ),
        tags=props.tags,
        opts=ResourceOptions(provider=provider,parent=self, depends_on=depends_on),
    )
    return lin_vm