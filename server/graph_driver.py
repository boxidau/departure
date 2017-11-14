from neo4j.v1 import GraphDatabase, basic_auth
from router import Route, RouteStep

class GraphDriver:
    def __init__(self,
                 graph_user,
                 graph_password,
                 graph_host):
        self.db_driver = GraphDatabase.driver(
            "bolt://{}".format(graph_host),
            auth=basic_auth(
                graph_user,
                graph_password,
            )
        )

    def _get_session(self):
        return self.db_driver.session()


    def get_all_routes(self, origin, destination):
        with self._get_session() as session:
            results = session.run(
                "MATCH (origin:Location { name: {origin} }), "
	            "(destination:Location { name: {destination} }), "
                "p = (origin)-[*]->(destination)"
                "RETURN p",
                parameters={
                    'origin': origin,
                    'destination': destination
                })

            return filter(
                Route.validate_route_timing,
                [Route(path.values()[0]) for path in results]
            )

    def add_transit(self,
                    origin_name,
                    destination_name,
                    transit_type,
                    departure_time,
                    arrival_time,
                    name):
        with self._get_session() as session:
            # unable to properly parameterize the transit type
            if transit_type not in RouteStep.allowed_types:
                print('Invalid transit_type')
            return session.run(
                "MATCH (origin:Location { name: {origin_name} }), "
                "(destination:Location { name: {destination_name} }) \n"
                "CREATE (origin)-[:%s {"
                "   departure_time: {departure_time},"
                "   arrival_time: {arrival_time},"
                "   name: {name}"
                "}]->(destination)" % transit_type,
                parameters={
                    'origin_name': origin_name,
                    'destination_name': destination_name,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'name': name,
                }
            )
