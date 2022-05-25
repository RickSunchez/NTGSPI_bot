sudo docker build -t ntspi_bot .
sudo docker run -d --restart=always --name=ntspi_bot ntspi_bot