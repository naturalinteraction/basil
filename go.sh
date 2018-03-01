git update-index --assume-unchanged series.pkl
python setup_segment.py build_ext --inplace
python dip.py "$@"

