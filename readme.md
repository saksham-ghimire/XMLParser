# Tally Xml Parser

The following repository is an simplistic API implementation that parses xml files
generated by Tally to .xlsx file based on designated filter. i.e : ``VCHTYPE = Receipt`` (for this assignment)

## Steps to replicate

* Clone the existing repository
* Create an python environment

```
python -m venv env 
or
python3 -m venv env
```

* Install prerequisities modules

```
pip install -r requirements.txt
```

* Run the server

```
uvicorn main:app --reload
```

## Tech Stack

**Framework** : FastAPI

*Why FastAPI?*

*Fuck you that's why*

## Optimization approach

Here are some approach taken for optimization of above code.

#### Parsing and Memory optimization

The ``xml.etree.ElementTree`` module is used in the following code to parse XML data.
To avoid loading the entire file into memory at once, the ``ET.iterparse`` method
is used instead of the alternative ``ET.Parse`` method.
The code also clears the elements after they are processed to prevent
unexpected memory consumption issues.

```
if event == 'end' and elem.tag=="VOUCHER" and elem.attrib["VCHTYPE"]=="Receipt":
                l = Log(elem)
                if first:
                    Log.WorkSheet.append(list(l.Parent.keys()))
                    first = False
                l.process()
                l.write()
                elem.clear()
```

*Note: Process element at 'end' event not 'start' event since there's no assurance that entirity of element
has been loaded in memory at 'start' event.*

#### Code optimization

The code improves the flexibility of the operation by using a template
creation approach instead of a fully functional approach.
The previous implementation of the code, which used a fully functional approach,
is shown in the ``try.py`` file. By comparing the two files, it is possible to
see how the object creation overhead, calculation approach, and overall
flexibility have been improved in the ``handler.py`` file.

#### API Optimization

**Note: This has not been implemented yet due to time constraints for the assignment, but this approach seems feasible.**

Compress the file while writing it in order to reduce the amount of network resources used later on

## Working

**General Test**

**Consistency Test**
