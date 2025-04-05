import igraph as ig

from mapping_order import MappingDependencies


class MappingSimulator(MappingDependencies):
    def __init__(self):
        super().__init__()
        self.dag = ig.Graph()

    def get_dag_status(self):
        self.dag = self.get_dag_networkx()
        return self.dag

    def set_entity_failed(self, id: str):
        dag = self.get_dag()
        node_failed = dag.vs.find(name=id).index
        lst_nodes = dag.subcomponent(node_failed, mode="out")
        self._set_pyvis_attributes(dag=dag)
        for id_node in lst_nodes:
            if id_node == node_failed:
                dag.vs[id_node]["color"] = "red"
                dag.vs[id_node]["shape"] = "star"
            else:
                dag.vs[id_node]["color"] = "darkorange"
        network = self._igraph_to_networkx(dag=dag)
        return network


if __name__ == "__main__":
    lst_files_RETW = ["output/Usecase_Aangifte_Behandeling.json"]
    id_mapping_failed = "o319"
    mapping_simulator = MappingSimulator()
    for file_RETW in lst_files_RETW:
        success = mapping_simulator.add_RETW_file(file_RETW=file_RETW)
        if success:
            dag = mapping_simulator.set_entity_failed(id=id_mapping_failed)
            mapping_simulator.plot_dag_networkx(
                dag, file_html_out="output/dag_simulated.html"
            )
