import json
import argparse


def get_shallow_dependencies(ns_data, item):
    if available_from_digging(ns_data, item) \
            or item not in ns_data["all_items"]:
        return {}
    return ns_data["all_items"][item]["required"]


def recursive_discover_dependencies(ns_data, item, count):
    all_deps = {
        "name": item,
        "count": count,
        "precedence": 1,
        "unit_deps": [],
        "machine": None
    }
    machines = {
    }

    shallow_deps = get_shallow_dependencies(ns_data, item)
    all_items = ns_data["all_items"]
    for dep, count in shallow_deps.items():
        parent_deps, parent_machines = recursive_discover_dependencies(
                                            ns_data,
                                            dep,
                                            count
                                        )
        all_deps["unit_deps"].append(parent_deps)
        for m_name, m_preced in parent_machines.items():
            machines[m_name] = min(
                                    machines.get(m_name, float("inf")),
                                    m_preced
                                )

    if len(all_deps["unit_deps"]):
        all_deps["precedence"] = max([
                                d["precedence"] for d in all_deps["unit_deps"]
                                ]) + 1

    if item in all_items:
        machine = all_items[item]["machine"]
        all_deps["machine"] = machine
        machines[machine] = min(
                                    machines.get(machine, float("inf")),
                                    all_deps["precedence"] - 1
                            )
    return all_deps, machines


def flatten_and_simplify_dependencies(dep_node):
    if len(dep_node["unit_deps"]) == 0:
        return {dep_node["name"]: dep_node["count"]}
    result = {}
    for dep in dep_node["unit_deps"]:
        dep_fundamentals = flatten_and_simplify_dependencies(dep)
        result = combine_flattened_dependencies(
                    result,
                    dep_fundamentals,
                    multiplier_g2=dep_node["count"]
                )
    return result


def combine_flattened_dependencies(g1, g2, multiplier_g2=1, inplace=False):
    g = g1 if inplace else dict(g1)
    for k, v in g2.items():
        g[k] = g.get(k, 0) + multiplier_g2*v
    return g


def is_dep(item, graph):
    if item == graph["name"]:
        return True
    for dep in graph["unit_deps"]:
        if is_dep(item, dep):
            return True
    return False


def available_from_digging(ns_data, item):
    return item in ns_data["available_from_digging"]


def resolve_machines_dep(ns_data, machines):
    all_machines = list(machines)
    all_machines_dep = {}
    i = 0
    while i < len(all_machines):
        machine = all_machines[i]
        m_graph, ms_required = recursive_discover_dependencies(
                                    ns_data,
                                    machine,
                                    1
                                )
        all_machines_dep = combine_flattened_dependencies(
                                all_machines_dep,
                                flatten_and_simplify_dependencies(m_graph)
                            )
        ms_required = [m for m in ms_required.keys() if not is_dep(m, m_graph)]
        for m_required in ms_required:
            if m_required not in all_machines:
                all_machines.append(m_required)
        i += 1
    return all_machines_dep


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "query",
        help="item to search",
        type=str
    )
    parser.add_argument(
        "--mm",
        help="whether to manufacture all depending machines",
        action="store_true"
    )
    parser.add_argument(
        "-d", "--data",
        help="path to data file",
        type=str,
        default="data.json"
    )
    parser.add_argument(
        "-o", "--output",
        help="path to output result",
        type=str
    )

    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        ns_data = json.load(f)
        ns_data["all_items"] = {i["name"]: i for i in ns_data["all_items"]}

    query = args.query.strip()
    if query not in ns_data["all_items"]:
        print(f"{query} not found, try again.")
        exit(-1)

    graph, required_machines = recursive_discover_dependencies(
                                    ns_data,
                                    query,
                                    1
                                )

    machines_prereq = []
    machines_manufactured = []
    for rm in required_machines:
        if not is_dep(rm, graph):
            machines_prereq.append(rm)
        else:
            machines_manufactured.append(rm)
    required_fundamentals = flatten_and_simplify_dependencies(graph)

    if args.mm:
        required_fundamentals = combine_flattened_dependencies(
                                    required_fundamentals,
                                    resolve_machines_dep(
                                        ns_data,
                                        machines_prereq
                                    )
                                )

    if args.output is None:
        print("Result:")
        print(json.dumps(
                graph,
                indent=4,
                ensure_ascii=False
        ))
        print(json.dumps(
                required_fundamentals,
                indent=4,
                ensure_ascii=False
        ))
        print("Equipment manufactured:", machines_manufactured)
        print("Extra machines required:", machines_prereq)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({
                    "graph": graph,
                    "machine manufactured in the process": machines_manufactured,  # noqa: E501
                    "extra machines required": machines_prereq,
                    "fundamentals": required_fundamentals
                },
                f,
                indent=4,
                ensure_ascii=False
            )
