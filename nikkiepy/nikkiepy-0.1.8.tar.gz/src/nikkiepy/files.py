import os

def mkfile(path, name, extension="txt"):
    path = path # Where to make the file
    name = name # Name for the file
    extension = extension # Type of file. Examples: .exe, .jpeg, .jpg, .mp4, etc

    try:
        f = open(f"{path}/{name}.{extension}", 'x')  # Creates the file
        f.close()  # Finished
        print(f"File: {name}.{extension} has been made in: {path}")

    except FileExistsError:
        print(f"File: {name}.{extension} already exists in {path}!")

    except FileNotFoundError:
        choice = input(str(f"Folder \"{path}\" doesn't exist, do you want to make it? (Y/N): "))
        if choice.lower() == "y":
            os.mkdir(path)
            print(f"Made folder: {path}")
            try:
                f = open(f"{path}/{name}.{extension}", 'x')  # Creates the file
                f.close()  # Finished
                print(f"File: {name}.{extension} has been made in: {path}")

            except FileExistsError:
                print(f"File: {name}.{extension} already exists in {path}!")
        else:
            print("Operation cancelled.")


    except OSError as err:
        print(f"OS Error: {err}")

    except PermissionError:
        print(f"No permission to write to {path}!")

def delfile(file):
    file = file # Gets the file
    if os.path.exists(file): # Checks if file exists
        os.remove(file) # Deletes the file
        print(f"File: {file} successfully deleted!")
    else:
        print(f"File {file} doesn't exist!")

def delfolder(folder):
    folder = folder # Gets the folder
    if os.path.exists(folder): # Checks if folder exists
        try:
            os.rmdir(folder) # Deletes the folder
            print(f"Folder: {folder} successfully deleted!")

        except FileNotFoundError:
            print(f"Folder doesn't exist!")

        except OSError as err:
            print(f"OS Error: {err}")

        except PermissionError:
            print(f"No permission to write to {folder}")
    else:
        print(f"Folder doesn't exist!")