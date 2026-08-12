FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod ./
COPY cmd/ cmd/
COPY internal/ internal/

RUN go build -o server ./cmd/server/main.go

FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/server .

EXPOSE 8888

CMD ["./server"]
