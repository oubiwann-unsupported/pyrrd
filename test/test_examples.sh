DIR="./examples"
pwd
cd $DIR
for FILE in `find *.py`
    do
    PYTHONPATH=../ python $FILE
    done
rm *.rrd

