"""
SPARQL Endpoint for RDF files using RDFLib + Flask.
Place your .ttl / .rdf / .n3 / .jsonld files in the ./data/ directory.
"""

import os
import glob
import logging
from flask import Flask, request, jsonify, render_template
from rdflib import ConjunctiveGraph
from rdflib.plugins.sparql.processor import SPARQLUpdateProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------

RDF_DIR = os.environ.get("RDF_DIR", "./data")

FORMAT_MAP = {
    ".ttl":     "turtle",
    ".turtle":  "turtle",
    ".rdf":     "xml",
    ".xml":     "xml",
    ".n3":      "n3",
    ".nt":      "nt",
    ".jsonld":  "json-ld",
    ".trig":    "trig",
}


def load_graph() -> ConjunctiveGraph:
    """Load all RDF files found in RDF_DIR into a ConjunctiveGraph."""
    g = ConjunctiveGraph()
    patterns = [os.path.join(RDF_DIR, f"*{ext}") for ext in FORMAT_MAP]
    files = [f for pat in patterns for f in glob.glob(pat)]

    if not files:
        logger.warning("No RDF files found in '%s'. Add .ttl/.rdf/.n3/.jsonld files.", RDF_DIR)
    else:
        for path in sorted(files):
            ext = os.path.splitext(path)[1].lower()
            fmt = FORMAT_MAP.get(ext, "turtle")
            try:
                g.parse(path, format=fmt)
                logger.info("Loaded %s (%d triples total)", path, len(g))
            except Exception as exc:
                logger.error("Failed to parse %s: %s", path, exc)

    return g


# Load once at startup; reload endpoint available for dev convenience
graph = load_graph()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    triple_count = len(graph)
    return render_template("index.html", triple_count=triple_count)


@app.route("/sparql", methods=["GET", "POST"])
def sparql():
    """Execute a SPARQL SELECT / ASK / CONSTRUCT / DESCRIBE query."""
    query = (request.form.get("query") or request.args.get("query") or "").strip()

    if not query:
        return jsonify({"error": "No query provided."}), 400

    try:
        results = graph.query(query)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    # Determine result type
    if results.type == "SELECT":
        vars_ = [str(v) for v in results.vars]
        rows = []
        for row in results:
            rows.append({var: (str(row[var]) if row[var] is not None else None)
                         for var in vars_})
        return jsonify({"type": "SELECT", "vars": vars_, "results": rows})

    elif results.type == "ASK":
        return jsonify({"type": "ASK", "result": bool(results.askAnswer)})

    elif results.type in ("CONSTRUCT", "DESCRIBE"):
        # Return Turtle serialisation
        ttl = results.graph.serialize(format="turtle")
        return jsonify({"type": results.type, "graph": ttl})

    return jsonify({"error": "Unsupported query type."}), 400


@app.route("/reload", methods=["POST"])
def reload_graph():
    """Reload all RDF files from disk without restarting the server."""
    global graph
    graph = load_graph()
    return jsonify({"status": "reloaded", "triples": len(graph)})


@app.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "triples": len(graph),
        "rdf_dir": os.path.abspath(RDF_DIR),
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
