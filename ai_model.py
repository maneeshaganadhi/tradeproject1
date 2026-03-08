from sklearn.linear_model import LogisticRegression
import numpy as np

# create model
model = LogisticRegression()

# training data
X = np.array([[1],[2],[3],[4]])
y = np.array([0,0,1,1])

# train model
model.fit(X,y)

def predict_value(value:int):
    prediction = model.predict([[value]])
    return int(prediction[0])