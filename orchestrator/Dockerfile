# Build stage
FROM elixir:1.17-slim AS build

RUN apt-get update -y && \
    apt-get install -y build-essential git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV MIX_ENV=prod

# Install hex and rebar
RUN mix local.hex --force && \
    mix local.rebar --force

# Install dependencies
COPY mix.exs ./
RUN mix deps.get --only $MIX_ENV && \
    mix deps.compile

# Compile application
COPY config config
COPY lib lib
RUN mix compile

# Build release
RUN mix release

# Runtime stage
FROM debian:bookworm-slim AS runtime

RUN apt-get update -y && \
    apt-get install -y libstdc++6 openssl libncurses5 locales ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Create non-root user
RUN groupadd --gid 1000 orchestrator && \
    useradd --uid 1000 --gid orchestrator --shell /bin/bash --create-home orchestrator

WORKDIR /app

# Copy release from build stage
COPY --from=build --chown=orchestrator:orchestrator /app/_build/prod/rel/orchestrator ./

USER orchestrator

ENTRYPOINT ["bin/orchestrator"]
CMD ["start"]
