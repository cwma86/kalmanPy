# kalmanPy
Python Kalman filter project

# Install
## Create venv
Using pip 3 install python virtual environment and required dependancies
```bash
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Compile protobuf
This project uses protobuf which needs to be compiled
run make from repo root 
```bash
make
```
# Running the applications

## Tracker
to run the tracker navigate to the tracker source repo
```bash 
cd src/tracker
./tracker.py
```

## Simulator
to run the Simulator navigate to the Simulator source repo
```bash 
cd src/Simulator
./Simulator.py
```
