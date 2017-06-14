from pprint import pprint as pp

edges = [
    ['a', 'b'],
    ['b', 'c'],
    ['p', 'q'],
    ['q', 'u'],
    ['r', 'f'],
    ['e', 'r'],
    ['e', 't'],
    ['p', 't'],
]

groups = {}
groups_sizes = []
g = 0
for source, target in edges:
    if source not in groups and target in groups:
        groups[source] = groups[target]
        groups_sizes[groups[target]] += 1
    elif source in groups and target not in groups:
        groups[target] = groups[source]
        groups_sizes[groups[source]] += 1
    elif source not in groups and target not in groups:
        groups[target], groups[source] = g, g
        groups_sizes.append(0)
        groups_sizes[g] += 2
        g += 1
    elif groups[target] != groups[source]:
        if groups_sizes[groups[target]] > groups_sizes[groups[source]]:
            for node, group in groups.items():
                if group == groups[source]:
                    groups[node] = groups[target]
        else:
            for node, group in groups.items():
                if group == groups[target]:
                    groups[node] = groups[source]

pp(groups)
pp(groups_sizes)
best_group = groups_sizes.index(max(groups_sizes))
print('best group is ', best_group)

edges = [(source,target) for source, target in edges if groups[source] == best_group]

pp(edges)
