import json

from dag_etl import EtlDag
from etl_failure_simulator import ETLFailureSimulator
from graph_retw_files import GraphRETWFiles

if __name__ == "__main__":
    """Examples of the class use-cases
    """
    # List of RETW files to process, order of the list items is irrelevant
    lst_files_RETW = [
        "output/Usecase_Aangifte_Behandeling.json",
        "output/Usecase_Test_BOK.json",
        "output/DMS_LDM_AZURE_SL.json",

    ]

    """File dependencies
    * Visualizes of the total network of files, entities and mappings
    * Visualizes of a given entity's network of connected files, entities and mappings
    * Visualizes dependencies between files, based on entities they have in common
    """
    graph_files = GraphRETWFiles()
    graph_files.add_RETW_files(files_RETW=lst_files_RETW)
    # Visualization of the total network of files, entities and mappings
    graph_files.plot_graph_total(file_html="output/graph_files_total.html")
    # Visualization of a given entity's network of connected files, entities and mappings
    graph_files.plot_entity_journey(
        code_model="Da_Central_CL",
        code_entity="DmsProcedure",
        file_html="output/entity_journey.html",
    )
    # Visualization of dependencies between files, based on entities they have in common
    graph_files.plot_file_dependencies(file_html="output/file_dependencies.html")

    """ETL Flow (DAG)
    * Determine the ordering of the mappings in an ETL flow
    * Visualizes the ETL flow for all RETW files combined
    """
    etl_dag = EtlDag()
    etl_dag.add_RETW_files(files_RETW=lst_files_RETW)
    # Determine the ordering of the mappings in an ETL flow: a list of mapping dictionaries with their RunLevel and RunLevelStage
    dict_mapping_order = etl_dag.get_mapping_order()
    with open("output/mapping_order.jsonl", "w", encoding="utf-8") as file:
        json.dump(dict_mapping_order, file)
    # Visualization of the ETL flow for all RETW files combined
    etl_dag.plot_etl_dag(file_html="output/ETL_flow.html")

    """Failure simulation
    * Sets a failed object status
    * Visualization of the total network of files, entities and mappings
    """
    lst_id_entities_failed = ["o36", "o60"] # Set for other examples
    etl_simulator = ETLFailureSimulator()
    # Adding RETW files to generate complete ETL DAG
    etl_simulator.add_RETW_files(files_RETW=lst_files_RETW)
    # Set failed node
    etl_simulator.set_entities_failed(lst_id_entities_failed)
    # Create fallout report file
    dict_mapping_order = etl_simulator.get_report_fallout()
    with open("output/dag_run_fallout.json", "w", encoding="utf-8") as file:
        json.dump(dict_mapping_order, file, indent=4)
    # Create fallout visualization
    etl_simulator.plot_dag_fallout(file_html="etl_templates/output/dag_run_report.html")