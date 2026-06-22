"""Avaliação do Agente ELLAS sobre as competency questions da dissertação.

Roda TODAS as perguntas do catálogo (Query_SPARQL.txt) pelo agente e mede:
  - geração: o agente produziu um SPARQL?
  - validade: a consulta executou sem erro no GraphDB?
  - utilidade: retornou ao menos 1 resultado?
  - esforço: nº de tentativas (auto-correção) e se precisou relaxar filtros.

Gera métricas agregadas + relatórios evaluation_report.csv / .json
(prontos para citar na dissertação).

Uso:
  python evaluate.py            # roda todas as perguntas
  python evaluate.py 5          # roda só as 5 primeiras (teste rápido)
"""
import sys
import csv
import json
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from agent import CATALOG, run_agent, count_bindings


def evaluate(limit=None, delay=None):
    # Sem rate limit no Ollama (local); só espaçamos no Groq (nuvem)
    if delay is None:
        from config import LLM_PROVIDER
        delay = 0.0 if LLM_PROVIDER == "ollama" else 5.0
    items = CATALOG[:limit] if limit else CATALOG
    rows = []
    print(f"Avaliando {len(items)} competency questions...\n")

    for i, item in enumerate(items, 1):
        q = item["question"]
        if i > 1 and delay:
            time.sleep(delay)  # respeita o rate limit (TPM) da Groq
        res = run_agent(q)
        nb = count_bindings(res["results"])
        valid = res["error"] is None and res["sparql"] is not None
        non_empty = valid and nb > 0
        status = "OK " if non_empty else ("VAZIO" if valid else "ERRO")
        rows.append({
            "n": i,
            "question": q,
            "status": status,
            "bindings": nb,
            "attempts": res["n_attempts"],
            "relaxed": res["relaxed"],
            "valid": valid,
            "non_empty": non_empty,
            "error": (res["error"] or "")[:200],
            "elapsed": res["elapsed"],
            "sparql": (res["sparql"] or "").strip(),
        })
        print(f"[{i:>2}/{len(items)}] {status} | {nb:>4} res | {res['n_attempts']}x"
              f"{' (relaxed)' if res['relaxed'] else ''} | {q[:60]}")

    total = len(rows)
    n_valid = sum(r["valid"] for r in rows)
    n_nonempty = sum(r["non_empty"] for r in rows)
    n_relaxed = sum(r["relaxed"] for r in rows)
    avg_attempts = sum(r["attempts"] for r in rows) / total if total else 0

    print("\n" + "=" * 60)
    print("RESUMO DA AVALIAÇÃO")
    print("=" * 60)
    print(f"Total de perguntas .............. {total}")
    print(f"SPARQL válido (sem erro) ........ {n_valid}/{total} ({100*n_valid/total:.0f}%)")
    print(f"Com resultados (não vazio) ...... {n_nonempty}/{total} ({100*n_nonempty/total:.0f}%)")
    print(f"Precisaram relaxar filtros ...... {n_relaxed}")
    print(f"Média de tentativas ............. {avg_attempts:.2f}")

    # Relatórios
    with open("evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": total, "valid": n_valid, "non_empty": n_nonempty,
                "relaxed": n_relaxed, "avg_attempts": round(avg_attempts, 2),
                "valid_rate": round(n_valid / total, 3) if total else 0,
                "non_empty_rate": round(n_nonempty / total, 3) if total else 0,
            },
            "rows": rows,
        }, f, ensure_ascii=False, indent=2)

    with open("evaluation_report.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "status", "bindings", "attempts", "relaxed", "elapsed", "question"])
        for r in rows:
            w.writerow([r["n"], r["status"], r["bindings"], r["attempts"],
                        r["relaxed"], r["elapsed"], r["question"]])

    print("\nRelatórios salvos: evaluation_report.json / evaluation_report.csv")
    return rows


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    evaluate(limit)
