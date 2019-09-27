# Hacker News Saltines

[Data Science Flask App](https://saltines.herokuapp.com/) 

[Build Week App](https://saltines.now.sh/)

The Flask app mimics the design of Hacker News while using the Lambda School color scheme. Currently it provides five JSON endpoints.

## 1. Top 100 Salty Users
Returns a dict of the 100 users with the highest average salt scores.

Endpoint: [https://saltines.herokuapp.com/salty-users](https://saltines.herokuapp.com/salty-users)

Sample command: `curl https://saltines.herokuapp.com/salty-users`

Returns: `{"Aloha":-1.5098,"BoppreH":-3.2191,"Dewie3":-1.5155,"Dilpil":-2.0146,"GHFigs":-4.1276,"Guvante":-1.5535,"Nick_C":-1.8424, ... }`

## 2. Top 100 Salty Comments

Returns a dict of the 100 comments with the highest salt scores.

Endpoint: [https://saltines.herokuapp.com/salty-comments](https://saltines.herokuapp.com/salty-comments)

Sample command: `curl https://saltines.herokuapp.com/salty-comments`

Returns: `{"Fuck war, too? Right?":-1.6249, "No":-1.296, ... }`

## 3. Which hours of the day has the saltiest comments

Returns a dict of the hours of the day and the number of comments which score below -0.5.

Endpoint: [https://saltines.herokuapp.com/salty-hours](https://saltines.herokuapp.com/salty-hours)

Sample command: `curl https://saltines.herokuapp.com/salty-hours`

Returns: `{"0.0":35,"1.0":41,"2.0":24,"3.0":39,"4.0":28,"5.0":23,"6.0":23,"7.0":14,"8.0":20,"9.0":28,... "23.0":43}`

## 4. Which day of the week has the saltiest comments

Returns a dict of days of the week and the the number of comments which score below -0.5. Mondays are 1.0.

Endpoint: [https://saltines.herokuapp.com/salty-days](https://saltines.herokuapp.com/salty-days)

Sample command: `curl https://saltines.herokuapp.com/salty-days`

Returns: `{"1.0":128,"2.0":124,"3.0":141,"4.0":144,"5.0":158,"6.0":95,"7.0":117}`

## 5. Top 10 saltiest comments of a user

Returns a dict of comments and scores of a given user

Endpoint: [https://saltines.herokuapp.com/user-comments/(username)](https://saltines.herokuapp.com/user-comments/(name))

Sample command: `curl https://saltines.herokuapp.com/user-comments/patio11`

Returns: `{"* What justifies the laws that compelled my parents to send me to a place they knew (at some level) was hurting me? Benign paternalism which says \"X% of students really dislike the experience of attending school.  The average case for dropouts is 'totally $&#38;$#ed.'  We'll institutionalize them now because it is a darn sight cheaper than institutionalizing them later, permanently.\"":-0.731 ... }`


![Data Pipeline Flow](Data%20Pipeline%20Flow.png)


<!--
A simple flask app following HN design. Returns the saltiest users, saltiest comments, and saltiness by time.
![Screenshots](app_proof.png)
-->
