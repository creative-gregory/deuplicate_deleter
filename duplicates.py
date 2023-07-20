import os
from datetime import datetime

class Queue(object):
  def __init__(self):
    self.q = list()

  def size(self):
    return len(self.q)
  
  def is_empty(self):
    if self.size() == 0:
      return True
    else:
      return False
    
  def enqueue(self, data):
    self.q.insert(0, data)
  
  def dequeue(self):
    if not self.is_empty():
      return self.q.pop()
    else:
      return None
    
def exec_scan(path_list):
  file_dict = dict()

  if len(path_list) > 1:
    for path in path_list:
      scan_for_duplicates(path=path, file_dict=file_dict)

  return file_dict
      
def scan_for_duplicates(path, file_dict):
  if os.path.exists(path=path):
    for root, dir, files in os.walk(path):
      date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(rf"{date_time} - Scanning: {root}")

      for file in files:
        curr_file_path = os.path.join(root, file)
        file_stats = os.stat(curr_file_path)

        file_info = {
            "path": curr_file_path,
            "size": round(file_stats.st_size / (1024 * 1024), 2) # measured in MB
            }

        if file not in file_dict:
          file_dict[file] = [file_info]
          
        else:
          file_dict[file].append(file_info)
      date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(rf"{date_time} - Scan Completed for: {root}")

  else:
    print(rf"Path does not exist: {path}")

def eval_dupe_data(dupe_data):
  dupe_count = 0
  dupe_size = 0

  for dupe_key, dupe_list in dupe_data.items():
    if len(dupe_list) > 1:
      dupe_count += 1

      print(rf"Duplicates for: {dupe_key}")

      for dupe_path in dupe_list:
        file_stats = os.stat(dupe_path)
        dupe_size += file_stats.st_size / (1024 * 1024)
        print(dupe_path + rf" - {round(file_stats.st_size / (1024 * 1024), 2)} MB")
        
      print("\n")

  print(rf"Number of duplicates found {dupe_count}, total of {round((dupe_size/2)/1000, 2)} GB.")


