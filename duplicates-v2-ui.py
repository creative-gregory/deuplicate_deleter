from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import sleep
import duplicates as d
import json, os
from send2trash import send2trash
from threading import Thread

root_width = 1000
root_height = 350

def scan_for_duplicates(path, file_dict):
  if os.path.exists(path=path):
    for root, dir, files in os.walk(path):
      for file in files:
        print(file)
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

  else:
    print(rf"Path does not exist: {path}")

def get_file_count(location):
  file_count = 0
  file_count += sum(1 for _, _, files in os.walk(location) for f in files) 

  return file_count

# def add_path_entry_to_frame():
#   base_entry_y_pos = 20
#   base_button_y_pos = 25
#   num_paths = len(path_list) + 1

#   if num_paths <= 10:
#     path_entry = Entry(root, bd= 2, width=20,font="font-size=16")
#     path_list.append(path_entry)

#     path_entry.update()
#     path_entry.focus()
#     path_entry.place(x=755, y=base_entry_y_pos*num_paths)

#     add_path_button.place(x=root_width - add_path_button.winfo_reqwidth() - 10, y=base_button_y_pos*(num_paths + 1))
#     add_path_button.update()

def get_entry_data(path_list):
  entry_path_list = list()
  
  for path in path_list:
    if not os.path.exists(path=path):
      messagebox.showwarning("Attention - Path Error", message=rf"The following location does not exist and will be skipped: {path}." + "\nPress OK to Continue.")

    elif path in entry_path_list:
      messagebox.showwarning("Attention - Path Error", message=rf"The following location is already being searched: {path}." + "\nPress OK to Continue.")
      
    else:
      entry_path_list.append(path)

  return entry_path_list

def evalute_data(dup_data):
  for k in list(dup_data.keys()):
    if len(dup_data[k]) <= 1:
      del dup_data[k]

def populate_treeview(dup_data):
  parent_id = 0

  for file_name, duplicate_data in dup_data.items():
    child_id = 0
    tree_view.insert(parent="", index="end", iid=str(parent_id), values=(file_name, "", ""), open=True)

    for file_data in duplicate_data:
      path, size = file_data.get("path"), file_data.get("size")
      
      tree_view.insert(parent=rf"{parent_id}", index="end", iid=rf"{parent_id}.{child_id}", values=("", path, size), open=True)
      child_id += 1
    
    parent_id += 1

def begin_scan():
  clear_treeview()

  path_list = path_text.get('1.0', 'end').strip().split("\n")
  # needs to be cleaned up, for some reason the list still has a single empty string/char index

  print(path_list)

  if path_list:
    paths_to_scan = get_entry_data(path_list=path_list)
    duplicate_dict = d.exec_scan(path_list=paths_to_scan)

    if duplicate_dict:
      evalute_data(dup_data=duplicate_dict)
      populate_treeview(dup_data=duplicate_dict)

    else:
      messagebox.showinfo("Information","There are no duplicate files to remove.")
  else:
    messagebox.showwarning("Attention - Path Error", message=rf"No paths given." + "\nPress OK to Continue.")

def remove_selected_from_tree():
  n = 1
  max_selected = len(tree_view.selection()) + 1
  amount_deleted = 0.0

  for treeview_index in tree_view.selection():
    file_path, size = tree_view.item(treeview_index)['values'][1], tree_view.item(treeview_index)['values'][2]
    
    if file_path:
      if messagebox.askyesno("Remove Duplicate","Are you sure you want to remove the file:\n" + rf"{file_path}?"):
        send2trash(file_path)
        progress(n=n, max_selected=max_selected)
        amount_deleted += float(size)
        n += 1

    else:
      messagebox.showwarning("Attention - Selection Error", 
                             message=rf"Parent cell selected for {tree_view.item(treeview_index)['values'][0]} Please select a child cell for deletion to continue." + "\nPress OK to Continue.")
 
  final_message(amount_deleted=amount_deleted)

def final_message(amount_deleted):
  messagebox.showinfo("Information","All operation have concluded.\n" + rf"{amount_deleted} MB was recovered.")
  progress_bar['value'] = 0
  clear_treeview()

def delete_sequence():
  print("Delete Selected Files.")
  remove_selected_from_tree()

def treeview_selection(event=None): # Allows the selection of multiple cells at a time  
  tree_view.selection_toggle(tree_view.focus())
  # print(tree_view.selection())

def clear_treeview():
  for item in tree_view.get_children():
   tree_view.delete(item)

def progress(n, max_selected):
    if progress_bar['value'] < 100:
        progress_bar['value'] += (n / max_selected) * 100

# Tkinter Setup
root = Tk()
root.title("Delete Duplicate Files")
root.geometry(rf"{root_width}x{root_height}")

path_label = ttk.Label(text="Directories to Search:" )
path_label.update()
path_label.place(x=755, y=1)

path_text = Text(root, height=10, width=30, font=("Helvetica", 10))
path_text.update()
path_text.focus()
path_text.place(x=755, y=20)

# add_path_button = Button(root, text="Add Another Path", command=add_path_entry_to_frame)
# add_path_button.update()
# add_path_button.place(x=root_width - add_path_button.winfo_reqwidth() - 10, y=50)

scan_button = ttk.Button(root, text="Begin Scan", command=lambda:Thread(target=begin_scan).start())
scan_button.update()
scan_button.place(x=815, y=root_height - 100, height=25, width=125)

delete_button = ttk.Button(root, text="Delete Selected Items", command=lambda:Thread(target=delete_sequence).start())
delete_button.update()
delete_button.place(x=815, y=root_height - 70, height=25, width=125)

progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=730, mode='determinate')
progress_bar.update()
progress_bar.place(x=1.5, y=301)
# print(progress_bar.winfo_reqwidth()) # need to update before getting size from progress_bar.winfo_reqwidth() or progress_bar.winfo_reqheight()

# Treeview Frame Setup
tree_height = 300
tree_width = 750

tree_view_frame = Frame(root)
tree_view_frame.place(x=1, y=1, width=tree_width, height=tree_height)

# Tree View Scrollbar
tree_scrollbar = Scrollbar(tree_view_frame)
tree_scrollbar.pack(side=RIGHT, fill=Y)

# Treeview
tree_view = ttk.Treeview(tree_view_frame, yscrollcommand=tree_scrollbar.set, selectmode="none")
tree_view.place(x=1, y=1, width=tree_width-20, height=tree_height)
tree_view.bind("<ButtonRelease-1>", treeview_selection)

tree_scrollbar.config(command=tree_view.yview)

tree_view['columns'] = ("name", "path", "size")

# Create Columns
tree_view.column("#0", width=20, minwidth=25)
tree_view.column("name", anchor=W, width=125)
tree_view.column("path", anchor=W, width=400)
tree_view.column("size", anchor=E, width=50)

# Create Headings
tree_view.heading("#0", text="", anchor=W)
tree_view.heading("name", text="File Name", anchor=CENTER)
tree_view.heading("path", text="File Path", anchor=CENTER)
tree_view.heading("size", text="File Size (MB)", anchor=CENTER)

if __name__ == "__main__":
  root.mainloop()

