Title - User Story 11

Synopsis - This document is the guide to run User Story 11 in their environment

User Story - Due to the recent rise in malaria cases due to seasonal natural occurrences like floods the government wants to predict the number of patients that would be affected during that season in the future year to take necessary action

Prerequisites - Following are the database and code related prequisites that need to be fullfilled before running the script.

1. Database - 	a. Redis server should be up and running.
		b. Data should have been inserted in to Redis database.

2. Code - 	a. Install python packages (redis, datetime, pandas, matplotlib, statsmodel)


Inputs - The python program asks users for following input -
		a. User will be notified with exising diseases historical information (e.g. We have historical data for the diseases ['MEASLES', 'RUBELLA'])
		b. Disease name - "Please enter the Disease to forecast" (Enter the Disease name from the notified diseases)
		c. User will be notified with the available historical date of disease
		d. Weeks to forecast - "Please enter the number of weeks to forecast e.g. 10" (Enter the number of weeks to forecast the disease severity)
