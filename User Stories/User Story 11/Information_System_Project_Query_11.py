import redis
from datetime import datetime, timedelta
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
import pandas as pd
import statsmodels.api as sm
import matplotlib

r = redis.Redis(db=0, decode_responses=True)

diseases = []

for key in r.scan_iter("DISEASE:H:*"):
        return_value = r.hkeys(key)
        for i in range(len(return_value)):
                if return_value[i] not in diseases:
                        diseases.append(return_value[i])

print(f"We have historical data for the diseases {diseases} \nPlease enter the Disease to forecast")
inp = input()

if inp == '' or inp.upper() not in diseases:
        print(f"We do not have {inp} disease history in out database. Please try again.")
        exit()

matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12
matplotlib.rcParams['text.color'] = 'k'

dates = []
keys = []
values = []
country = []

for key in r.scan_iter("DISEASE:H:*"):
        return_keys = r.hkeys(key)
        for i in range(len(return_keys)):
                if return_keys[i] == inp.upper():
                        hash_date = datetime.strptime(key.split(':')[3], "%Y-%m").date()
                        country.append(key.split(':')[2])
                        dates.append(hash_date)
                        keys.append(return_keys[i])
                        return_values = r.hget(key, return_keys[i])
                        values.append(return_values)

if dates==[] or values==[]:
        print("Sorry right now we are facing issue with retreiving values from Redis. Please contact responsible.")
        exit()

df = pd.DataFrame(zip(dates, values), columns=('dates', 'values'))

df['values'] = df['values'].astype(float)

max_date = df['dates'].max()

print(f"We have historical data for Disease {inp.upper()} until {max_date}")
print("Please enter the number of weeks to forecast e.g. 10")
inp_fc = input()

try:
    float(inp_fc)
except ValueError:
    print(f"{inp_fc} is not a number. Please try again by giving number")
    exit()
        
if float(inp_fc) > 100:
        print(f"Input {inp_fc} weeks has crossed maximum limit. Please try again by giving number within 100")
        exit()

forecast_date = max_date + timedelta(weeks= float(inp_fc))

df = df.sort_values('dates')
df = df.groupby('dates')['values'].sum().reset_index()
df = df.set_index('dates')
df.index = pd.to_datetime(df.index)

y = df['values'].resample('MS').mean()

mod = sm.tsa.statespace.SARIMAX(y,
                                order=(1, 1, 1),
                                seasonal_order=(0, 1, 1, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

pred_uc = results.get_prediction(start=max_date, end=forecast_date, dynamic=False)
pred_ci = pred_uc.conf_int()
ax = y.plot(label='observed', figsize=(14, 6))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Years')
ax.set_ylabel(f'Disease "{inp.upper()}" registered cases')
plt.legend()
plt.show()
