import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("elsa_vekt.csv")
data['Date'] = pd.to_datetime(data['Date'])

# Fill missing dates
date0 = data["Date"].iloc[0]
dateN = data["Date"].iloc[-1]
new_idx = pd.date_range(date0, dateN)
new_idx = pd.Index(new_idx, name="Date")
data_indexed = data.set_index("Date").reindex(new_idx)

# Interpolate missing weights
D = data_indexed.interpolate()
D = D.reset_index()

# Least squares
def f(theta, x):
    f = theta[0] * (1 - np.e**(-theta[1] * x))
    return f

def residuals(theta, x, y):
    func = f(theta, x)
    return (y - func)**2

def gradient(theta, x):
    return np.array([1 - np.e**(-theta[1] * x), theta[0] * x * np.e**(-theta[1] * x)])
    #return 25 * x * np.e**(-theta * x)

def hessian(theta, x):
    return np.array([[0, x * np.e**(-theta[1] * x)],
                     [x * np.e**(-theta[1] * x), -theta[0] * x**2 * np.e**(-theta[1] * x)]])

# initial values
x = D.index.to_numpy() + 234 - 108
y = D["Weight"].to_numpy()
max_iter = 10

theta = np.array([25, 0.007])
thetas = np.array([theta])
r = residuals(theta, x, y)
error = np.array([np.sum(r)])

for i in range(max_iter):
    r = residuals(theta, x, y)
    J = gradient(theta, x)

    JTJ = np.linalg.inv(np.dot(J, J.T))
    JTJJ = np.dot(JTJ, J)
    JTJJr = np.dot(JTJJ, r)
    theta += JTJJr
    thetas = np.append(thetas, [theta], axis=0)
    error = np.append(error, np.sum(residuals(theta, x, y)))


theta_min = thetas[np.argmin(error),:]
x_long = np.linspace(1,730,730)

fin_weight = theta_min[0].round(2)

plt.plot(x, y, label="Measured weight")
plt.plot(x_long, f(theta_min, x_long), linestyle="--", label="Estimate weight")
plt.plot(x_long, np.ones(len(x_long))*theta_min[0], linestyle=":", label=f"estimated final weight: {fin_weight} kg")
plt.grid()
plt.legend(loc="center right")
plt.show()