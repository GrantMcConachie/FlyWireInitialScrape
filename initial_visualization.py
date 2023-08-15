"""
This is an initial visualization of the FlyWire data connectome data for the olfactory
system. 

Files used in this script can be downloaded at https://codex.flywire.ai/api/download. 
Files used are the 'Classification' csv file and the 'Connections' file. For a successful 
run, download these two datasets, put them in a folder called 'Data' and unzip them. 
Run this script in the parent folder.

@author: Grant McConachie
"""


import pandas as pd
from tqdm import tqdm
import json
import numpy as np
import matplotlib.pyplot as plt


class Data:
    """
    Methods to get the FlyWire data into JSON files
    """
    def __init__(
            self,
            connection_file_loc="./Data/connections.csv",
            classification_file_loc="./Data/classification.csv",
            exist_file='n',
            file_loc=""
    ):
        """
        Creating dataframes of each of the csv files

        Inputs:
            `connection_file_loc` :string: - location of 'connection.csv'

            `classification_file_loc` :string: - location of 'classification.csv'

            `exist_file` :char: - 'n' if there is no existing json file
        """
        self.connection_df = pd.read_csv(connection_file_loc)
        self.classification_df = pd.read_csv(classification_file_loc)
        if exist_file:
            self.file_loc = file_loc

    def olfactory_neruons(self, _class):
        """
        Searches through classification dataframe and finds all the neurons of a
        certain class

        Input:
            `_class` :string: - class you want to query

        Output:
            `list_olf_neurons` :list: - list of 'root_id's of the neruons in the
            class '_class'
        """
        list_neurons = []

        for index, row in self.classification_df.iterrows():
            if row["class"] == _class:
                list_neurons.append(row["root_id"])

        return list_neurons
    
    def neuron_connections(self, list_neurons, save='y', name="olfactory_connectome"):
        """
        Find all of the connections in 'connections.csv' that are connected to a
        list that you input

        Input:
            `list_neurons` :list: - list of integers of neuron 'root_id's you want 
            to know the connections of.

            `save_data` :char: - y saves data to the pwd 

            `name` :str: - name of the json file you're saving

        Output:
            `neuron_connection` :dict: - neurons and their lists of connecting 
            neurons and how strong their connections are and what type of 
            connections they have
        """
        # Initializing a dictionary with all of the neurons in 'list_neurons'
        neuron_connection = {}
        for neuron in list_neurons:
            neuron_connection[neuron] = {
                "downstream": [],
                "strength": [],
                "connection_type": []
            }

        # Looping through 'connection.csv' and appending dict
        with tqdm(total=len(self.connection_df.index), desc=name) as pbar:
            for index, row in self.connection_df.iterrows():
                pre_root_id = row["pre_root_id"]

                # Ignoring neurons not in list_neurons
                if pre_root_id not in list_neurons:
                    pass
                else:
                    neuron_connection[pre_root_id]["downstream"].append(row["post_root_id"])
                    neuron_connection[pre_root_id]["strength"].append(row["syn_count"])
                    neuron_connection[pre_root_id]["connection_type"].append(row["nt_type"])

                pbar.update(1)

        if save:
            self.save_data(neuron_connection, name)

        return neuron_connection
    
    def list_down_stream_regions(self):
        """
        Lists all of the downstream regions that are in list neurons.

        Output:
            `downstream_regions` :list: - list of downstream regions.
        """
        # Load important variables
        downstream_regions = []
        data = self.load_json()
        classification_df = self.classification_df

        # Loop through dictionary
        for i, (key, value) in enumerate(data.items()):
            for downstream in value["downstream"]:
                row = classification_df.iloc[np.where(classification_df["root_id"] == downstream)[0]]
                _class = row["class"].iloc[0]

                # seeing if class already in donwstream regions
                if _class in downstream_regions:
                    pass
                else:
                    downstream_regions.append(_class)

        return downstream_regions

    def load_json(self):
        """
        Loads in the json file as a  dict 
        """
        f = open(self.file_loc)
        data = json.load(f)

        return data
    
    def save_data(self, data, name):
        """
        saves the data that you input to a json file in pwd

        Input:
            `data` :dict: - data you want to be saved

            `name` :str: - title of the dataset
        """
        with open(name + ".json", "w") as f:
            json.dump(data, f)

class GraphData:
    """
    Methods for visualizing JSON formated data
    """
    def connectivity_matrix(self, data_frames, upstream_axis=0):
        """
        Creates connectivity matricies

        Input:
            `data_frames` :list of dataframes: - 2D list with both areas you want 
            to create a connectivity matrix of. If you want a self connectivity 
            matrix, pass in the same dataframe twice

            `upstream_axis` :int: - which region you want to be upstream

        Output:
            `matricies` :list: - list of connectivity matricies
        """
        # Catching if more than 2 dataframes are given
        if len(data_frames) != 2:
            raise ValueError(f"data_frames must contain 2 entries. You put {len(data_frames)}")
        
        # Creating a list of neurons
        list_loc2_neurons = list(data_frames[1-upstream_axis].keys())

        # Creating a connectivity matrix
        connect_matrix = np.zeros((
            len(data_frames[upstream_axis]), 
            len(data_frames[1-upstream_axis])
        ))
        
        # Looping through the first 
        for i, (key, value) in enumerate(data_frames[upstream_axis].items()):
            for j, downstream in enumerate(value["downstream"]):
                # Checking if neurons are in the olfactory system
                if str(downstream) not in list_loc2_neurons:
                    pass
                else:
                    idx_downstream = list_loc2_neurons.index(str(downstream))
                    connect_matrix[i][idx_downstream] = value["strength"][j]

        return connect_matrix


    def visualize_single_area(self, parent_dir, loc, normalize=True):
        """
        Creates a connectivity matrix for all the neurons in the file specified

        Input:
            `parent_dir` :str: - parent directory of JSON files

            `loc` :str: - class you want to visualize

            `normalize` :bool: - Normalizes the connectivity matrix to 1
        """
        file_path = parent_dir + loc + "_connections.json"

        # Load in json dict and creating lists of neurons
        data = Data(exist_file='y', file_loc=file_path).load_json()
        connect_matrix = self.connectivity_matrix([data, data])

        # Normalizing the graph
        if normalize:
            connect_matrix = connect_matrix / connect_matrix.max()

        # Plotting
        plt.imshow(connect_matrix, cmap="Greys", interpolation='none')
        plt.title("Within area connection matrix: " + loc)
        plt.ylabel("Upstream Neuron")
        plt.xlabel("Downstream Neuron")
        plt.colorbar()
        plt.show()

    def connectivity_matrix_multiple_areas(self, file_loc, loc_1, loc_2, normalize=True):
        """
        Creates a connectivity matric between two areas

        Input:
            `file_loc` :str: - parent directory of JSON files

            `loc_1` :str: - 1st location

            `loc_2` :str: - 2nd location
            
            `normalize` :bool: - Normalizes the connectivity matrix to 1
        """
        # Load in both JSON dicts and create connectivity matrix
        loc_1_data = Data(exist_file='y', file_loc=file_loc+loc_1+"_connections.json").load_json()
        loc_2_data = Data(exist_file='y', file_loc=file_loc+loc_2+"_connections.json").load_json()
        connect_matrix_1 = self.connectivity_matrix([loc_1_data, loc_2_data], upstream_axis=0)
        connect_matrix_2 = self.connectivity_matrix([loc_1_data, loc_2_data], upstream_axis=1)

        # Normalizing the graph
        if normalize:
            connect_matrix_1 = connect_matrix_1 / connect_matrix_1.max()
            connect_matrix_2 = connect_matrix_2 / connect_matrix_2.max()

        # Plotting
        fig, ax = plt.subplots(1,2, layout="constrained")
        plt_1 = ax[0].imshow(connect_matrix_1, cmap="binary", interpolation='none')
        ax[0].set_title(f"{loc_1} --> {loc_2}")
        ax[0].set_ylabel(f"{loc_1}")
        ax[0].set_xlabel(f"{loc_2}")

        plt_2 = ax[1].imshow(connect_matrix_2, cmap="binary", interpolation='none')
        ax[1].set_title(f"{loc_2} --> {loc_1}")
        ax[1].set_ylabel(f"{loc_2}")
        ax[1].set_xlabel(f"{loc_1}")       

        fig.colorbar(plt_1)
        fig.colorbar(plt_2)
        plt.show()



if __name__ == '__main__':

    # Query Data and save to json
    unpacked_data = Data()
    regions = ['olfactory', 'ALPN', 'LHLN', 'LHCENT']
    # for region in regions:
    #     list_neurons = unpacked_data.olfactory_neruons(region)
    #     unpacked_data.neuron_connections(
    #         list_neurons=list_neurons, 
    #         save='y', 
    #         name=region+"_connections"
    #     )

    # # List downstream connects
    # for region in regions:
        # json_data = Data(exist_file='y', file_loc="./"+region+"_connections.json")
        # downstream = json_data.list_down_stream_regions()
        # num_neurons = len(json_data.olfactory_neruons(region))
        # print(region, "downstream regions:", downstream)
        # print("Number neurons in", region, ":", num_neurons, "\n")

    # json_data = Data(exist_file='y', file_loc="./ALPN_connections.json")
    # downstream = json_data.list_down_stream_regions()
    # num_neurons = len(json_data.olfactory_neruons("ALPN"))
    # print("ALPN downstream regions:", downstream)

    # # Graphing data
    # GraphData().visualize_single_area(parent_dir="./", loc="olfactory")
    GraphData().connectivity_matrix_multiple_areas(file_loc="./", loc_1="ALPN", loc_2="LHCENT", normalize=False)
 