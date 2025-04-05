# Mapping dependency parser

Builds insight in the network of entities and mappings by using RETW ouput files in order to:

1. Determine if there is no feedback in the ETL (ETL should be acyclic)
2. Determine what the ordering of the mapping should be in an ETL job
3. Determine what the consequences are if an ETL step failed

The ordering of mappings can be determined using ```mapping_order.py``` and changing the list with filenames in the variable ```lst_files_RETW``` in the ```main``` function. During this process the acyclic check is also performed.

A simulation of a failure of ETL can be simulated using ```mapping_simulator.py```. The list with filenames in the variable ```lst_files_RETW``` in the ```main``` function can be adjusted. In the same function you can 'simulate' an ETL-step failure by adjusting the variable ```id_entity_failed```; although the variable name suggests only entities can fail, you can also set this ID to a mapping. 
