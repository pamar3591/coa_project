import os
import sys
import shutil

# check if folder already exists, if yes, delete folder along with all its contents
def delete_and_create_folder(folder_name):
    if os.path.isdir(os.path.join(sys.argv[1],'output_dir/',folder_name)):
        shutil.rmtree(os.path.join(sys.argv[1],'output_dir/',folder_name))
    os.mkdir(os.path.join(sys.argv[1], 'output_dir/', folder_name))

delete_and_create_folder('Data')
delete_and_create_folder('Data/yearData')
delete_and_create_folder('permData')
delete_and_create_folder('Results')
delete_and_create_folder('coaCSV')
delete_and_create_folder('final')
delete_and_create_folder('final_add')
delete_and_create_folder('processedFiles')
delete_and_create_folder('judges')
delete_and_create_folder('diagnostics')
delete_and_create_folder('diagnostics/unmerged_csl')
delete_and_create_folder('filter')

