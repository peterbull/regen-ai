FROM ollama/ollama

RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y gcc libc-dev libpq-dev python3-pip git

RUN pip install huggingface_hub

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
