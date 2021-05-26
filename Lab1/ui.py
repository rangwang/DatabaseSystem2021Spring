from tkinter import Tk, Toplevel, Canvas, END, LabelFrame, Frame, Label, NS, EW, E, W, S, N, NSEW, Entry, Text, Scrollbar, VERTICAL
from tkinter.ttk import Combobox, Button, Treeview
import function as func
import pymysql


resTree = None
castTable = None 
frame2 = None
actorEntry = None
roleEntry = None

def get_value():
    queryItem = qCombo.get()
    if queryItem == '电影':
        movie_viceQ()
    elif queryItem == '导演':
        director_viceQ()
    elif queryItem == '演员':
        actor_viceQ()
    elif queryItem == '用户':
        user_viceQ()
    elif queryItem == '片单':
        mList_viceQ()

def update_movie(movieID, title, year, rating, director, genre, region):
    global resTree

    func.update_movie(movieID, title, year, rating, director, genre, region)
    for line in castTable.get_children():
        print(castTable.item(line)['values'])
        func.update_actor_role(movieID, castTable.item(line)['values'])

def update_director(ori_name, director_name, director_gender, director_birth):
    func.update_director(ori_name, director_name, director_gender, director_birth)
    # pass

def update_actor(ori_name, actor_name, actor_gender, actor_birth):
    func.update_actor(ori_name, actor_name, actor_gender, actor_birth)
    # pass


def new_row():
    global castTable
    castTable.insert('', 'end', values=('演员名字', '扮演角色'))

def select_row():
    actorEntry.delete(0, END)
    roleEntry.delete(0, END)

    selected = castTable.focus()

    values = castTable.item(selected, 'values')

    actorEntry.insert(0, values[0])
    roleEntry.insert(0, values[1])

def update_row():
    selected = castTable.focus()
    castTable.item(selected, text='', values=(actorEntry.get(), roleEntry.get()))

    actorEntry.delete(0, END)
    roleEntry.delete(0, END)

def delete_row():
    global castTable
    selected_items = castTable.selection()
    for selected_item in selected_items:
        castTable.delete(selected_item)

def show_movie_details():
    global resTree, castTable, frame2, actorEntry, roleEntry
    # print(movieID)

    selected_item = resTree.focus()
    selected_row = resTree.item(selected_item)
    # print(selected_row)
    movieID = selected_row['values'][0]
    movie_info = func.get_movie_details(movieID)
    
    # print(movie_info)
    movie_details_win = Toplevel(win)
    movie_details_win.title("moviedb")
    movie_details_win.rowconfigure(2, weight=1)
    movie_details_win.columnconfigure(0, weight=1)
    movie_details_win.resizable(0,0)
    
    frame1 = Frame(movie_details_win)
    frame1.rowconfigure(6,weight=1)
    frame1.columnconfigure(2,weight=1)
    frame1.grid(row=0,sticky=N+EW)
    titleLabel = Label(frame1, text="电影名称").grid(row=0,column=0,sticky=W,padx=2, pady=2)
    titleEntry = Entry(frame1)
    titleEntry.grid(row=0,column=1,sticky=W,padx=2)
    titleEntry.insert(0, movie_info['title'])
    yearLabel = Label(frame1, text="上映年份").grid(row=1,column=0,sticky=W,padx=2, pady=2)
    yearEntry = Entry(frame1)
    yearEntry.grid(row=1,column=1,sticky=W,padx=2)
    yearEntry.insert(0, movie_info['year'])
    ratingLabel = Label(frame1, text="平均打分").grid(row=2,column=0,sticky=W,padx=2, pady=2)
    ratingEntry = Entry(frame1)
    ratingEntry.grid(row=2,column=1,sticky=W,padx=2)
    ratingEntry.insert(0, movie_info['avg_rating'])
    directorLabel = Label(frame1, text="导演").grid(row=3,column=0,sticky=W,padx=2, pady=2)
    directorEntry = Entry(frame1)
    directorEntry.grid(row=3,column=1,sticky=W,padx=2)
    directorEntry.insert(0, movie_info['director'])
    producerLabel = Label(frame1, text="出品人").grid(row=4,column=0,sticky=W,padx=2, pady=2)
    producerEntry = Entry(frame1)
    producerEntry.grid(row=4,column=1,sticky=W,padx=2)
    producerEntry.insert(0, movie_info['producer'])
    genreLabel = Label(frame1, text="电影类型").grid(row=5,column=0,sticky=W,padx=2, pady=2)
    genreEntry = Entry(frame1)
    genreEntry.grid(row=5,column=1,sticky=W,padx=2)
    genreEntry.insert(0, movie_info['genre'])
    regionLabel = Label(frame1, text="制作国家/地区").grid(row=6,column=0,sticky=W,padx=2, pady=2)
    regionEntry = Entry(frame1)
    regionEntry.grid(row=6,column=1,sticky=W,padx=2)
    regionEntry.insert(0, movie_info['region'])

    frame2 = LabelFrame(movie_details_win, text = "演职员表")
    frame2.rowconfigure(3,weight=1)
    frame2.columnconfigure(3,weight=1)
    frame2.grid(row=1,sticky=N+EW)
    castTable = Treeview(frame2, show="headings")
    castTable["columns"] = ("演员", "扮演角色")
    castTable.heading("演员", text = "演员")
    castTable.heading("扮演角色", text = "扮演角色")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)

    for item in movie_info['actor_role']:
        castTable.insert("", 'end', values=[item[0], item[1]])
    actorEntry = Entry(frame2)
    actorEntry.grid(row=1,column=0,sticky=W,padx=2)

    roleEntry = Entry(frame2)
    roleEntry.grid(row=1,column=1,sticky=W,padx=2)
    
    chooserowButton = Button(frame2, text="选择行", command=select_row)
    chooserowButton.grid(row=1,column=2,sticky=W,padx=2)

    updaterowButton = Button(frame2, text="修改行", command=update_row)
    updaterowButton.grid(row=1,column=3,sticky=W,padx=2)

    addButton = Button(frame2, text = "增加演员", command = new_row)
    addButton.grid(row=2, column=0, sticky=W, pady=2, padx=2)
    deleteButton = Button(frame2, text = "删除演员", command = delete_row)
    deleteButton.grid(row=2, column=3, sticky=W, pady=2, padx=2)
    updateButton = Button(movie_details_win, text = "保存更改", command = lambda:update_movie(movieID, titleEntry.get(), yearEntry.get(), ratingEntry.get(), directorEntry.get(), genreEntry.get(), regionEntry.get()))
    updateButton.grid(row=3, sticky=EW, pady=2)

    movie_details_win.mainloop()

def add_addmovie(title, year, rating, director, genre, region):
    global resTree
    movieID = func.insert_movie(title, year, rating, director, genre, region)
    for line in castTable.get_children():
        func.insert_actor(movieID, castTable.item(line)['values'])
    


def add_movie():
    global resTree, castTable, frame2, actorEntry, roleEntry
    
    movie_details_win = Toplevel(win)
    movie_details_win.title("moviedb")
    movie_details_win.rowconfigure(2, weight=1)
    movie_details_win.columnconfigure(0, weight=1)
    movie_details_win.resizable(0,0)
    
    frame1 = Frame(movie_details_win)
    frame1.rowconfigure(6,weight=1)
    frame1.columnconfigure(2,weight=1)
    frame1.grid(row=0,sticky=N+EW)
    titleLabel = Label(frame1, text="电影名称").grid(row=0,column=0,sticky=W,padx=2, pady=2)
    titleEntry = Entry(frame1)
    titleEntry.grid(row=0,column=1,sticky=W,padx=2)
    # titleEntry.insert(0, movie_info['title'])
    yearLabel = Label(frame1, text="上映年份").grid(row=1,column=0,sticky=W,padx=2, pady=2)
    yearEntry = Entry(frame1)
    yearEntry.grid(row=1,column=1,sticky=W,padx=2)
    # yearEntry.insert(0, movie_info['year'])
    ratingLabel = Label(frame1, text="平均打分").grid(row=2,column=0,sticky=W,padx=2, pady=2)
    ratingEntry = Entry(frame1)
    ratingEntry.grid(row=2,column=1,sticky=W,padx=2)
    # ratingEntry.insert(0, movie_info['avg_rating'])
    directorLabel = Label(frame1, text="导演").grid(row=3,column=0,sticky=W,padx=2, pady=2)
    directorEntry = Entry(frame1)
    directorEntry.grid(row=3,column=1,sticky=W,padx=2)
    # directorEntry.insert(0, movie_info['director'])
    producerLabel = Label(frame1, text="出品人").grid(row=4,column=0,sticky=W,padx=2, pady=2)
    producerEntry = Entry(frame1)
    producerEntry.grid(row=4,column=1,sticky=W,padx=2)
    # producerEntry.insert(0, movie_info['producer'])
    genreLabel = Label(frame1, text="电影类型").grid(row=5,column=0,sticky=W,padx=2, pady=2)
    genreEntry = Entry(frame1)
    genreEntry.grid(row=5,column=1,sticky=W,padx=2)
    # genreEntry.insert(0, movie_info['genre'])
    regionLabel = Label(frame1, text="制作国家/地区").grid(row=6,column=0,sticky=W,padx=2, pady=2)
    regionEntry = Entry(frame1)
    regionEntry.grid(row=6,column=1,sticky=W,padx=2)
    # regionEntry.insert(0, movie_info['region'])

    frame2 = LabelFrame(movie_details_win, text = "演职员表")
    frame2.rowconfigure(3,weight=1)
    frame2.columnconfigure(3,weight=1)
    frame2.grid(row=1,sticky=N+EW)
    castTable = Treeview(frame2, show="headings")
    castTable["columns"] = ("演员", "扮演角色")
    castTable.heading("演员", text = "演员")
    castTable.heading("扮演角色", text = "扮演角色")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)

    # for item in movie_info['actor_role']:
    #     castTable.insert("", 'end', values=[item[0], item[1]])
    actorEntry = Entry(frame2)
    actorEntry.grid(row=1,column=0,sticky=W,padx=2)

    roleEntry = Entry(frame2)
    roleEntry.grid(row=1,column=1,sticky=W,padx=2)
    
    chooserowButton = Button(frame2, text="选择行", command=select_row)
    chooserowButton.grid(row=1,column=2,sticky=W,padx=2)

    updaterowButton = Button(frame2, text="修改行", command=update_row)
    updaterowButton.grid(row=1,column=3,sticky=W,padx=2)

    addButton = Button(frame2, text = "增加演员", command = new_row)
    addButton.grid(row=2, column=0, sticky=W, pady=2, padx=2)
    deleteButton = Button(frame2, text = "删除演员", command = delete_row)
    deleteButton.grid(row=2, column=3, sticky=W, pady=2, padx=2)
        
    updateButton = Button(movie_details_win, text = "保存更改", command = lambda:add_addmovie(titleEntry.get(), yearEntry.get(), ratingEntry.get(), directorEntry.get(), genreEntry.get(), regionEntry.get()))
    updateButton.grid(row=3, sticky=EW, pady=2)

    movie_details_win.mainloop()

def delete_movie():
    global resTree
    selected_items = resTree.selection()
    for selected_item in selected_items:
        selected_row = resTree.item(selected_item)
        delete_movieID = selected_row['values'][0]
        func.delete_movie(delete_movieID)
        resTree.delete(selected_item)
    

def show_director_details():
    global resTree, castTable, frame2
    # print(movieID)

    selected_item = resTree.focus()
    selected_row = resTree.item(selected_item)
    # print(selected_row)
    director_name = selected_row['values'][0]
    # print(director_name)
    director_info, movie_info = func.get_director_details(director_name)
    

    director_details_win = Toplevel(win)
    director_details_win.title("director")
    director_details_win.resizable(0,0)
    
    frame1 = Frame(director_details_win)
    frame1.grid(row=0,sticky=N+EW)
    directorLabel = Label(frame1, text="导演名").grid(row=0,column=0,sticky=W,padx=2, pady=2)
    directorEntry = Entry(frame1)
    directorEntry.grid(row=0,column=1,sticky=W,padx=2)
    directorEntry.insert(0, director_info['director_name'])

    genderLabel = Label(frame1, text="性别").grid(row=1,column=0,sticky=W,padx=2, pady=2)
    genderEntry = Entry(frame1)
    genderEntry.grid(row=1,column=1,sticky=W,padx=2)
    genderEntry.insert(0, director_info['director_gender'])

    birthLabel = Label(frame1, text="出生日期").grid(row=2,column=0,sticky=W,padx=2, pady=2)
    birthEntry = Entry(frame1)
    birthEntry.grid(row=2,column=1,sticky=W,padx=2)
    birthEntry.insert(0, director_info['director_birthdate'])

    frame2 = LabelFrame(director_details_win, text = "参与电影")
    frame2.grid(row=1,sticky=N+EW)
    castTable = Treeview(frame2, show="headings")
    castTable["columns"] = ("电影名称", "电影类别", "上映年份", "上映地区")
    castTable.heading("电影名称", text = "电影名称")
    castTable.heading("电影类别", text = "电影类别")
    castTable.heading("上映年份", text = "上映年份")
    castTable.heading("上映地区", text = "上映地区")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)
    # castTable.insert("", 'end', values=['Titanic', 'Romance', '1995', 'USA'])
    for item in movie_info:
        castTable.insert("", 'end', values=[item['movie_title'], item['genres'], item['movie_year'], item['regions'],])
    
    updateButton = Button(director_details_win, text = "保存更改", command = lambda: update_director(director_name, directorEntry.get(), genderEntry.get(), birthEntry.get()))
    updateButton.grid(row=1, sticky=S+EW, pady=2)

    director_details_win.mainloop()

# def add_director():
#     global resTree
#     resTree.insert('', 'end', values=('导演名', '性别', '出生日期'))

def delete_director():
    global resTree
    selected_items = resTree.selection()
    for selected_item in selected_items:
        selected_row = resTree.item(selected_item)
        delete_directorname = selected_row['values'][0]
        func.delete_director(delete_directorname)
        resTree.delete(selected_item)

def show_actor_details():
    global resTree, castTable, frame2
    # print(movieID)

    selected_item = resTree.focus()
    selected_row = resTree.item(selected_item)
    # print(selected_row)
    actor_name = selected_row['values'][0]
    # print(director_name)
    actor_info = func.get_actor_details(actor_name)

    actor_details_win = Toplevel(win)
    actor_details_win.title("actor")
    actor_details_win.resizable(0,0)
    
    frame1 = Frame(actor_details_win)
    frame1.grid(row=0,sticky=N+EW)
    actorLabel = Label(frame1, text="演员名").grid(row=0,column=0,sticky=W,padx=2, pady=2)
    actorEntry = Entry(frame1)
    actorEntry.grid(row=0,column=1,sticky=W,padx=2)
    actorEntry.insert(0, actor_info['actor_name'])

    genderLabel = Label(frame1, text="性别").grid(row=1,column=0,sticky=W,padx=2, pady=2)
    genderEntry = Entry(frame1)
    genderEntry.grid(row=1,column=1,sticky=W,padx=2)
    genderEntry.insert(0, actor_info['actor_gender'])

    birthLabel = Label(frame1, text="出生日期").grid(row=2,column=0,sticky=W,padx=2, pady=2)
    birthEntry = Entry(frame1)
    birthEntry.grid(row=2,column=1,sticky=W,padx=2)
    birthEntry.insert(0, actor_info['actor_birthdate'])

    frame2 = LabelFrame(actor_details_win, text = "参与电影")
    frame2.grid(row=1,sticky=N+EW)
    castTable = Treeview(frame2, show="headings")
    castTable["columns"] = ("电影名称", "角色")
    castTable.heading("电影名称", text = "电影名称")
    castTable.heading("角色", text = "角色")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)
    for i in range(len(actor_info['movie_title'])):
        castTable.insert("", 'end', values=[actor_info['movie_title'][i], actor_info['movie_role'][i]])

    updateButton = Button(actor_details_win, text = "保存更改", command = lambda: update_actor(actor_name, actorEntry.get(), genderEntry.get(), birthEntry.get()))
    updateButton.grid(row=1, sticky=S+EW, pady=2)

    actor_details_win.mainloop()

# def add_actor():
#     global resTree
#     resTree.insert('', 'end', values=('演员名', '性别', '出生日期'))

def delete_actor():
    global resTree
    selected_items = resTree.selection()
    for selected_item in selected_items:
        selected_row = resTree.item(selected_item)
        delete_actorname = selected_row['values'][0]
        func.delete_actor(delete_actorname)
        resTree.delete(selected_item)

def show_user_details():
    global resTree, castTable, frame2
    # print(movieID)

    selected_item = resTree.focus()
    selected_row = resTree.item(selected_item)
    # print(selected_row)
    userID = selected_row['values'][0]
    # print(director_name)
    user_info, follow_info, followedby_info, create_info, like_info, review_info = func.get_user_details(userID)

    user_details_win = Toplevel(win)
    user_details_win.title("user")
    # user_details_win.resizable(0,0)
    canvas = Canvas(user_details_win)
    mainFrame = Frame(canvas)
    mainFrame.columnconfigure(0, weight=1)
    vbar = Scrollbar(user_details_win, orient=VERTICAL, command=canvas.yview)

    canvas.configure(yscrollcommand=vbar.set)
    vbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    mainFrame.grid(row=0, column=0, sticky=NSEW)
    canvas.create_window((0,0), window=mainFrame, anchor="nw")
    mainFrame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

    frame1 = Frame(mainFrame)
    frame1.grid(row=0,column=0, sticky=N+EW)
    userLabel = Label(frame1, text="用户昵称").grid(row=0,column=0,sticky=W,padx=2, pady=2)
    userEntry = Entry(frame1)
    userEntry.grid(row=0,column=1,sticky=W,padx=2)
    userEntry.insert(0, user_info['nickname'])
    genderLabel = Label(frame1, text="性别").grid(row=1,column=0,sticky=W,padx=2, pady=2)
    genderEntry = Entry(frame1)
    genderEntry.grid(row=1,column=1,sticky=W,padx=2)
    genderEntry.insert(0, user_info['gender'])
    birthLabel = Label(frame1, text="出生日期").grid(row=2,column=0,sticky=W,padx=2, pady=2)
    birthEntry = Entry(frame1)
    birthEntry.grid(row=2,column=1,sticky=W,padx=2)
    birthEntry.insert(0, user_info['birthdate'])

    frame2 = LabelFrame(mainFrame, text = "关注")
    frame2.grid(row=1,column=0,sticky=N+EW)
    frame2.columnconfigure(0, weight=1)
    castTable = Treeview(frame2, show="headings")
    castTable["columns"] = ("用户ID", "昵称")
    castTable.heading("用户ID", text = "用户ID")
    castTable.heading("昵称", text = "昵称")
    castTable.grid(row=0, column=0, sticky=EW)
    for i in range(len(follow_info['f_userID'])):
        castTable.insert("", 'end', values=[follow_info['f_userID'][i], follow_info['f_user_name'][i]])

    frame3 = LabelFrame(mainFrame, text = "粉丝")
    frame3.grid(row=2,sticky=N+EW)
    frame3.columnconfigure(0, weight=1)
    castTable = Treeview(frame3, show="headings")
    castTable["columns"] = ("用户ID", "昵称")
    castTable.heading("用户ID", text = "用户ID")
    castTable.heading("昵称", text = "昵称")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)
    for i in range(len(followedby_info['userID'])):
        castTable.insert("", 'end', values=[followedby_info['userID'][i], followedby_info['user_name'][i]])


    frame4 = LabelFrame(mainFrame, text = "创建的片单")
    frame4.grid(row=3,sticky=N+EW)
    frame4.columnconfigure(0, weight=1)
    castTable = Treeview(frame4, show="headings")
    castTable["columns"] = ("片单ID", "片单名")
    castTable.heading("片单ID", text = "片单ID")
    castTable.heading("片单名", text = "片单名")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)
    for i in range(len(create_info['mListID'])):
        castTable.insert("", 'end', values=[create_info['mListID'][i], create_info['mList_name'][i]])

    frame5 = LabelFrame(mainFrame, text = "收藏的片单")
    frame5.grid(row=4,sticky=N+EW)
    frame5.columnconfigure(0, weight=1)
    castTable = Treeview(frame5, show="headings")
    castTable["columns"] = ("片单ID", "片单名")
    castTable.heading("片单ID", text = "片单ID")
    castTable.heading("片单名", text = "片单名")
    castTable.grid(row=0, columnspan=4, sticky=NSEW)
    for i in range(len(like_info['like_mListID'])):
        castTable.insert("", 'end', values=[like_info['like_mListID'][i], like_info['like_mList_name'][i]])

    frame6 = LabelFrame(mainFrame, text = "影评")
    frame6.grid(row=4,sticky=N+EW)
    castTable = Treeview(frame6, show="headings")
    castTable["columns"] = ("电影ID", "电影名", "评分", "评语", "评论日期")
    castTable.heading("电影ID", text = "电影ID")
    castTable.heading("电影名", text = "电影名")
    castTable.heading("评分", text = "评分")
    castTable.heading("评语", text = "评语")
    castTable.heading("评论日期", text = "评论日期")
    castTable.grid(row=0, sticky=NSEW)
    for i in range(len(review_info['movieID'])):
        castTable.insert("", 'end', values=[review_info['movieID'][i], review_info['title'][i], review_info['numeric_rating'][i], review_info['verbal_rating'][i], review_info['review_date'][i]])

    # updateButton = Button(mainFrame, text = "保存更改", command = update_user)
    # updateButton.grid(row=5, sticky=S+EW, pady=2)

    user_details_win.mainloop()

# def add_user():
#     global resTree
#     resTree.insert('', 'end', values=('用户ID', '标题', '上映年份', '平均打分'))

def delete_user():
    global resTree
    selected_items = resTree.selection()
    for selected_item in selected_items:
        selected_row = resTree.item(selected_item)
        delete_userID = selected_row['values'][0]
        func.delete_user(delete_userID)
        resTree.delete(selected_item)

def show_mList_details():
    global resTree, castTable, frame2
    # print(movieID)

    selected_item = resTree.focus()
    selected_row = resTree.item(selected_item)
    mListID = selected_row['values'][0]
    mListID_info, movie_list = func.get_mList_details(mListID)

    mList_details_win = Toplevel(win)
    mList_details_win.title("mList")
    mList_details_win.resizable(0,0)
    
    frame1 = Frame(mList_details_win)
    frame1.grid(row=0,sticky=N+EW)
    mListLabel = Label(frame1, text="片单ID").grid(row=0,column=0,sticky=W,padx=2, pady=2)
    mListEntry = Entry(frame1)
    mListEntry.grid(row=0,column=1,sticky=W,padx=2)
    mListEntry.insert(0, mListID_info['mListID'])

    nameLabel = Label(frame1, text="片单名").grid(row=1,column=0,sticky=W,padx=2, pady=2)
    nameEntry = Entry(frame1)
    nameEntry.grid(row=1,column=1,sticky=W,padx=2)
    nameEntry.insert(0, mListID_info['list_name'])

    creatorLabel = Label(frame1, text="创建者").grid(row=2,column=0,sticky=W,padx=2, pady=2)
    creatorEntry = Entry(frame1)
    creatorEntry.grid(row=2,column=1,sticky=W,padx=2)
    creatorEntry.insert(0, mListID_info['createdby'])

    frame2 = LabelFrame(mList_details_win, text = "电影列表")
    frame2.grid(row=1,sticky=N+EW)
    castTable = Treeview(frame2, show="headings")
    castTable["columns"] = ("电影名称", "上映年份", "平均打分")
    castTable.heading("电影名称", text = "电影名称")
    castTable.heading("上映年份", text = "上映年份")
    castTable.heading("平均打分", text = "平均打分")

    castTable.grid(row=0, columnspan=4, sticky=NSEW)
    for i in range(len(movie_list)):
        castTable.insert("", 'end', values=[movie_list['title'][i], movie_list['year'][i], movie_list['avg_rating'][i]])

    # updateButton = Button(mList_details_win, text = "保存更改", command = update_mList)
    # updateButton.grid(row=1, sticky=S+EW, pady=2)

    mList_details_win.mainloop()

def add_mList():
    global resTree
    resTree.insert('', 'end', values=('片单编号', '标题', '创建者'))

def delete_mList():
    global resTree
    selected_items = resTree.selection()
    for selected_item in selected_items:
        resTree.delete(selected_item) 

def clear_resultFrame():
    for widget in resultFrame.winfo_children():
        widget.destroy()

def clear_optionFrame():
    for widget in optionFrame.winfo_children():
        widget.destroy()

def get_movie_search(genre, region, title, director, actor):
    global resTree
    clear_resultFrame()
    clear_optionFrame()

    movie_info = {}
    if genre == "--影片种类--":
        genre = ''
    
    if region == "--出产地区--":
        region = ''

    if title == "--输入影片名--":
        title = ''

    if director == "--输入导演名--":
        director = ''

    if actor == "--输入演员名--":
        actor = ''

    movie_info['genre'] = genre
    movie_info['region'] = region
    movie_info['title'] = title
    movie_info['director'] = director
    movie_info['actor'] = actor
    # print(movie_info)
    movies = func.select_movie(movie_info)
    # print(movies)
    ybar=Scrollbar(resultFrame,orient='vertical')
    resTree = Treeview(resultFrame, show = "headings", yscrollcommand=ybar.set)
    ybar['command']=resTree.yview
    resTree["columns"] = ("电影编号", "标题", "上映年份", "平均打分")
    resTree.heading("电影编号", text = "电影编号")
    resTree.heading("标题", text = "标题")
    resTree.heading("上映年份", text = "上映年份")
    resTree.heading("平均打分", text = "平均打分")
    resTree.grid(row=0, column = 0, sticky=NSEW)
    ybar.grid(row=0, column = 1, sticky=NS)
    for movie in movies:
        movieID = str(movie['movieID'])
        title = str(movie['title'])
        year = str(movie['year'])
        avg_rating = str(movie['avg_rating'])
        resTree.insert("", 'end', values=[movieID, title, year, avg_rating])

    detailButton = Button(optionFrame, text = "详细信息", command = show_movie_details)
    detailButton.grid(row=0, column=0, sticky=EW, padx = 25)

    addButton = Button(optionFrame, text = "增加", command = add_movie)
    addButton.grid(row=0, column=1, sticky=EW, padx = 25)

    deleteButton = Button(optionFrame, text = "删除", command = delete_movie)
    deleteButton.grid(row=0, column=2, sticky=EW, padx = 25)
    # return None

def get_director_search(director_name):
    global resTree
    clear_resultFrame()
    clear_optionFrame()

    if director_name == "--输入导演名--":
        director_name = ''
         
    director = func.select_director(director_name)

    ybar=Scrollbar(resultFrame,orient='vertical')
    resTree = Treeview(resultFrame, show = "headings", yscrollcommand=ybar.set)
    ybar['command']=resTree.yview
    resTree["columns"] = ("导演名", "性别", "出生日期")
    resTree.heading("导演名", text = "导演名")
    resTree.heading("性别", text = "性别")
    resTree.heading("出生日期", text = "出生日期")
    resTree.grid(row=0,column = 0, sticky=NSEW)
    ybar.grid(row=0, column = 1, sticky=NS)
    for d in director:
        resTree.insert("", 'end', values=[d['director_name'], d['director_gender'], d['director_birthdate']])
    # resTree.insert("", 'end', values=['jack', 'M', '1994-9-1'])

    detailButton = Button(optionFrame, text = "详细信息", command = show_director_details)
    detailButton.grid(row=0, column=0, sticky=EW, padx = 25)

    # addButton = Button(optionFrame, text = "增加", command = add_director)
    # addButton.grid(row=0, column=1, sticky=EW, padx = 25)

    deleteButton = Button(optionFrame, text = "删除", command = delete_director)
    deleteButton.grid(row=0, column=2, sticky=EW, padx = 25)

def get_actor_search(actor_name):
    global resTree
    clear_resultFrame()
    clear_optionFrame()

    if actor_name == "--输入演员名--":
        actor_name = ''
         
    actors = func.select_actor(actor_name)

    ybar=Scrollbar(resultFrame,orient='vertical')
    resTree = Treeview(resultFrame, show = "headings", yscrollcommand=ybar.set)
    ybar['command']=resTree.yview
    resTree["columns"] = ("演员名", "性别", "出生日期")
    resTree.heading("演员名", text = "演员名")
    resTree.heading("性别", text = "性别")
    resTree.heading("出生日期", text = "出生日期")
    resTree.grid(row=0, column = 0, sticky=NSEW)
    ybar.grid(row=0, column = 1, sticky=NS)
    for actor in actors:
        resTree.insert("", 'end', values=[actor['actor_name'], actor['actor_gender'], actor['actor_birthdate']])

    detailButton = Button(optionFrame, text = "详细信息", command = show_actor_details)
    detailButton.grid(row=0, column=0, sticky=EW, padx = 25)

    # addButton = Button(optionFrame, text = "增加", command = add_actor)
    # addButton.grid(row=0, column=1, sticky=EW, padx = 25)

    deleteButton = Button(optionFrame, text = "删除", command = delete_actor)
    deleteButton.grid(row=0, column=2, sticky=EW, padx = 25)

def get_user_search(user_name):
    global resTree
    clear_resultFrame()
    clear_optionFrame()

    if user_name == "--输入用户昵称--":
        user_name = ''

    users = func.select_user(user_name)

    ybar=Scrollbar(resultFrame,orient='vertical')
    resTree = Treeview(resultFrame, show = "headings", yscrollcommand=ybar.set)
    ybar['command']=resTree.yview
    resTree["columns"] = ("用户ID", "昵称", "性别", "出生日期")
    resTree.heading("用户ID", text = "用户ID")
    resTree.heading("昵称", text = "昵称")
    resTree.heading("性别", text = "性别")
    resTree.heading("出生日期", text = "出生日期")
    resTree.grid(row=0, column = 0, sticky=NSEW)
    ybar.grid(row=0, column = 1, sticky=NS)
    for user in users:
        resTree.insert("", 'end', values=[user['userID'], user['user_name'], user['user_gender'], user['user_birthdate']])

    detailButton = Button(optionFrame, text = "详细信息", command = show_user_details)
    detailButton.grid(row=0, column=0, sticky=EW, padx = 25)

    # addButton = Button(optionFrame, text = "增加", command = add_user)
    # addButton.grid(row=0, column=1, sticky=EW, padx = 25)

    deleteButton = Button(optionFrame, text = "删除", command = delete_user)
    deleteButton.grid(row=0, column=2, sticky=EW, padx = 25)

def get_mList_search(mList_name):
    global resTree
    clear_resultFrame()
    clear_optionFrame()

    if mList_name == "--输入片单名--":
        mList_name = ''

    mLists = func.select_mList(mList_name)

    ybar=Scrollbar(resultFrame,orient='vertical')
    resTree = Treeview(resultFrame, show = "headings", yscrollcommand=ybar.set)
    ybar['command']=resTree.yview
    resTree["columns"] = ("片单ID", "片单名")
    resTree.heading("片单ID", text = "片单ID")
    resTree.heading("片单名", text = "片单名")
    resTree.grid(row=0, column = 0, sticky=NSEW)
    ybar.grid(row=0, column = 1, sticky=NS)
    for mList in mLists:
        resTree.insert("", 'end', values=[mList['mListID'], mList['list_name']])

    detailButton = Button(optionFrame, text = "详细信息", command = show_mList_details)
    detailButton.grid(row=0, column=1, sticky=EW, padx = 25)

    # addButton = Button(optionFrame, text = "增加", command = add_mList)
    # addButton.grid(row=0, column=1, sticky=EW, padx = 25)

    # deleteButton = Button(optionFrame, text = "删除", command = delete_mList)
    # deleteButton.grid(row=0, column=2, sticky=EW, padx = 25)

def clear_viceQFrame():
    for widget in viceQueryFrame.winfo_children():
        widget.destroy()

def movie_viceQ():
    clear_viceQFrame()
    clear_resultFrame()

    genreCombo = Combobox(viceQueryFrame)
    genreCombo['value'] = ('--影片种类--', 'Crime', 'Drama', 'Adventure', 'Western', 'Thriller', 'Action', 'Sci-Fi', 'Fantasy', 'Biography', 'History', 'War', 'Mystery', 'Romance', 'Horror', 'Film-Noir', 'Comedy', 'Family', 'Animation', 'Sport', 'Musical')
    genreCombo['state'] = 'readonly'
    genreCombo.grid(row=0,column=0,sticky=W,padx=2)
    genreCombo.current(0)

    regionCombo = Combobox(viceQueryFrame)
    regionCombo['value'] = ('--出产地区--', 'Australia', 'Georgia', 'UK', 'West Germany', 'Austria', 'Algeria', 'Mexico', 'Germany', 'Japan', 'Yugoslavia', 'Switzerland', 'India', 'Spain', 'Hong Kong', 'Sweden', 'Turkey', 'Ireland', 'France', 'Soviet Union', 'Italy', 'USA', 'Argentina', 'Iran', 'Canada', 'Estonia', 'China', 'South Africa', 'Bulgaria', 'South Korea')
    regionCombo['state'] = 'readonly'
    regionCombo.grid(row=0,column=1,sticky=W,padx=2)
    regionCombo.current(0)

    titleEntry = Entry(viceQueryFrame)
    titleEntry.grid(row=0,column=2,sticky=W,padx=2)
    titleEntry.insert(0, '--输入影片名--')

    directorEntry = Entry(viceQueryFrame)
    directorEntry.grid(row=0,column=3,sticky=W,padx=2)
    directorEntry.insert(0, '--输入导演名--')

    actorEntry = Entry(viceQueryFrame)
    actorEntry.grid(row=0,column=4,sticky=W,padx=2)
    actorEntry.insert(0, '--输入演员名--')
  
    searchButton = Button(viceQueryFrame, text="查询", command=\
        lambda:get_movie_search(genreCombo.get(), regionCombo.get(), titleEntry.get(), directorEntry.get(), actorEntry.get()))
    searchButton.grid(row=0,column=5,sticky=E)


def director_viceQ():
    clear_viceQFrame()
    clear_resultFrame()

    directorEntry = Entry(viceQueryFrame)
    directorEntry.grid(row=0,column=3,sticky=W,padx=2)
    directorEntry.insert(0, '--输入导演名--')

    searchButton = Button(viceQueryFrame, text="查询", command=\
        lambda:get_director_search(directorEntry.get()))
    searchButton.grid(row=0,column=5,sticky=E)

def actor_viceQ():
    clear_viceQFrame()
    clear_resultFrame()

    actorEntry = Entry(viceQueryFrame)
    actorEntry.grid(row=0,column=4,sticky=W,padx=2)
    actorEntry.insert(0, '--输入演员名--')

    searchButton = Button(viceQueryFrame, text="查询", command=\
        lambda:get_actor_search(actorEntry.get()))
    searchButton.grid(row=0,column=5,sticky=E)

def user_viceQ():
    clear_viceQFrame()
    clear_resultFrame()

    userEntry = Entry(viceQueryFrame)
    userEntry.grid(row=0,column=4,sticky=W,padx=2)
    userEntry.insert(0, '--输入用户昵称--')

    searchButton = Button(viceQueryFrame, text="查询", command=\
        lambda:get_user_search(userEntry.get()))
    searchButton.grid(row=0,column=5,sticky=E)

def mList_viceQ():
    clear_viceQFrame()
    clear_resultFrame()

    mListEntry = Entry(viceQueryFrame)
    mListEntry.grid(row=0,column=4,sticky=W,padx=2)
    mListEntry.insert(0, '--输入片单名--')

    searchButton = Button(viceQueryFrame, text="查询", command=\
        lambda:get_mList_search(mListEntry.get()))
    searchButton.grid(row=0,column=5,sticky=E)

win=Tk()
win.title("moviedb")
win.rowconfigure(2, weight=1)
win.columnconfigure(0, weight=1)
win.geometry('960x540')

queryFrame = LabelFrame(win,text="查询")
queryFrame.rowconfigure(1, weight=1)
queryFrame.columnconfigure(2, weight=1)
qCombo = Combobox(queryFrame)
qCombo['value'] = ('--选择搜索项--', '电影', '导演', '演员', '用户', '片单')
qCombo['state'] = 'readonly'
qCombo.grid(row=0,column=1,sticky=W)
qCombo.current(0)
chooseButton = Button(queryFrame, text="选择", command=get_value)
chooseButton.grid(row=0,column=2,sticky=W)
queryFrame.grid(row=0,sticky=EW)

# vice query
viceQueryFrame = LabelFrame(win,text="详细查询", bg = 'grey',height = 100)
viceQueryFrame.rowconfigure(0, weight=1)
viceQueryFrame.columnconfigure(5, weight=1)
viceQueryFrame.grid(row=1,sticky=EW)

# result
resultFrame = LabelFrame(win,text="结果", bg = 'grey', width = 1200, height=500)
resultFrame.rowconfigure(0,weight=1)
resultFrame.columnconfigure(0,weight=1)
resultFrame.grid(row=2, column = 0, sticky=NSEW)

# more options
optionFrame = Frame(win, bg = 'grey', height=100)
optionFrame.rowconfigure(0,weight=1)
optionFrame.columnconfigure(0,weight=1)
optionFrame.columnconfigure(1,weight=1)
optionFrame.columnconfigure(2,weight=1)
optionFrame.grid(row=3,sticky=S+EW)

win.mainloop()

# {'Australia', 'Georgia', 'UK', 'West Germany', 'Austria', 'Algeria', 'Mexico', 'Germany', 'Japan', 'Yugoslavia', 'Switzerland', 'India', 'Spain', 'Hong Kong', 'Sweden', 'Turkey', 'Ireland', 'France', 'Soviet Union', 'Italy', 'USA', 'Argentina', 'Iran', 'Canada', 'Estonia', 'China', 'South Africa', 'Bulgaria', 'South Korea'}