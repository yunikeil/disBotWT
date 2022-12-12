import os


move_from = r'C:\Users\iyuna\source\repos\python\yunikeil\disBotWT\mainDiscord.py'
move_to = r'U:\home\yunikeil\disProject\mainDiscord.py'

# Windows
os.system(f'copy {move_from} {move_to}')
#print(f'copy {move_from} {move_to}')
print("copied!")
os.system('explorer')

# Unix
# os.system('cp file1.txt file7.txt')

