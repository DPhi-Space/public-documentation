FROM --platform=$BUILDPLATFORM tonistiigi/xx AS xx

FROM --platform=$BUILDPLATFORM rust:alpine AS builder
COPY --from=xx / /

RUN apk add clang lld musl-dev openssl-dev

ARG TARGETPLATFORM
WORKDIR /app
COPY src/ src/
COPY Cargo.toml .
COPY Cargo.lock .

RUN xx-cargo build --release --bin dphi-example --target-dir ./build && \
    xx-verify ./build/$(xx-cargo --print-target-triple)/release/dphi-example

RUN mv ./build/$(xx-cargo --print-target-triple)/release/dphi-example .

FROM gcr.io/distroless/cc-debian12
COPY --from=builder /app/dphi-example /dphi-example
USER 65532:65532
ENTRYPOINT ["/dphi-example"]
