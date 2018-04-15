import re
import os
while True:
    name = input('please input URL=')
    folder_name = re.findall(r'https://www.instagram.com/(.*)/',name)
    os.mkdir('c:/py/instagram/save/%s'%folder_name[0])

    follow_file = open('c:/py/instagram/name.txt','a')
    # follow_file.write('\n')
    follow_file.write(name+'\n')
    follow_file.close()

    artist_file = open('c:/py/instagram/%s.txt'%folder_name[0],'w')
    artist_file.close()
    print('complete')
    pass