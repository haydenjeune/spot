from subprocess import call
from pathlib import Path

import boto3
from tabulate import tabulate

from spot.launch_config import LaunchConfig


def get_name_from_instance(instance):
    """Extract the Name of an instance given it's boto3 Instance object"""
    tags = instance.tags
    # What a strange way for boto to return tags, surely a single dict would do?
    if tags is not None:
        for tag in tags:
            if tag['Key'] == "Name":
                return tag['Value']
    return None


class SpotManager(object):
    """A class to encapsulate the logic for managing spot instances."""
    def __init__(self, profile_name, region):
        self.session = boto3.session.Session(profile_name=profile_name, region_name=region)
        self.ec2 = self.session.resource("ec2", region_name=region)

        # Maps for displaying instance information
        self.attr_maps = MapCollection()
        self.attr_maps.add(AttributeMap('ID', lambda i: i.instance_id))
        self.attr_maps.add(AttributeMap('Name', get_name_from_instance))
        self.attr_maps.add(AttributeMap('Type', lambda i: i.instance_type))
        self.attr_maps.add(AttributeMap('State', lambda i: i.state["Name"]))
        self.attr_maps.add(AttributeMap('Avail. Zone', lambda i: i.placement['AvailabilityZone']))
        self.attr_maps.add(AttributeMap('Public DNS', lambda i: i.public_dns_name))
        self.attr_maps.add(AttributeMap('Public IP', lambda i: i.public_ip_address))
        self.attr_maps.add(AttributeMap('AMI ID', lambda i: i.image_id))
        self.attr_maps.add(AttributeMap('Spot Instance', lambda i: i.spot_instance_request_id is not None))

    def launch(self, path):
        """Launches a spot instance based on the config yaml file at the given path."""
        cfg = LaunchConfig(path)

        # If no AZ has been specified, place in the cheapest AZ
        cheapest = self._find_cheapest_AZ(cfg.get('InstanceType'))
        if cfg.is_not_defined("Placement"):
            print(f"No AZ specified. {cheapest['AvailabilityZone']} at ${cheapest['SpotPrice']} chosen.")
            cfg.add(Placement={'AvailabilityZone': cheapest['AvailabilityZone']})


        print(f"Launching {cfg.get('InstanceType')} in {cfg.get('Placement')['AvailabilityZone']}")
        self.ec2.create_instances(**cfg.kwargs())

    def list(self):
        """Lists all running instances in the default region."""
        instances = self.ec2.instances.all()
        instance_data = [self.attr_maps.evaluate(i) for i in instances]
        headers = self.attr_maps.names()
        print(tabulate(instance_data, headers=headers))

    def terminate(self, instance_id):
        """Terminates an instance with the given instance_id."""
        instance = self.ec2.Instance(instance_id)
        instance.terminate()

    def ssh(self, instance_id, user):
        """Opens a ssh session into the instance with the given instance id"""
        instance = self.ec2.Instance(instance_id)

        # Base ssh command
        ssh_command = ["ssh", f"{user}@{instance.public_ip_address}"]

        # Add private key if needed
        key_name = instance.key_name
        if key_name is not None:
            key_location = Path.home() / ".ssh" / (key_name + ".pem")
            if not key_location.exists():
                raise RuntimeError(f"No private key exists at {str(key_location)}")
            ssh_command.extend(["-i", str(key_location)])

        call(ssh_command)

    def _find_cheapest_AZ(self, instance_type):
        """Finds the cheapest AZ in the default region for the specified type of spot instance."""
        client = self.session.client('ec2')

        # Count number of AZs in region to determine how many records to request
        az = client.describe_availability_zones()
        az_count = len(az['AvailabilityZones'])

        # Request most recent price for all AZs
        response = client.describe_spot_price_history(InstanceTypes=[instance_type], MaxResults=az_count,
                                                        ProductDescriptions=['Linux/UNIX (Amazon VPC)'])
        price_dict = {}
        for zone_price in response['SpotPriceHistory']:
            price_dict[zone_price['AvailabilityZone']] = zone_price['SpotPrice']

        # Return name and price of cheapest AZ
        cheapest = {}
        cheapest['AvailabilityZone'], cheapest['SpotPrice'] = min(price_dict.items(), key=lambda x: x[1])

        return cheapest


class AttributeMap(object):
    """A map representing the output of a function when applied to a given object.

    This is used for extracting information from instance objects for listing.
    """
    def __init__(self, name, map_func):
        self.name = name
        self.map_func = map_func

    def __call__(self, instance):
        return self.map_func(instance)


class MapCollection(object):
    """A collection of AttributeMaps with methods for returning all names and evaluating maps in the collection"""
    def __init__(self):
        self.maps = []

    def add(self, map):
        self.maps.append(map)

    def names(self):
        return [map.name for map in self.maps]

    def evaluate(self, object):
        return [map(object) for map in self.maps]


if __name__ == "__main__":
    manager = SpotManager('spot')
    manager.list()
    print(manager._find_cheapest_AZ('p2.xlarge'))
    manager.launch('gpu.yaml')
    manager.list()
