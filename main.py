#Thanks to @NeuralNine - YouTube
#Importing the necessary modules. If the modules are not present, try "pip install <modulename>" in your shell
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as web
import datetime as dt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

#Loading Data
#Obtaining  the data from a finance API, here stooq, with the given constraints

#Company Name input (ticker symbol)
company = input("Enter the ticker symbol of the company (eg: META)> ")

#Setting days amount
start = dt.datetime(2012,1,1)
end = dt.datetime(2024,1,1)

#Fetching data from the given company and start and end dates
data = web.DataReader(company, 'stooq', start, end)

#Preparing the data
#Using the scaler to fit the data (prices) into a 0 - 1 range
#Creating two numpy arrays of different dimensions used to train the model
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1,1))


#Number of days to take into consideration to predict the following day's price
prediction_days = 365

x_train, y_train = [], []

for x in range(prediction_days, len(scaled_data)):
    
    x_train.append(scaled_data[x-prediction_days:x, 0])
    y_train.append(scaled_data[x, 0])

#Converting the basic lists into numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

#Building the model
#Adding layers to the model and finally a dense layer for the prediction
#Epochs can be increased for better precision
model = Sequential()

#Different layers of the model. Structure includes having alternate LSTM and Dropout layers finally ending with a Dense layer (for prediction)
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))

#Prediction Layer (DENSE)
model.add(Dense(units=1)) 

#Compiling the model with mean squared error loss function
#Model is not saved as different files and fitted directly into the program to run it on the go
#If you want, you can save the model with specific number of epoch and reuse the model to predict further data.
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, epochs=50,batch_size=32) #Change epochs to alter the number of times the model goes through the data. I recommend 50.

#Loading Test Data

#Obtaining a different timeline from the defined start and end dates for the test data
test_start = dt.datetime(2024,2,2)
test_end = dt.datetime.now()

#Fetching
test_data = web.DataReader(company, 'stooq', test_start, test_end)
actual_prices = test_data['Close'].values

total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)

model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
model_inputs = model_inputs.reshape(-1,1)
model_inputs = scaler.transform(model_inputs)


#Making predicitions on test data
x_test = []

for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x-prediction_days:x, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

predicted_prices = model.predict(x_test)
predicted_prices = scaler.inverse_transform(predicted_prices)

#Plotting test predicitions
plt.plot(actual_prices, color="black", label=f"Actual {company} Price")
plt.plot(predicted_prices, color="red", label=f"Predicted {company} Price")
plt.title(f"{company} Share Price")
plt.xlabel('Time')
plt.ylabel(f'{company} Share Price')
plt.legend()
plt.show()


#Predicting oncoming price
real_data = [model_inputs[len(model_inputs) + 1 - prediction_days:len(model_inputs+1),0]]
real_data = np.array(real_data)
real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

#Prediction
prediction = model.predict(real_data)
prediction = scaler.inverse_transform(prediction)
print(f"The prediction is {prediction}")