# A script that parses the wikipedia page into JSON.
# run wget http://en.wikipedia.org/wiki/List_of_mobile_country_codes
# then this..
import csv
import json
import os
from collections import defaultdict

from BeautifulSoup import BeautifulSoup

from mobile_codes import Operator


def parse_mnc_wikipedia():
    with open('List_of_mobile_country_codes', 'r') as htmlfile:
        soup = BeautifulSoup(htmlfile)
        operators = []

        for table in soup.findAll('table', attrs={'class': 'wikitable'}):
            for row in table.findAll('tr'):
                mcc, mnc, brand, operator = row.findChildren()[:4]
                if mcc.text in ['MCC', '']:
                    continue

                operators.append(Operator(operator=operator.text, brand=brand.text, mcc=mcc.text, mnc=mnc.text))

        return operators


def parse_mnc_itu():
    with open(os.path.join('csv', 'itu.csv'), 'rb') as csvfile:
        reader = csv.reader(csvfile)
        operators = []

        for line in reader:
            if not line[0]:
                operator_name = line[1]
                mcc, mnc = line[2].split()
                operators.append(MNCOperator(operator=operator_name, brand=operator_name, mcc=mcc, mnc=mnc))

        return operators

def parse_sid_ifast():
    with open(os.path.join('csv', 'nationalsid.csv'), 'rb') as csvfile:
        reader = csv.reader(csvfile)
        operators = []

        for line in reader:
            operators.append(SIDOperator(*line)

        return operators



def merge_wiki_itu():
    wiki_operators = parse_mnc_wikipedia()
    itu_operators = parse_mnc_itu()
    merged_operators = {}

    for operator in wiki_operators:
        operator_key = operator.mcc, operator.mnc
        merged_operators[operator_key] = operator

    for operator in itu_operators:
        operator_key = operator.mcc, operator.mnc
        merged_operators[operator_key] = operator

    return merged_operators.values()


def write_mnc_operators(mnc_operators):
    with open('mobile_codes/json/mnc_operators.json', 'wb') as outfile:
        outfile.write(json.dumps(mnc_operators))

def write_sid_operators(operators):


if __name__ == '__main__':
    write_mnc_operators(merge_wiki_itu())
