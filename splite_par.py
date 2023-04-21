import csv
import re

# Define the regular expression pattern for matching separator symbols
pattern = r'[,.?:;]'

# Open the input CSV file and the output text file
with open('2023-FH1_submission_directory/NEB_test_par/NEB_test_par.csv', 'r') as csv_file, open('2023-FH1_submission_directory/NEB_test_par/NEB_raw_test_par.txt', 'w') as txt_file:
    # Create a CSV reader object
    csv_reader = csv.reader(csv_file, delimiter='|')
    
    # Loop over each row in the CSV file
    for row in csv_reader:
        # Get the name and text from the row
        name = row[0]
        text = row[1]
        
        text = text.replace('§', '').replace('#', '').replace('¬', '').replace('~','').replace('»','').replace('«','')
        text = text.lstrip(",.;?!:")
        # Split the text into segments based on the separator symbols using regular expressions
        segments = re.split(pattern, text)
        
        # Write the segmented text to the output file
        for i, segment in enumerate(segments):
            segment_name = f"{name}_{i+1}"
            if segment is not None and segment.strip() != '':
                txt_file.write(f"{segment_name}|{segment.strip()}\n")
