#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ! pip install numpy
# ! pip install pandas 
# ! pip install flask 
# ! pip install cryptography
# ! pip install regex
# ! pip install fuzzywuzzy 


# In[2]:


# #### Dataset-preparation module ####

# import pandas as pd

# basics_df = pd.read_csv("title.basics.tsv", sep = '\t')
# crew_df = pd.read_csv("title.crew.tsv", sep = '\t')
# ratings_df = pd.read_csv("title.ratings.tsv", sep = '\t')
# movies_df = pd.merge(basics_df, crew_df, on = "tconst")
# movies_df = pd.merge(movies_df, ratings_df, on = "tconst")
# movies_df = movies_df[["tconst", "originalTitle", "startYear", "genres", "directors", "averageRating", "numVotes"]]
# movies_df.dropna(inplace = True)
# movies_df = movies_df[(movies_df["originalTitle"] != "\\N") & (movies_df["startYear"] != "\\N") &
#                       (movies_df["genres"] != "\\N") & (movies_df["directors"] != "\\N") &
#                       (movies_df["averageRating"] != "\\N") & (movies_df["numVotes"] != "\\N")]
# movies_df = movies_df[movies_df["directors"].apply(lambda x: len(x) < 15)]
# movies_df.reset_index(inplace = True, drop = True)

# names_df = pd.read_csv("name.basics.tsv", sep = '\t')
# names_df = names_df[["nconst", "primaryName"]]
# names_df.dropna(inplace = True)
# names_df = names_df[(names_df["primaryName"] != "\\N")]
# names_df.rename(columns = {"nconst":"directors"}, inplace = True)
# names_df.reset_index(inplace = True, drop = True)

# movies_df = pd.merge(movies_df, names_df, on = "directors")
# movies_df = movies_df[movies_df["startYear"].apply(lambda x: int(x) > 2005)]
# movies_df.to_csv("movies.csv", index = False)

# movies_df = pd.read_csv("movies.csv")
# movies_df_1 = movies_df.loc[:movies_df.shape[0] / 2, :]
# movies_df_2 = movies_df.loc[movies_df.shape[0] / 2:, :]
# movies_df_1.to_csv("movies_1.csv")
# movies_df_2.to_csv("movies_2.csv")


# In[ ]:


'''
Enter the following details on login page for a successful login:
1. Select radio button labeled as "Existing User"
2. Type "Arghya" on User field
3. Type "MT21014@iiitd" on Password field
A successful login attempt will redirect to the next page containing the user's favourites list.
'''

import numpy as np
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
from cryptography.fernet import Fernet
import re
from fuzzywuzzy import process
import os 
from itertools import combinations

pd.set_option("colheader_justify", "center")

user_id_retained, n = "", 0
html_string = '''<!DOCTYPE html>
<html lang = "en">
    <head>
        <link rel = "stylesheet" href = "style4.css"/>
    </head>
    <body>
        {table}
    </body>
</html>'''

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():
    
    global n, html_string
    n = 0
    
    users_df = pd.read_csv("Users.csv")
    key = bytes.fromhex("47513459507931446361376559686c66394971506f4353725a34453846664354413155506f4f6e4a7755493d")
    fernet = Fernet(key)
    user_id = ""
    password = ""
    user_type = ""
    message = "Please enter the desired search criteria and press the enter button."
    
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")
        user_type = request.form.get("user_type")
    
    if user_type == "New User":
        if user_id == "":
            message = "User Id cannot be empty!"
        elif user_id in users_df["User ID"].values:
            message = "User Id already exists!\nPlease try a different one."
        elif len(password) < 8:
            message = "Password must be at least eight characters long!"
        else: 
            enc_password = fernet.encrypt(password.encode())
            users_df = users_df.append({"User ID": user_id, "Password": enc_password.decode()}, ignore_index = True)
            users_df.to_csv("Users.csv", index = False)
            message = "User details have been saved successfully!"
    elif user_type == "Existing User":
        user_list = users_df.index[users_df["User ID"] == user_id].tolist()
        if user_id == "":
            message = "User Id cannot be empty!"
        elif len(user_list) == 0:
            message = "Invalid user name!"
        elif password != fernet.decrypt(users_df.iloc[user_list[0]]["Password"].encode()).decode():
            message = "Invalid password!"
        else:
            return redirect(url_for("user_homepage", user_id = user_id))
    else:
        message = "Please select a user type."
    
    return render_template("Index.html", message = message)


@app.route("/user_homepage/<user_id>", methods = ["GET", "POST"])
def user_homepage(user_id):
    
    global user_id_retained, n, html_string               
    if n == 0:
        user_id_retained = user_id          
    n += 1                         
    
    favourites_file_path = "Favourites/" + user_id_retained + ".csv"
    if os.path.exists(favourites_file_path):
        favourites_df = pd.read_csv(favourites_file_path, index_col = 0)
    else:
        favourites_df = pd.DataFrame(columns = ["originalTitle", "startYear", "genres", "primaryName", 
                                                "averageRating", "numVotes"])
    favourites_df_ = favourites_df.rename(columns = {"originalTitle":"Series Name", 
                                                    "startYear":"Start Year",
                                                    "genres":"Genres", "primaryName":"Directed By", 
                                                    "averageRating" : "Rating", "numVotes":"Votes"})  
    
    temp_favourites_html = open("static/temp_favourites.html", "w")
    temp_favourites_html.write(html_string.format(table = favourites_df_.to_html()))
    temp_favourites_html.close()
    
    action_type = ""
    favourites_removal_str = ""
    message = "Please select an option and click on the enter button to proceed."
    flag = 0

    if request.method == "POST":
        
        action_type = request.form.get("action_type")
        favourites_removal_str = request.form.get("favourites_removal").strip()
        
        if not bool(re.match("(\d+)(\s*,\s*\d+)*$", favourites_removal_str)):
                flag, message = 1, "Invalid entry in favourites-removal field!"
        
    if action_type == "Search movies":   
        return redirect(url_for("movie_search", user_id = user_id_retained))
    elif action_type == "Get movie recommendation":
        return redirect(url_for("movie_recommendation", user_id = user_id_retained))
    elif action_type == "Remove favourites" and flag == 0:
        old_len = favourites_df.shape[0]
        favourites_removal = favourites_removal_str.replace(" ", "").split(",")
        favourites_removal = set([int(i) for i in favourites_removal]).intersection(favourites_df.index)
        favourites_df = favourites_df.drop(favourites_removal)
        favourites_df.to_csv(favourites_file_path)
        favourites_df_ = favourites_df.rename(columns = {"originalTitle":"Series Name", 
                                                    "startYear":"Start Year",
                                                    "genres":"Genres", "primaryName":"Directed By", 
                                                    "averageRating" : "Rating", "numVotes":"Votes"}) 
        temp_favourites_html = open("static/temp_favourites.html", "w")
        temp_favourites_html.write(html_string.format(table = favourites_df_.to_html()))
        temp_favourites_html.close()
        new_len = favourites_df.shape[0]
        
        if old_len == new_len:
            message = "No existing entry has been removed from favourites list!"
        else:
            message = str(old_len - new_len) + " existing entries have been removed from favourites list!"
        
    
    return render_template("User Homepage.html", message = message)
        

@app.route("/movie_search/<user_id>", methods = ["GET", "POST"])
def movie_search(user_id):
    
    global user_id_retained, html_string
    
    movies_df_1 = pd.read_csv("movies_1.csv", index_col = 0)
    movies_df_2 = pd.read_csv("movies_2.csv", index_col = 0)
    movies_df = pd.concat([movies_df_1, movies_df_2])
    movies_df["score"] = movies_df.averageRating * movies_df.numVotes
    movie_search_result_df = pd.DataFrame(columns = ["originalTitle", "startYear", "genres", "primaryName", 
                                                "averageRating", "numVotes"])

    genres = movies_df["genres"].str.split(",")
    genres = genres.to_numpy()
    genres = np.concatenate(genres)
    genres = np.unique(genres)
    
    action_type = ""
    chosen_genre = ""
    chosen_director = ""
    chosen_rating = movies_df["averageRating"].min()
    start_year = movies_df["startYear"].min()
    end_year = movies_df["startYear"].max()
    favourites_addition = ""
    recommendation_count = 0
    minimum_director_matching_score = 85
    message = "Please select an option, fill the desired fields, and press the enter button."
    flag = 0

    if request.method == "POST":
        
        action_type = request.form.get("action_type")
        chosen_genre = request.form.get("chosen_genre")
        chosen_director_str = request.form.get("chosen_director").strip()
        start_year_str = request.form.get("start_year").strip()
        chosen_rating_str = request.form.get("chosen_rating").strip()
        favourites_addition_str = request.form.get("favourites_addition").strip()
        
        if chosen_director_str != "":
            if bool(re.match("[a-zA-Z\s]+$", chosen_director_str)):
                chosen_director = chosen_director_str
            else:
                flag = 1
        if start_year_str != "":
            if start_year_str.isdecimal():
                if ((int(start_year_str) < movies_df["startYear"].min()) or (int(start_year_str) > movies_df["startYear"].max())):
                    flag = 2
                else:
                    start_year = int(start_year_str)
                    end_year = start_year + 1
            else:
                flag = 3
        if chosen_rating_str != "":
            if bool(re.match("[0-9]{0,2}(\.[0-9]{1,2})?$", chosen_rating_str)):
                chosen_rating = float(chosen_rating_str)
            else:
                flag = 4 
        if not bool(re.match("(\d+)(\s*,\s*\d+)*$", favourites_addition_str)):
                flag = 5
        recommendation_count = 10
        
    if action_type == "Search movies" and flag in [1, 2, 3, 4]:
        if flag == 1:
            message = "Invalid director name!"
        elif flag == 2:
            message = ("Start year should range from " + str(movies_df["startYear"].min()) + 
                       " to " + str(movies_df["startYear"].max()) + "!")
        elif flag == 3:
            message = "Invalid start year!"
        elif flag == 4:
            message = "Invalid rating!"
    if action_type == "Add movies to favorites" and flag == 5:
        message = "Invalid entry in favourites-addition field!"
            
    if action_type == "Search movies" and flag not in [1, 2, 3, 4]:     
        movie_search_result_df = movies_df
        movie_search_result_df = movie_search_result_df[movie_search_result_df["genres"].str.contains(chosen_genre)]
        iteration_count = 0
        while iteration_count <= 5:
            iteration_count += 1
            movie_search_result_df_ = movie_search_result_df

            if iteration_count == 1:  
                if chosen_rating >= 9:
                    chosen_rating = 8
            elif iteration_count == 2:  
                if chosen_rating >= 8:
                    chosen_rating = 7
                elif end_year - start_year <= 2:
                    start_year -= 1
                    end_year += 1
                minimum_director_matching_score -= 5
            elif iteration_count == 3: 
                if chosen_rating >= 7:
                    chosen_rating = 6
                if end_year - start_year <= 4:
                    start_year -= 2
                    end_year += 2
                elif end_year - start_year <= 5:
                    start_year -= 3
                    end_year += 3
                minimum_director_matching_score -= 10
            elif iteration_count == 4:
                if chosen_rating >= 6:
                    chosen_rating = 5
                start_year = movies_df["startYear"].min()
                end_year = movies_df["startYear"].max()
                minimum_director_matching_score -= 20
            elif iteration_count == 5:
                chosen_rating = movies_df["averageRating"].min()
                minimum_director_matching_score = 0

            if chosen_director != "":
                matching_directors = process.extractBests(chosen_director, movie_search_result_df_["primaryName"], 
                                                          score_cutoff = minimum_director_matching_score, 
                                                          limit = movies_df.shape[0])
                movie_search_result_df_ = movie_search_result_df_.loc[[matching_director[2] for matching_director in 
                                                                       matching_directors]]

            movie_search_result_df_ = movie_search_result_df_[(movie_search_result_df_["startYear"] >= start_year) & 
                                                          (movie_search_result_df_["startYear"] <= end_year)]

            movie_search_result_df_ = movie_search_result_df_[(movie_search_result_df_["averageRating"] >= chosen_rating)]

            movie_search_result_df_ = movie_search_result_df_.nlargest(recommendation_count, ["score", "startYear"])

            if movie_search_result_df_.shape[0] >= recommendation_count:
                break

        movie_search_result_df = movie_search_result_df_[["originalTitle", "startYear", "genres", "primaryName", 
                                                      "averageRating", "numVotes"]]
        if recommendation_count != 0:
            message = "Desired result has been successfully fetched!"
    
    elif action_type == "Add movies to favorites" and flag != 5: 
        old_len, new_len = 0, 0
        favourites_file_path = "Favourites/" + user_id_retained + ".csv"
        if os.path.exists(favourites_file_path):
            favourites_df = pd.read_csv(favourites_file_path, index_col = 0)
        else:
            favourites_df = pd.DataFrame(columns = ["originalTitle", "startYear", "genres", "primaryName", 
                                                "averageRating", "numVotes"])
        old_len = favourites_df.shape[0]
        movies_df_temp = movies_df[["originalTitle", "startYear", "genres", "primaryName", 
                                                      "averageRating", "numVotes"]]
        favourites_addition = favourites_addition_str.replace(" ", "").split(",")
        favourites_addition = set([int(i) for i in favourites_addition]).intersection(movies_df_temp.index)
        favourites_df = pd.concat([favourites_df, movies_df_temp.loc[favourites_addition]]).drop_duplicates()
        favourites_df = favourites_df[["originalTitle", "startYear", "genres", "primaryName", 
                                                      "averageRating", "numVotes"]]
        favourites_df.to_csv(favourites_file_path)
        new_len = favourites_df.shape[0]
        
        if old_len == new_len:
            message = "No new entry has been added to favourites list!"
        else:
            message = str(new_len - old_len) + " new entries have been added to favourites list!"
        
    movie_search_result_temp_df = movie_search_result_df.rename(columns = {"originalTitle":"Series Name", 
                                                                           "startYear":"Start Year",
                                                                           "genres":"Genres", "primaryName":"Directed By", 
                                                                           "averageRating" : "Rating", "numVotes":"Votes"})
    
    temp_search_result_html = open("static/temp_search_result.html", "w")
    temp_search_result_html.write(html_string.format(table = movie_search_result_temp_df.head(10).to_html()))
    temp_search_result_html.close()
    
    return render_template("Movie Search.html", genres = genres, message = message, user_id = user_id_retained)
    

@app.route("/movie_recommendation/<user_id>", methods = ["GET", "POST"])
def movie_recommendation(user_id):    

    global user_id_retained, html_string
    
    movies_df_1 = pd.read_csv("movies_1.csv", index_col = 0)
    movies_df_2 = pd.read_csv("movies_2.csv", index_col = 0)
    movies_df = pd.concat([movies_df_1, movies_df_2])
    movies_df["score"] = movies_df.averageRating * movies_df.numVotes
    
    chosen_filter = "latest"
    message = "Please select a filter type and press the enter button."
    flag = 0
    
    recommended_movies_df = pd.DataFrame(columns = ["originalTitle", "startYear", "genres", "primaryName", 
                                                    "averageRating", "numVotes"])
    recommended_movies_df_ = pd.DataFrame(columns = ["originalTitle", "startYear", "genres", "primaryName", 
                                                     "averageRating", "numVotes"])
    
    if request.method == "POST":
        chosen_filter = request.form.get("filter_type")
        flag = 1

    if flag == 1:
        favourites_file_path = "Favourites/" + user_id_retained + ".csv"    
        if os.path.exists(favourites_file_path):
            favourites_df = pd.read_csv(favourites_file_path, index_col = 0)
        else:
            favourites_df = pd.DataFrame(columns = ["originalTitle", "startYear", "genres", "primaryName", 
                                                        "averageRating", "numVotes"])

        favourite_genres_and_directors = favourites_df["genres"].str.split(",").to_numpy()
        for i in range(favourite_genres_and_directors.shape[0]):
            favourite_genres_and_directors[i].append(favourites_df["primaryName"].values[i])

        frequent_items_list = []
        for i in range(favourite_genres_and_directors.shape[0]):
            li1 = list(combinations(favourite_genres_and_directors[i], 2))
            if len(li1) > 0:
                for j in range(len(li1)):
                    frequent_items_list.append(li1[j])
            li2 = list(combinations(favourite_genres_and_directors[i], 3))
            if len(li2) > 0:
                for j in range(len(li2)):
                    frequent_items_list.append(li2[j])
        
        if len(frequent_items_list) < 10:
            message = "Please add a few more movies to your favourites list to get a personalized recommendation!"
        else:
            li1, li2, li3 = [], [], []
            for i in set(frequent_items_list):
                li1.append(i)
                li2.append(frequent_items_list.count(i))
                li3.append(len(i))   
            frequent_items_df = pd.DataFrame(list(zip(li1, li2, li3)), 
                             columns = ["Tuples", "Frequency", "Tuple size"]).nlargest(10, ["Frequency", "Tuple size"])
            frequent_items_df.reset_index(inplace = True, drop = True)

            merged_genres_and_directors = movies_df["genres"] + "," + movies_df["primaryName"]
            merged_genres_and_directors = merged_genres_and_directors.str.split(",")
            merged_genres_and_directors_df = merged_genres_and_directors.to_frame("Items")

            for i in range(frequent_items_df.shape[0]):
                s = set(frequent_items_df.loc[i]["Tuples"])
                temp_df = merged_genres_and_directors_df[merged_genres_and_directors_df["Items"].apply(
                                                 lambda x: len(set(x) & s) == len(s))]
                if chosen_filter == "latest":
                    temp_df = movies_df.loc[temp_df.index.difference(favourites_df.index)].nlargest(2, ["startYear", "score"])
                elif chosen_filter == "relevance":
                    temp_df = movies_df.loc[temp_df.index.difference(favourites_df.index)].nlargest(2, ["score", "startYear"])
                if temp_df.shape[0] == 2:
                    temp_df_ = temp_df.loc[temp_df.index[1:2]]
                    recommended_movies_df_ = pd.concat([recommended_movies_df_, temp_df_]).drop_duplicates() 
                    temp_df = temp_df.loc[temp_df.index[0:1]]
                recommended_movies_df = pd.concat([recommended_movies_df, temp_df]).drop_duplicates()
            if recommended_movies_df.shape[0] < 10:
                recommended_movies_df = pd.concat([recommended_movies_df, recommended_movies_df_]).drop_duplicates()
                
            message = "Desired result has been successfully fetched!"
    
    recommended_movies_df = recommended_movies_df[["originalTitle", "startYear", "genres", "primaryName", 
                                                     "averageRating", "numVotes"]]
    recommended_movies_df = recommended_movies_df.rename(columns = {"originalTitle":"Series Name", 
                                                                    "startYear":"Start Year",
                                                                    "genres":"Genres", "primaryName":"Directed By", 
                                                                    "averageRating" : "Rating", "numVotes":"Votes"})
       
    temp_recommendations_html = open("static/temp_recommendations.html", "w")
    temp_recommendations_html.write(html_string.format(table = recommended_movies_df.head(10).to_html()))
    temp_recommendations_html.close()
    
    return render_template("Movie Recommendation.html", message = message, user_id = user_id_retained)


if __name__ == '__main__':
    app.run(debug = False, host = "0.0.0.0")

