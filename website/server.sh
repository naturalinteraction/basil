# google-chrome http://localhost:8000/list_CSV.html &
google-chrome http://localhost:8000/chart.html?csv=CSV/blueshift-aprile.csv &
google-chrome http://localhost:8000/chart.html?csv=CSV/noir-aprile.csv &
google-chrome http://localhost:8000/chart.html?csv=http://natural-interaction.s3-website-eu-west-1.amazonaws.com/CSV/zero/noir.csv &
# google-chrome http://localhost:8000/chart.html?csv=CSV/visible-aprile.csv &
# google-chrome http://localhost:8000/chart.html?csv=http://natural-interaction.s3-website-eu-west-1.amazonaws.com/CSV/zero/visible.csv &
python -m SimpleHTTPServer
