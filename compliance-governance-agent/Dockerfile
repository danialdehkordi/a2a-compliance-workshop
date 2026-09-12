# ==============================================================================
# 🏛️ TODO EXERCISE B.4: Multi-Stage Cloud Run Dockerfile for Go Policy Engine
# ==============================================================================
# 1. Builder stage: use `golang:1.22-alpine` as builder.
#    - Set WORKDIR /app
#    - Copy go.mod and Go packages (cmd/, internal/)
#    - Compile binary: `CGO_ENABLED=0 go build -o server ./cmd/server/main.go`
#
# 2. Runtime stage: use minimal `alpine:3.19`.
#    - Set WORKDIR /app
#    - Copy compiled binary from builder stage
#    - Expose port 8888 (or Cloud Run $PORT)
#    - Set ENTRYPOINT / CMD to run `./server`
# ==============================================================================

# TODO EXERCISE B.4: Write your multi-stage Dockerfile below

