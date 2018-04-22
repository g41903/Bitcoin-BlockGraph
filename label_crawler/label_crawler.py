# setup library imports
import io, time, json, copy
import requests
from bs4 import BeautifulSoup

def parse(s, label = None):
    result = list()
    base_url = "https://www.walletexplorer.com"
    for a in s.find_all('a', href = True): 
        result.append([base_url + a['href'] + "/addresses", a.text, label])
    return result
        

def parse_homepage(html, mapping):
    """
    Take the Top Wallets off of Wallet Explorer and get a list of
    top wallets
    Args: 
        html(string): String of HTML corresponding to walletexporer.com
    
    Returns:
        wallets (2d list): list of strings needed to query website
        cols: type of wallet
        rows: strings to advance to wallet page
    """
    wallets = list()
    r  = requests.get(html)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    colnames = soup.find_all('ul') # len(colnames) = 5 for each wallet type
    for i in range(len(colnames)):
        label = mapping[i]
        wallets.append(parse(colnames[i], label))
    return wallets

def parse_addr(html, name = None, types = None):
    """
    Take each address in a wallet
    Args: 
        html(string): String of HTML corresponding to a wallet
    
    Returns:
        addrs(dict): Dictionary of addr => {balance, incoming_tx, last_used}
    """
    addrs = dict()
    r = requests.get(html)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    addresses = soup.find_all('tr')
    for addr in addresses:
        data = addr.find_all('td')
        if len(data) != 0:
            addrs[find_address(data)] = {
                "balance": find_balance(data),
                "incoming_tx": find_incoming(data),
                "last_used": find_lastused(data),
                "types": types,
                "name": name
            }    
    return addrs

def find_address(data):
    return data[0].find('a').text

def find_balance(data):
    return float(data[1].text)

def find_incoming(data):
    return int(data[2].text)

def find_lastused(data):
    return int(data[3].text)

def main():
    result = list()
    mapping = {0: "Exchange", 1:"Pool", 2:"Services", 3:"Gambling", 4:"Old"}
    home = parse_homepage("https://www.walletexplorer.com/", mapping)
    for label in range(len(home)):
        for name in home[label]: # list[0] = string, list[1] =name, list[2] = label
            result.append(parse_addr(name[0], name[1], name[2]))
  	    print(name[1])
    with open("labels.json", 'w') as out:  
        json.dumps(result, out)    

if __name__ == "__main__":
    main()
