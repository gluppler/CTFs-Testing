import utils.helpers as helpers

def resizer(x, y, option, image_path):

    x = int(x)
    y = int(y)
    option = option.lower()

    if option == "resize":
        helpers.resize_image(image_path, x, y)
    
    elif option == "crop": # not implemented for now
        helpers.crop_image(image_path, x, y, int(x)+100, int(y)+100)  
    elif option == "convert": # not implemented for now
        helpers.convert_image_format(image_path, y)  
    else:
        print("Invalid option. Please choose 'resize', 'crop', or 'convert'.")
