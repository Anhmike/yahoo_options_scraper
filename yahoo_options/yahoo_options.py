from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

browser = webdriver.PhantomJS(executable_path=r'E:\coding\phantomjs\bin\phantomjs.exe')
browser.set_window_size(1120, 550)

stock_symbols = ["NFLX","TSLA","MSFT"]

for stock in stock_symbols:
    url = ("https://finance.yahoo.com/quote/" + stock + "/options?p=" + stock)
    print("Processing stock: " + stock)
    
    calls_file = open(stock + "_calls.csv", "a", newline='')
    calls_file.truncate(0)
    puts_file = open(stock + "_puts.csv", "a", newline='')
    puts_file.truncate(0)
    
    browser.get(url)
    html = browser.page_source

    #accept cookies if needed
    if browser.find_elements_by_xpath("//*[@name='agree']"):
        browser.find_element_by_xpath("//*[@name='agree']").click()
    html = browser.page_source
    
    soup = BeautifulSoup(html, "html.parser")
    
    #save all expiration dates in adictionary
    option_control = soup.find('div', attrs={"class":"option-contract-control"})
    expiration_dates = option_control.find_all('option')
    exiprations_dict = {}
    for date in expiration_dates:
        exiprations_dict[date.text] = date['value'] 
        
    expirations_list = list(exiprations_dict.keys())
    
    is_first = True
    for expiration in exiprations_dict: 
        #first expiration date is already loaded
        if is_first == True:
            is_first = False
            calls_file.write("," + expirations_list[0].replace(","," ") + "\n")
            puts_file.write("," + expirations_list[0].replace(","," ") + "\n")
        
        else:
            time.sleep(2)
            new_url = "https://finance.yahoo.com/quote/" + stock + "/options?p=" + stock +"&date=" + exiprations_dict[expiration]
            print("Processing exparation: " + expiration)
            browser.get(new_url)
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            calls_file.write("\n," + expiration.replace(","," ") + "\n")
            puts_file.write("\n," + expiration.replace(","," ") + "\n")
    
        contract_sections = soup.find_all("section", attrs={"class": "Mt(20px)"})
    
        #loop over Calls and Puts
        for k in range(2):
            option_trs = contract_sections[k].find_all("tr")
        
            column_names = option_trs[0].find_all('span')
    
            #read the captions    
            captions = []
            for column_name in column_names:
                captions.append(column_name.text)
    
            #loop over every laie
            all_values=[]
            i = 0
            for option in option_trs:
                if i == 0:
                    i+=1
                    continue
                    
                column_values = option.find_all('td')
        
                #read the values of a single line
                values = []
                for column_value in column_values:
                    values.append(column_value.text)
                
                all_values.append(values)
        
            #wrote the retults into csv file
            df = pd.DataFrame(all_values, columns=captions)
            if k == 0:
                df.to_csv(calls_file)
            else:
                df.to_csv(puts_file)
    
    calls_file.close
    puts_file.close
    
browser.quit()