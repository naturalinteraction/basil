# google-chrome http://localhost:8000/list_CSV.html &
# google-chrome http://localhost:8000/chart.html?csv=CSV/blueshift-aprile.csv &
# google-chrome http://localhost:8000/chart.html?csv=CSV/visible-hawk.csv &

google-chrome http://localhost:8000/chart.html?csv=CSV/visible-aprile.csv &
google-chrome http://localhost:8000/chart.html?csv=http://natural-interaction.s3-website-eu-west-1.amazonaws.com/CSV/zero/visible.csv &

# google-chrome http://localhost:8000/chart.html?csv=http://natural-interaction.s3-website-eu-west-1.amazonaws.com/CSV/zero/visible-hawk.csv &
# google-chrome http://localhost:8000/chart.html?csv=http://natural-interaction.s3-website-eu-west-1.amazonaws.com/CSV/alessandrovalli/botany-batch^basilico.csv &
python -m SimpleHTTPServer
