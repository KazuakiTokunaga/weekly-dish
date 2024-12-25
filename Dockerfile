FROM ghcr.io/astral-sh/uv:python3.10-bookworm

# install dependencies
# RUN apt-get update && apt-get install -y

# Accept build arguments
ARG GCP_SA_CREDENTIAL
ENV GCP_SA_CREDENTIAL=$GCP_SA_CREDENTIAL

# copy files
COPY . ./src

# create environment in src directory
WORKDIR /src
RUN uv sync --frozen

# run app
WORKDIR /src/app
EXPOSE 8080
CMD uv run streamlit run app.py --server.port 8080 --server.address 0.0.0.0