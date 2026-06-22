# SPARQL Endpoint

A lightweight local SPARQL endpoint for querying RDF files, built with **RDFLib** and **Flask**, served via **Docker**.

## Features

- Loads all RDF files from `./data/` at startup (`.ttl`, `.rdf`, `.n3`, `.nt`, `.jsonld`, `.trig`)
- Supports `SELECT`, `ASK`, `CONSTRUCT`, and `DESCRIBE` queries
- Interactive web UI with syntax editor, example queries, and CSV export
- `↻ Reload RDF` button — add/edit files without restarting
- `Ctrl+Enter` keyboard shortcut to run queries

---

## Quickstart

### 1 — Add your RDF files

Drop your `.ttl` / `.rdf` / `.n3` / `.jsonld` files in the `data/` directory:

```
data/
  my_tools.ttl
  ontology.rdf
  ...
```

### 2 — Run with Docker Compose

```bash
docker compose up --build
```

Open <http://localhost:5000> in your browser.

### 3 — Without Docker (dev mode)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
FLASK_DEBUG=1 python app.py
```

---

## Project Structure

```
.
├── app.py                  # Flask application
├── templates/
│   └── index.html          # Web UI
├── data/                   # ← Put your RDF files here
│   └── example.ttl
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/` | Web UI |
| `POST` | `/sparql` | Execute a SPARQL query (`query` form field) |
| `GET`  | `/sparql?query=…` | Same via GET |
| `POST` | `/reload` | Reload all RDF files from disk |
| `GET`  | `/status` | Health check + triple count |

### Example curl

```bash
curl -X POST http://localhost:5000/sparql \
  --data-urlencode "query=SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RDF_DIR` | `./data` | Path to directory containing RDF files |
| `PORT` | `5000` | Port to listen on |
| `FLASK_DEBUG` | `0` | Set to `1` for dev auto-reload |

---

## Supported RDF Formats

| Extension | Format |
|-----------|--------|
| `.ttl`, `.turtle` | Turtle |
| `.rdf`, `.xml` | RDF/XML |
| `.n3` | Notation3 |
| `.nt` | N-Triples |
| `.jsonld` | JSON-LD |
| `.trig` | TriG |

---

## Tips

- **Multiple files**: all files in `data/` are merged into one graph at load time.
- **Reload without restart**: click **↻ Reload RDF** in the UI or `POST /reload` after editing files.
- **Named graphs**: use `.trig` files if you need named graphs (ConjunctiveGraph is used internally).
- **Performance**: for very large datasets (>10M triples) consider [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) instead.
