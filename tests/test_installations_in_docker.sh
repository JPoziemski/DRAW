#!/bin/bash

# Below functions test installation of correct platforms, programms and requirements and their versions
# To test installations uncomment two lines in Dockerfile (setting the workdir to tests and running this script)
# and comment two lines running analysis (setting workdir to bin and running gui_app.py)
# Test performs during build and returns nothing if installation was right
# Otherwise it returns messeges and informs what is wrong

# Test platforms and tools
assertDependency() {
    if ! dpkg -l | grep -q $1; then
        echo "Test failed. Dependency $1 is not installed" 
        return
    fi
    if ! dpkg -l | awk '{print $2 ":" $3}' | grep -q "$1:$2"; then
        echo "Test failed. Dependency $1:$2 is installed but with wrong version:"
        dpkg -l | awk '{print $2 ":" $3}' | grep "$1"
    fi
}

# Test python modules
assertPythonModule() {
    if ! pip3 freeze | grep -q $1; then
        echo "Test failed. Python module $1 is not installed"
        return
    fi
    if ! pip3 freeze | grep -q "$1==$2"; then
        echo "Test failed. Python module $1:$2 is installed but with wrong version:"
        pip3 freeze | grep "$1"
    fi
}

# Test R packages
assertRPackage() {
    R_OUTPUT=`echo "installed.packages()" | Rscript -`

    if ! echo $R_OUTPUT | grep -q $1; then
        echo "Test failed. R package $1 is not installed"
    fi
}

assertDependency "openjdk-8-jre:amd64" "8u252-b09-1ubuntu1"
assertDependency "python3" "3.8.2-0ubuntu2"
assertDependency "python3-pip" "20.0.2-5ubuntu1"
assertDependency "r-base" "3.6.3-2"

assertDependency "bowtie2" "2.3.5.1-6build1"
assertDependency "fastqc" "0.11.9+dfsg-2"
assertDependency "hisat2" "2.1.0-4"
assertDependency "igv" "2.4.17+dfsg-1"
assertDependency "samtools" "1.10-3"
assertDependency "stringtie" "2.1.1+ds-2"
assertDependency "wget" "1.20.3-1ubuntu1"

assertPythonModule "bokeh" "2.0.2"
assertPythonModule "colorcet" "2.0.2"
assertPythonModule "Flask" "1.1.2"
assertPythonModule "matplotlib" "3.2.1"
assertPythonModule "numpy" "1.18.4"
assertPythonModule "pandas" "1.0.3"
assertPythonModule "sklearn" "0.0"

assertRPackage "DESeq2"

