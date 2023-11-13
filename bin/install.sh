

sudo apt install -y python3-pip
sudo apt install -y proj-bin

sudo python3 -m pip cache purge

sudo pip install --upgrade pip

sudo pip3 install --upgrade --no-cache-dir mavsdk
sudo pip3 install --upgrade --no-cache-dir httplib2 requests pyserial
sudo pip3 install --upgrade --no-cache-dir pyproj


