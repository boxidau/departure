import arrow

# all of this logic sucks
# do not use it for anything EVER
# it's horrifically inefficient and makes a shit tonne of assumptions

class Route:

    # if you're waiting at a location for more than 20 mins your route sucks
    MAX_LOCATION_WAIT = 20*60

    def __init__(self, path):
        # convert all the nodes to location RouteSteps
        location_map = {n.id: RouteStep(n) for n in path.nodes}
        route_steps = []

        for (idx, edge) in enumerate(path):
            if idx == 0:
                # add the origin for the first edge
                route_steps.append(location_map[edge.start])
            route_steps.append(RouteStep(edge))
            route_steps.append(location_map[edge.end])
            idx += 1

        self.route_steps = Route.__generate_details(route_steps)
        if self.is_missed():
            # increment all the dates by a day
            for step in self.route_steps:
                step.make_tomorrow()


    @classmethod
    def validate_route_timing(cls, route):
        for (idx, route_step) in enumerate(route.route_steps):
            if route_step.type == 'location':
                if route_step.duration >= Route.MAX_LOCATION_WAIT:
                    return False
            else:
                if idx - 2 >= 0:
                    previous_transit = route.route_steps[idx - 2]
                    if previous_transit.arrival_time > \
                            route_step.departure_time:
                        return False
        return True

    def is_missed(self):
        now = arrow.now(tz='US/Pacific')
        for step in self.route_steps:
            if step.type != 'location':
                if step.departure_time < now:
                    return True
        return False

    @classmethod
    def validate_route_steps(cls, route_steps):
        for idx, step in enumerate(route_steps):
            # turns out I should have combined
            # the locations and transits after processing
            # but too late now, cbf fixing this so therefore
            # a route should always have odd steps as transits
            # even steps are locations
            #      0         1          2          3          4
            # (location)-[transit]->(location)-[transit]->(location)
            # check even steps
            if idx % 2 == 0 and step.type != 'location':
                raise AssertionError(
                    'Route is invalid, location found at an odd index')

        # make sure last step is a location, first is checked above
        if route_steps[-1].type != 'location':
            raise AssertionError('Route is invalid, doesn\'t end in a location')


    @classmethod
    def __generate_details(cls, route_steps):
        Route.validate_route_steps(route_steps)
        # we know it's a valid route now
        # iterate through the route and create departure/arrival times
        # for untimed transits

        backtrack_done = False
        for (idx, step) in enumerate(route_steps):
            # find first timed leg
            if not backtrack_done and step.departure_time:
                # first timed leg found
                # work backwards setting concrete times on untimed transits
                dep_time = step.departure_time
                for prev_idx in list(range(idx-2, 0, -2)):
                    route_steps[prev_idx].set_times_align_next_departure(
                        dep_time)
                    dep_time = route_steps[prev_idx].departure_time
                backtrack_done = True
                continue

            if step.type != 'location' \
                    and not step.departure_time \
                    and (idx - 2 >= 0):
                # use the previous transit times and align on arrival
                step.set_times_align_previous_arrival(
                    route_steps[idx-2].arrival_time)

        # all transits are calculated
        # now calculate location (wait) times
        for (idx, step) in enumerate(route_steps):
            if step.type == 'location':
                if idx-1 > 0:
                    # for a location arrival and departure are swapped
                    # because my logic for this whole thing is kinda fucked
                    step.set_arrival(route_steps[idx-1].arrival_time)
                try:
                    step.set_departure(route_steps[idx+1].departure_time)
                except IndexError:
                    # last location, no steps after this
                    pass
        return route_steps

    @property
    def total_duration(self):
        return int((self.route_steps[-2].arrival_time
                    - self.route_steps[1].departure_time).total_seconds())

    def __str__(self):
        return "<Route steps=[{}]>".format(
            ', '.join([step.__str__() for step in self.route_steps]))

    def to_dict(self):
        return {
            "total_duration": self.total_duration,
            "steps": [route_step.to_dict() for route_step in self.route_steps]
        }

class RouteStep:
    allowed_types = ['walk', 'train', 'shuttle', 'location']

    def __init__(self, node):
        self.type = None
        self.properties = node.properties

        # edge (transit)
        if hasattr(node, 'type'):
            self.type = node.type.lower()

        # node (location)
        if hasattr(node, 'labels'):
            # can't get label by index from a set
            # don't want to pop,,, but maybe
            for label in node.labels:
                if label.lower() == 'location':
                    self.type = label.lower()
                break

        if self.type not in RouteStep.allowed_types:
            raise TypeError('Unknown route step type {}'.format(self.type))

    # takes a time string like 8:55
    # converts to an arrow representing TODAY at that time
    @classmethod
    def _string_to_time(cls, time_str):
        now = arrow.now(tz='US/Pacific')
        time_str_parts = time_str.split(':')
        return now.replace(
            microsecond=0,
            second=0,
            hour=int(time_str_parts[0]),
            minute=int(time_str_parts[1]),
        )

    # increment all the dates by 1 day
    # arrow should probably handle DST changes but I haven't checked
    def make_tomorrow(self):
        if 'departure_time' in self.properties:
            self.properties['departure_time'] = self.departure_time.shift(days=1)
        if 'arrival_time' in self.properties:
            self.properties['arrival_time'] = self.arrival_time.shift(days=1)


    @property
    def departure_time(self):
        try:
            departure_time = self.properties['departure_time']
            if type(departure_time) == str:
                return RouteStep._string_to_time(
                    self.properties['departure_time'])
            else:
                return departure_time
        except KeyError:
            return None

    @property
    def arrival_time(self):
        try:
            arrival_time = self.properties['arrival_time']
            if type(arrival_time) == str:
                return RouteStep._string_to_time(
                    self.properties['arrival_time'])
            else:
                return arrival_time
        except KeyError:
            return None

    @property
    def duration(self):
        try:
            return abs(
                int((self.arrival_time-self.departure_time).total_seconds()))
        except TypeError:
            return 0

    def set_arrival(self, arrival):
        self.properties['arrival_time'] = arrival

    def set_departure(self, departure):
        self.properties['departure_time'] = departure

    def set_times_align_next_departure(self, next_departure):
        self.properties['arrival_time'] = next_departure
        self.properties['departure_time'] = next_departure.shift(
            seconds=-self.properties['duration'])

    def set_times_align_previous_arrival(self, previous_arrival):
        self.properties['departure_time'] = previous_arrival
        self.properties['arrival_time'] = previous_arrival.shift(
            seconds=self.properties['duration'])
        pass

    def __str__(self):
        return "<{} properties={}>".format(
            self.type.title(), repr(self.properties))

    def to_dict(self):
        output = {
            "type": self.type,
        }
        if self.type == 'location':
            output['name'] = self.properties['name']
            output['latitude'] = self.properties['latitude']
            output['longitude'] = self.properties['longitude']

        output['departure_time'] = self.departure_time.isoformat() \
            if self.departure_time else None
        output['arrival_time'] = self.arrival_time.isoformat() \
            if self.arrival_time else None
        output['duration'] = self.duration
        return output
