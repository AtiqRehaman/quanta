from PIL import Image
import os


def folder_resize(data): #To resize multiple images make a folder 
    dimentions = tuple(map(int, input("Enter dimentions(Width x Height):").split()))
    resized_folder =  os.path.join(data ,"Resized")
    os.makedirs(resized_folder, exist_ok=True)
    print(f"Changing dimentions into (Width x Height) {dimentions}...")
    for file in os.listdir(data):
        path = os.path.join(data, file)
        try:
            with Image.open(path) as img:
                resized_img = img.resize(dimentions)
                resized_path = os.path.join(resized_folder, file)
                resized_img.save(resized_path) 
        except Exception as e:
            print(file)
            
    print("Image resize completed.")

def file_resize(data): #To resize a image 
    dimentions = tuple(map(int, input("Enter dimentions(Width x Height):").split()))
    print("Changing dimentions into (Width x Height)",dimentions)
    img = Image.open(data)
    resized = img.resize(dimentions)
    resized.save(data)
    print("Image resize completed.")

data = input("Enter the path of image or folder:")

method = input("Enter a method(File or Folder):")
if method.upper() == "FOLDER":
    folder_resize(data)
elif method.upper() == "FILE":
    file_resize(data)
else:
    print("Invalid input!please select File or Folder.")