# RHSI ADS-B Demo

This demo will utilize an OpenShift instance and 2 System Nodes. Each System Node will forward ADS-B information to a container that will combine all the data and forward to a Single UI. The UI is inside a container within OpenShift. With Skupper, we will connect the Bare Metal Nodes to the OpenShift Project to feed the Combiner Container with ADS-B Data. Another system is needed to build the containers and compile the code needed.

We will be utilizing the demo found here with the UI branch being pulled from here. This demo was originally created to demonstrate Red Hat Device Edge. We will be refactoring some of this code to use within this demo.
(Big thanks to Jason Dudash and Rich Lucente for the work they did on the RHDE Demo!)

For this demo, we will be utilizing RHPDS and Bare Metal. However, this can be changed to match your environment.

### RHPDS:
  RHEL 9 Base
  Red Hat OpenShift Container Platform 4.13 Workshop
### Bare Metal:
  RHEL 9 Base - Minimal Install
  RHEL 9 Base - Server with GUI

Consolidated GIT Repo [here](https://github.com/jwells2525/RHSI-Demo).
USE THIS REPO!

## Modify/Build Code
Done on the Development System. It is assumed that you have copied the repository to your local system. Where you will have 3 folders from the above GIT Repo (ads-b-service, combiner-service, and rhde-mapvizthing).

# Compile ADS-B Forwarder Executables
Additional ADS-B Files Needed are located [here](https://github.com/jwells2525/RHSI-Demo/tree/main/ads-b-service).

  1. Install golang
	
 	sudo dnf install golang
  2. Run Script to Copy Service Code
	
 	bash get_adsb_service.sh
  3. Copy the Source Code to Make Two
	
 	cp ads-b-service.go ads-b-service-two.go
  4. Modify Second Code
	
 	vi ads-b-service-two.go
  
  	Change portNumber   = “8888” to portNumber   = “8889”
  5. Compile Code
	
 	go build ads-b-service.go

	go build ads-b-service-two.go
  6. Retain ads-b-service and ads-b-service-two for Distribution to RHEL 9 Systems
  7. Retain a00a02.json and ab2ae0.json from Link Provided with Executable Files

# Combiner Container
Code for the Combiner can be found [here](https://github.com/jwells2525/RHSI-Demo/tree/main/combiner-service).
Combiner Container PreBuilt on 8-17-2023 can be found on
quay.io/rh_ee_jwells/rhsi-demo-combiner:latest

  1. Install Podman
	
 	sudo dnf install podman
  2. Change Directory to Build Container from
	
 	cd combiner
  3. Create the Container
	
 	podman build -t rhsi-demo-combiner .
  4. Push the Container to an Image Repository
     This example will assume you are using quay.io and uses my user account (rh_ee_jwells) and a Repo that was made (rhsi-demo)

	podman login quay.io

	podman push rhsi-demo-combiner:latest quay.io/rh_ee_jwells/rhsi-demo-combiner

# Map Container
NOTE: THIS STEP IS COMPLETED IN THE OPENSHIFT SETUP PHASE OF THE
INSTRUCTIONS. DO NOT DO THIS STEP UNTIL TOLD TO DO SO.
  1. Install Podman
	
 	sudo dnf install podman
  2. Change Message URL from Map Code

	cd rhde-mapvizthing

	cd Map/webapp

	vi src/app/Dashboard/WorldMap.tsx

  Change Line 30 (Starts with const FLIGHTS_API_URL = ) to Read:

	const FLIGHTS_API_URL = ‘https://{URL THAT YOU GOT FROM BELOW}/combined_get
  3. Modify Containerfile for Container Build

	cd Map/webapp
	
 	cp containers/Containerfile .
Change the Lines as Follows:

	ADD ../package*.json ./ to ADD package*.json ./
	
 	ADD ../. . to ADD . .
  4. Build the Container
	
 	podman build -t rhsi-demo-map .
  5. Push the Container to an Image Repository
     This example will assume you are using quay.io and uses my user account (rh_ee_jwells) and a Repo that was made (rhsi-demo)

	podman login quay.io
	
 	podman push rhsi-demo-map:latest quay.io/rh_ee_jwells/rhsi-demo-map

## Setup OpenShift
These instructions are built from a prebuilt repo. If using your own images, replace with your URL where necessary.
Instructions should be run on a system that can reach and is logged into the OpenShift Cluster.

  1. Create New Project for hello-world
	
 	oc new-project rhsi-demo
  2. Add Deployment with Image to Project
	
 	oc create deployment combiner --image quay.io/rh_ee_jwells/rhsi-demo-combiner
  3. Expose Deployment on Port
	
 	oc expose deployment combiner --port 5000
  4. Create Route for Project
	
 	oc create route edge --service=combiner --insecure-policy=Redirect
  5. Get the URL of the Project
	
 	oc get route combiner -o jsonpath='{.spec.host}{"\n"}'
  6. Use this URL in the Steps Above to Create the Map Container
  7. Add Deployment with Image to Project
	
 	oc create deployment map --image quay.io/rh_ee_jwells/rhsi-demo-map
  8. Expose Deployment on Port
	
 	oc expose deployment map --port 8080
  9. Create Route for Project
	
 	oc create route edge --service=map --insecure-policy=Redirect
  10. Get the URL of the Project
	
 	oc get route map -o jsonpath='{.spec.host}{"\n"}'
  11. In a Web Browser, Open the URL and you Should see a Map focused on the DC Area
  12. Install Skupper on System Connected to OpenShift
	
 	curl https://skupper.io/install.sh | sh
  14. Enable Skupper for the Namespace
	
 	skupper init --enable-console --enable-flow-collector --console-auth unsecured

## Setup Systems
This will cover setting up both systems. There are 2 different executable, json, and gateway configs. For the purpose of these instructions, I will treat them the same. However, each system gets 1 and the other system will get the other files.
Instructions should be run on a system that can reach and is logged into the OpenShift Cluster.

  1. Setup Skupper Repos

	# sudo subscription-manager config --rhsm.manage_repos=1

	# sudo subscription-manager list --available | less (To Get the Pool ID)

	# sudo subscription-manager attach --pool={Pool ID from Step b)

	sudo subscription-manager repos --enable=service-interconnect-1-for-rhel-9-x86_64-rpms
  2. Install Skupper Packages

	sudo dnf install skupper-cli skupper-router
  3. Log in to the OpenShift Cluster

     NOTE: Depending on the System, the OC command line tool may need to be installed.
  4. Enable the Skupper Gateway

	skupper gateway init –-type service
  5. Create the Local Service
  
  System 1:

	skupper service create adsb1 8887
  System 2:
  
  	skupper service create adsb2 8890
  6. Bind the Service to the Local Host
  
  System 1:

	skupper gateway bind adsb1 localhost 8888
  System 2: 
  
  	skupper gateway bind adsb2 localhost 8889
  7. Copy the Executable and JSON FIle to System
  8. Execute the Executable
  
  System 1:

	./ads-b-service -f a00a02.json
  System 2:

	./ads-b-service-two -f ab2ae0.json

At this point you should see the tracks on the map and updating frequently.
