import pymysql

db  = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="db_lab1",charset="utf8")

# 向数据库中增加项

# 增加一部电影，包括导演
def insert_movie(title, year, rating, director, genre, region):
    movieID = 0
    genrelist = genre[1:-1].split(',')
    regionlist = region[1:-1].split(',')
    for genre in genrelist:
        genre = genre[1:-1]
    for region in regionlist:
        region = region[1:-1]

    cursor = db.cursor()
    
    insert_movie_sql = "INSERT INTO Movie (title, `year`, avg_rating) VALUES (\"" + title+"\", \"" + year + "\", \"" + rating +"\");"
    select_movieID_sql = "SELECT movieID FROM Movie WHERE title=\"" +title +"\";"

    print(title)
    cursor.execute(insert_movie_sql)
    db.commit()
    cursor.execute(select_movieID_sql)
    movieID = cursor.fetchone()[0]
    print(movieID)
    
    genre_num = len(genrelist)
    region_num = len(regionlist)

    insert_direct_sql = "INSERT INTO Direct (movieID, director_name) VALUES (\"" + str(movieID)+"\", \"" + director +"\");"
    cursor.execute(insert_direct_sql)
    for i in range(genre_num):
        insert_genres_sql = "INSERT INTO genres (movieID, genre) VALUES (\"" + str(movieID)+"\", \"" + genrelist[i] +"\");"
        cursor.execute(insert_genres_sql)
    for i in range(region_num):
        insert_produc_sql = "INSERT INTO produce_countries (movieID, \
            produce_country) VALUES (\"" + str(movieID)+"\", \"" + regionlist[i] +"\");"
        cursor.execute(insert_produc_sql)
    db.commit()
    return movieID

# 增加一个演员
def insert_actor(movieID, actor_role):
    actor_name = actor_role[0]
    role_name = actor_role[1]
    cursor = db.cursor()
    insert_actin_sql = "INSERT INTO Act_in (movieID, actor_name, role) VALUES (\"" + str(movieID)+"\", \"" + actor_name+"\", \"" + role_name + "\");"

    try:
        cursor.execute(insert_actin_sql)
        db.commit()
    except:
        db.rollback()

# 删除数据库中的项

# 删除一个用户及其发表的评论、创建的片单、关注他的用户
def delete_user(userID):
    cursor = db.cursor() 
    delete_user_sql = "DELETE FROM _User WHERE userID=\""+str(userID)+"\";"
    try:
        cursor.execute(delete_user_sql)
        db.commit()
    except:
        db.rollback()

# 删除一部电影
def delete_movie(movieID):
    cursor = db.cursor()
    print(movieID)
    delete_movie_sql = "DELETE FROM Movie WHERE movieID=" +str(movieID) + ";"
    cursor.execute(delete_movie_sql)
    db.commit() 

# 删除一个导演
def delete_director(director_name):
    cursor = db.cursor()
    delete_director_sql = "DELETE FROM Direct WHERE director_name=\"" +str(director_name) + "\";"
    try:
        cursor.execute(delete_director_sql)
        db.commit()
    except:
        db.rollback() 

# 删除一个演员
def delete_actor(actor_name):
    cursor = db.cursor()
    delete_actor_sql = "DELETE FROM Act_in WHERE actor_name=\"" +str(actor_name) + "\";"
    try:
        cursor.execute(delete_actor_sql)
        db.commit()
    except:
        db.rollback() 

# 修改数据库中的项

# 修改一部电影、导演、演员、制片的信息
def update_movie(movieID, title, year, rating, director, genre, region):
    genrelist = genre[1:-1].split(', ')
    regionlist = region[1:-1].split(',')
    for i in range(len(genrelist)):
        genrelist[i] = genrelist[i][1:-1]
    for i in range(len(regionlist)):
        regionlist[i] = regionlist[i][1:-1]
    print(genrelist)
    cursor = db.cursor()
    
    update_movie_sql = "UPDATE Movie SET title = \"" + title + "\", `year` = \"" + year + "\", avg_rating = \""+rating+"\" WHERE movieID = "+str(movieID)+";"
    # select_movieID_sql = "SELECT movieID FROM Movie WHERE title=\"" +title +"\";"

    print(title)
    cursor.execute(update_movie_sql)
    db.commit()
    # cursor.execute(select_movieID_sql)
    # movieID = cursor.fetchone()[0]
    print(movieID)
    delete_genre_sql = "DELETE FROM genres WHERE movieID = " + str(movieID) + ";"
    delete_region_sql = "DELETE FROM produce_countries WHERE movieID = " + str(movieID) + ";"
    cursor.execute(delete_genre_sql)
    cursor.execute(delete_region_sql)

    genre_num = len(genrelist)
    region_num = len(regionlist)

    update_direct_sql = "UPDATE Direct SET director_name = \"" + director + "\" WHERE movieID = "+str(movieID)+";"
    cursor.execute(update_direct_sql)
    for i in range(genre_num):
        insert_genres_sql = "INSERT INTO genres (movieID, genre) VALUES (" + str(movieID) + ", \"" + genrelist[i] + "\");" 
        cursor.execute(insert_genres_sql)
    for i in range(region_num):
        insert_region_sql = "INSERT INTO produce_countries (movieID, produce_country) VALUES (" + str(movieID) + ", \"" + regionlist[i] + "\");"
        cursor.execute(insert_region_sql)
    db.commit()

def update_director(ori_name, director_name, director_gender, director_birth):
    update_director_sql = "UPDATE Direct SET director_name = \"" + director_name + "\", director_gender = \"" + director_gender + "\", director_birthdate = \"" + director_birth + "\" WHERE director_name = \"" + ori_name + "\";"
    cursor = db.cursor()
    cursor.execute(update_director_sql)


def update_actor_role(movieID, actor_role):
    actor_name = actor_role[0]
    role_name = actor_role[1]
    print(actor_name)
    print(role_name)
    cursor = db.cursor()

    delete_actin_sql = "DELETE FROM Act_in WHERE movieID = " + str(movieID) + ";"

    insert_actin_sql = "INSERT INTO Act_in (movieID, actor_name, role) VALUES (" + str(movieID) + ", \"" + actor_name + "\", \"" + role_name + "\");"

    # try:
    cursor.execute(delete_actin_sql)
    cursor.execute(insert_actin_sql)
    #     db.commit()
    # except:
    #     db.rollback()

def update_actor(ori_name, actor_name, actor_gender, actor_birth):
    update_actor_sql = "UPDATE Act_in SET actor_name = \"" + actor_name + "\", actor_gender = \"" + actor_gender + "\", actor_birthdate = \"" + actor_birth + "\" WHERE actor_name = \"" + ori_name + "\";"
    cursor = db.cursor()
    cursor.execute(update_actor_sql)

# 查询数据库中的项

# 按照类型、出产国家、导演、参演演员、标题查找一部电影
def select_movie(movie_info):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    title = movie_info['title'] 
    genre = movie_info['genre']
    region = movie_info['region']
    actor_name = movie_info['actor']
    director_name = movie_info['director']

    select_movie_sql = "SELECT DISTINCT movieID, title, `year`, avg_rating FROM movie_info WHERE title LIKE \'%"+title+"%\' and genre Like \'%"+genre+"%\' and produce_country Like \'%"+region+"%\' and actor_name Like \'%"+actor_name+"%\' and director_name Like \'%"+director_name+"%\';"
    # print(select_movie_sql)
    cursor.execute(select_movie_sql)
    movies = cursor.fetchall()

    return movies

def get_movie_details(movieID):
    cursor = db.cursor(pymysql.cursors.DictCursor)

    select_movie_sql = "SELECT * FROM movie_info WHERE movieID = "+str(movieID)+";"
    # print(select_movie_sql)
    cursor.execute(select_movie_sql)
    raw_movie_info = cursor.fetchall()
    movie_info = {}
    # movie_info['movieID'] = raw_movie_info[0]['movieID']
    movie_info['title'] = raw_movie_info[0]['title']
    movie_info['year'] = raw_movie_info[0]['year']
    movie_info['avg_rating'] = raw_movie_info[0]['avg_rating']
    movie_info['director'] = raw_movie_info[0]['director_name']
    movie_info['producer'] = raw_movie_info[0]['director_name']
    movie_info['genre'] = set()
    movie_info['region'] = set()
    movie_info['actor_role'] = set()

    for item in raw_movie_info:
        movie_info['genre'].add(item['genre'])
        movie_info['region'].add(item['produce_country'])
        movie_info['actor_role'].add((item['actor_name'], item['role']))
    return movie_info

# 按姓名查询导演
def select_director(director_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    select_director_sql = "SELECT DISTINCT director_name, director_gender, director_birthdate FROM Direct WHERE director_name LIKE \'%"+director_name+"%\';"
    cursor.execute(select_director_sql)
    director = cursor.fetchall()
    return director

def get_director_details(director_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)

    select_director_sql = "SELECT * FROM director_movie WHERE director_name = \""+director_name+"\";"
    # print(select_movie_sql)
    cursor.execute(select_director_sql)
    raw_director_info = cursor.fetchall()
    # print(raw_director_info)
    director_info = {}
    director_info['director_name'] = raw_director_info[0]['director_name']
    director_info['director_gender'] = raw_director_info[0]['director_gender']
    director_info['director_birthdate'] = raw_director_info[0]['director_birthdate']
    movieIDset = set()
    movie_info = []

    for item in raw_director_info:
        movieIDset.add(item['movieID'])

    for item in movieIDset:
        select_director_movie_sql = "SELECT * FROM movie_detail WHERE movieID = " + str(item) + ";"
        cursor.execute(select_director_movie_sql)
        raw_director_movie_info = cursor.fetchall()
        movie_info_dict = {}

        movie_info_dict['movie_title'] = raw_director_movie_info[0]['title']
        # print()
        movie_info_dict['movie_year'] = raw_director_movie_info[0]['year']
        movie_info_dict['genres'] = set()
        movie_info_dict['regions'] = set()
        for rdmi in raw_director_movie_info:
            movie_info_dict['genres'].add(rdmi['genre'])
            movie_info_dict['regions'].add(rdmi['produce_country'])
        movie_info.append(movie_info_dict)

    return director_info, movie_info

# 按姓名查询演员
def select_actor(actor_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    select_actor_sql = "SELECT DISTINCT actor_name, actor_gender, actor_birthdate FROM Act_in WHERE actor_name LIKE \'%"+actor_name+"%\';"
    cursor.execute(select_actor_sql)
    actors = cursor.fetchall()
    return actors

def get_actor_details(actor_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)

    select_actor_sql = "SELECT * FROM actor_movie WHERE actor_name = \""+actor_name+"\";"
    cursor.execute(select_actor_sql)
    raw_actor_info = cursor.fetchall()
    actor_info = {}
    actor_info['actor_name'] = raw_actor_info[0]['actor_name']
    actor_info['actor_gender'] = raw_actor_info[0]['actor_gender']
    actor_info['actor_birthdate'] = raw_actor_info[0]['actor_birthdate']

    actor_info['movie_title'] = []
    actor_info['movie_role'] = []
    for item in raw_actor_info:
        actor_info['movie_title'].append(item['title'])
        actor_info['movie_role'].append(item['role'])
    return actor_info

# 按昵称查询一个用户发表的评论、片单，喜欢的片单，好友关系
def select_user(user_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    select_user_sql = "SELECT * FROM _User WHERE user_name LIKE \'%"+user_name+"%\';"
    cursor.execute(select_user_sql)
    users = cursor.fetchall()
    return users

def get_user_details(userID):
    cursor = db.cursor(pymysql.cursors.DictCursor)

    select_user_sql = "SELECT * FROM _User WHERE userID = "+str(userID)+";"
    cursor.execute(select_user_sql)
    raw_user_info = cursor.fetchone()
    user_info = {}
    user_info['nickname'] = raw_user_info['user_name']
    user_info['gender'] = raw_user_info['user_gender']
    user_info['birthdate'] = raw_user_info['user_birthdate']

    select_follow_sql = "SELECT * FROM user_follow WHERE userID = "+str(userID)+";"
    cursor.execute(select_follow_sql)
    raw_follow_info = cursor.fetchall()
    follow_info = {}
    follow_info['f_userID'] = []
    follow_info['f_user_name'] = []
    for item in raw_follow_info:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        follow_info['f_userID'].append(item['f_userID'])
        sql = "SELECT user_name FROM _User WHERE userID = "+str(item['f_userID'])+";"
        cursor.execute(sql)
        follow_info['f_user_name'].append(str(cursor.fetchone()['user_name']))


    select_followedby_sql = "SELECT * FROM user_follow WHERE f_userID = \""+str(userID)+"\";"
    cursor.execute(select_followedby_sql)
    raw_followedby_info = cursor.fetchall()
    followedby_info = {}
    followedby_info['userID'] = []
    followedby_info['user_name'] = []
    for item in raw_followedby_info:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        followedby_info['userID'].append(item['userID'])
        sql = "SELECT user_name FROM _User WHERE userID = "+str(item['userID'])+";"
        cursor.execute(sql)
        followedby_info['user_name'].append(str(cursor.fetchone()['user_name']))

    select_create_sql = "SELECT * FROM user_mList WHERE createdby = \""+str(userID)+"\";"
    cursor.execute(select_create_sql)
    raw_create_info = cursor.fetchall()
    create_info = {}
    create_info['mListID'] = []
    create_info['mList_name'] = []
    for item in raw_create_info:
        create_info['mListID'].append(item['mListID'])
        create_info['mList_name'].append(item['list_name'])

    select_like_sql = "SELECT * FROM user_like_mList WHERE userID = \""+str(userID)+"\";"
    cursor.execute(select_like_sql)
    raw_like_info = cursor.fetchall()
    like_info = {}
    like_info['like_mListID'] = []
    like_info['like_mList_name'] = []
    for item in raw_create_info:
        like_info['like_mListID'].append(item['mListID'])
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT list_name FROM Movie_List WHERE mListID = "+str(item['mListID'])+";"
        cursor.execute(sql)
        like_info['like_mList_name'].append(item['list_name'])

    select_review_sql = "SELECT * FROM user_review WHERE userID = \""+str(userID)+"\";"
    cursor.execute(select_review_sql)
    raw_review_info = cursor.fetchall()
    review_info = {}
    review_info['movieID'] = []
    review_info['title'] = []
    review_info['numeric_rating'] = []
    review_info['verbal_rating'] = []
    review_info['review_date'] = []
    for item in raw_review_info:
        review_info['movieID'].append(item['movieID'])
        review_info['title'].append(item['title'])
        review_info['numeric_rating'].append(item['numeric_rating'])
        review_info['verbal_rating'].append(item['verbal_rating'])
        review_info['review_date'].append(item['date'])

    # print(review_info)
    # print(followedby_info)
    # print(create_info)
    # print(like_info)

    return user_info, follow_info, followedby_info, create_info, like_info, review_info

# 按昵称查询一个用户发表的评论、片单，喜欢的片单，好友关系
def select_mList(mList_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    select_mList_sql = "SELECT * FROM Movie_List WHERE list_name LIKE \'%"+mList_name+"%\';"
    cursor.execute(select_mList_sql)
    mLists = cursor.fetchall()
    return mLists

def get_mList_details(mListID):
    cursor = db.cursor(pymysql.cursors.DictCursor)

    select_mList_sql = "SELECT * FROM Movie_List WHERE mListID = "+str(mListID)+";"
    cursor.execute(select_mList_sql)
    raw_mList_info = cursor.fetchone()
    mListID_info = {}
    mListID_info['mListID'] = raw_mList_info['mListID']
    mListID_info['list_name'] = raw_mList_info['list_name']
    createdby = raw_mList_info['createdby']
    select_createdby_sql = "SELECT user_name FROM _User WHERE userID = "+str(createdby)+";"
    cursor.execute(select_createdby_sql)
    raw_createdby_info = cursor.fetchone()
    mListID_info['createdby'] = raw_createdby_info['user_name']

    movie_list = {}
    movie_list['title'] = []
    movie_list['year'] = []
    movie_list['avg_rating'] = []

    select_movie_sql = "SELECT * FROM movie_mList WHERE mListID = "+str(mListID)+";"
    cursor.execute(select_movie_sql)
    raw_movie_info = cursor.fetchall()
    for movie in raw_movie_info:
        movie_list['title'].append(movie['title'])
        movie_list['year'].append(movie['year'])
        movie_list['avg_rating'].append(movie['avg_rating'])
    
    return mListID_info, movie_list

# # 按姓名查询制片人
# def select_producer(producer_name):
#     cursor = db.cursor(pymysql.cursors.DictCursor)
#     select_producer_sql = "SELECT DISTINCT (producer_name, producer_gender, producer_birthdate) FROM Produce WHERE producer_name LIKE (%s)" %(producer_name)
#     cursor.execute(select_producer_sql)
#     producer = cursor.fetchone()
#     return producer