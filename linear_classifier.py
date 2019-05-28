import pickle
import sys
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# load the data from the pickled storage file
with open(sys.argv[1], 'rb') as datafile:
    data = pickle.load(datafile)

# break the model into the independent variables and dependent variable
X = data[:,:-1]
y = data[:,-1]

# create a linear regression model
reg = LinearRegression().fit(X, y)

# test on some new data
with open('20120101.pkl', 'rb') as datafile:
    test_data = pickle.load(datafile)

predictions = reg.predict(test_data[:,:-1])
ground_truth = test_data[:,-1]

# determine loss with R^2 regression score
r2 = r2_score(ground_truth, predictions)
print(r2)