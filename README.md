# Delivery Route Creation and Optimization

## Intro

Last-mile delivery of e-commerce orders is a segment of the supply chain with potential for cost reduction if delivery routes can be optimized. This project makes an attempt at solving the Vehicle Routing Problem.

## Walkthrough

1. A list of 2,000 addresses was obtained from the City of Calgary open [Parcel Address](https://data.calgary.ca/Base-Maps/Parcel-Address/9zvu-p8uz) database.
![](./output/figures/source_data.png)

2. A local instance of the [Project-OSRM backend](https://github.com/Project-OSRM/osrm-backend) running in a Docker container was used to calculate a distance matrix as the driving time between every pair of addresses.

3. Addresses were then clustered into 40 routes by passing the distance matrix to the scikit-learn agglomerative clustering algorithm. The number of routes is user defined.
![](./output/figures/clustered.png)

4. OSRM was then used to solve the travelling salesman problem for each route.
![](./output/figures/routes.png)