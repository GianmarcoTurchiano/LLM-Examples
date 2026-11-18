# Esempi d'uso degli LLM (Large Language Model)

Esempi didattici che mostrano come utilizzare i "modelli di linguaggi" istanziati localmente o remotamente con [Ollama](https://docs.ollama.com/) per mezzo della libreria Python ufficiale.

```bash 
git clone https://github.com/GianmarcoTurchiano/LLM-Examples
cd LLM-Examples
python -m venv .venv

# Su Linux/MacOS:
source .venv/bin/activate
# Altrimenti, su Windows:
./.venv/Scripts/Activate.ps1

pip install -r requirements.txt
```

Questa repository contiene due notebook, che illustrano due tipologie di LLM.

- [**Decision Models**](https://github.com/GianmarcoTurchiano/LLM-Examples/blob/main/decision_models.ipynb) [[Kaggle](https://www.kaggle.com/code/gianmarcoturchiano/decision-models-examples)]
    - Tipi di domande:
        - Noul;
        - Choice;
        - Score.
    - Impiegare le risposte di un modello decisionale in un'applicazione.
- [**Autoregressive Decoders**](https://github.com/GianmarcoTurchiano/LLM-Examples/blob/main/text_generation.ipynb) [[Kaggle](https://www.kaggle.com/code/gianmarcoturchiano/text-generation-examples/notebook?scriptVersionId=370820485)]
    - Inviare prompt a un modello;
    - Impostare un prompt di sistema;
    - Conversare col modello;
    - Manipolare la cronologia dei messaggi;
    - Output strutturati;
    - Esporre "tool" al modello;
    - Loop "agentico".