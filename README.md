# FlyWireInitialScrape
This is an initial dive into the flywire data

`initial_visualization.py` contains a `Data` class and a `GraphData` class with some helpful modules on turning the .csv files into more useable formats.

## JSON files
JSON files are formated as follows

```json
"neuron_id (e.g. 720575940659611777)" : {
  "downstream": ['list of downstream neurons'],
  "strength": ['list of # of synaptic connections corresponding to neurons in "downstream"'],
  "connection_type": ['list of neurotransmitter released at every synaptic connection corresponding to neurons in "downstream"']
}
```
