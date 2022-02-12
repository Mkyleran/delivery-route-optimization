Steps

1. intake address data (.csv) 24 aero dr.
2. Geocode addresses
  - Open Calgary Parcel Address
  - Google Maps
  - Foursquare
3. Time and distance matrix
  - OSRM
  - OpenRouteService
  - Google Maps
  - Mapbox
4. Cluster into routes
  - by driving distance
  - by driving time
  - elbow rule, optimal routes
  - sklearn DBScan precalculated distance
  - test with sklearn.pairwise distance for euclidean distances
5. Time and distance matrix (the matrix from pt. 3 should be usable for this)
6. Route sequence TSP
  - OSM
  - OpenRouteService
7. Evaluate
  - R4M


## Resources

### APIs

- Gold standard [R4M](https://route4me.io) TSP VRP
- [Routific](https://dev.routific.com) TSP VRP
- [Google Maps](https://developers.google.com/maps/documentation)
- [Mapbox](https://docs.mapbox.com/api/overview/)
  - Matrix: max 25, driving-traffic max 10
  - Optimization: max 12
  - Directions: max 25
- [Verso VROOM](https://blog.verso-optim.com/category/route-optimization/api/) Docker + Python
- [Interline Valhala](https://www.interline.io/valhalla/) Docker + Homebrew
- OSRM docker
- OSR docker
 
[Online Routers](https://wiki.openstreetmap.org/wiki/Routing/online_routers)

#### [Top 10 Map Direction API – Routing Libraries](https://www.igismap.com/top-10-map-direction-api-routing-libraries-navigation-free-or-paid/)

1. Open Source Routing Machine
2. YOURS navigation API
3. Create Your Own Customized API: Take either shapefile or OSM data. Create R tree and generate the network graph. Implement A* or any shortest path alogrithm. Fix all issues and improve the speed.

### Data

- [Kaggle Taxi](https://www.kaggle.com/c/nyc-taxi-trip-duration/overview)




Summary

1. Project Planning
2. Project Setup
3. Project Workflow
4. Project Development
5. Project Deployment
6. Project Presentation


## 1. Project Planning

In the planning phase, you’ll prepare several documents to help guide you through the execution of your project.

Deadline: Finished and reviewed by a mentor on week 10 day 5.

a) Project Description
You should have a document describing your project idea. In other words, what your project is all about. It should contain at least the following:

- Project title
- Goal you try to achieve
- Project description - What problem your project solves

__Deliverable__: Project description document

## 2. Project Setup

To start off on the right foot, you’ll need a good project setup:

  1. Git repo setup  
Create a repo on GitHub and give access to all team members.  
[delivery-route-pptimization](https://github.com/Mkyleran/delivery-route-optimization)

  2. Access to Data  
Data gathering is one of the most important parts of the project. Sometimes, it can take a lot of time and data we find are not completely as we expected. Make sure to plan enough time for this step.

__Deliverable__: Data are ready

Open Calgary

- [Parcel Address](https://data.calgary.ca/Base-Maps/Parcel-Address/9zvu-p8uz/data)
- [Speed Limits](https://data.calgary.ca/Health-and-Safety/Speed-Limits/2bwu-t32v)
- [Community District Boundaries](https://data.calgary.ca/Base-Maps/Community-District-Boundaries/surr-xmvs)
- [Community Points](https://data.calgary.ca/Base-Maps/Community-Points/j9ps-fyst)
- [City Quadrants](https://data.calgary.ca/Base-Maps/City-Quadrants/g2n2-qnvh)
- [City Boundary](https://data.calgary.ca/Base-Maps/City-Boundary/erra-cqp9)
- [Forward Sortation Area](https://data.calgary.ca/Base-Maps/Forward-Sortation-Area/n2w2-2k2q)


## 3. Project Workflow

  1. Project Communication
We highly recommend that you implement a daily check-in with one of the mentors. It will be good if you can create a Progress Report where you track your progress each day and what are your current struggles. This way, every mentor will be able to help you anytime and check:

- What has been accomplished
- What will you be working on
- What hurdles are you facing

__Deliverable__: Progress Report

  2. Project Workflow
You need to take a few key decisions to ensure a smooth project workflow. Ideally, you should think about the following:

What are the project milestones: you need to create a list of the project milestones and specify what are the deadlines.  
__Deliverable__: Project milestones document

## 4. Project Development

You should work on the development of your project according to your feature list and project milestones. Be aware that there is a Demo Day coming on Week 12 Day 4 and you need to keep enough time for polishing results, making a presentation and to prepara yourself for the Demo Day.

## 5. Project Deployment

If your project allows you it would be great if you can deploy your model and show how it works during the presentation.

- Flask API app with UI
- Streamlit.io
- hiroku

## 6. Project Presentation

It’s important to take some time to structure the presentation of your project.

- Who is the target audience:
  - You have 2 targets: Employers and the public.
    - For prospective employers you should focus on what you’ve accomplished, highlight - your skills, the technologies you used.
    - For the public, it’s more about the user experience.
- You should have a slides ready with some interesting visualizations. If your project allows it you can do a live demo to show how it works. Try not to show your code during the presentation since the most of the audience won't be able to understand it properly.
- Audio/video setup: it’s important that you check your setup to ensure that everything works.
- Presentation practice: It’s important to practice before Demo Day. You should practice in front of a mentor so you can get some feedback.

__Deadlines__: - Practice Demo (with mentors): Demo Day minus 1 - Demo Day