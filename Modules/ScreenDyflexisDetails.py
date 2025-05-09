import tkinter as tk
import tkinter.ttk as ttk
from pprint import pprint

import customtkinter as ctk

from Modules.Constants import Constants
from Modules.dataClasses import EventDataObject


class ScreenDyflexisDetails(tk.Toplevel):
  eventData = None
  def __init__(self, eventData:EventDataObject):
    tk.Toplevel.__init__(self)
    window_width = 500
    window_height = 400

    self.eventData = eventData
    self.configure(background=Constants.primary_color)
    # get screen dimension
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()

    # find the center point
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    # create the screen on window console
    # self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    self.attributes("-topmost", False)
    self.title('Dyflexis Details')
    self.master.configure(background=Constants.primary_color)

    self.rowconfigure(0,weight=1)
    self.columnconfigure(0,weight=1)

    tabview = ctk.CTkTabview(master=self,width=525)
    tabview.grid(row=0, column=0, sticky=tk.NSEW,padx=10,pady=10)

    tabview.add("agenda items")  # add tab at the end
    tabview.add("dyflexis data")  # add tab at the end
    # tabview.set("agenda items")  # set currently visible tab
    tabview.set("dyflexis data")  # set currently visible tab


    # self.textbox = ctk.CTkTextbox(self, width=window_width/2,height=20, corner_radius=0)
    # self.textbox.configure(height=20)
    # self.textbox.grid(row=0, column=0, sticky=tk.NSEW)
    tabview.tab("agenda items").rowconfigure(0, weight=1)
    tabview.tab("agenda items").columnconfigure(0, weight=1)
    tabview.tab("agenda items").columnconfigure(1, weight=0)

    tabview.tab("dyflexis data").rowconfigure(0, weight=1)
    tabview.tab("dyflexis data").columnconfigure(0, weight=1)
    tabview.tab("dyflexis data").columnconfigure(1, weight=0)

    columns = ('date', 'title', 'id')
    self.treeview = ttk.Treeview(
      master=tabview.tab("agenda items"),
      columns=columns,
      show='headings')
    self.treeview.grid(row=0, column=0, sticky=tk.NSEW)
    vsb = ttk.Scrollbar(
      master=tabview.tab("agenda items"),
      orient="vertical",
      command=self.treeview.yview)
    vsb.grid(row=0,column=1, sticky=tk.NS)

    # define headings
    self.treeview.heading('date', text='date')
    self.treeview.heading('title', text='title')
    self.treeview.heading('id', text='id')
    self.treeview.column('0', width=90, anchor=tk.W)
    self.treeview.column('1', width=300, anchor=tk.W)
    self.treeview.column('2', width=120, anchor=tk.W)

    if self.eventData is not None:
      for shift in self.eventData.shift:
        self.treeview.insert(
          '',
          tk.END,
          values=(shift.date, shift.title, shift.id
                  )
        )

    columns = ('date', 'title', 'id')
    self.dyflexisTree = ttk.Treeview(
      master=tabview.tab("dyflexis data"),
      columns=columns,
      show='headings')
    self.dyflexisTree.grid(row=0, column=0, sticky=tk.NSEW)
    vsb = ttk.Scrollbar(
      master=tabview.tab("dyflexis data"),
      orient="vertical",
      command=self.dyflexisTree.yview)
    vsb.grid(row=0,column=1, sticky=tk.NS)
    # define headings 520
    self.dyflexisTree.heading('date', text='date')
    self.dyflexisTree.heading('title', text='title')
    self.dyflexisTree.heading('id', text='id')
    self.dyflexisTree.column('0',width=90,anchor=tk.W)
    self.dyflexisTree.column('1',width=300,anchor=tk.W)
    self.dyflexisTree.column('2',width=120,anchor=tk.W)

    if self.eventData is not None:
      for list in self.eventData.list:
        parent =self.dyflexisTree.insert(
          '',
          tk.END,
          values=(list.date,len(list.events)+len(list.assignments)+len(list.agenda))
        )
        for event in list.events:
          self.dyflexisTree.insert(
            parent,
            tk.END,
            values=(' ' , event['text'], event['id'])
          )
        for event in list.assignments:
          self.dyflexisTree.insert(
            parent,
            tk.END,
            values=(' ' , event['text'], event['id'])
          )
        for event in list.agenda:
          self.dyflexisTree.insert(
            parent,
            tk.END,
            values=(' ' , event['text'], event['id'])
          )