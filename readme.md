# nunuk

Build your own Claude Code — a small, terminal-based coding agent in Python.

## Run

```bash
git clone https://github.com/<you>/nunuk.git
cd nunuk
cp .env.example .env   # set OPENROUTER_API_KEY=...
./agent                # interactive REPL
./agent -p "list the files in this directory"   # one-shot
./agent --doctor       # verify env
```

Requires Python 3.12+ and [`uv`](https://docs.astral.sh/uv/). The wrapper script installs dependencies on first run.

## License

[MIT](./LICENSE)
