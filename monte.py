import pandas as pd
import numpy as np
from scipy.stats import truncnorm
import bondModel
import concurrent.futures
import matplotlib.pyplot as plt
import seaborn as sns

def get_truncated_normal(mean, sd, low, upp):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


def get_pred_inflation(filename = "economic_data/predicted_inflation.csv"):
    predicted_inflation_df = pd.read_csv(filename)
    initial = predicted_inflation_df["inflation"].to_list()
    upper = predicted_inflation_df["upper"].to_list()
    lower = predicted_inflation_df["lower"].to_list()
    return initial, upper, lower


def get_intrestDic(initial, upper, lower, k = 1000):
    monteDic = {}
    
    for month in range(0, len(initial)):
        boot = get_truncated_normal(mean=initial[month], sd = 3.8, low=lower[month], upp=upper[month]).rvs(k)
        monteDic[month] = boot

    intrestDic = {}
    for inflation in range(0, k):
        symulatedInflation = []
        for month in np.arange(0, len(initial), 1):
            symulatedInflation.append(monteDic[month][inflation]) 
            intrestDic[inflation] = symulatedInflation
    
    return intrestDic

def get_modelDic(intrestDic, peroid , cost):
    modelDic = {}
    #get models and save total to modelDic where len(modelDic["COI"][0]) = peroid
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_model = {executor.submit(bondModel.get_inflation_models, intrestDic[key], peroid , cost): key for key in intrestDic.keys()}
        for future in concurrent.futures.as_completed(future_to_model):
            data = future.result()
            for key in data.keys():
                if key not in modelDic.keys():
                    modelDic[key] = [data[key]["total"].to_list()]
                else:
                    modelDic[key].append(data[key]["total"].to_list())
    
    return modelDic
                
                
def get_annualBondReturn(modelDic, peroid):
    annualBondReturn = {}

    for symbol in modelDic.keys():
        mothDic = {}
        bond = modelDic[symbol]
        
        for symumaltion in range(0, len(bond)):
            one_symumaltion = bond[symumaltion]
            
            for i in range(0, len(one_symumaltion)):
                if i not in mothDic.keys():
                    mothDic[i] = [one_symumaltion[i]]
                else:
                    mothDic[i].append(one_symumaltion[i])
        
        yearData = {}
        j = 1
        for i in range(0, peroid):
            if (i + 1) % 12 == 0:
                yearData[j] = mothDic[i]
                j += 1
                
        annualBondReturn[symbol] = yearData
        
    return annualBondReturn


def get_range_and_proc(histBondReturn, symbol, year):
    freq = histBondReturn[symbol][year][0]
    temp = np.round(histBondReturn[symbol][year][1])

    returnRange = []
    for i in range(0, len(temp) - 1):
        returnRange.append(f"{round(int(temp[i]), -1)} - {round(int(temp[i + 1]), -1)}")

    proc = []
    for num in freq:
        proc.append(round(num / sum(freq), 2))

    return returnRange, proc


def get_probDic(annualBondReturn):
    histBondReturn = {}
    probDic = {}

    for year in range(1, 13):
        minimum = float("inf")
        maximum = 0
        for symbol in annualBondReturn.keys():
            minimum = min(min(annualBondReturn[symbol][year]), minimum)
            maximum = max(max(annualBondReturn[symbol][year]), maximum)
            
        for symbol in annualBondReturn.keys():
            if symbol not in histBondReturn.keys():
                histBondReturn[symbol] = {year : np.histogram(annualBondReturn[symbol][year], range = (minimum, maximum))}
                returnRange, proc = get_range_and_proc(histBondReturn, symbol, year)
                probDic[symbol] = {year : {"returnRange" : returnRange, "percentage" : proc}}
                
            else:
                histBondReturn[symbol].update({year : np.histogram(annualBondReturn[symbol][year], range = (minimum, maximum))})
                returnRange, proc = get_range_and_proc(histBondReturn, symbol, year)
                probDic[symbol].update({year : {"returnRange" : returnRange, "percentage" : proc}})
                
    return probDic


def get_yearHeatDic(probDic):
    prob = pd.DataFrame.from_dict({(i,j): probDic[i][j] 
                           for i in probDic.keys() 
                           for j in probDic[i].keys()},
                       orient='index').reset_index()

    prob = prob.rename(columns={'level_0': 'bond', 'level_1': 'year'})

    yearHeat = {}
    for year in range(1, 13):
        yearDf = prob[prob["year"] == year]
        temp = np.array(yearDf["percentage"].to_numpy())
        bonds = yearDf["bond"].to_numpy()

        matrix = [yearDf["returnRange"].to_numpy()[0]]
        for r in temp:
            matrix.append(r)

        hope = pd.DataFrame(matrix)
        hope.columns = hope.iloc[0]
        hope = hope[1:].astype(float)
        hope["bondName"] = bonds
        hope = hope.set_index("bondName")
        
        yearHeat[year] = hope.transpose()
        
    return yearHeat

def make_heatmap(data):
    row = 3 + 1
    col = 2 + 1
    fig, ax = plt.subplots(row, col, figsize = (25, 25), dpi = 50)
    year = 1
    for r in range(0, row):
        for c in range(0, col):
            sns.heatmap(data[year], annot=True, linewidths=.5, cmap="Greens", cbar=False, ax=ax[r][c])
            ax[r][c].set_title(f"Year {year}")
            ax[r][c].set_ylabel('')    
            ax[r][c].set_xlabel('')
            year += 1
    
    plt.show()
        
    return fig


def get_inflation_monteCarloOutput(cost = 50000, peroid = 144, k = 1000):
    initial, upper, lower = get_pred_inflation()
    
    intrestDic = get_intrestDic(initial, upper, lower, k)
    modelDic = get_modelDic(intrestDic, peroid, cost)
    annualBondReturn = get_annualBondReturn(modelDic, peroid)
    probDic = get_probDic(annualBondReturn)
    yearHeat = get_yearHeatDic(probDic)
    return yearHeat


def main():
    yearHeat = get_inflation_monteCarloOutput(cost = 50000, peroid = 144, k = 10)
    make_heatmap(yearHeat)


if __name__ == "__main__":
    main()