from flask import Flask, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
import re

# app instance
app = Flask(__name__)
CORS(app)

# urls of the websites we want to fetch the data from
url_list = [
    'https://www.hajjumrahhub.co.uk/umrah-packages.html', 
    'https://www.hajis.co.uk/umrah-packages-2023/', 
    'https://www.duatravels.co.uk/umrah-packages', 
    'https://www.islamictravel.co.uk/umrah-packages.html',
    'https://www.travelhouseuk.co.uk/cheap-umrah-packages/',
    'https://www.zamzamtravels.org.uk/umrah-packages-2023-uk',
    'https://www.makkahmadinatours.co.uk/',
    'https://www.hajjandumrahexperts.co.uk/umrahpackages.php',
    'https://www.safaandmarwatours.co.uk/',
    'https://www.alhijaztravel.com/umrah-packages/cheap-umrah-packages.html',
]

# this function searches for umrah packages based on the div class names found in the package_classes list 
def find_packages(url_list):
    package_classes = [
        'mainPackageDesc', 
        'middle', 
        'tourmaster-tour-content-wrap', 
        'suportive-div',
        'card-body',
        'article-body',
        'umrah-package',
        'pkg',
        'card1',
        'umrah-box',
        'tourmaster-tour-content-wrap'
        ]
    packages_found = []
    removed_sentences = [
        'Perform Umrah with Best Price', 'View Details', 
        'View Details' , '›',
        'nothingToRemoveOnDuatravels',
        'FlightMakkahMedinahVisa', 'Get Details', 'Beat my quote', '\n',
        'StarDuration', 'Star Star', 'Star Star Star', 'Star Star Star Star Star', 'Star Duration',
        'From Only', 'From', 'Price',
        '(Deposit £50)', '(Deposit',
        'Included:HOTEL + VISA + FLIGHT :',
        'Flight Economy', 'Hotel', 'Visa', 'Transfers', 'Extra Cost', 'Hotel', 'Sharing Quad',
        'Fr.',
        '02032900001', '0203-290-0001', 'tel:02032900001'
        ]
    
    removed_from_price = [
        '0203-290-0001',
        '0208-004-4454'
    ]

    for url in url_list:
        # interact with the url
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser') # parse the data
            package_prices = soup.find_all(class_=package_classes) # find all div classes stored in the package_classes list
        
            # return found packages 
            if package_prices:
                print(f"Package prices found on {url}:")
                for price in package_prices:
                    scrapped_data = price.get_text()

                    # split the data into 'Package' and 'Price' based on '£' symbol & append the found data to the packages_found list
                    if '£' in scrapped_data:
                        package, price = scrapped_data.split('£', 1)
                        packages_found.append({
                            'Umrah Travel Agent': url.replace('https://www.', '').split('/')[0],
                            'Package Details': package.strip(),
                            'Price': '£' + price.strip()
                        })
                    else:
                        packages_found.append({
                            'Umrah Travel Agent': url.replace('https://www.', '').split('/')[0],
                            'Package Details': scrapped_data.strip(),
                            'Price': ''
                        })

                # clean the data that's in the package details and price column 
                for package_info in packages_found:
                    # remove any 3 or > digit number from the package details column
                    package_details = package_info['Package Details']
                    package_details = re.sub(r'\b\d{3,}\b', '', package_details)
                    package_info['Package Details'] = package_details
                    
                    # remove unwanted words/sentences from the package details column
                    for sentence in removed_sentences:
                        package_info['Package Details'] = package_info['Package Details'].replace(sentence, '').strip().replace('PackageMakkah', 'Package Makkah')
                        package_info['Package Details'] = re.sub(r'(\d+)([A-Za-z]+)', r'\1 \2', package_info['Package Details']) # add a space between any number and the following word in 'Package Details'
                        num_comma = package_info['Package Details'].split() # remove any number followed by a comma from the 'Package Details' column
                        updated_details = ' '.join(sequence for sequence in num_comma if not re.match(r'\d+,$', sequence))
                        package_info['Package Details'] = updated_details
                        
                    # cleanup the Price column
                    for i in range(len(removed_from_price)):
                        removed_from_price[i] = removed_from_price[i].replace(removed_from_price[i], '')
                            
                    package_info['Price'] = re.sub(r'\b(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}|(?:\+44|0) ?(?:\d{3,4}) ?(?:\d{5}|\d{3} ?\d{3,4}))\b', '', package_info['Price']) # remove uk and north america phone numbers
                    package_info['Price'] = re.sub(r'[^\d£,.\s]', '', package_info['Price']) # remove alphabetical characters
                    package_info['Price'] = re.sub(r'(?<!\d,)\b\d{1,2}\b(?![\d,])', '', package_info['Price']) # get rid of numbers that are 1 or 2 digits unless before a comma
                    package_info['Price'] = re.sub(r'(\d+),(\d+)', r'\1\2', package_info['Price'])  # remove commas from numbers
        
                    # if there are 2 numbers in the price column then only return the smaller price
                    prices = re.findall(r'£\d{3,}', package_info['Price']) # extract all prices with 3 or more digits
                    if len(prices) >= 2:
                        package_info['Price'] = min(prices)
                    package_info['Price'] = package_info['Price'].replace(' ', '').replace('\n', '').replace('\t', '').replace('££', '£') # remove spaces
            else:
                print(f"No package prices found on {url}")
        else:
            print(f"Failed to fetch data from {url}")
         
    return packages_found

# # sort the prices cheapest to highest
def sort_packages_by_price(df):
    df.loc[:, 'Price'] = df['Price'].replace('[^\d£.]', '', regex=True) # Remove non-numeric characters from the 'Price' column except for '£' and '.'
    df = df[df['Price'].str.match(r'^£?\d+(\.\d+)?$')] # Filter out rows where 'Price' doesn't start with '£' or doesn't contain numeric values
    df.loc[:, 'Price'] = df['Price'].replace('£', '', regex=True).astype(float) # Convert 'Price' to float
    sorted_df = df.sort_values('Price', ascending=True) # Sort the DataFrame by 'Price'
    # Reset the index to run in order
    sorted_df.reset_index(drop=True, inplace=True)
    sorted_df.loc[:, 'Price'] = sorted_df['Price'].apply(lambda x: '£{:,.2f}'.format(x)) # Format 'Price' column as currency again
    return sorted_df

data = find_packages(url_list) # get the data from the find_package_prices function
df = pd.DataFrame(data) # put the data into a pandas dataframe
sorted_prices = sort_packages_by_price(df) # link the functions together

print(tabulate(sorted_prices, headers='keys', tablefmt='pretty', stralign='left')) # print DataFrame in a tabulated format

# define the new API endpoint to serve Umrah packages data
@app.route("/api/packages", methods=['GET'])
@cross_origin()
def get_packages_api():
    data = find_packages(url_list)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True) # port 5001 because 5000 seems to have an issue with CORS when getting frontend requests