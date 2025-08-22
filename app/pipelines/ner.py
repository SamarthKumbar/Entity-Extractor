
import re, json, sys
from datetime import datetime
import numpy as np

def try_load_hf():
    try:
        from transformers import pipeline
        nlp = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        return nlp
    except Exception:
        return None

def normalize_date(s):
    s = s.strip()
    fmts = ["%m/%d/%y","%m/%d/%Y","%d/%m/%Y","%d %B %Y","%d %b %Y","%Y-%m-%d"]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f).date()
            if dt.year < 1970:
                dt = dt.replace(year=dt.year + 100)
            return dt.isoformat()
        except Exception:
            pass
    m = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{2,4})", s)
    if m:
        d, mon, y = m.groups()
        y = "20"+y if len(y)==2 else y
        for fmt in ["%d %B %Y","%d %b %Y"]:
            try:
                return datetime.strptime(f"{d} {mon} {y}", fmt).date().isoformat()
            except Exception:
                pass
    return s

def parse_money_span(span):
    s = span.replace(",", "")
    cur = None
    mcur = re.search(r"\b([A-Z]{3})\b", s)
    if mcur: cur = mcur.group(1)
    mamt = re.search(r"([0-9]+(?:\.[0-9]+)?)", s)
    amount = float(mamt.group(1)) if mamt else None
    unit = None
    if re.search(r"\b(mio|million|mn)\b", s, re.I): unit = "million"
    elif re.search(r"\b(bn|billion)\b", s, re.I): unit = "billion"
    return {"amount": amount, "currency": cur, "unit": unit}

def regex_finance(text):
    ent = {}
    m = re.search(r"\b([A-Z]{2}[A-Z0-9]{9}[0-9])\b", text)
    if m: ent["ISIN"] = m.group(1)
    m = re.search(r"\b([A-Z]{3})?\s*([0-9]+(?:\.[0-9]+)?)\s*(mio|million|mn|bn|billion)\b", text, re.I)
    if m:
        cur = m.group(1).upper() if m.group(1) else None
        amt = float(m.group(2))
        unit = "million" if m.group(3).lower() in ["mio","million","mn"] else "billion"
        ent["Notional"] = {"amount": amt, "currency": cur, "unit": unit}
    m = re.search(r"\b(Quarterly|Monthly|Semi[- ]?annual|Semiannual|Annually|Annual|Bi[- ]?weekly|Weekly)\b", text, re.I)
    if m: ent["PaymentFrequency"] = m.group(1).capitalize()
    m = re.search(r"\b([a-z]{3,5}\s*\+\s*\d+\s*bps)\b", text, re.I)
    if m: ent["Coupon/Spread"] = re.sub(r"\s+", "", m.group(1))
    m = re.search(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b", text)
    if m: ent["Date"] = normalize_date(m.group(1))
    m = re.search(r"\b([A-Z0-9]{3,})\s+FLOAT\b", text)
    if m: ent["Underlying"] = m.group(1)
    m = re.search(r"Underlying\s*[:\-]\s*([^\n\r]+)", text, re.I)
    if m and "Underlying" not in ent: ent["Underlying"] = m.group(1).strip()
    m = re.search(r"\b(BANK\s+[A-Z]+)\b", text)
    if m: ent["Counterparty"] = m.group(1)
    return ent

def map_hf_to_schema(hf_results, text):
    mapped = {"_raw_ner": hf_results}
    orgs = [r for r in hf_results if r.get("entity_group") == "ORG"]
    dates = [r for r in hf_results if r.get("entity_group") == "DATE"]
    money = [r for r in hf_results if r.get("entity_group") == "MONEY"]
    prods = [r for r in hf_results if r.get("entity_group") in ("MISC","PRODUCT")]
    if orgs:
        org = max(orgs, key=lambda r: len(r["word"]))
        mapped["Counterparty"] = org["word"].strip()
    if dates:
        d = normalize_date(dates[0]["word"])
        mapped["Date"] = d
    if money:
        span = money[0]["word"]
        mapped["Notional"] = parse_money_span(span)
    m = re.search(r"\b([A-Z0-9]{3,})\s+FLOAT\b", text)
    if m:
        mapped["Underlying"] = m.group(1)
    elif prods:
        mapped["Underlying"] = prods[0]["word"]
    return mapped

def merge_dicts(a, b):
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k].update(v)
        else:
            out[k] = v
    return out

def convert_float32_to_float(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_float32_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_float32_to_float(elem) for elem in obj]
    else:
        return obj

def run_ner(file_path=None, text_content=None, out_path=None):
    if file_path:
        try:
            text = open(file_path, "r", encoding="utf-8").read()
        except FileNotFoundError:
            print(f"Error: Input file not found at {file_path}")
            sys.exit(1)
    elif text_content:
        text = text_content
    else:
        raise ValueError("Either file_path or text_content must be provided")

    nlp = try_load_hf()
    engine = "huggingface" if nlp else "regex"
    base = {}
    
    if nlp:
        try:
            hf_res = nlp(text)
            base = map_hf_to_schema(hf_res, text)
        except Exception as e:
            print(f"Hugging Face pipeline error: {e}")
            engine = "regex"
            base = {}

    regex_res = regex_finance(text)
    result = merge_dicts(base, regex_res)
    result["_engine"] = engine
    result = convert_float32_to_float(result)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result

