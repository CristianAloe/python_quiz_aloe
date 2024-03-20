from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(100), nullable=False)


# Ripulisci il database eliminando tutte le domande attuali
def delete_all_questions():
    with app.app_context():
        db.session.query(Question).delete()
        db.session.commit()

# Aggiungi domande relative agli argomenti specificati
def add_questions():
    with app.app_context():
        # Ripulisci il database prima di aggiungere nuove domande
        delete_all_questions()

        # Lista di argomenti e relative domande con risposte
        topics_questions = [
            ("Sviluppo di intelligenza artificiale in Python", [
                ("Qual è uno dei principali framework per lo sviluppo di Intelligenza Artificiale in Python?", "TensorFlow", "PyTorch", "Keras"),
                ("Cosa si intende per 'transfer learning'?", "Utilizzare conoscenze apprese da un problema per risolverne un altro", "Trasferire dati tra dispositivi", "Un metodo per trasferire la conoscenza di un modello ad un altro"),
                ("Quale funzione di attivazione è comunemente usata in reti neurali per la classificazione binaria?", "Sigmoid", "ReLU", "Tanh"),
                ("Cosa significa 'backpropagation' in machine learning?", "Un algoritmo per aggiornare i pesi della rete neurale", "Un tipo di rete neurale ricorrente", "Un metodo per generare nuove istanze di dati di addestramento"),
                ("Cosa si intende per 'batch normalization' in deep learning?", "Normalizzare gli input di ogni layer per accelerare l'addestramento", "Ridurre la dimensione del batch di addestramento", "Normalizzare i dati di input prima di addestrare il modello")
            ]),
            ("Visione computerizzata", [
                ("Cosa è un filtro Sobel?", "Un filtro per rilevare il gradiente dell'immagine", "Un filtro per la riduzione del rumore", "Un filtro per la segmentazione dell'immagine"),
                ("Che cos'è l'operatore di Canny?", "Un algoritmo per rilevare i bordi nelle immagini", "Un algoritmo per la trasformazione geometrica delle immagini", "Un algoritmo per l'estrazione di features locali nelle immagini"),
                ("Cosa fa l'algoritmo di RANSAC?", "Trova la migliore trasformazione tra insiemi di punti", "Rileva i contorni nelle immagini", "Calcola la distanza euclidea tra punti"),
                ("Cosa si intende per 'segmentazione semantica'?", "Assegnare una classe ad ogni pixel dell'immagine", "Dividere l'immagine in regioni omogenee", "Estrarre features da un'immagine"),
                ("Qual è uno dei principali dataset utilizzati per il riconoscimento di oggetti?", "COCO", "Imagenet", "MNIST")
            ]),
            ("NLP (Programmazione neurolinguistica)", [
                ("Cosa è l'analisi sentimentale?", "Identificare estrarre opinioni e sentimenti da testi", "Generare testi in linguaggio naturale", "Analizzare la struttura sintattica di un testo"),
                ("Che cos'è l'elaborazione del linguaggio naturale?", "Il campo della linguistica computazionale che si occupa dell'interazione tra computer e linguaggio umano", "Un metodo per tradurre automaticamente il linguaggio naturale in linguaggio di programmazione", "Un'analisi del linguaggio basata su regole grammaticali"),
                ("Cosa fa un modello di lingua?", "Assegna probabilità a sequenze di parole", "Traduce testi da una lingua all'altra", "Genera testi casuali"),
                ("Cos'è l'estrazione di informazioni?", "Estrae informazioni strutturate da testi non strutturati", "Trova parole chiave nei testi", "Filtra le informazioni non rilevanti"),
                ("Qual è uno degli algoritmi più utilizzati per il part-of-speech tagging?", "HMM (Hidden Markov Model)", "SVM (Support Vector Machine)", "K-means")
            ]),
            ("Applicazione di modelli di intelligenza artificiale alle applicazioni Python", [
                ("Qual è uno dei principali framework per lo sviluppo di applicazioni di intelligenza artificiale in Python?", "Scikit-learn", "PyQt", "Dash"),
                ("Cosa si intende per 'pipeline' in machine learning?", "Una sequenza di trasformazioni dei dati seguita da un modello di apprendimento", "Un tipo di modello neurale", "Un metodo per creare interfacce grafiche"),
                ("Cosa fa un modello di classificazione?", "Assegna classi a nuovi dati in base a quelli di addestramento", "Filtra i dati di addestramento", "Classifica i modelli in base alla loro precisione"),
                ("Cos'è il clustering?", "Un metodo per dividere i dati in gruppi omogenei", "Un metodo per generare dati casuali", "Un tipo di regressione"),
                ("Qual è uno dei principali algoritmi di clustering?", "K-means", "SVM (Support Vector Machine)", "Linear Regression")
            ])
        ]

        # Aggiungi domande al database
        for topic, questions in topics_questions:
            for question, option1, option2, option3 in questions:
                correct_option = option1  # La prima opzione è quella corretta
                random.shuffle([option1, option2, option3])  # Mischia le opzioni
                new_question = Question(question=question, option1=option1, option2=option2, option3=option3, answer=correct_option)
                db.session.add(new_question)

        # Esegui il commit delle modifiche
        db.session.commit()

# Aggiungi le nuove domande al database
add_questions()


# Funzione per ottenere domande casuali dal database
def get_random_questions(num_questions):
    all_questions = Question.query.all()
    random_questions = random.sample(all_questions, min(len(all_questions), num_questions))
    return random_questions

# Funzione per calcolare il punteggio dell'utente
def calculate_score(answers):
    correct_answers = 0
    total_questions = len(answers)
    for answer in answers:
        question = Question.query.get(answer['id'])
        if question and answer['selected_option'] == question.answer:
            correct_answers += 1
    score = (correct_answers / total_questions) * 100
    print("Punteggio calcolato:", score)  # Aggiungi questa riga per stampare il punteggio calcolato
    return score
    return score


@app.route('/')
def index():
    add_questions()  # Aggiungi le domande al database se non sono già presenti
    return redirect(url_for('quiz'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Ottenere le risposte dell'utente
        user_answers = []
        for key, value in request.form.items():
            if key.isdigit():
                user_answers.append({'id': int(key), 'selected_option': value})
        if len(user_answers) != 10:  # Controlla se sono state risposte tutte le domande
            return "Per favore, rispondi a tutte le domande prima di continuare."
        score = calculate_score(user_answers)
        print("Punteggio passato a score.html:", score)  # Aggiungi questa riga per stampare il punteggio passato
        return redirect(url_for('score', score=score))  # Passa il punteggio come parametro nell'URL
    else:
        # Ottenere domande casuali dal database e renderizzare la pagina quiz.html
        questions = get_random_questions(10)
        return render_template('quiz.html', questions=questions)


# Dichiarazione della variabile globale best_score
best_score = 0

@app.route('/score')
def score():
    score = request.args.get('score', default=0, type=float)
    global best_score
    best_score = max(best_score, score)  # Aggiornamento del best_score
    return render_template('score.html', score=score)

# Aggiungi un endpoint per ottenere il best_score
@app.route('/best_score')
def get_best_score():
    return str(best_score)


# Inizializzazione del database
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)