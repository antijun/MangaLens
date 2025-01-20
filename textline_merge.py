import itertools
import numpy as np
import networkx as nx
from typing import List, Set
from collections import Counter
from shapely.geometry import Polygon


class Quadrilateral:
    def __init__(self, pts, font_size, angle, centroid, fg_color=(0, 0, 0), bg_color=(255, 255, 255), text="", prob=1.0):
        self.pts = pts  # List of points (x, y)
        self.font_size = font_size
        self.angle = angle
        self.centroid = centroid
        self.fg_color = fg_color  # Default to black
        self.bg_color = bg_color  # Default to white
        self.text = text  # Default to an empty string
        self.prob = prob  # Default probability value (e.g., 1.0)

    def distance(self, other):
        # Calculate the distance between the centroids of two quadrilaterals
        return np.linalg.norm(np.array(self.centroid) - np.array(other.centroid))


class TextBlock:
    def __init__(self, lines, texts, font_size, angle, prob, fg_color, bg_color):
        self.lines = lines
        self.texts = texts
        self.font_size = font_size
        self.angle = angle
        self.prob = prob
        self.fg_color = fg_color
        self.bg_color = bg_color

    def get_combined_bbox(self):
        """Calculate the bounding box that encompasses all lines."""
        x_coords = [pt[0] for line in self.lines for pt in line]
        y_coords = [pt[1] for line in self.lines for pt in line]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        return x_min, y_min, x_max - x_min, y_max - y_min


def split_text_region(bboxes, connected_region_indices, gamma=0.5, sigma=2):
    connected_region_indices = list(connected_region_indices)

    # Base case: single or no region
    if len(connected_region_indices) <= 1:
        return [set(connected_region_indices)]

    if len(connected_region_indices) == 2:
        fs1 = bboxes[connected_region_indices[0]].font_size
        fs2 = bboxes[connected_region_indices[1]].font_size
        fs = max(fs1, fs2)

        if bboxes[connected_region_indices[0]].distance(bboxes[connected_region_indices[1]]) < (1 + gamma) * fs:
            return [set(connected_region_indices)]
        else:
            return [{connected_region_indices[0]}, {connected_region_indices[1]}]

    # Create a graph to calculate distances
    G = nx.Graph()
    for idx in connected_region_indices:
        G.add_node(idx)
    for (u, v) in itertools.combinations(connected_region_indices, 2):
        G.add_edge(u, v, weight=bboxes[u].distance(bboxes[v]))

    # Minimum spanning edges and distance checks
    edges = nx.algorithms.tree.minimum_spanning_edges(G, algorithm='kruskal', data=True)
    distances_sorted = sorted([edge[2]['weight'] for edge in edges])
    fontsize = np.mean([bboxes[idx].font_size for idx in connected_region_indices])
    distances_mean = np.mean(distances_sorted)
    distances_std = np.std(distances_sorted)
    std_threshold = max(0.3 * fontsize + 5, 5)

    # No further split if the distances are within thresholds
    if distances_sorted[0] <= distances_mean + distances_std * sigma and distances_std < std_threshold:
        return [set(connected_region_indices)]

    # Recursive splitting
    new_regions = []
    for node_set in nx.algorithms.components.connected_components(G):
        # Prevent infinite recursion by ensuring node_set size decreases
        if len(node_set) < len(connected_region_indices):
            new_regions.extend(split_text_region(bboxes, node_set))
        else:
            new_regions.append(set(node_set))  # Add as-is if no progress
    return new_regions


def merge_bboxes_text_region(bboxes: List[Quadrilateral], width, height):
    G = nx.Graph()
    for i, box in enumerate(bboxes):
        G.add_node(i, box=box)

    for ((u, ubox), (v, vbox)) in itertools.combinations(enumerate(bboxes), 2):
        if ubox.distance(vbox) < ubox.font_size * 1.3:
            G.add_edge(u, v)

    region_indices = []
    for node_set in nx.algorithms.components.connected_components(G):
        region_indices.extend(split_text_region(bboxes, node_set))

    for node_set in region_indices:
        nodes = list(node_set)
        txtlns = np.array(bboxes)[nodes]

        fg_color = tuple(np.round(np.mean([box.fg_color for box in txtlns], axis=0)).astype(int))
        bg_color = tuple(np.round(np.mean([box.bg_color for box in txtlns], axis=0)).astype(int))

        majority_dir = Counter([box.angle for box in txtlns]).most_common(1)[0][0]

        if majority_dir == 'h':
            nodes = sorted(nodes, key=lambda x: bboxes[x].centroid[1])
        elif majority_dir == 'v':
            nodes = sorted(nodes, key=lambda x: -bboxes[x].centroid[0])
        txtlns = np.array(bboxes)[nodes]

        yield TextBlock(
            lines=[box.pts for box in txtlns],
            texts=[box.text for box in txtlns],
            font_size=int(np.min([box.font_size for box in txtlns])),
            angle=np.rad2deg(np.mean([box.angle for box in txtlns])) - 90,
            prob=np.mean([box.prob for box in txtlns]),
            fg_color=fg_color,
            bg_color=bg_color
        )
