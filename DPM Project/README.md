## Guidelines

- "Project.py" is the main file containing the python source code for the web application. The HTML files corresponding to the webpages exist in the "templates" folder, and the CSS files, along with various supporting image files, are contained in the "static" folder. The files "movies_1.csv" and "movies_2.csv" collectively comprise our web-series/movies database.

- For a decent user experience, open the web app on a standard 14-inch laptop.

- Create your user id and password to signup, or type "Arghya" on the user id field and "MT21014@iiitd" on the password field to log in to an existing account. Passwords are stored in encrypted form in the "Users.csv" file. The application ensures that all user ids are distinct.

- A successful signup/login attempt will redirect to the page containing the user's favorites list. On this page, the user can remove items from his favorites list. Additionally, the user has the choice of proceeding either to the search page or to the recommendations page. He can also directly log out from here.

- The search page allows users to search movies based on genre, director names, start year, and minimum ratings. The director-name field even accepts partial and slightly erroneous director names as input. All fields other than the genre field are optional. Ten most appropriate search results matching the given input are always displayed as output in a tabular form in order of rating and popularity. This page also empowers users to add movies to their favorites list. The addition process ensures that the favorites list will never contain duplicate entries.

- The recommendation page always recommends ten movies based on the individual's favorites list. The recommendations can be of the most relevant series or the most recent series. Like the search results, the recommendations also appear in sorted order. The recommendation is primarily based on the most frequently occurring genres and director names appearing in the user's favorites list.




