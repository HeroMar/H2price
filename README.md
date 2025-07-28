<p align="center"><img src="Images/H2price_header.png" /></p>


## 1. Description
Program designed to calculate current price of hydrogen fuel. 
Due to the lack of a market price for this kind of fuel there was a need to calculate its value according to a created algorithm.
This algorithm takes into account latest prices of diesel oil, electricity and water in specific shares.
Information about diesel oil that prices change nearly every day are automatically imported from website.
Remaining two factors (cost of electricity and water) that in this case change so much less frequently (quarterly or even less) are entered manually in dedicated admin panel.
In addition to calculating hydrogen fuel price, the program is responsible for storing historical data and presenting them in a user-friendly form.
GUI consists of two parts - the initial one with basic information and the detailed one containing all historiacal data.


## 2. Functionality
* updating the price of hydrogen fuel that base on specific algorithm,
* storing information in a database,
* web scraping diesel oil prices,
* manual entry of energy and water prices via the administration panel,
* providing information about historical data and basic statistical parameters,
* presenting data in a user-friendly form.


## 3. Solved problems
Booting time - to reduce initialization time, the webscraping mechanism runs only once a day (during the first launch of the program). In any other case, all data are loaded from the local database that is much faster. 

Gaps in the input data - hydrogen fuel price is updating every day but related information about costs of diesel, electricity and water are not always providing with such frequency. In this case, their latest published values are taken into account until new ones appear.


## 4. Tech stack
Python 3 with specified libraries:
* sqlite3,
* pandas,
* tkinter + ttkbootstrap,
* matplotlib.

Figma for GUI design.


## 5. Showcase
<p align="center"><img src="Images/H2price_GIF.gif" width: 100%  /></p>