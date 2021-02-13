There are five .csv files used to interact with the model, assign parameters and hazard scenario in this directory:

#### 1- "network_nodes.csv"
This file contains a list of entities with their attributes as follow:
- id: entity id,
- type: entity type For example, in a water distribution system, entity types could be pump stations, treatment plants, etc.
- loc_x & loc_y: entity longtitude and lattitude
- reqExpr_Mean, reqExpr_SD, reqExpr_Dist: the mean, standard deviation, and distribution of the required number of experts or crews to fix the entity. In post-disaster, these variables are evaluated in the damage assessment phase. In pre-disaster, they can be estimated for expected damage. Note that there are three options to define the distribution, including "uniform", "normalDist", and "logNormDist" distributions.
- reqTime_Mean,reqTime_SD,reqTime_Dist: mean, standard deviation, and distribution of required time repair an entity.
- reqBudg_Mean,reqBudg_SD,reqBudg_Dist: mean, standard deviation, and distribution of required budget or cost to fix an entity.
- reqEqp: equipment or supply required for fixing each entity if damaged.
- priority: priority of fixing each entity compared to other entities. For example, in an electric distribution system, substations that provide electricity to hospitals might have a higher priority than substations that provide electricity to residential areas. The priority level can be 1, 2, or 3, while the lower value indicates the higher priority.
- damage_prob: the probability of damage in the range of 0.0 to 1.0. In post-disaster conditions and after assessing damages, damage probability can be set to 0.0 and 1.0 for "functional" and "damaged" entities, respectively.
- dep_Mean,dep_SD,dep_Dist: mean, standard deviation, and distribution of dependencies. This is not applicable yet.

#### 2- "network_edges.csv"
This file is used to insert required data for edges (e.g., pipes and transmission lines are considered as edges in water and power distribution systems, respectively). Most of the variables are similar to the node file mentioned above.
- id: entity id
- node1: head node,
- node2: tail node,
- type: entity type
- directivity: it can be 1 or 2. 1 indicates that the edge is directional from node1 to node2, and 2 represents bidirectional edges.
- reqExpr_Mean,reqExpr_SD,reqExpr_Dist: menioned above
- reqTime_Mean,reqTime_SD,reqTime_Dist: mentioned above
- reqBudg_Mean,reqBudg_SD,reqBudg_Dist: mentioned above
- reqEqp: mentioned above,
- damage_prob: mentioned above
- dep_Mean,dep_SD,dep_Dist: mentioned above

#### 3- "crew_availability.csv"
This file inserts data about crew availability timeframe. The inserted data turns to a step function in the scripts in which each data point represents the start point of each step. Four variables define each data point:
- time: always starts with time zero. Inserted points are supposed to be increasing in time.
- mean, sd and distribution represent the parameters and distribution for each step. Thus, in the following example, 100 crews or experts are available at time 0 (distribution is uniform). This state is changed in 20 days when the total number of crews is randomly selected from a normal distribution (N(250, 50)). After 30 days (t=50), the total number of crews is decreased to 130 crews and stays constant for the simulation.
time mean sd distribution
0 100 0 uniform
20 250 50 normalDist
50 130 0 uniform\
Note: In case a model is not dependent on crews or other resources mentioned below, crew availability can be defined in a row (0, inf, 0, uniform).

#### 4- "budget_availability.csv"
Similar to crew availability.

#### 5- "supply_availability.csv"
Available supplies are assigned in this file. Supplies can be provided from two sources: inside (internal) and outside (external) sources.
- supply name: is the type of supply. Note that this name must be exactly similar to "reqEqp" mentioned in the nodes and edges files (1&2).
- inside_no: the number of supplies available inside the jurisdiction.
- inside_shipping_time: the time required to transport supplies to the jurisdiction or site.
- inside_cost: cost
- outside_no: the number of supplies available outside the jurisdiction.
- outside_shipping_time: the time required to ship supplies to the jurisdiction or site
- outside_cost: cost
In the following example, hv_sub is type of a supply and there are three items available inside the jurisdiction. Cost and transporting time are zero. These resources are prioritize to be used in the post-disaster restoration compared to the external resources. If more supplies are required (more than three items in the following example), they are ordered and transported from the external source. In this example, 1000 items are available outside the jurisdiction while it takes 60 days to transport and $850k to order.\
hv_sub 3 0 0 1000 60 850

#### Next step
Once the input parameters are set for network entities, post-disaster restoration is simulated and outputs are generated by executing "run.py". More information is provided in "run.py" file about the steps taken to simulate the process and generate outputs. Generated outputs are available in "\output" directory with a brief explanation.
