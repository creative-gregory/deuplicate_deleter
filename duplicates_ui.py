import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from time import sleep
import duplicates as d
import json, os
from send2trash import send2trash
from threading import Thread
from datetime import datetime

class DuplicatesGUI(tk.Frame):
    
  def __init__(self, window=None):
    super().__init__(window)
    self.root           = window
    self.window_height  = 400
    self.window_width   = 1000

    self.screen_width   = self.root.winfo_screenwidth()
    self.screen_height  = self.root.winfo_screenheight()

    self.root.title("Delete Duplicate Files")
    self.root.geometry(rf"{self.window_width}x{self.window_height}+{(self.screen_width - self.window_width) // 2}+{(self.screen_height - self.window_height) // 2}")

    self.tree_view_frame = tk.Frame(root)
    self.tree_scrollbar = tk.Scrollbar(self.tree_view_frame)
    self.tree_view = ttk.Treeview(self.tree_view_frame, yscrollcommand=self.tree_scrollbar.set, selectmode="none")

    self.base_progress_text = "Current Step: "
    self.progress_label = ttk.Label(text="")

    self.draw_widgets()

    self.path_list       = list()
    self.duplicates_dict = dict()

  def confirm_entry_text(self):
    entry_path_list = list()
    
    for path in self.path_list:
      if not os.path.exists(path=path):
        messagebox.showwarning("Attention - Path Error", message=rf"The following location does not exist and will be skipped: {path}." + "\nPress OK to Continue.")

      elif path in entry_path_list:
        messagebox.showwarning("Attention - Path Error", message=rf"The following location is already being searched: {path}." + "\nPress OK to Continue.")
        
      else:
        entry_path_list.append(path)

    return entry_path_list

  def evalute_data(self):
    for k in list(self.duplicates_dict.keys()):
      if len(self.duplicates_dict[k]) <= 1:
        del self.duplicates_dict[k]

  def populate_treeview(self):
    parent_id = 0

    for file_name, duplicate_data in self.duplicates_dict.items():
      child_id = 0
      self.tree_view.insert(parent="", index="end", iid=str(parent_id), values=(file_name, "", ""), open=True)

      for file_data in duplicate_data:
        path, size = file_data.get("path"), file_data.get("size")
        
        self.tree_view.insert(parent=rf"{parent_id}", index="end", iid=rf"{parent_id}.{child_id}", values=("", path, size), open=True)
        child_id += 1

        # date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print(rf"{date_time} - Populating: {path}")

      parent_id += 1

  def disable_scrollbar(self):
    self.tree_scrollbar.pack_forget()

  def enable_scrollbar(self):
    self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

  def scan(self, path_text):
    self.progress_label.config(text = self.base_progress_text + "Beginning Scan Process")

    self.clear_treeview()
    self.disable_scrollbar()

    self.path_list = str(path_text.get('1.0', 'end')).strip().split("\n")
   
    if self.path_list and '' not in self.path_list:  # removes single empty string/char index from tk.Text().get()
      self.paths_to_scan = self.confirm_entry_text()
      
      self.progress_bar.config(mode='indeterminate')
      self.progress_bar.start(25)

      self.progress_label.config(text = self.base_progress_text + "Searching for Duplicates")
      self.duplicates_dict = d.exec_scan(path_list=self.paths_to_scan)
      
      date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(rf"{date_time} - Scan Completed")

      if self.duplicates_dict:
        self.progress_label.config(text = self.base_progress_text + "Evaluating Duplicates Found")
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(rf"{date_time} - Evaluation Beginning")
      
        self.evalute_data()
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(rf"{date_time} - Evaluation Completed")

        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(rf"{date_time} - TreeView Population Beginning")

        self.populate_treeview()
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(rf"{date_time} - TreeView Population Completed")


        self.progress_bar.stop()
        self.enable_scrollbar()
        self.progress_label.config(text = self.base_progress_text + "Duplicate Evaluation and Table Population Completed")
      else:
        messagebox.showinfo("Information","There are no duplicate files to remove.")

    else:
      messagebox.showwarning("Attention - Path Error", message=rf"No paths given." + "\nPress OK to Continue.")

    

  def remove_from_treeview(self, treeview_index):
    file_path, size = self.tree_view.item(treeview_index)['values'][1], self.tree_view.item(treeview_index)['values'][2]
    self.tree_view.item(treeview_index, value=("" , rf"Deleted: {file_path}", "-"))

  def remove_selected_from_tree(self):
    self.progress_label.config(text = self.base_progress_text + "Removing Selected Duplicates")

    self.progress_bar.config(mode='determinate')
    n, max_selected = 1, len(self.tree_view.selection()) + 1
    amount_deleted = 0.0

    for treeview_index in self.tree_view.selection():
      file_path, size = self.tree_view.item(treeview_index)['values'][1], self.tree_view.item(treeview_index)['values'][2]
      
      if file_path:
        if messagebox.askyesno("Remove Duplicate","Are you sure you want to remove the file:\n" + rf"{file_path}?"):
          send2trash(file_path)
          self.update_progress(n=n, max_selected=max_selected)
          self.remove_from_treeview(treeview_index=treeview_index)
          amount_deleted += float(size)
          n += 1

      else:
        messagebox.showwarning("Attention - Selection Error", 
                              message=rf"Parent cell selected for {self.tree_view.item(treeview_index)['values'][0]} Please select a child cell for deletion to continue." + "\nPress OK to Continue.")
  
    self.final_message(amount_deleted=amount_deleted)

  def treeview_selection(self, tree_view): # Allows the selection of multiple cells at a time  
    self.tree_view.selection_toggle(tree_view.focus())
    print(self.tree_view.selection())

  def final_message(self, amount_deleted):
    messagebox.showinfo("Information","All operation have concluded.\n" + rf"{amount_deleted} MB was recovered.")
    self.progress_bar['value'] = 0
    
  def delete_sequence(self):
    print("Delete Selected Files.")
    self.remove_selected_from_tree()

  def clear_treeview(self):
    for item in self.tree_view.get_children():
      self.tree_view.delete(item)

  def update_progress(self, n, max_selected):
      if self.progress_bar['value'] < 100:
          self.progress_bar['value'] += (n / max_selected) * 100

  def draw_widgets(self):
    print("Drawing Widgets")
    
    self.progress_label.update()
    self.progress_label.place(x=250, y=350)

    self.path_label = ttk.Label(text="Directories to Search:" )
    self.path_label.update()
    self.path_label.place(x=755, y=1)

    self.path_text = tk.Text(self.root, height=10, width=30)
    self.path_text.update()
    self.path_text.focus()
    self.path_text.place(x=755, y=20)

    self.scan_button = ttk.Button(self.root, text="Begin Scan", command=lambda:Thread(target=self.scan, args=[self.path_text]).start())
    self.scan_button.update()
    self.scan_button.place(x=815, y=self.window_height - 100, height=25, width=125)

    self.delete_button = ttk.Button(self.root, text="Delete Selected Items", command=lambda:Thread(target=self.delete_sequence).start())
    self.delete_button.update()
    self.delete_button.place(x=815, y=self.window_height - 70, height=25, width=125)  

    self.progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=730, mode='determinate')
    self.progress_bar.update()
    self.progress_bar.place(x=1.5, y=301)

    # Treeview Frame Setup
    self.tree_height = 300
    self.tree_width = 750
    self.tree_view_frame.place(x=1, y=1, width=self.tree_width, height=self.tree_height)

    # Treeview
    self.tree_view.place(x=1, y=1, width=self.tree_width-20, height=self.tree_height)
    self.tree_view.bind("<ButtonRelease-1>", lambda tree_view: self.treeview_selection(tree_view=self.tree_view))
    self.tree_scrollbar.config(command=self.tree_view.yview)

    # Create Columns
    self.tree_view['columns'] = ("name", "path", "size")

    self.tree_view.column("#0", width=20, minwidth=25)
    self.tree_view.column("name", anchor=tk.W, width=125)
    self.tree_view.column("path", anchor=tk.W, width=400)
    self.tree_view.column("size", anchor=tk.E, width=50)

    # Create Headings
    self.tree_view.heading("#0", text="", anchor=tk.W)
    self.tree_view.heading("name", text="File Name", anchor=tk.CENTER)
    self.tree_view.heading("path", text="File Path", anchor=tk.CENTER)
    self.tree_view.heading("size", text="File Size (MB)", anchor=tk.CENTER)

if __name__ == "__main__":
  root = tk.Tk()
  app = DuplicatesGUI(window=root)
  app.mainloop()