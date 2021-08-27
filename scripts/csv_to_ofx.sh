#!/bin/bash

input_file=$1
output_path=$2
output_file="$2/output.ofx"
ofxstatement convert -t paypal '$input_file' '$output_file'
sed -i "s/></>\\r\\n</g" $output_file


