import boto3
from spot.launch_config import LaunchConfig
from tabulate import tabulate


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
    def __init__(self, profile_name):
        session = boto3.session.Session(profile_name=profile_name)
        self.ec2 = session.resource("ec2")

        # Maps for displaying instance information
        self.attr_maps = MapCollection()
        self.attr_maps.add(AttributeMap('ID', lambda i: i.instance_id))
        self.attr_maps.add(AttributeMap('Name', lambda i: get_name(i.tags)))
        self.attr_maps.add(AttributeMap('Type', lambda i: i.instance_type))
        self.attr_maps.add(AttributeMap('State', lambda i: i.state["Name"]))
        self.attr_maps.add(AttributeMap('Public DNS', lambda i: i.public_dns_name))
        self.attr_maps.add(AttributeMap('Public IP', lambda i: i.public_ip_address))
        self.attr_maps.add(AttributeMap('AMI ID', lambda i: i.image_id))
        self.attr_maps.add(AttributeMap('Spot Instance', lambda i: i.spot_instance_request_id is not None))

    def launch(self, path):
        """Launches a spot instance based on the config yaml file at the given path."""
        cfg = LaunchConfig(path)
        print(cfg.kwargs())
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
    manager.launch("gpu.yaml")
    manager.list()
