#NOTE : Totally ignore this file it only exists to serve as comparison for code optimization between handler.py and itself. This might necessarily not even work. 

import xml.etree.ElementTree as ET
import openpyxl


wb = openpyxl.Workbook()
ws = wb.active or wb.create_sheet()


def get(data,key):
    v = data.find(key)
    if v is None:
        return ''
    return v.text
def element_creator(elem,data,parent=None,additional_kwargs={}):

    elem.attrib['Transaction Type'] = elem.tag
    if elem.tag == 'Parent':
        elem.attrib['Date'] = get(data,"DATE")
        elem.attrib['Transaction Type'] = "Parent"
        elem.attrib['Vch No'] = get(data,"VOUCHERNUMBER") 
        elem.attrib['Ref No'] = 'N/A'
        elem.attrib['Ref Type'] = 'N/A'
        elem.attrib['Ref Date'] = 'N/A'
        elem.attrib['Debtor'] = get(data,"PARTYLEDGERNAME") 
        elem.attrib['Ref Amount'] = 'N/A'
        elem.attrib['Amount'] = 'Perform Later'
        elem.attrib['Particulars'] = get(data,"PARTYLEDGERNAME")
        elem.attrib['Vch Type'] = "Receipt"

    elif elem.tag == "Child" :
        elem.attrib = {**parent.attrib}
        elem.attrib['Transaction Type'] = elem.tag
        elem.attrib['Ref No'] = get(data,"NAME") 
        elem.attrib['Ref Type'] = get(data,"BILLTYPE") 
        elem.attrib['Ref Date'] = get(data,"REF DATE")
        elem.attrib['Ref Amount'] = get(data,"AMOUNT")  
    
    elif elem.tag == "Others" :
        elem.attrib = {**parent.attrib}
        elem.attrib['Transaction Type'] = elem.tag
        elem.attrib['Amount'] = get(data,"AMOUNT")
        elem.attrib = {**elem.attrib,**additional_kwargs}
        
def write(elem):
    
    ws.append(list(elem.attrib.values()))
    for i in elem:
        ws.append(list(i.attrib.values()))
    
def process_element(elem):
    Parent = ET.Element('Parent')
    element_creator(Parent,data=elem)
    try:
        entries = elem.findall("ALLLEDGERENTRIES.LIST")
        childs = entries[0].findall("BILLALLOCATIONS.LIST")
        others = entries[1].findall("BANKALLOCATIONS.LIST")
        for c in childs:
            child = ET.Element('Child')
            element_creator(child,data=c,parent=Parent)
            Parent.append(child)
        for o in others:
            other = ET.Element('Others')
            element_creator(other,data=o,parent=Parent,additional_kwargs={'Debtor':entries[1].find("LEDGERNAME").text})
            Parent.append(other)
            
    
    except AttributeError:
        print("exception encounrterd")
    
    return Parent


def main():
    # Set up the iterparse object
    with open("Input.xml", 'rb') as f:
        context = ET.iterparse(f, events=('end',))
        for event, elem in context:
            if event == 'end' and elem.tag=="VOUCHER" and elem.attrib["VCHTYPE"]=="Receipt":
                p = process_element(elem)
                write(p)

    wb.save('spreadsheet.xlsx')

if __name__ == "__main__":
    main()
