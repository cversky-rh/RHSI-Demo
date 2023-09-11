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
