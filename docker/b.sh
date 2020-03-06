
# docker build -t hansen1416/docs .

# docker run -dit --name docs --restart unless-stopped -p 8100:8100 --mount type=bind,source=/home/hlz/docs,target=/home/docs hansen1416/docs

# docker exec -it docs bash

# jupyter notebook --ip 0.0.0.0 --port 8100 --allow-root
