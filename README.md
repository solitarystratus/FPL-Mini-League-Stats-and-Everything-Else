hopeitworks2.py is my code for whatever I did. Thanks to ChatGPT and Codeium AI, I somehow ended up making something that works to a manageable extent. 
This program fetches data from the official FPL site. Right now I left it with no options for user input. My input is the mini-league code of PlayFantasy365.
So once we get all the data, we convert the data into a pandas dataframe. 
The pagination thing doesn't work, I learned it from Codeium but it's useless here. The API always gives data of the first page so it's better to stick to the mini leagues.
Anyway, the code takes sum of GW 2 and GW 3 points as well as GW 1, GW 2 and GW 3 points, separately.
The pairings are random and unique. In each 1v1 pairing, the manager with more points is declared as winner and the other one is, well, loser. 
So once we're done with sums, pairings, declaring winners and likes of me (Losers), we proceed towards creating an Excel file. 
The excel file has three sheets. First one contains whatever we got from the website itself, i.e, manager name, team name and total points. Second and third sheets have two different pairings. Second one has the total of GW 2 and GW 3 points, while the third one has the total of GW1, GW2 and GW3 points.
Once I run the code, I get the excel file. Yay! Done. Toodles!
