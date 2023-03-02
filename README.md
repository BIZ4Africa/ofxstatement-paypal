# ofxstatement-paypal

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Paypal plugin for ofxstatement 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project provides a custom plugin for [ofxstatement](https://github.com/kedder/ofxstatement) for Paypal. It is based
on the work done by gerasiov (https://github.com/gerasiov/ofxstatement-paypal/).

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format, suitable for importing to GnuCash / Odoo. Plugin for ofxstatement parses a particular proprietary bank statement format and produces common data structure, that is then formatted into an OFX file.

Users of ofxstatement have developed several plugins for their banks. They are listed on main [`ofxstatement`](https://github.com/kedder/ofxstatement) site. If your bank is missing, you can develop
your own plugin.

## Installation

### From PyPI repositories
```
pip3 install ofxstatement-paypal
```

### From source
```
git clone git@github.com:EtsBIZ4Africa/ofxstatement-paypal.git 
python3 setup.py install
```

## Usage
From Paypal Web interface, download a CSV personnalized report for the period you wish.

```
$ ofxstatement convert -t paypal-ng input.csv output.ofx
```
