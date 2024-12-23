FROM ghcr.io/astral-sh/uv:python3.10-bookworm

# install dependencies
# RUN apt-get update && apt-get install -y

# copy files
COPY . ./src

# create environment in src directory
WORKDIR /src
RUN uv sync --frozen

# run app
WORKDIR /src
EXPOSE 8080
CMD uv run python main.py