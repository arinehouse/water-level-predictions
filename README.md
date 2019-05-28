# Water Level Predictions

### Introduction
For my EARS 3 (Elementary Oceanography) final project at Dartmouth College, I aimed to explore the notion that the tides are extremely complex and difficult to predict. Using my background in computer science and machine learning in particular, I wanted to see if mathematical models could be used to accurately predict the tides. The simple implementation given here currently uses a linear regression model, with the vast majority of the workload having been the actual collection of data to use for prediction. This project is meant to establish a groundwork for possible future data collection and research into this problem.

### Development
To run the scripts locally follow these instructions:

1. Clone this project to your local machine
```
git clone https://github.com/arinehouse/water-level-predictions
```

2. Create a virtual environment called "env" (naming it this will be automatically ignored by git)
```
python3 -m venv env
```
N.B. If you do not have `venv` installed you should do so first:
```
python3 -m pip install --user virtualenv
```

3. Activate the virtual environment
```
source env/bin/activate
```

4. Install dependencies
```
pip install -r requirements.txt
```

5. Run the code!
```
python linear_classifier.py 20130101.pkl
```
N.B. You do not need to run `gather_data.py`; the data is already included in the repo as `20130101.pkl`. If you'd like to create new data though, feel free! You can fetch all data since July 1st, 2000, for example, by calling `python gather_data 20000701`.

### Authors
[Adam Rinehouse](https://github.com/arinehouse)

### Acknowledgements
Thanks to NOAA CO-OPTS for their excellent [API](https://tidesandcurrents.noaa.gov/api/).