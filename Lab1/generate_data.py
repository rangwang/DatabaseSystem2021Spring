#-------------------------generate user
firstname=['zhao', 'qian', 'sun', 'li', 'zhou', 'wu', 'zheng', 'wang', 'feng', 'chen', 'chu', 'wei', 'jiang', 'shen', 'han', 'yang']

f = open('./user_data.txt','w')
# for i in range(100):
#     f.write(str(i)+'\n')
# f.close()

for j in range(0, 16):
    # print(j)
    for i in range(0, 10000):
        nickname= firstname[j]+str(i)
        gender = ''
        if i % 3 == 0:
            gender = 'F'
        elif i % 3 == 1:
            gender = 'M'
        else:
            gender = 'UNK'

        birth = '1984-4-9'
        f.write("("+'\''+gender+'\', '+'\"'+nickname +'\", \"'+birth+"\"),\n")
f.close()
#-----------------------generate movieList
# for i in range(0, 16):
#     for j in range(10):
#         mListname = firstname[i]+str(j)+' favourite'
#         print("(\"" + mListname + "\", " + str(i*10+j+1) + "),")

#----------------------generate review
# verbal = ["It's fine.", "It's awful.", "It's amazing!"]
# j = 0
# for i in range(250):
#     if j < 160:
#         print("(" + str(i) + ", " + str(j) + ", \"2019-1-4\", " + str(5) + ", \"" + verbal[0] + "\"),")
#         print("(" + str(i) + ", " + str(j+1) + ", \"2020-1-4\", " + str(5) + ", \"" + verbal[1] + "\"),")
#         print("(" + str(i) + ", " + str(j+2) + ", \"2021-1-4\", " + str(5) + ", \"" + verbal[2] + "\"),")
#         j += 3
#         if j == 159:
#             j = 0

#----------------------generate Listed
#----------------------generate _like
#----------------------generate follow
# for i in range(160):
#     print("(" + str(i+1) +", "+ str(i+1) + "),")
