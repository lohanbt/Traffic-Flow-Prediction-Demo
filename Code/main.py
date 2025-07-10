
from tkinter import * 
from tkinter.ttk import *
import tkinter as tk
import tkintermapview
import map_utils
import actions
import json


########## RUN THE GUI ##########


def main():

  ######################### Prepare the data #########################
  scats = map_utils.get_scats()
  graph = map_utils.build_graph("map/coordinates.csv")

  # TODOs
  # 1. Run the GUI
  ######################### GUI #########################

  ###  ROOT FRAME
  root = Tk()
  root.title("Traffic Flow Prediction System")
  root.geometry("960x800")
  root.rowconfigure(0, weight=1)
  root.rowconfigure(1, weight=10)
  root.rowconfigure(2, weight=10)
  root.columnconfigure(0, weight=100)


  ### TITLE
  title_frame = tk.Frame(root, relief="solid", background="lightblue")
  title_frame.grid(row=0, column=0, sticky=NSEW)
  title_frame.columnconfigure(0, weight=1)
  title = tk.Label(title_frame, text="Traffic Flow Prediction System", font=("Helvetica", 24), background="lightblue")
  title.grid(row=0, column=0, padx=20, pady=20)

  ### BODY FRAMES 
  body_frame = tk.Frame(root)
  body_frame.grid(row=1, column=0, padx=0, sticky=NSEW)
  body_frame.columnconfigure(0, weight=10)
  body_frame.columnconfigure(1, weight=3)
  body_frame.rowconfigure(0, weight=2)
  body_frame.rowconfigure(1, weight=3)

  ### FRAME FOR SCAT INPUTS
  input_frame = tk.Frame(body_frame, padx=30, pady=5, background="#F0F4BF")
  input_frame.grid(row=0, column=0, sticky=NSEW)
  input_frame.rowconfigure(0, weight=1)
  input_frame.rowconfigure(1, weight=1)
  input_frame.columnconfigure(0, weight=1)
  input_frame.columnconfigure(1, weight=1)
  input_frame.columnconfigure(2, weight=3)

  ### FRAME FOR BUTTON AND OUTPUTS
  output_frame = tk.Frame(body_frame, padx=0, pady=5, background="#FAE0D8")
  output_frame.grid(row=1, column=0, sticky=NSEW)
  output_frame.rowconfigure(0, weight=1)
  output_frame.rowconfigure(1, weight=1)

  paths_frame = tk.Frame(body_frame, padx=20, pady=5, background="#FFF5ED")
  paths_frame.grid(row=0, column=1, sticky=NSEW, rowspan=2)


  ### CHOOSE DEPARTURE SCAT 
  departure_label = Label(input_frame, text="Departure Scat:", font=("Helvetica", 16, 'bold'))
  departure_label.grid(row=0, column=0, sticky=W)
  departure_menu = OptionMenu( input_frame , StringVar() , *scats)
  departure_menu.grid(row=0, column=1, padx=20, sticky=E)

  ### CHOOSE DEPARTMENT SCAT
  destination_label = Label(input_frame, text="Destination Scat:", font=("Helvetica", 16, 'bold'))
  destination_label.grid(row=1, column=0, sticky=W)
  destination_menu = OptionMenu( input_frame , StringVar() , *scats )
  destination_menu.grid(row=1, column=1, padx=20, sticky=E)

  ### Variable for Radio button (paths)
  v = StringVar(body_frame, "0")
 
  # Dictionary to create multiple buttons
  values = {"Path 1" : "1",
            "Path 2" : "2",
            "Path 3" : "3",
            "Path 4" : "4",
            "Path 5" : "5"}
  
  # Loop is used to create multiple Radiobuttons
  # rather than creating each button separately
  for (text, value) in values.items():
      tk.Radiobutton(paths_frame, text = text, variable = v, 
                  value = value, background="#FFF5ED").grid(row=int(value), column=0, padx=10, pady=5, sticky="w")
  

  ### SHOW RESULT
  ### Result variable (display path)
  result_var = StringVar()
  result_var.set("Path to destination: ")
  result = Label(output_frame, textvariable=result_var, font=("Helvetica", 16, 'bold'))
  result.grid(row=0, column=0, padx=(30, 10), sticky=W)

  ### Cost variable (display time)
  cost_var = StringVar()
  cost_var.set("Path cost")
  cost = Label(output_frame, textvariable=cost_var, font=("Helvetica", 16, 'bold'))
  cost.grid(row=1, column=0, padx=(30, 10), sticky=W)

  # Store found paths
  result_list = StringVar()

  ### MAP GUI
  map_label = tk.Frame(root, background="#F1DEEE")
  map_label.grid(row=2, column=0, sticky=NSEW)
  map_widget = tkintermapview.TkinterMapView(map_label, width=920, height=400)

  map_widget.set_position(-37.8215, 145.0365)
  map_widget.set_zoom(13)
  map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
  map_widget.grid(row=0, column=0, padx=20, pady=20)
  map_widgets = map_utils.print_all_intersections(map_widget, [])


  ### BUTTON FUNCTION
  def find_path(map_widget=map_widget, paths_frame= paths_frame):
    start = departure_menu.cget("text")
    end = destination_menu.cget("text")
    results = actions.find_path(graph, start, end)

    travel_times = []
    paths = []
    for result in results:
      travel_times.append(result[0])
      paths.append(result[1])
    print(travel_times)
    values = {"Path "+str(i+1)+ ": "+ str(travel_times[i]) + " minutes": i for i in range(len(paths))}
    paths_frame.destroy()
    paths_frame = tk.Frame(body_frame, padx=20, pady=5, background="#FFF5ED")
    paths_frame.grid(row=0, column=1, sticky=NSEW, rowspan=2)
    for (text, value) in values.items():
      tk.Radiobutton(paths_frame, text = text, variable = v, 
                  value = value, background="#FFF5ED", command=show_path).grid(row=value, column=0, padx=10, pady=5, sticky="w")
    v.set("0")
    result_list.set(json.dumps(results))
    print("Results:", results)
    cost_var.set("Path cost: " + str(results[0][0]) + " minutes")
    result_var.set("Path to destination: " + "->".join([str(node) for node in results[0][1]]))
    
    map_widget.delete_all_marker()
    map_widget.delete_all_path()
    map_utils.print_path(map_widget, results[0][1])

  ### SHOW PATH FUNCTION (show path on map)
  def show_path():
    # Get the paths variable & set the text to match option
    paths = json.loads(result_list.get())
    print("Paths:", paths)
    current_value = int(v.get())
    current_path = paths[current_value]
    cost_var.set("Path cost: " + str(current_path[0]) + " minutes")
    result_var.set("Path to destination: " + "->".join([str(node) for node in current_path[1]]))

    # Show on map (Reset map, create new markers, create new paths)
    map_widget.delete_all_marker()
    map_widget.delete_all_path()

    map_utils.print_path(map_widget, current_path[1])

  ### BUTTON
  button = tk.Button( input_frame , text = "Find path", command = find_path)
  button.grid(row=0, column=2, padx=10, pady=5, sticky='nse', rowspan=2)


  # Start the Tkinter event loop
  root.mainloop()

if __name__ == '__main__':
  main()
