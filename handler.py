import xml.etree.ElementTree as ET
import openpyxl
from datetime import datetime
import os

def get(data,key):
    v = data.find(key)
    if v is None:
        return ''
    return v.text

class Log:

    Workbook = openpyxl.Workbook()
    WorkSheet = Workbook.active or Workbook.create_sheet()

    def __init__(self, log_data:ET.Element) -> None:
        self.Parent = {
            'Date': datetime.strptime(get(log_data,"DATE"), "%Y%m%d").date() if get(log_data,"DATE") != '' else '',
            'Transaction Type': 'Parent',
            'Vch No' : get(log_data,"VOUCHERNUMBER"),
            'Ref No' : 'NA',
            'Ref Type': 'NA',
            'Ref Date' : 'NA',
            'Debtor' : get(log_data,"PARTYLEDGERNAME") ,
            'Ref Amount':'NA',
            'Amount': 'NA',
            'Particulars':get(log_data,"PARTYLEDGERNAME"),
            'Vch Type':'Receipt',
            'Amount Verified':'NA'
        }
        self.Entries = log_data.findall("ALLLEDGERENTRIES.LIST")
        try:
            self.childEntries = self.Entries[0].findall("BILLALLOCATIONS.LIST")
            self.otherEntries = self.Entries[1].findall("BANKALLOCATIONS.LIST")
            # for addtional consistency and edge cases
        except IndexError:
            self.childEntries = []
            self.otherEntries = []


        self.Child = []
        self.Others = []
    

    def populate_child_entries(self):
        for i in self.childEntries:
            child = {**self.Parent}
            child['Transaction Type'] = 'Child'
            child['Ref No'] = get(i,"NAME")
            child['Ref Type'] = get(i,"BILLTYPE")
            child['Ref Date'] = get(i,"REF DATE")
            try:
                child['Debtor'] = get(self.Entries[0],"LEDGERNAME")
                child['Particulars'] = get(self.Entries[0],"LEDGERNAME") 
            except IndexError:
                child['Debtor'] =''
                child['Particulars']= ''

            child['Ref Amount'] = get(i,"AMOUNT") 
            self.Child.append(child)

    def populate_third_party_entries(self):
        for i in self.otherEntries:
            others = {**self.Parent}
            others['Transaction Type'] = 'Others'
            others['Amount'] = get(i,"AMOUNT")
            try:
                others['Debtor'] = get(self.Entries[1],"LEDGERNAME")
                others['Particulars'] = get(self.Entries[1],"LEDGERNAME")
            except IndexError:
                others['Debtor'] = ''
                others['Particulars'] =''
            self.Others.append(others)

    def calculate(self):
        try:
            total = sum(float(i['Ref Amount']) for i in self.Child)
            self.Parent['Amount'] = float(get(self.Entries[0],"AMOUNT"))
            if total == self.Parent['Amount']:
                self.Parent['Amount Verified'] = 'Yes'
            else:
                self.Parent['Amount Verified'] = 'No'
        except:
            self.Parent['Amount'] = ''
            self.Parent['Amount Verified'] = ''

    def process(self):
        self.populate_child_entries()
        self.populate_third_party_entries()
        self.calculate()
        return self
    
    def write(self):
        self.WorkSheet.append(list(self.Parent.values()))
        for i in self.Child:
            self.WorkSheet.append(list(i.values()))
        for i in self.Others:
            self.WorkSheet.append(list(i.values()))
        

def ProcessFile(filepath):
    first = True
    with open(filepath, 'rb') as f:
        context = ET.iterparse(f, events=('end',))
        for event, elem in context:
            if event == 'end' and elem.tag=="VOUCHER" and elem.attrib["VCHTYPE"]=="Receipt":
                l = Log(elem)
                if first:
                    Log.WorkSheet.append(list(l.Parent.keys()))
                    first = False
                l.process()
                l.write()
                elem.clear()
    Log.Workbook.save(f'outputs/{filepath.split(".")[0]}.xlsx')
    os.remove(filepath)

