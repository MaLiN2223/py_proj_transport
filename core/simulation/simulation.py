import time

from core.data_structures import Graph
from core.simulation.bus import Bus
from core.simulation.stop import Stop
from core.simulation.generators import BusGenerator
from core.simulation.line import LineStop, Line
from core.simulation.status_printer import StatusPrinter


class Simulation:
    def __init__(self, config):
        """Read configuration and do sth with it"""
        self.finished = False
        self.steps = -1
        self.buses = []
        self.lines = []
        self.stops = {}
        self.bus_generator = BusGenerator()
        self.printer = StatusPrinter()

        self.__create_stops(config.stops)
        self.graph = Graph.from_config(config.graph_dict)
        """
             A - 1 - B - 2 - C - 1 - D
             |       |
             1       5
             |       |
             E - 1 - F
        """
        self.__create_lines(config.lines_dict)

    def mainloop(self):
        while not self.finished:
            self._update()
            self.__print()
            time.sleep(0.1)

    def __print(self):
        if self.steps >= 1:
            print('________________________________________________________')
            print('STEP ', self.steps)
            for bus in self.buses:
                print('Bus{ id:', bus.id, 'line:', bus.line.number, 'route:', bus.route, 'last stop:',
                      bus.current_stop_name,
                      ' next stop:', bus.next_stop_name, 'time to next:', bus.time_to_next_stop)

    def _update(self):
        self.steps += 1
        self.__update_buses()
        self.__clean_buses()
        self.__generate_buses()

    def __update_buses(self):
        for bus in self.buses:
            bus.move()

    def __update_passengers(self):
        for bus in self.buses:
            if bus.ticks_to_next_stop == 0:
                self.__transfer_out(self.stops[bus.current_stop_name], bus)
                self.__transfer_between(self.stops[bus.current_stop_name], bus)
                self.__transfer_in(self.stops[bus.current_stop_name], bus)

    def __transfer_out(self, stop, bus):
        for bus_group in bus.passengers:  # wysiadanie
            if bus_group.destination == stop.name:
                bus.passengers.remove(bus_group)
                break

    def __transfer_in(self, stop, bus):
        for stop_group in stop.passengers:  # wsiadanie
            dest = stop_group.destination
            if self.graph.get_path_between(stop.name, dest)[0] == bus.next_stop_name:
                for i in range(len(bus.passengers)):
                    if bus.passengers[i].destination == dest:
                        bus.passengers[i] += stop_group
                        break
                if i == len(bus.passengers):
                    bus.passengers.append(stop_group)

    def __transfer_between(self, stop, bus):
        for bus_group in bus.passengers:  # przesiadanie
            pass  # TODO

    def __generate_buses(self):
        for line in self.lines:
            new_buses = line.tick()
            for i in range(len(new_buses)):
                if new_buses[i]:
                    self.buses.append(Bus(line, i))

    def __clean_buses(self):
        q = [bus for bus in self.buses if bus.current_stop == bus.line.last_stop(bus.route)]
        for b in q:
            self.buses.remove(b)

    def __create_lines(self, lines):
        for line in lines.values():
            route1, route2 = [], []
            curr_route = line['route1']
            for i in range(len(curr_route)):
                route1.append(LineStop(curr_route[i],
                                       self.graph[curr_route[i], curr_route[i + 1]] if i < len(curr_route) - 1 else 0))

            curr_route = line['route2']
            for i in range(len(curr_route)):
                route2.append(LineStop(curr_route[i],
                                       self.graph[curr_route[i], curr_route[i + 1]] if i < len(curr_route) - 1 else 0))

            self.lines.append(Line(line, route1, route2))

    def __create_stops(self, stops):
        self.stops = {stop_name: Stop(stop_name) for stop_name in stops}
