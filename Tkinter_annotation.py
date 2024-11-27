import cv2
import numpy as np
from tkinter import Tk, Label, Canvas, filedialog, messagebox, simpledialog
from tkinter import ttk, Toplevel
from PIL import Image, ImageTk
import customtkinter
import torch
from Segmentator import SAM_Segmentator
from Polygon_segmentator import Polygon_Segmentator
from constants import *

class ImageEditor:
     def __init__(self, root):
          self.root=root
          self.root.title("Image Editor")
          self.root.configure(bg=COLOUR_ROOT_BG)
          self.device= "cuda" if torch.cuda.is_available() else "cpu"
          #Initialize variables
          self.image=None          #Loaded image (Image that is used to show created boxes)
          self.original_image=None #Original image (Image passed to the SAM model)
          self.tk_image=None       #Image format for canvas
          #Coordinated passed to the SAM model for segmentation purposes
          self.rect_start=None     #Coordinates of rect starting point (x,y)
          self.rect_end=None       #Coordinated of rect ending point (x,y)
          #The name specified from set of data created using SAM
          self.file_name=None
          #Zoom factors
          self.zoom_value = ZOOM_VALUE
          self.zoom_factor = ZOOM_FACTOR
          self.min_zoom = ZOOM_MIN
          self.max_zoom = ZOOM_MAX
          #Original image dimensions
          self.image_shape=None
          #Prompt state
          self.prompt_state=None
          #Initialize query box
          self.query_box=None

          # Polygon drawing state
          self.drawing_polygon = False
          self.first_polygon = True
          self.edit_polygon = False
          self.first_edit_polygon = True
          self.polygon_points = []

          #Segemtation result
          self.segment = None

          #Apperance mode
          customtkinter.set_appearance_mode('dark')

          #Create GUI elements
          self.canvas=Canvas(root, width=1200, height=800,  bg=COLOUR_CANVAS_BG, highlightthickness=0)
          self.canvas.pack(side="left", padx=10, pady=20)  # Position the canvas on the left side

          # Create a frame for the buttons on the right side
          button_frame =customtkinter.CTkFrame(root)
          button_frame.pack(side="right", fill="y", padx=20)

          #Buttons:
          # Group 1: Main actions (Load, Save, Reset, Perform Segmentation, Exit)
          self.load_button = customtkinter.CTkButton(button_frame,text="Load", command=self.load_image)          
          self.save_button = customtkinter.CTkButton(button_frame, text="Save", command=self.save_image)
          self.reset_button = customtkinter.CTkButton(button_frame, text="Reset Annotation", command=self.reset_rectangle)
          self.draw_polygon_button = customtkinter.CTkButton(button_frame, text="Draw Polygon", command=self.start_polygon_drawing)
          self.perform_segmentation_button = customtkinter.CTkButton(button_frame, text="Perform segmentation", command=self.perform_segmentation)
          self.exit_button = customtkinter.CTkButton(button_frame, text="Exit", command=root.quit)

          # Arrange these buttons in the grid (1 column, multiple rows)
          self.load_button.grid(row=0, column=0, pady=10, sticky="ew")
          self.save_button.grid(row=1, column=0, pady=10, sticky="ew")
          self.reset_button.grid(row=2, column=0, pady=10, sticky="ew")
          self.draw_polygon_button.grid(row=3, column=0, pady=10, sticky="ew")
          #self.reset_polygon_button.grid(row=4, column=0, pady=10, sticky="ew")
          self.perform_segmentation_button.grid(row=4, column=0, pady=10, sticky="ew")
          self.exit_button.grid(row=5, column=0, pady=10, sticky="ew")

          # Create a frame for other controls
          second_frame = customtkinter.CTkFrame(button_frame)
          second_frame.grid(row=7, column=0, pady=20, sticky="ew")

          # Zoom controls (Zoom In, Zoom Out)
          self.zoom_in_button = customtkinter.CTkButton(second_frame, text="Zoom In", command=self.zoom_in)
          self.zoom_out_button = customtkinter.CTkButton(second_frame, text="Zoom Out", command=self.zoom_out)

          # Arrange zoom buttons horizontally
          self.zoom_in_button.grid(row=1, column=0, padx=10, pady=20, sticky="ew")
          self.zoom_out_button.grid(row=1, column=1, padx=10, pady=20, sticky="ew")

          # Mask edit controls
          self.edit_mask_polygon = customtkinter.CTkButton(second_frame, text="Edit Polygon",command=self.edit_mask_polygon)
          self.edit_mask_button = customtkinter.CTkButton(second_frame, text="Edit Mask",command=self.edit_mask)

          # Arrrange mask control buttons
          self.edit_mask_polygon.grid(row=2, column=0, padx=10, sticky="ew")
          self.edit_mask_button.grid(row=2, column=1, padx=10, sticky="ew")

          # Bind mouse events for rectangle drawing (unchanged)
          self.canvas1 = Canvas(root, width=500, height=500, bg=COLOUR_CANVAS_MOUSE)
          self.canvas.bind("<Button-1>", self.on_mouse_down)
          self.canvas.bind("<Double-1>", self.on_double_click) 
          self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
          self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
          self.canvas.bind("<Motion>", self.on_mouse_move)  
          self.canvas.bind("<Button-3>", self.on_mouse2_down)
          self.canvas.bind("<ButtonRelease-3>", self.on_mouse2_up)


     #Method that loads image file
     def load_image(self):
        """Load the image from a computer."""
        file_path=customtkinter.filedialog.askopenfilename(filetypes=[("Image files"," *.jpeg *.jpg *.png")])     #Find any files to load
        self.file_name=file_path.split("/")[-1]   #Store the file name of image
        self.root.title(self.file_name)
        if file_path:
               #Load image with OpenCV
               self.image=cv2.imread(file_path)
               self.image=cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
               #Store the original image shape
               self.image_shape=[self.image.shape[1],self.image.shape[0]] #width, height
               #Copy the original image of original shape
               self.original_image=self.image.copy()
               self.zoom_value=1.0
               self.update_canvas()

               #Load arrays that are used if points are used
               self.input_point = np.empty((0, 2))
               self.input_label = np.empty((0,))
               self.box_list=[]

               #Setup the mask used for polygon drawing
               self.mask = np.zeros((self.image_shape[1], self.image_shape[0]), dtype=np.uint8)
    
     #Zoom in method
     def zoom_in(self):
        """Zoom in by increasing the zoom factor."""
        self.zoom_value = min(self.zoom_value + self.zoom_factor, self.max_zoom)
        self.update_canvas()

     #Zoom out method
     def zoom_out(self):
        """Zoom out by decreasing the zoom factor."""
        self.zoom_value = max(self.zoom_value - self.zoom_factor, self.min_zoom)
        self.update_canvas()

     #Define point prompt method
     def edit_mask(self):
          """Edit a mask created using polygons or SAM"""
          if self.segment is not None or self.edit_polygon==True:
               if self.edit_polygon==True:
                    self.segment.edit_poylgon_segmentation(self.polygon_points)
                    self.polygon_points.clear()
                    self.drawing_polygon = False

               else:
                    self.segment.edit_segmentation(self.rect_start, 
                                              self.rect_end)
                    self.drawing_polygon = False
               self.update_canvas_annotated_image()
               self.edit_polygon=False

     def edit_mask_polygon(self):
          """Start drawing polygon for editing the mask."""
          self.edit_polygon=True
          self.drawing_polygon=True
          self.polygon_points.clear()
          if self.first_edit_polygon:
                messagebox.showinfo("Polygon for mask editing", "Create a polygon to edit the mask.")
                self.first_edit_polygon=False
          
     #Start drawing a polygon
     def start_polygon_drawing(self):
          """Start polygon drawing mode."""
          self.drawing_polygon = True
          self.polygon_points.clear()
          self.segment = None
          if self.first_polygon:
               self.file_name=simpledialog.askstring("Polygon Mode", "Click on the canvas to add vertices. Double-click to complete. \n Enter the filename (without extension):")
               self.first_polygon=False

     #Complete a polygon creation
     def complete_polygon(self):
          """Complete the polygon and stop polygon drawing mode."""
          if len(self.polygon_points) < 3:
               messagebox.showwarning("Polygon Error", "At least 3 points are needed to complete a polygon.")
               return
          messagebox.showinfo("Polygon", "Polygon created successfully.")

          self.drawing_polygon = False
          # Draw the completed polygon on the image
          if self.edit_polygon == True:
               cv2.polylines(self.image, [np.array(self.polygon_points)], isClosed=True, color=(255, 0, 0), thickness=2)
          else:
               cv2.polylines(self.image, [np.array(self.polygon_points)], isClosed=True, color=(255, 255, 255), thickness=2)
          self.update_canvas()
          #print("Polygon points:", self.polygon_points)  

     #Mouse action methods:
     def on_mouse_down(self, event):
         if self.image is not None:
               if self.drawing_polygon is False:
                    self.rect_start=(event.x-self.x, event.y-self.y) 
               else:
                    x, y = int((event.x - self.x) / self.zoom_value), int((event.y - self.y) / self.zoom_value)
                    self.polygon_points.append((x, y))
                    self.update_canvas()

     #Compplete the polygon on double click
     def on_double_click(self, event):
        """Complete the polygon when double-clicked."""
        self.number_of_polygons=1
        if self.drawing_polygon:
            self.complete_polygon()
            self.polygon=Polygon_Segmentator(self.zoomed_image, 
                                             self.file_name, 
                                             self.image_shape, 
                                             self.polygon_points, 
                                             self.mask)
            self.polygon.create_polygon()

     def on_mouse_drag(self, event):
         if self.rect_start:
              self.rect_end=(event.x-self.x, event.y-self.y)
              self.update_canvas()

     def on_mouse_up(self, event):
         if self.rect_start:
               self.rect_end=(event.x-self.x, event.y-self.y)
               if self.rect_start == self.rect_end:
                    self.input_point = np.append(self.input_point,[self.rect_start], axis=0)
                    self.input_label = np.append(self.input_label, [1], axis=0)
               else:
                    # if self.rect_start[0] > self.rect_end[0] or self.rect_start[1] > self.rect_end[1]:
                    #      self.rect_temp=self.rect_start
                    #      self.rect_start=self.rect_end
                    #      self.rect_end=self.rect_temp
                    self.box=[self.rect_start[0], self.rect_start[1], self.rect_end[0], self.rect_end[1]]
                    self.box_list.append(self.box)
                    print(f"Box: {self.box}")
                    print(f"Image shape: {self.image.shape}")
                    #If there is only one box, create a numpy array
                    if len(self.box_list)==1:
                         self.input_point = np.array(self.box)
                         self.input_label = np.append(self.input_label, [1], axis=0)

                    #If there is more than one box, create torch tensor
                    else:
                         self.input_point = torch.tensor(self.box_list, device=self.device)
                    
     
     def on_mouse_move(self, event):
         if self.image is not None:
             #Draw the cross on canvas
             self.update_canvas(crosshair=(event.x-self.x, event.y-self.y))

     #Second mouse button
     def on_mouse2_down(self, event):
         if self.image is not None:
              self.rect_start=(event.x-self.x, event.y-self.y)

     def on_mouse2_up(self, event):
         if self.rect_start:
               self.rect_end=(event.x-self.x, event.y-self.y)
               if self.rect_start == self.rect_end:
                    self.input_point= np.append(self.input_point,[self.rect_start], axis=0)
                    self.input_label = np.append(self.input_label, [0],axis=0)
               if self.rect_start[0] > self.rect_end[0] or self.rect_start[1] > self.rect_end[1]:
                         self.rect_temp=self.rect_start
                         self.rect_start=self.rect_end
                         self.rect_end=self.rect_temp
               
                    

     #Update the canvas method
     def update_canvas(self, crosshair=None):
         if self.image is not None:
               # Resize the image based on the zoom factor
               self.zoomed_width = int(self.image.shape[1] * self.zoom_value)
               self.zoomed_height = int(self.image.shape[0] * self.zoom_value)
               self.zoomed_image = cv2.resize(self.image, (self.zoomed_width, self.zoomed_height))

               #Display image
               self.canvas.delete("all")
               self.tk_image=ImageTk.PhotoImage(image=Image.fromarray(self.zoomed_image))
               # Calculate coordinates to center the image
               canvas_width = self.canvas.winfo_width()
               canvas_height = self.canvas.winfo_height()
               self.x = (canvas_width - self.zoomed_width) // 2
               self.y = (canvas_height - self.zoomed_height) // 2
               #Display the image at central coordinates
               self.canvas.create_image(self.x,self.y,anchor="nw", image=self.tk_image)

               # Draw temporary polygon while adding points
               if self.drawing_polygon==True and self.polygon_points:
                    scaled_points = [(int(px * self.zoom_value) + self.x, int(py * self.zoom_value) + self.y) for px, py in self.polygon_points]
                    for i in range(1, len(scaled_points)):
                         self.canvas.create_line(scaled_points[i - 1], scaled_points[i], fill="red", width=3)
                    if len(scaled_points) > 1:
                         self.canvas.create_line(scaled_points[-1], scaled_points[0], fill="red", width=3)  # Close the loop

                              
               #Draw rectangle on canvas
               if self.rect_start and self.rect_end:
                    x1,y1 = self.rect_start
                    x2,y2 = self.rect_end
                    self.canvas.create_rectangle(x1+self.x,y1+self.y,x2+self.x,y2+self.y, outline=COLOUR_BOX_OUTLINE, width=2)
               #Try to draw the all the stored boxes (if there is more than one)
               try:
                    for box in self.box_list:
                         x1, y1, x2, y2 = box
                         self.canvas.create_rectangle(x1 + self.x, y1 + self.y, x2 + self.x, y2 + self.y, outline=COLOUR_BOX_OUTLINE, width=2)
               except:
                    pass
               #Try to draw all the stored points (if there is more than one)
               try:
                    for point in self.input_point:
                         x1, y1 = point
                         self.canvas.create_rectangle(x1 + self.x, y1 + self.y, x1 + self.x, y1 + self.y, outline=COLOUR_BOX_OUTLINE, width=2)               
               except:
                    pass
               #Display the cross for easier annotation
               if crosshair:
                    cx,cy=crosshair
                    canvas_width=self.canvas.winfo_width()
                    canvas_height=self.canvas.winfo_height()
                    self.canvas.create_line(0+self.x, cy+self.y, canvas_width+cx+self.x, cy+self.y, fill=COLOUR_LINE, dash=(2,2))
                    self.canvas.create_line(cx+self.x, 0+self.y, cx+self.x, canvas_height+cy+self.y, fill=COLOUR_LINE, dash=(2,2))

     #Update canvas with annotated image to show annotations
     def update_canvas_annotated_image(self):
         if self.segment.annotated_image is not None:
               #Display image
               self.canvas.delete("all")
               self.tk_image=ImageTk.PhotoImage(image=Image.fromarray(self.segment.image_with_contours))
               self.canvas.create_image(self.x,self.y,anchor="nw", image=self.tk_image)
               self.image=self.segment.image_with_contours.copy()
               self.image=cv2.resize(self.image, (self.original_image.shape[1], self.original_image.shape[0]))
               #Reset all the taken points, boxes and box lists
               self.rect_start=None
               self.rect_end=None
               self.input_point = np.empty((0, 2))
               self.input_label = np.empty((0,))
               self.box_list=[]

     #Update canvas performed only if the annotation is accepted
     def update_canvas_annotated_image_accepted(self):
         if self.segment.annotated_image is not None:
               #Display image
               self.canvas.delete("all")
               self.tk_image=ImageTk.PhotoImage(image=Image.fromarray(self.segment.image_with_contours))
               self.canvas.create_image(self.x,self.y,anchor="nw", image=self.tk_image)
               self.image=self.segment.image_with_contours.copy()
               self.image=cv2.resize(self.image, (self.original_image.shape[1], self.original_image.shape[0]))
               #Reset all the taken points, boxes and box lists
               self.rect_start=None
               self.rect_end=None
               self.input_point = np.empty((0, 2))
               self.input_label = np.empty((0,))
               self.box_list=[]

               if self.query_box != None:
                    self.query_box.destroy()
           
     #Update canvas with annotated image
     def update_canvas_original_image(self):
         if self.original_image is not None:
               #Display image
               self.canvas.delete("all")
                # Resize the image based on the zoom factor
               zoomed_width = int(self.original_image.shape[1] * self.zoom_value)
               zoomed_height = int(self.original_image.shape[0] * self.zoom_value)
               self.zoomed_image = cv2.resize(self.original_image, (zoomed_width, zoomed_height))
               #Display image
               #self.canvas.delete("all")
               self.tk_image=ImageTk.PhotoImage(image=Image.fromarray(self.zoomed_image))
               self.canvas.create_image(self.x,self.y,anchor="nw", image=self.tk_image)
           

     #Method that performs image segmentation
     def perform_segmentation(self):
          if self.image is not None:
               #Set the string name of saved annotations
               self.file_name=simpledialog.askstring("Annotation", "Enter the filename (without extension):")
               # #Check the prompt state based od starting and ending point
               if self.rect_start == self.rect_end:
                    self.prompt_state="Point"
               elif self.rect_start != self.rect_end:
                    self.prompt_state="Box"
               #Show the selected prompt
               messagebox.showinfo("Select prompt", f"Selected prompt is {self.prompt_state}!")
               print(self.input_point)
               print(self.input_label)
               self.segment=SAM_Segmentator(self.zoomed_image, 
                                            self.file_name, 
                                            self.input_point, 
                                            self.input_label , 
                                            self.image_shape, 
                                            self.prompt_state)
               if self.segment.semgentation_successful:
                    self.update_canvas_annotated_image()
                    #messagebox.showinfo( "Segmentation", "Image segmentated. Mask and txt saved successfully!")
                    self.query_user()

     #Query method to check if the user is satisfied with the annotation
     def query_user(self):
          self.image=self.segment.image_with_contours.copy()
          
          self.input_point = np.empty((0, 2))
          self.input_label = np.empty((0,))
          self.box_list=[]
          self.query_box = customtkinter.CTkToplevel(self.root)
          self.query_box.title("Perform Segmentation")
          
          message = customtkinter.CTkLabel(self.query_box, text="Do you want to store segmentation?")
          message.pack(pady=20)
          
          accept_button = customtkinter.CTkButton(self.query_box, text="Accept", command=self.update_canvas_annotated_image_accepted)
          accept_button.pack(padx=20, pady=10)
          
          # Reject button
          '''
          FIX:
          It is better not to use reset_rectangle in this situation, it is better to use the image that have stored image with previous annotations and mask from previous segmetations.
          '''
          reject_button = customtkinter.CTkButton(self.query_box, text="Reject", command=self.reset_rectangle)
          reject_button.pack(padx=20)

          self.update_canvas_annotated_image()

     #Save the image method
     def save_image(self):
          if self.image is not None:
               
               self.image=self.original_image.copy()
               self.rect_start=None
               self.rect_end=None
               self.input_point = np.empty((0, 2))
               self.input_label = np.empty((0,))
               self.box_list=[]
               if self.segment != None:
                    annotation_save_path=f"AnnotatedDataset/txt/annotation{self.file_name}.txt"
                    with open(annotation_save_path, "w") as f:
                         f.write(self.segment.yolo_annotation)

                    mask_save_path=f"AnnotatedDataset/masks/{self.file_name}_mask.png"
                    # Resize the mask to the original image size
                    cv2.imwrite(mask_save_path, (self.segment.resized_mask * 255).astype(np.uint8))
                    
                    # Save the annotated image
                    output_image_path = f"AnnotatedDataset/annotations/{self.file_name}_annotated.png"
                    self.annotated_image_real_size= cv2.cvtColor(self.segment.annotated_image_real_size, cv2.COLOR_BGR2RGB)
                    cv2.imwrite(output_image_path, self.annotated_image_real_size)
                    self.image1= cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    cv2.imwrite(output_image_path, self.image1)
               else:
                    mask_save_path=f"AnnotatedDataset/masks/{self.file_name}_mask.png"
                    # Resize the mask to the original image size
                    cv2.imwrite(mask_save_path, (self.polygon.resized_mask * 255).astype(np.uint8))
                    
                    # Save the annotated image
                    output_image_path = f"AnnotatedDataset/annotations/{self.file_name}_annotated.png"
                    self.image1= cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    cv2.imwrite(output_image_path, self.image1)
               self.input_point = np.empty((0, 2))
               self.input_label = np.empty((0,))
               self.drawing_polygon = False
               if self.query_box != None:
                    self.query_box.destroy()
               self.update_canvas_original_image()

     #Reset the rectangle method (in case the user is not satisfied with the bounding box)
     def reset_rectangle(self):
          if self.image is not None:
               # Reset the temporary image to the original
               self.image=self.original_image.copy()
               self.rect_start = None
               self.rect_end = None
               self.update_canvas_original_image()
               self.input_point = np.empty((0, 2))
               self.input_label = np.empty((0,))
               self.box_list=[]

               #If polygon exists:
               self.polygon_points.clear()
               self.drawing_polygon = False
               self.first_polygon=True
               self.first_edit_polygon=True
               self.mask = np.zeros((self.image_shape[1], self.image_shape[0]), dtype=np.uint8)
     
               if self.query_box != None:
                    self.query_box.destroy()
               

if __name__=="__main__":
       root=customtkinter.CTk()
       app=ImageEditor(root)
       root.mainloop()
