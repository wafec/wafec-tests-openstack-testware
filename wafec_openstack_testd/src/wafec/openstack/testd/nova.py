from novaclient import client

from .base import DriverBase, StateBase, ObserverBase, WaitState
from .exceptions import NotFoundException, StateMismatchException

_DEFAULT_VERSION = '2'


class NovaDriver(DriverBase):
    def __init__(self, session, glance_driver, neutron_driver, version=_DEFAULT_VERSION):
        DriverBase.__init__(self)
        self.session = session
        self.version = version
        self.client = client.Client(self.version, self.session)
        self.glance_driver = glance_driver
        self.neutron_driver = neutron_driver

    def server_create(self, server_name, flavor_name, image_name, network_name):
        image = self.glance_driver.image_get(image_name)
        flavor = self.flavor_get(flavor_name)
        network = self.neutron_driver.network_get(network_name)
        server = self.client.servers.create(
            name=server_name,
            image=image.id,
            flavor=flavor.id,
            network=network.id
        )
        return server

    def server_get(self, server_name):
        servers = self.client.servers.list(search_opts={'name': server_name})
        if servers:
            server = servers[0]
            return server
        else:
            raise NotFoundException()

    def server_list(self, name=None):
        search_opts = {}
        if name:
            search_opts['name'] = name
        servers = self.client.servers.list(search_opts=search_opts)
        return servers

    def server_delete(self, server_name):
        server = self.server_get(server_name)
        server.delete()

    def flavor_get(self, flavor_name):
        flavors = self.client.flavors.list(search_opts={'name': flavor_name})
        if flavors:
            flavor = flavors[0]
            return flavor
        else:
            raise NotFoundException()


class ServerState(StateBase):
    def __init__(self):
        StateBase.__init__(self)
        self.status = None
        self.task_state = None
        self.vm_state = None
        self.power_state = None

    @property
    def state_props(self):
        return ['status', 'task_state', 'vm_state', 'power_state']

    @staticmethod
    def of(status, task_state, vm_state, power_state):
        inst = ServerState()
        inst.status = status
        inst.task_state = task_state
        inst.vm_state = vm_state
        inst.power_state = power_state
        return inst

    @staticmethod
    def from_server(server):
        if server is None:
            raise ValueError('server is None')
        return ServerState.of(
            server.status,
            getattr(server, 'OS-EXT-STS:task_state'),
            getattr(server, 'OS-EXT-STS:vm_state'),
            str(getattr(server, 'OS-EXT-STS:power_state'))
        )


class NovaObserver(ObserverBase):
    def __init__(self, nova_driver):
        ObserverBase.__init__(self)
        self.nova_driver = nova_driver

    def server_observe(self, server_name, states):
        states_index = 0
        if not states:
            raise ValueError('states is empty')

        def supplier():
            server = self.nova_driver.server_get(server_name)
            return server

        def condition(server):
            nonlocal states_index
            state = states[states_index]
            server_state = ServerState.from_server(server)
            if server_state.compare_with(state):
                states_index += 1
            if states_index >= len(states):
                return True
            return False

        result = WaitState.wait_while(condition, supplier, 60000)
        if not result:
            raise StateMismatchException()
