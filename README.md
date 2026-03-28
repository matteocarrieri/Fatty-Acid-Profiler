# 🧪 Fatty Acid Profiler

> Analisi automatizzata del profilo in acidi grassi di **latte e formaggi** da dati cromatografici GC-FAME  
> Interfaccia desktop Tkinter · Python · Indici nutrizionali · Visualizzazioni interattive

---

## 📌 Descrizione

**Fatty Acid Profiler** è un'applicazione desktop sviluppata in Python per l'analisi qualitativa e quantitativa del profilo in acidi grassi di matrici lattiero-casearie, a partire da dati cromatografici espressi come **% di esteri metilici degli acidi grassi (FAME)**.

Il tool calcola automaticamente i principali **indici nutrizionali lipidici** utilizzati in letteratura scientifica e genera visualizzazioni comparative tra campioni di diversa provenienza (latte bovino, ovino, caprino; formaggi DOP).

---

## 🎯 Funzionalità principali

| Feature | Descrizione |
|---|---|
| 📂 Import CSV | Caricamento dati GC-FAME in formato tabulare |
| 📋 Tabella acidi grassi | Visualizzazione codice cromatografico, categoria (SFA/MUFA/PUFA), tipo n- |
| 📐 Indici nutrizionali | Calcolo automatico di AI, TI, PUFA/SFA, n-3/n-6, h/H, HI |
| 📈 Grafici | Profilo a barre + torta SFA/MUFA/PUFA per campione |
| ⚖ Confronto | Istogramma comparativo degli indici tra tutti i campioni |
| 💾 Export | Report CSV o Excel con dati + indici calcolati |

---

## 📐 Indici nutrizionali implementati

### Indice di Aterogenicità (AI)
Proposto da **Ulbricht & Southgate (1991)**:

$$AI = \frac{C12:0 + 4 \times C14:0 + C16:0}{\Sigma MUFA + \Sigma PUFA_{n-6} + \Sigma PUFA_{n-3}}$$

> **AI < 1.0** considerato desiderabile. Valori elevati correlano con maggiore rischio aterogeno.

### Indice di Trombogenicità (TI)
$$TI = \frac{C14:0 + C16:0 + C18:0}{0.5 \cdot \Sigma MUFA + 0.5 \cdot \Sigma n\text{-}6 + 3 \cdot \Sigma n\text{-}3 + (n\text{-}3/n\text{-}6)}$$

> **TI < 1.5** desiderabile. Misura la tendenza pro-trombotica del profilo lipidico.

### Rapporto PUFA/SFA
> ≥ 0.45 raccomandato dalla **WHO/FAO (2010)**.

### Rapporto n-3/n-6
> ≥ 0.25 ottimale per il bilanciamento della risposta infiammatoria (**Simopoulos, 2002**).

### Rapporto h/H (ipocolesterolemizzanti / ipercolesterolemizzanti)
$$h/H = \frac{C18:1 + \Sigma PUFA_{n-6} + \Sigma PUFA_{n-3}}{C12:0 + C14:0 + C16:0}$$

> **Santos-Silva et al. (2002)**. Valori più alti indicano profilo più favorevole.

---

## 📊 Dataset incluso

Il dataset di riferimento (`data/latte_e_formaggi.csv`) contiene composizioni in acidi grassi per:

| Campione | Origine | n acidi grassi |
|---|---|---|
| Latte Bovino | *Bos taurus* | 18 |
| Latte Ovino | *Ovis aries* | 18 |
| Latte Caprino | *Capra hircus* | 18 |
| Parmigiano Reggiano | DOP — stagionatura 24 mesi | 18 |
| Pecorino Romano | DOP — latte ovino intero | 18 |

Valori basati su letteratura peer-reviewed (Chilliard et al., 2006; Nudda et al., 2003; INRAN, 2000).

---

## 🗂 Formato CSV atteso

```csv
sample,fatty_acid,abbreviation,category,n_type,percentage
Latte Bovino,Acido Palmitico,C16:0,SFA,,28.01
Latte Bovino,Acido Oleico,C18:1 n-9,MUFA,n-9,22.98
Latte Bovino,Acido Linoleico,C18:2 n-6,PUFA,n-6,2.51
```

| Colonna | Tipo | Note |
|---|---|---|
| `sample` | string | Nome del campione (opzionale, default "Campione") |
| `fatty_acid` | string | Nome esteso dell'acido grasso |
| `abbreviation` | string | Codice cromatografico (es. C18:1 n-9) |
| `category` | string | SFA / MUFA / PUFA |
| `n_type` | string | n-3 / n-6 / n-7 / n-9 (opzionale) |
| `percentage` | float | % FAME sul totale |

---

## 🚀 Installazione e avvio

```bash
# 1. Clona la repository
git clone https://github.com/<tuo-username>/fatty-acid-profiler.git
cd fatty-acid-profiler

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Avvia l'applicazione
python app.py
```

> **Requisiti**: Python ≥ 3.10, tkinter (incluso nella distribuzione standard)

---

## 🖥 Screenshot

> *L'app carica automaticamente il dataset di esempio all'avvio.*

| Tab | Contenuto |
|---|---|
| 📋 Dati | Tabella codificata per categoria (rosa=SFA, blu=MUFA, verde=PUFA) |
| 📐 Indici | 9 card con valori, interpretazione e riferimento bibliografico |
| 📈 Grafici | Profilo a barre + torta per il campione selezionato |
| ⚖ Confronto | Istogramma comparativo multi-campione |

---

## 📚 Riferimenti bibliografici

- Ulbricht, T.L.V. & Southgate, D.A.T. (1991). Coronary heart disease: seven dietary factors. *The Lancet*, 338(8773), 985–992.
- Santos-Silva, J., Bessa, R.J.B. & Santos-Silva, F. (2002). Effect of genotype, feeding system and slaughter weight on the quality of light lambs. *Livestock Production Science*, 77(2–3), 187–194.
- Simopoulos, A.P. (2002). The importance of the ratio of omega-6/omega-3 essential fatty acids. *Biomedicine & Pharmacotherapy*, 56(8), 365–379.
- Chilliard, Y. et al. (2006). Ruminant milk fat plasticity. *Reproduction Nutrition Development*, 46(5), 565–579.
- WHO/FAO (2010). *Fats and fatty acids in human nutrition*. FAO Food and Nutrition Paper 91.

---

## 👨‍💻 Autore

**Matteo**  
MSc Candidate — Biotecnologie Mediche, Veterinarie e Farmaceutiche (LM-9)  
Università di Bologna · DIMEVET  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=flat&logo=linkedin)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-grey?style=flat&logo=github)](https://github.com)

---

## 📄 Licenza

MIT License — libero utilizzo con attribuzione.

