import urllib.parse
import requests
import tkinter as tk
from tkinter import messagebox, ttk
import folium
import webbrowser
import os

def convert_distance(distance_miles, unit):
    if unit == 'kilometers':
        return distance_miles * 1.60934
    return distance_miles

def show_message(title, message):
    messagebox.showinfo(title, message)

def save_route_info(route, converted_distance, unit):
    with open("route_info.txt", "w") as file:
        file.write(f"Route from {orig} to {dest}\n")
        file.write(f"Distance: {converted_distance:.2f} {unit}\n")
        file.write(f"Duration: {route['formattedTime']}\n")
    show_message("Route Information", "Route information saved to 'route_info.txt'.")

def get_route():
    global orig, dest
    orig = orig_entry.get().strip()
    dest = dest_entry.get().strip()
    unit_preference = unit_var.get()
    
    if not orig or not dest:
        show_message("Input Error", "Please enter both origin and destination.")
        return

    # Construct API URL
    main_api = "https://www.mapquestapi.com/directions/v2/route?"
    url = main_api + urllib.parse.urlencode({'from': orig, 'to': dest, 'key': key})

    # Make the request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if 'route' in data:
            route = data['route']
            converted_distance = convert_distance(route['distance'], unit_preference)

            # Clear previous results
            for i in tree.get_children():
                tree.delete(i)

            # Insert new results into the table
            tree.insert("", "end", values=(orig, dest, f"{converted_distance:.2f} {unit_preference}", route['formattedTime']))

            # Save route information
            save_route_info(route, converted_distance, unit_preference)

            # Display the map
            display_map(data['route'])
        else:
            show_message("Error", "No route found. Please check your start and destination locations.")
    else:
        show_message("Error", f"Error: {response.status_code}\n{response.text}")

def clear_route():
    orig_entry.delete(0, tk.END)
    dest_entry.delete(0, tk.END)
    unit_var.set('miles')  # Reset to default
    for i in tree.get_children():
        tree.delete(i)

def display_map(route):
    # Create a map centered around the midpoint
    start_location = route['locations'][0]['latLng']
    end_location = route['locations'][1]['latLng']
    mid_point = [(start_location['lat'] + end_location['lat']) / 2, (start_location['lng'] + end_location['lng']) / 2]

    m = folium.Map(location=mid_point, zoom_start=10)

    # Add markers for start and end locations
    folium.Marker(location=[start_location['lat'], start_location['lng']], tooltip='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=[end_location['lat'], end_location['lng']], tooltip='End', icon=folium.Icon(color='red')).add_to(m)

    # Add the route as a polyline
    points = [(loc['latLng']['lat'], loc['latLng']['lng']) for loc in route['locations']]
    folium.PolyLine(points, color='blue', weight=5, opacity=0.7).add_to(m)

    # Save the map to an HTML file
    map_file = 'map.html'
    m.save(map_file)

    # Open the map in the default web browser
    webbrowser.open('file://' + os.path.realpath(map_file))

# API Configuration
key = "hOak7xku2fS8oxrFLKQk9TK8uPMFh0KU"  # Replace with your actual API key

# Create main Tkinter window
root = tk.Tk()
root.title("MapQuest Route Finder")
root.configure(bg='#FDF6E3')  # Cream background color

# Entry for origin
orig_label = tk.Label(root, text="Enter Origin:", bg='#FDF6E3', fg='#333333')
orig_label.pack(pady=5)
orig_entry = tk.Entry(root, width=30)
orig_entry.pack(pady=5)

# Entry for destination
dest_label = tk.Label(root, text="Enter Destination:", bg='#FDF6E3', fg='#333333')
dest_label.pack(pady=5)
dest_entry = tk.Entry(root, width=30)
dest_entry.pack(pady=5)

# Unit selection
unit_var = tk.StringVar(value='miles')
unit_label = tk.Label(root, text="Select distance unit:", bg='#FDF6E3', fg='#333333')
unit_label.pack(pady=5)

unit_frame = tk.Frame(root, bg='#FDF6E3')
unit_frame.pack(pady=5)
tk.Radiobutton(unit_frame, text='Kilometers', variable=unit_var, value='kilometers', bg='#FDF6E3').pack(side=tk.LEFT)
tk.Radiobutton(unit_frame, text='Miles', variable=unit_var, value='miles', bg='#FDF6E3').pack(side=tk.LEFT)

# Button to get route
get_route_button = tk.Button(root, text="Get Route", command=get_route, bg='#FFD700', fg='#333333')  # Gold button
get_route_button.pack(pady=10)

# Button to clear route
clear_route_button = tk.Button(root, text="Clear Route", command=clear_route, bg='#FF6347', fg='#FFFFFF')  # Tomato button
clear_route_button.pack(pady=5)

# Results Table
columns = ('Start Location', 'End Location', 'Distance', 'Duration')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('Start Location', text='Start Location')
tree.heading('End Location', text='End Location')
tree.heading('Distance', text='Distance')
tree.heading('Duration', text='Duration')
tree.pack(pady=10)

# Run the application
root.mainloop()
