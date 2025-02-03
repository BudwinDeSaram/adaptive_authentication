# README #

Learning State Machine for Adaptive Authentication (LSMAA)

## What this repositor contains ##

This repository contains an adaptive authentication system built using learning state machine concept. The FlexFringe framework (originally from https://github.com/tudelft-cda-lab/FlexFringe.git) has used to build the state machine. 

## How to get set up ##


The system has containerised using Docker. To run the Docker file execute

`$ docker build -t <image_name> .`
`$ docker run -it -p 8080:8080 <image_name>`