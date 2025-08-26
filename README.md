# SHasaS - backend

**Autor:** Jiří Vecko

---

## 1. Abstrakt

Cílem tohoto projektu je navrhnout a popsat architekturu backendového systému, který umožní umělé inteligenci (AI) efektivně pracovat s technickými daty o chytré domácnosti. Systém transformuje nestrukturované dokumenty (PDF, HTML, obrázky) do multimodální znalostní báze, která se skládá z vektorové databáze a znalostního grafu. Jádrem systému je RAG (Retrieval-Augmented Generation), který poskytuje relevantní kontext AI agentovi pro generování přesných odpovědí. Interakce se systémem probíhá přes REST API.

---

## 2. Architektura Řešení

### 2.1 High-Level Diagram

Architektura je navržena tak, aby oddělovala proces zpracování dat (ingestion) od procesu dotazování (querying). Znázorňuje ji `HL diagram`.

![HL diagram](hl-diagram.drawio.svg)

### 2.2 Hlavní komponenty:

* **Ingestion Pipeline:** Přijímá zdrojové dokumenty (PDF, HTML, CSV, Markdown, obrázky), provádí parsování a extrakci textu/struktur a posílá data k indexaci.
* **Indexace:** Zajišťuje, že dotaz najde správné kousky textu nebo přesné vztahy a RAG díky tomu sestaví kvalitní odpověď s citacemi.
* **Storage Layer:**
    * **Vector Database:** Ukládá krátké kusy textu (chunky) a jejich číselné vektory, aby šlo hledat podle významu, ne jen podle shody slov.
    * **Knowledge Graph:** Ukládá fakta a vztahy (např. zařízení → výrobce → parametry), aby šly dělat přesné dotazy a snadno se dohledalo, odkud informace pochází.
* **RAG Orchestrator:** 
  * Přijme dotaz z API, najde relevantní texty ve Vector DB a související fakta v Knowledge Graphu, spojí je dohromady a připraví zadání pro LLM. 
  * Následně ze získaného textu udělá finální odpověď s citacemi a metadaty.
* **LLM Agent:** Generuje odpověď v přirozeném jazyce na základě poskytnutého kontextu a instrukcí; vrací „raw“ výstup ke zpracování orchestrátorem.
* **API Gateway:** Poskytuje jednoduché HTTP rozhraní (např. `POST /query` a `POST /feedback`), kontroluje vstupy a práva a vrací finální odpovědi ve formátu JSON klientům.

### 2.3 Výběr technologií a zdůvodnění

Následující tabulka podrobně popisuje výběr technologií pro jednotlivé moduly systému, včetně zdůvodnění volby s ohledem na klíčové vlastnosti.

| Modul | Navržená Technologie | Zdůvodnění (Výkon, Licence, Integrace, Omezení) |
| :--- | :--- | :--- |
| **Ingestion Pipeline** | **Prefect** | **Výkon:** Jednoduše řídí úlohy „na pozadí“ (asynchronně), plánování a automatické opakování neúspěšných kroků. <br> **Licence:** Open‑source, vhodné i pro komerční použití; k dispozici i cloud verze. <br> **Integrace:** Přirozené pro Python, snadné spouštění parsovacích skriptů a volání API. <br> **Omezení:** Menší ekosystém pluginů než u „větších“ orchestrátorů, ale výrazně snazší začátky. |
| **Indexace** | **LlamaIndex (LlamaIndex Inc.)** | **Výkon:** Pomáhá budovat RAG. Umí rozdělit text na menší části (chunky), vytvořit indexy pro rychlé hledání a nastavit “retrievery”; zvládne i chytřejší dělení a zkracování textu (sumarizaci). <br> **Licence:** MIT (volná licence, dá se použít i v komerčních projektech bez složitých podmínek). <br> **Integrace:** Funguje jako “lepidlo” mezi soubory, modely pro embeddings, vektorovými databázemi a grafy; má spoustu hotových konektorů, takže se rychle propojuje. <br> **Omezení:** Je to vyšší vrstva nad detaily, takže při řešení nízkoúrovňových chyb může být ladění složitější. |
| **Storage Layer** | *Konceptuální vrstva* | Vrstvu tvoří dvě specializované databáze níže; dohromady tvoří znalostní bázi pro sémantické vyhledávání i přesná fakta. |
| **Vector Database** | **Qdrant** | **Výkon:** Rychlé sémantické vyhledávání, „designed for real‑time applications“ – nízká latence pro online dotazy. <br> **Licence:** Open‑source, přívětivé pro firmy. <br> **Integrace:** Oficiální Python klient, podpora v LlamaIndex; filtry nad metadaty. <br> **Omezení:** Potřebuje RAM pro vektory a základní DevOps péči. |
| **Knowledge Graph** | **Memgraph** | **Výkon:** Rychlá grafová databáze v paměti (in‑memory), vhodná pro dotazy v reálném čase – třeba hledání kompatibilit a závislostí. <br> **Licence:** K dispozici komerční edice, použitelné ve firmách. <br> **Integrace:** Existuje Python klient. <br> **Omezení:** Pro analytiku nad celým grafem je potřeba dobře navržené schéma a indexy. |
| **RAG Orchestrator** | **LlamaIndex „Query Engine“** | **Výkon:** Řídí kroky RAG – vyhledá data v Qdrant (vektory) a v Memgraphu (graf), výsledky seřadí a zkrátí, a připraví zadání (prompt) pro LLM. <br> **Licence:** MIT (volná licence, dá se použít i v komerčních projektech bez složitých podmínek). <br> **Integrace:** Snadno propojuje LLM, vektorové databáze i grafové databáze. <br> **Omezení:** Je to framework – složitější přizpůsobení. |
| **LLM Agent** | **OpenAI** | **Výkon:** Vysoká kvalita odpovědí a dobrá rychlost pro produkční RAG scénáře. <br> **Licence:** Komerční API (platí se podle použití). <br> **Integrace:** Jednoduché REST API a oficiální knihovny; dobrá podpora i v LlamaIndex. <br> **Omezení:** Náklady a limity; u citlivých dat je nutné řešit zásady a šifrování. |
| **API Gateway** | **FastAPI** (framework) | **Výkon:** Velmi rychlý Python framework. <br> **Licence:** MIT (volné použití, i komerční). <br> **Integrace:** Snadno napojí Python logiku (např. RAG orchestrátor) a umí automaticky vygenerovat dokumentaci (OpenAPI/Swagger). <br> **Omezení:** Menší ekosystém doplňků než u starších frameworků (např. Django). |


### 2.4 Testování a metriky

### Navrhované testovací metody

Tři úrovně testování:

1.  **Automatické testy (na úrovni kódu):**
    * **Unit testy:** Ověřují samostatnou funkčnost jednotlivých komponent (např. funkce pro parsování PDF, formátování API odpovědi).
    * **Integrační testy:** Testují spolupráci mezi moduly (např. zda RAG orchestrátor správně volá vektorovou databázi a LLM agenta). Cílem je odhalit problémy v komunikaci mezi komponentami.

2.  **Evaluační skripty (automatizované hodnocení kvality):**
    * **Vytvoření "zlatého" datasetu:** Připraví se sada stovek párů otázek a ideálních odpovědí.
    * **Spouštění skriptů:** Systém automaticky odpoví na všechny otázky z datasetu. Následně se vyhodnotí výstupy a vypočítají metriky jako *Faithfulness* a *Answer Relevancy* porovnáním s "ideálním" stavem. To umožňuje rychlé testování při každé změně v systému.

3.  **Lidské hodnocení:**
    * **Testování:** Dvě verze systému (např. s různými LLM nebo nastavením promptu) jsou nasazeny a uživatelé nebo testeři hodnotí, která verze dává lepší odpovědi.
    * **Pravidelné revize:** Specialisté pravidelně procházejí vzorek odpovědí a hodnotí jejich správnost a užitečnost na škále (např. 1-5). Zpětná vazba z endpointu `/feedback` je cenným zdrojem pro tento proces.

### Metriky

Metriky lze rozdělit na dvě hlavní kategorie: **hodnocení kvality RAG pipeline** a **provozní metriky**.

#### Kvalita RAG pipeline:
* **Faithfulness (Věrnost):** Měří, do jaké míry je vygenerovaná odpověď fakticky podložena poskytnutým kontextem. Cílem je minimalizovat "halucinace" LLM. Vyjadřuje se jako procentuální shoda.
* **Answer Relevancy (Relevance odpovědi):** Hodnotí, jak dobře odpověď odpovídá na původní dotaz uživatele.
* **Context Precision & Recall (Přesnost a úplnost kontextu):** 
**Precision** měří, kolik z nalezených dokumentů bylo relevantních. **Recall** měří, kolik ze všech relevantních dokumentů v databázi se podařilo najít.
* **Knowledge Coverage (Pokrytí znalostí):** Vyjadřuje, na jaké procento otázek z předem definovaného testovacího setu je systém schopen uspokojivě odpovědět.

#### Provozní metriky:
* **Doba odezvy (Latency):** Celkový čas od přijetí dotazu na API po vrácení odpovědi klientovi.
* **Chybovost (Error Rate):** Procento požadavků, které selhaly z technických důvodů (např. chyba v kódu, nedostupnost LLM API).

---

## 3. Implementační detail

### 3.1 Pseudokód: Segmentace dokumentů na smysluplné bloky

Cílem je rozdělit dokumenty na bloky, které jsou dostatečně malé pro kontextové okno LLM, ale zároveň dostatečně velké na to, aby obsahovaly ucelenou myšlenku.

[segmentation.py](segmentation.py)

---

## 4. Návrh API rozhraní

Komunikace probíhá přes REST API ve formátu JSON.

### Endpoint: `POST /query`

Zadání dotazu a získání odpovědi od AI agenta.

**Request Body:**

```json
{
  "query": "Jaké jsou komunikační protokoly podporované zařízením Shelly Pro 4PM (chytrý spínač s měřením spotřeby)?",
  "session_id": "user_session_1a2b3c",
  "filters": {
    "manufacturer": "Shelly",
    "document_type": "datasheet"
  }
}
```

**Successful Response (200 OK):**

```json
{
  "answer": "Zařízení Shelly Pro 4PM podporuje komunikaci přes Wi-Fi (802.11 b/g/n), Bluetooth 4.2 pro snadné párování a také LAN (Ethernet).",
  "context": [
    {
      "source_document": "shelly_pro_4pm_datasheet_v1.2.pdf",
      "page": 2,
      "relevance_score": 0.92,
      "content": "Connectivity: Wi-Fi (2.4 GHz), Bluetooth 4.2, and LAN interface for stable connection."
    },
    {
      "source_document": "shelly_pro_line_manual.pdf",
      "page": 12,
      "relevance_score": 0.85,
      "content": "All Pro line devices feature both Wi-Fi and Ethernet connectivity..."
    }
  ],
  "query_id": "q_a1b2c3d4e5"
}
```

### Endpoint: `POST /feedback`

Odeslání zpětné vazby na kvalitu odpovědi pro budoucí vylepšování systému.

**Request Body:**

```json
{
  "query_id": "q_a1b2c3d4e5",
  "rating": 5,
  "is_helpful": true,
  "correction": null
}
```

**Successful Response (202 Accepted):**

```json
{
  "status": "feedback_received",
  "query_id": "q_a1b2c3d4e5"
}
```
---

## 5. Schéma komunikačního rozhraní mezi moduly

* Klient pošle HTTP POST požadavek na API Gateway.

* API Gateway validuje požadavek a předá dotaz RAG Orchestratoru.

* RAG Orchestrator zahájí asynchronní volání:

  * Odešle dotaz na sémantické vyhledávání (převod na číselné vyjádření) do Vector Database.

  * Odešle dotaz na vyhledání entit a vztahů do Knowledge Graph.

  * Obě databáze vrátí relevantní data (segmenty textu a fakta).

* RAG Orchestrator zkombinuje data do jednoho kontextu a sestaví prompt.

* Prompt je odeslán do LLM Agent.

* LLM Agent vrátí vygenerovanou odpověď.

* RAG Orchestrator zkompletuje finální JSON odpověď včetně zdrojů.

* API Gateway odešle HTTP 200 odpověď Klientovi.