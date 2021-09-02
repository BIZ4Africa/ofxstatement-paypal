#!/bin/bash

input_file=$1
output_file=$2

ofxstatement convert -t paypal $input_file $output_file
sed -i "s/></>\\r\\n</g" $output_file


