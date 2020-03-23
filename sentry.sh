# Run this to get GeckoDriver for Firefox and Unix
wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
tar xvfz geckodriver-v0.26.0-linux64.tar.gz
rm geckodriver-v0.26.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin
chmod +x /usr/local/bin/geckodriver
echo "Successful instalation"