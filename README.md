# Mapping dependency parser

Builds insights in the network of entities and mappings, by using RETW ouput files, to determine:

* what the ordering of mappings should be for the ETL orchestrator and
* the consequences of a failure of a step in ETL process.
* whether the ETL flow has no closed loops (ETL-flows should be [acyclic](https://en.wikipedia.org/wiki/Directed_acyclic_graph)),

## Mapping order

The ordering of mappings can be determined using ```mapping_order.py``` and changing the list with filenames in the ```main``` function's variable ```lst_files_RETW```. This script also checks whether the ETL flow is acyclic.

### Output

Output generated by this script can be found in the files:

* ```output/dag_structure_*.html```, which shows the structure of the ETL, and
* ```output/mapping_order_*.jsonl```, which contains the ordering of the mapping executing which should be adopted by the orchestrator.

The asterisks in the filename indicates the iteration of each RETW file added to the network. This iterative output enables troubleshooting.

## ETL job failures

A simulation a failing ETL process can be simulated using ```mapping_simulator.py```. The list with filenames in the ```main``` function's variable ```lst_files_RETW``` can be adjusted. In the same function you can 'simulate' an ETL-step failure by adjusting the variable ```id_entity_failed```; although the variable name suggests only entities can fail, you can also set this ID to a mapping.

### Output

Output generated by this script can be found in the files:

* ```output/dag_run_report.html```, which is a graphical representation of the failure consequences, and
* ```output/dag_run_fallout.json```, which reports on the mappings/entities affected by the failure.
