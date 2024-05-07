from tkinter import *
from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import ttk
import query_new as qs 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

def AbsolutePath(directory):
    """ Get the absolute path of the directory where files or pictures are stored. """
    base_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_directory, directory)

def resize_image(path, size):
    """ Open an image and resize it to the specified size. """
    original_image = Image.open(path)
    resized_image = original_image.resize(size, Image.Resampling.LANCZOS)  # Updated to use Image.Resampling.LANCZOS
    return ImageTk.PhotoImage(resized_image)

def open_analytics_window():
    summary_window = tk.Toplevel()
    summary_window.title('Graph Analysis')
    summary_window.geometry("1366x720")

    # Use the same background as the main window
    bg_path = AbsolutePath(r'C:\Users\User\Desktop\Ronit-Projects\Temp-Work\GDS\bg2.jpg')
    bg_image = ImageTk.PhotoImage(Image.open(bg_path))
    bg_label = tk.Label(summary_window, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame for analysis buttons
    buttons_frame = tk.Frame(summary_window, bg='white')
    buttons_frame.place(relx=0.05, rely=0.1, relwidth=0.2, relheight=0.8)

    # Buttons for different types of graph analysis
    page_rank_button = tk.Button(buttons_frame, text="Page Rank", bg='lightgray', command=lambda: display_analysis('Page Rank'))
    page_rank_button.pack(fill='x', padx=10, pady=10)

    betweenness_button = tk.Button(buttons_frame, text="Betweenness", bg='lightgray', command=lambda: display_analysis('Betweenness'))
    betweenness_button.pack(fill='x', padx=10, pady=10)

    community_detection_button = tk.Button(buttons_frame, text="Community Detection", bg='lightgray', command=lambda: display_analysis('Community Detection'))
    community_detection_button.pack(fill='x', padx=10, pady=10)

    # Generate button
    generate_button = tk.Button(summary_window, text="Generate", bg='lightgray', command=lambda: generate_analysis_summary())
    generate_button.place(relx=0.05, rely=0.9, relwidth=0.2)

    # Frame for displaying the selected graph analysis content
    global content_frame
    content_frame = tk.Frame(summary_window, bg='lightgray', borderwidth=1, relief="sunken")
    content_frame.place(relx=0.3, rely=0.1, relwidth=0.65, relheight=0.8)

    # Keep references to the images to prevent garbage collection
    summary_window.bg_image = bg_image
    summary_window.mainloop()

def generate_analysis_summary(query):
    print(f"Generating analysis for: {query}")
    if query == 'Dominant Party':
        data = qs.find_dominant_party()  # Assuming this returns a list of dictionaries with keys 'Wins' and 'Party'
        # print(f"Data received for pie chart: {data}")
        generate_pie_chart(content_frame, data)
    elif query == "Recurring MNAs":
        data = qs.find_recurring_mnas()  # Ensure this function exists and returns data in the expected format
        # Add another type of visualization function here if needed
        print(f"Data received for bar chart: {data}")

def generate_pie_chart(root, data_json):

    
    data = json.loads(data_json)
    
    fig = Figure(figsize=(10, 5), dpi=100)
    plot = fig.add_subplot(111)

    # Extracting data for the pie chart
    wins = [item["Dominant Party"]["Wins"] for item in data]
    parties = [item["Dominant Party"]["Party"] for item in data]

    # Creating the pie chart
    wedges, texts, autotexts = plot.pie(wins, labels=parties, autopct='%1.1f%%', startangle=140)

    # Beautifying the labels
    for text, autotext in zip(texts, autotexts):
        text.set_color('grey')
        autotext.set_color('white')

    # Adding a legend
    plot.legend(wedges, parties, title="Parties", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Setting the title
    plot.set_title('Dominant Party Wins by Election Year')

    # Embedding the figure in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    

def open_summary_window():
    summary_window = tk.Toplevel()
    summary_window.title('Summary Analysis')
    summary_window.geometry("1366x720")

    # Use the same background as the main window
    bg_path = AbsolutePath(r'C:\Users\User\Desktop\Ronit-Projects\Temp-Work\GDS\bg2.jpg')
    bg_image = ImageTk.PhotoImage(Image.open(bg_path))
    bg_label = tk.Label(summary_window, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame for analysis buttons
    buttons_frame = tk.Frame(summary_window, bg='white')
    buttons_frame.place(relx=0.05, rely=0.1, relwidth=0.2, relheight=0.8)

    # Buttons for different types of analysis
    dominant_party_button = tk.Button(buttons_frame, text="Dominant Party", bg='lightgray', command=lambda: generate_analysis_summary('Dominant Party'))
    dominant_party_button.pack(fill='x', padx=10, pady=10)

    recurring_mnas_button = tk.Button(buttons_frame, text="Recurring MNAs", bg='lightgray', command=lambda: generate_analysis_summary('Recurring MNAs'))
    recurring_mnas_button.pack(fill='x', padx=10, pady=10)

    # Generate button
    generate_button = tk.Button(summary_window, text="Generate", bg='lightgray', command=lambda: generate_analysis_summary())
    generate_button.place(relx=0.05, rely=0.9, relwidth=0.2)

    # Frame for displaying the selected analysis content
    global content_frame
    content_frame = tk.Frame(summary_window, bg='lightgray', borderwidth=1, relief="sunken")
    content_frame.place(relx=0.3, rely=0.1, relwidth=0.65, relheight=0.8)

    # Keep references to the images to prevent garbage collection
    summary_window.bg_image = bg_image
    summary_window.mainloop()

def main():
    root = Tk()
    root.title('Election Analysis ')
    root.geometry("1366x720")

    # Setting up the background image
    bg_path = AbsolutePath(r'C:\Users\User\Desktop\Ronit-Projects\Temp-Work\GDS\bg2.jpg')
    bg_image = ImageTk.PhotoImage(Image.open(bg_path))
    bg_label = Label(root, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Title Label
    title_label = Label(root, text="Lumber one Elections", font=("Helvetica", 24, 'bold'), bg='white', fg='black')
    title_label.pack(pady=20)  # This will place the title at the top-center

    # Images for buttons
    ml_image = resize_image(AbsolutePath('ml.png'), (200, 200))
    analytics_image = resize_image(AbsolutePath('analytics.png'), (200, 200))
    summary_image = resize_image(AbsolutePath('summary.png'), (200, 200))

    # Creating a frame to contain buttons and labels
    my_frame = Frame(root, bg='white', borderwidth=0)  # Make sure the frame background matches the window if needed
    my_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Button and label for Analytics
    analytics_button = Button(my_frame, image=analytics_image, borderwidth=0, highlightthickness=0, command=open_analytics_window)
    analytics_button.grid(row=0, column=0, padx=20, pady=10)
    Label(my_frame, text="Analytics", bg='white', font=("Helvetica", 14)).grid(row=1, column=0)

    # Button and label for Machine Learning
    ml_button = Button(my_frame, image=ml_image, borderwidth=0, highlightthickness=0)
    ml_button.grid(row=0, column=1, padx=20, pady=10)
    Label(my_frame, text="Machine Learning", bg='white', font=("Helvetica", 14)).grid(row=1, column=1)

    # Button and label for Summary
    summary_button = Button(my_frame, image=summary_image, borderwidth=0, highlightthickness=0, command=open_summary_window)
    summary_button.grid(row=0, column=2, padx=20, pady=10)
    Label(my_frame, text="Summary", bg='white', font=("Helvetica", 14)).grid(row=1, column=2)

    signature_label = Label(root, text="Built by ARMY", font=("Helvetica", 14), bg='white', fg='black')
    signature_label.place(relx=1.0, rely=1.0, anchor='se')  # This will place the text at the bottom-right

    root.mainloop()

    
if __name__ == '__main__':
    main()
