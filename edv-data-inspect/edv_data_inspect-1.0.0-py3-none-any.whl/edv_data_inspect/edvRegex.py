import pyperclip, re


def main():

    # Regex object for Edv
    edvRegex = re.compile(r'''(
    (AS)     # AS for Asia. You can put AF, OC, EU etc
    ,
    (\d)+
    ,
    (\d{4}AS\d+)
    ,
    (CLM)    # I put Nepal Embassy here i.e KDU. You can put any embassy related to the region
    ,
    (Issued|Ready|Refused|Admission Processing)
    ,
    (\d+-\w+-\d+)
    ,
    (\d+-\w+-\d+)
    ,
    (\d)
    ,
    (\d)
    ,
    (\d)
    ,
    (\d)
    ,
    (\d)
    ,
    (\d)
    ,
    (\d)
    )''',re.VERBOSE|re.I)

    # for groups in edvRegex.findall('AS,6282,2019AS6282,KDU,Ready,23-Oct-2017,12-Aug-2019,0,0,1,0,0,0,0'):
    #     print(groups[0])
    #     print(groups[1])
    #     print(groups[2])
    #     print(groups[3])
    #     print(groups[4])
    #     print(groups[5])
    #     print(groups[6])
    #     print(groups[7])
    #     print(groups[8])    # visa issuesed number
    #     print(groups[9])

    text = str(pyperclip.paste())
    matches = []
    
    # Find total number of Issued Visa 
    # Total = Main Applicant + Family members
    # Matching copied string with Regex and storing in match list
    total = 0
    count = 0
    for groups in edvRegex.findall(text):
        matches.append(groups[0])
        total += int(groups[8])
        count += 1
        
    
    # Print total visa in the Terminal
    print("Total Visa: ", str(total))
    print('Main Applicant Number: ', str(count))
    print('Family Members number: ', str(total-count))
    
    
        #Opening file for writing purpose and write the data there in scrap.txt
    fileName = open('scrap.txt', 'w')
    if len(matches) > 0:
        pyperclip.copy('\n'.join(matches))
        fileName.write('\n'.join(matches))
    else:
        fileName.write('No data')    
    fileName.close()

if __name__ == '__main__':
    main()