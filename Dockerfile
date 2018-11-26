FROM python:3.7.1

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY check_sync /usr/local/bin/
RUN chmod u+x /usr/local/bin/check_sync

COPY mvol_ls /usr/local/bin/
RUN chmod u+x /usr/local/bin/mvol_ls

COPY put_dc_xml /usr/local/bin/
RUN chmod u+x /usr/local/bin/put_dc_xml

COPY put_struct_txt /usr/local/bin/
RUN chmod u+x /usr/local/bin/put_struct_txt

COPY validate /usr/local/bin/
RUN chmod u+x /usr/local/bin/validate
