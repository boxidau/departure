from graph_driver import GraphDriver
import click

@click.command()
@click.argument('input', type=click.File('r'))
def import_transit(input):
    graph = GraphDriver()
    for line in input:
        graph.add_transit(*line.split(','))

if __name__ == '__main__':
    import_transit()