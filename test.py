from collections import defaultdict

# Input list
mappings = [
    {"mapping": "o127", "source_tables": [0, 3, 6, 7, 8]},
    {"mapping": "o203", "source_tables": [8, 11]},
    {"mapping": "o248", "source_tables": [0, 3, 7]},
    {"mapping": "o315", "source_tables": [20]},
    {"mapping": "o335", "source_tables": [20]},
    {"mapping": "o365", "source_tables": [0]},
    {"mapping": "o376", "source_tables": [0]},
    {"mapping": "o388", "source_tables": [20]}
]

# Step 1: Build conflict graph
conflict_graph = defaultdict(set)
for i, a in enumerate(mappings):
    for j, b in enumerate(mappings):
        if i >= j:
            continue
        if set(a["source_tables"]) & set(b["source_tables"]):
            conflict_graph[a["mapping"]].add(b["mapping"])
            conflict_graph[b["mapping"]].add(a["mapping"])

conflict_graph

# Step 2: Assign stages using a greedy coloring algorithm
run_order = {}
used_colors = {}

for mapping in sorted(conflict_graph, key=lambda m: len(conflict_graph[m]), reverse=True):
    neighbor_colors = {run_order[neighbor] for neighbor in conflict_graph[mapping] if neighbor in run_order}
    color = 0
    while color in neighbor_colors:
        color += 1
    run_order[mapping] = color
    used_colors.setdefault(color, []).append(mapping)

# Step 3: Add mappings with no conflicts
for item in mappings:
    if item["mapping"] not in run_order:
        color = 0
        while color in used_colors:
            color += 1
        run_order[item["mapping"]] = color
        used_colors.setdefault(color, []).append(item["mapping"])

# Final result: group mappings by run stage
stages = [[] for _ in range(max(run_order.values()) + 1)]
for mapping, stage in run_order.items():
    stages[stage].append(mapping)

# Output
for i, stage in enumerate(stages):
    print(f"Stage {i+1}: {stage}")
