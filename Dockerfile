FROM archlinux/archlinux:latest

RUN pacman -Syu --noconfirm && pacman -S --noconfirm git wget libxml2 libxslt zip python-pip

RUN wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2004-x86_64-100.5.2.tgz && tar -xf mongodb*.tgz && \ 
  mv mongodb-database-tools-ubuntu2004-x86_64-100.5.2/bin/* /bin/ && \
  rm -rf mongodb-database-tools-ubuntu2004-x86_64-100.5.2*

WORKDIR /app
RUN chmod 777 /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -U -r requirements.txt

COPY . .

CMD ["python3","-m","Avenger"]
