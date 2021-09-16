from os import sep

def extract_participant_id(intermediate_participant_path):

    participant_id = intermediate_participant_path.split(sep)[-1]

    if not participant_id.endswith("@timestudy_com"):
        raise Exception("Wrong format for input folder path. Needs to be '..\\username@timestudy_com'")

    return participant_id


if __name__ == "__main__":
    intermediate_participant_path = r"E:\data\wocket\Wockets-win32-x64\resources\app\src\srv\MICROT\aditya4_internal@timestudy_com"

    participant_id = extract_participant_id(intermediate_participant_path)
    print("Participant ID  :  {}".format(participant_id))
