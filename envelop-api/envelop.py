#!/usr/bin/python
# -*- coding: utf-8 -*-

# Used to calculate the 'envelop' (the isochrone) given a maximum amount of time, a mean of transportation
# and a starting point with the map of Shanghai
# IMPORTANT : This code is not functional, it was based on function drawIsochrones from policosm package
# But the way to calculate trapezoid from a map in France and from a map in China is probably different
# which is why the function doesn't work

import os, sys

from descartes import PolygonPatch
from shapely.geometry import Point
from shapely.ops import cascaded_union
import math
import matplotlib.pyplot as plt
import colorlover as cl

from policosm.extractors.roadsGraph import *
import policosm.geoNetworks as pocogeo
from policosm.functions import *
from policosm.functions.getRtree import *
from policosm.geoFunctions.getEPSG import *

colors = [ (r/255,v/255,b/255) for r,v,b in cl.to_numeric(cl.scales['9']['seq']['Purples'])]
colors2 = [ (r/255,v/255,b/255) for r,v,b in cl.to_numeric(cl.scales['9']['seq']['Oranges'])]

fig = plt.figure()
ax = fig.add_subplot(111)

_SHANGHAI_MAP = 'data/shanghai_china.osm.gexf'
_BICYCLE_SPEED = 10.0
_SLOWEST_HUMAN_SPEED = 3000 / 1440  # "3km/h expressed in m/s"


def draw_circles(graph, tree, cutoff, polygons):
    for k, v in tree[0].iteritems():
        x, y = graph.node[k]['longitude'], graph.node[k]['latitude']
        circleRadius = _SLOWEST_HUMAN_SPEED * (cutoff - v)
        point = Point(x, y).buffer(circleRadius)
        polygons.append(point)

    return polygons


def draw_trapezoid(graph, tree, cutoff, polygons):
    for k, v in tree[1].iteritems():
        if len(v) > 1:
            for i in range(0, len(v) - 1):
                c1 = v[i]
                c2 = v[i + 1]
                c1x, c1y = graph.node[c1]['longitude'], graph.node[c1]['latitude']
                c2x, c2y = graph.node[c2]['longitude'], graph.node[c2]['latitude']

                adjacent = abs(c1x - c2x)
                hypothenuse = math.sqrt((c2x - c1x) ** 2 + (c2y - c1y) ** 2)
                angle = math.acos(adjacent / hypothenuse)  # quadrant 1

                if c1x > c2x and c2y >= c1y:  # quadrant 2
                    angle = math.pi - angle
                elif c1x > c2x and c2y < c1y:  # quadrant 3
                    angle = math.pi + angle
                elif c2x > c1x and c2y < c1y:  # quadrant 4
                    angle = 2 * math.pi - angle
                angle += math.pi / 2  # find the right angle

                circleRadius = _SLOWEST_HUMAN_SPEED * (cutoff - tree[0][c1])
                c1x1 = c1x + (circleRadius) * math.cos(angle)
                c1y1 = c1y + (circleRadius) * math.sin(angle)
                c1x2 = c1x + (circleRadius) * math.cos(angle + math.pi)
                c1y2 = c1y + (circleRadius) * math.sin(angle + math.pi)
                circleRadius = _SLOWEST_HUMAN_SPEED * (cutoff - tree[0][c2])
                c2x1 = c2x + (circleRadius) * math.cos(angle)
                c2y1 = c2y + (circleRadius) * math.sin(angle)
                c2x2 = c2x + (circleRadius) * math.cos(angle + math.pi)
                c2y2 = c2y + (circleRadius) * math.sin(angle + math.pi)
                polygon = Polygon([(c1x1, c1y1), (c1x2, c1y2), (c2x2, c2y2), (c2x1, c2y1)])
                polygons.append(polygon)

    return polygons


def bicycle_time(graph):
    bicycle = {}
    for edge in graph.edges():
        u, v = edge
        length = graph[u][v]['length']
        level = graph[u][v]['level']

        bicycle_allowed = True if level < 5 else False
        if bicycle_allowed:
            bicycle[edge] = length / (_BICYCLE_SPEED * 1000 / 3600.0)
        else:
            bicycle[edge] = None
    return bicycle


def add_bicycle_time_travel(graph):
    nx.set_edge_attributes(graph, 'bicycle', bicycle_time(graph))

    return graph


# point is starting point for envelop, tuple of (long, lat)
#  weight = 'pedestrian' or 'bicycle'
# time_available in seconds
def get_envelop(point, time_available, transportation):
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, _SHANGHAI_MAP)
    graph = nx.read_gexf(path=file_path)
    print("Cleaning gexf")
    graph = pocogeo.clean(graph)

    # x, y = point
    # # graph = pocogeo.linkNewNodes(graph, [(x, y)])
    # print("end link new nodes")
    # r = getGraphRtree(graph, generator='nodes', filename=None, interleaved=True)
    # print("end getgraphtree")
    # hits = r.nearest((x, y, x, y), 3, objects="raw")
    # n = pocogeo.nearestNodeFromLonLat(graph, x, y, list(hits))
    #
    # print(n)

    n = '475976364'

    graph = pocogeo.simplify_with_rdp(graph)
    print("Adding metric distances")
    graph = pocogeo.addMetricDistanceToEdges(graph, 4326)
    print("Adding time travel to edges")
    graph = pocogeo.addTimeTraveltoEdges(graph, transportation=['motorist']) \
        if transportation is 'pedestrian' else add_bicycle_time_travel(graph)
    print("Convert node coordinate")
    graph = pocogeo.convertNodesCoordinates(graph, 4326, 4479)

    polygons = []
    print("single source dijkstra")
    tree = nx.single_source_dijkstra(G=graph, source=n, weight=transportation, cutoff=time_available)
    print(len(tree))
    print("draw circles")
    polygons = draw_circles(graph, tree, time_available, polygons)
    print("draw trapezoids")
    polygons = draw_trapezoid(graph, tree, time_available, polygons)
    print("union")
    union = cascaded_union(polygons)
    return union


def drawRoads(G, edgeColorAttribute='level', edgeColorScale=9, nodeColorAttribute=None, nodeColorScale=None):
    edgeWidth = [1, 1, 1, 1, 1, 2, 2, 3, 3]
    pos = {}
    for n in G.nodes():
        pos[n] = (G.node[n]['longitude'], G.node[n]['latitude'])

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=0, alpha=0.5, color=colors[-1])

    # edges
    for i in range(0, 9):
        selectedEdges = [(u, v) for (u, v, d) in G.edges(data=True) if d['level'] == i]
        selectedColors = [colors[i] for e in selectedEdges]
        nx.draw_networkx_edges(G, pos, edgelist=selectedEdges, width=edgeWidth[i], edge_color=selectedColors, alpha=0.5)


if __name__ == "__main__":
    x, y = (31.2269459, 121.4860255)
    envelop = get_envelop((x,y), 3600, 'pedestrian')
    print(envelop)
    for p in envelop:
        patch = PolygonPatch(p, facecolor=colors2[-1], edgecolor=colors2[-1], alpha=0.15, zorder=1)
        ax.add_patch(patch)
    # drawRoads(graph)
    plt.show()
