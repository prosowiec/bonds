# Bonds
Estimates return of bonds investments over time using ARIMA and Monte Carlo simulation, project still in development. In this repo I tried to quantify uncertainty in economic data, knowing that it is almost impossible to always be right in predicting the future, as it is hard to predict an indicator that is not solely based on hard data, but for example can be influenced by politicians.

<a href="https://drive.google.com/uc?export=view&id=1u-9RW3p9vL15QmSJa6RJoOdAuJZsqFMK"><img src="https://drive.google.com/uc?export=view&id=1u-9RW3p9vL15QmSJa6RJoOdAuJZsqFMK" style="width: 650px; max-width: 100%; height: auto" title="Click to enlarge picture" />

## How to interpret the above graph?
For each value predicted by the ARIMA model, I gave it a normal distribution where the least expected value is a lower prediction interval and the highest is an upper interval. The standard deviation is 3.8 which corresponds to historical data. After giving distributions, the algorithm performs k simulations where return ranges and probabilities are established. So given all of this knowledge when looking at this graph we can check how ranges of returns change over time and which bond type is going to perform the best in a given economic environment. 


<a href="https://drive.google.com/uc?export=view&id=1jMMweh2AKCaDHcKRDiRPkauaRRmPp8FL"><img src="https://drive.google.com/uc?export=view&id=1jMMweh2AKCaDHcKRDiRPkauaRRmPp8FL" style="width: 650px; max-width: 100%; height: auto" title="Click to enlarge picture" />
